"""Tests for cache service."""

import pytest
import json
import hashlib
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from schoolreport.services.cache import CacheService


@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL client."""
    client = AsyncMock()
    client.fetchrow = AsyncMock(return_value=None)
    client.execute = AsyncMock(return_value="DELETE 1")
    return client


@pytest.fixture
def cache_service(mock_postgres):
    """Create CacheService with mocked client."""
    return CacheService(postgres_client=mock_postgres, ttl_days=30)


class TestCacheService:
    """Test cases for CacheService."""

    def test_generate_key_deterministic(self, cache_service):
        """Test that cache key generation is deterministic."""
        params = {"cod_ibge": "2304400", "ano": 2024}

        key1 = cache_service._generate_key("ATM", params)
        key2 = cache_service._generate_key("ATM", params)

        assert key1 == key2
        assert key1.startswith("ATM:")

    def test_generate_key_different_reports(self, cache_service):
        """Test that different reports produce different keys."""
        params = {"cod_ibge": "2304400"}

        key_atm = cache_service._generate_key("ATM", params)
        key_ats = cache_service._generate_key("ATS", params)

        assert key_atm != key_ats

    def test_generate_key_different_params(self, cache_service):
        """Test that different parameters produce different keys."""
        key1 = cache_service._generate_key("ATM", {"cod_ibge": "2304400"})
        key2 = cache_service._generate_key("ATM", {"cod_ibge": "1234567"})

        assert key1 != key2

    def test_generate_key_param_order_independent(self, cache_service):
        """Test that parameter order doesn't affect key."""
        params1 = {"ano": 2024, "cod_ibge": "2304400"}
        params2 = {"cod_ibge": "2304400", "ano": 2024}

        key1 = cache_service._generate_key("ATM", params1)
        key2 = cache_service._generate_key("ATM", params2)

        assert key1 == key2

    @pytest.mark.asyncio
    async def test_get_cache_hit(self, cache_service, mock_postgres):
        """Test cache hit returns GCS path."""
        mock_postgres.fetchrow.return_value = {
            "gcs_path": "gs://bucket/reports/ATM/test.pdf",
            "expires_at": datetime.utcnow() + timedelta(days=10),
        }

        result = await cache_service.get("ATM", {"cod_ibge": "2304400"})

        assert result == "gs://bucket/reports/ATM/test.pdf"
        mock_postgres.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cache_miss(self, cache_service, mock_postgres):
        """Test cache miss returns None."""
        mock_postgres.fetchrow.return_value = None

        result = await cache_service.get("ATM", {"cod_ibge": "2304400"})

        assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_error_returns_none(self, cache_service, mock_postgres):
        """Test that cache errors return None (graceful degradation)."""
        mock_postgres.fetchrow.side_effect = Exception("Database error")

        result = await cache_service.get("ATM", {"cod_ibge": "2304400"})

        assert result is None

    @pytest.mark.asyncio
    async def test_set_cache_success(self, cache_service, mock_postgres):
        """Test setting cache entry."""
        await cache_service.set(
            report_id="ATM",
            params={"cod_ibge": "2304400"},
            gcs_path="gs://bucket/reports/ATM/test.pdf",
            ttl_days=30,
        )

        mock_postgres.execute.assert_called_once()

        # Verify SQL contains upsert
        call_args = mock_postgres.execute.call_args
        sql = call_args[0][0]
        assert "INSERT INTO report_cache" in sql
        assert "ON CONFLICT" in sql

    @pytest.mark.asyncio
    async def test_set_cache_uses_default_ttl(self, cache_service, mock_postgres):
        """Test that default TTL is used when not specified."""
        await cache_service.set(
            report_id="ATM",
            params={"cod_ibge": "2304400"},
            gcs_path="gs://bucket/reports/test.pdf",
        )

        # Verify expires_at was calculated with default TTL
        call_args = mock_postgres.execute.call_args
        params = call_args[0][1]
        expires_at = params["expires_at"]

        # Should be approximately 30 days from now
        expected = datetime.utcnow() + timedelta(days=30)
        assert abs((expires_at - expected).total_seconds()) < 60  # Within 1 minute

    @pytest.mark.asyncio
    async def test_set_cache_custom_ttl(self, cache_service, mock_postgres):
        """Test setting cache with custom TTL."""
        await cache_service.set(
            report_id="ATM",
            params={"cod_ibge": "2304400"},
            gcs_path="gs://bucket/reports/test.pdf",
            ttl_days=7,  # Custom TTL
        )

        call_args = mock_postgres.execute.call_args
        params = call_args[0][1]
        expires_at = params["expires_at"]

        expected = datetime.utcnow() + timedelta(days=7)
        assert abs((expires_at - expected).total_seconds()) < 60

    @pytest.mark.asyncio
    async def test_set_cache_error_does_not_raise(self, cache_service, mock_postgres):
        """Test that cache set errors don't propagate (non-critical operation)."""
        mock_postgres.execute.side_effect = Exception("Database error")

        # Should not raise
        await cache_service.set(
            report_id="ATM",
            params={"cod_ibge": "2304400"},
            gcs_path="gs://bucket/test.pdf",
        )

    @pytest.mark.asyncio
    async def test_invalidate_specific_params(self, cache_service, mock_postgres):
        """Test invalidating cache for specific parameters."""
        mock_postgres.execute.return_value = "DELETE 1"

        result = await cache_service.invalidate(
            report_id="ATM",
            params={"cod_ibge": "2304400"},
        )

        assert result == 1
        mock_postgres.execute.assert_called_once()

        # Verify SQL uses cache_key
        call_args = mock_postgres.execute.call_args
        sql = call_args[0][0]
        assert "DELETE FROM report_cache WHERE cache_key" in sql

    @pytest.mark.asyncio
    async def test_invalidate_all_for_report(self, cache_service, mock_postgres):
        """Test invalidating all cache entries for a report."""
        mock_postgres.execute.return_value = "DELETE 5"

        result = await cache_service.invalidate(report_id="ATM", params=None)

        assert result == 5

        # Verify SQL uses report_id
        call_args = mock_postgres.execute.call_args
        sql = call_args[0][0]
        assert "DELETE FROM report_cache WHERE report_id" in sql

    @pytest.mark.asyncio
    async def test_invalidate_error_returns_zero(self, cache_service, mock_postgres):
        """Test that invalidation errors return 0."""
        mock_postgres.execute.side_effect = Exception("Database error")

        result = await cache_service.invalidate(report_id="ATM")

        assert result == 0


class TestCacheKeyFormat:
    """Test cache key format and hashing."""

    def test_key_format(self, cache_service):
        """Test cache key format is report_id:hash."""
        key = cache_service._generate_key("ATM", {"cod_ibge": "2304400"})

        parts = key.split(":")
        assert len(parts) == 2
        assert parts[0] == "ATM"
        assert len(parts[1]) == 16  # SHA256 truncated to 16 chars

    def test_key_uses_sha256(self, cache_service):
        """Test that key uses SHA256 hash."""
        params = {"cod_ibge": "2304400", "ano": 2024}
        params_str = json.dumps(params, sort_keys=True)
        expected_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]

        key = cache_service._generate_key("ATM", params)

        assert key == f"ATM:{expected_hash}"

    def test_empty_params_generates_valid_key(self, cache_service):
        """Test that empty params still generate valid key."""
        key = cache_service._generate_key("ATSBR", {})

        assert key.startswith("ATSBR:")
        assert len(key.split(":")[1]) == 16
