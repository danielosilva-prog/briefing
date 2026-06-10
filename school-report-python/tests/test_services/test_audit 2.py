"""Tests for audit logging service."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock

from schoolreport.services.audit import AuditService


@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL client."""
    client = AsyncMock()
    client.execute = AsyncMock()
    client.fetch = AsyncMock(return_value=[])
    return client


@pytest.fixture
def audit_service(mock_postgres):
    """Create AuditService with mocked client."""
    return AuditService(postgres_client=mock_postgres)


class TestAuditService:
    """Test cases for AuditService."""

    @pytest.mark.asyncio
    async def test_log_start_creates_entry(self, audit_service, mock_postgres):
        """Test that log_start creates an audit entry."""
        job_id = uuid4()
        report_id = "ATM"
        parameters = {"cod_ibge": "2304400", "ano": 2024}
        requester = "test_user"

        audit_id = await audit_service.log_start(
            job_id=job_id,
            report_id=report_id,
            parameters=parameters,
            requester=requester,
        )

        # Should return a UUID
        assert audit_id is not None

        # Should have called execute with INSERT
        mock_postgres.execute.assert_called_once()
        call_args = mock_postgres.execute.call_args
        sql = call_args[0][0]
        assert "INSERT INTO audit_logs" in sql

    @pytest.mark.asyncio
    async def test_log_start_with_metadata(self, audit_service, mock_postgres):
        """Test log_start with extra metadata."""
        job_id = uuid4()
        metadata = {"version": "1.0.0", "source": "api"}

        audit_id = await audit_service.log_start(
            job_id=job_id,
            report_id="ATM",
            parameters={},
            requester="system",
            metadata=metadata,
        )

        assert audit_id is not None

        # Verify metadata was passed
        call_args = mock_postgres.execute.call_args
        params = call_args[0][1]
        assert params["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_log_start_sets_processing_status(self, audit_service, mock_postgres):
        """Test that log_start sets status to 'processing'."""
        job_id = uuid4()

        await audit_service.log_start(
            job_id=job_id,
            report_id="ATM",
            parameters={},
            requester="system",
        )

        call_args = mock_postgres.execute.call_args
        params = call_args[0][1]
        assert params["status"] == "processing"

    @pytest.mark.asyncio
    async def test_log_start_database_error_propagates(self, audit_service, mock_postgres):
        """Test that database errors in log_start propagate."""
        mock_postgres.execute.side_effect = Exception("Database error")

        job_id = uuid4()

        with pytest.raises(Exception, match="Database error"):
            await audit_service.log_start(
                job_id=job_id,
                report_id="ATM",
                parameters={},
                requester="system",
            )

    @pytest.mark.asyncio
    async def test_log_complete_updates_entry(self, audit_service, mock_postgres):
        """Test that log_complete updates the audit entry."""
        audit_id = uuid4()
        gcs_path = "gs://bucket/reports/test.pdf"
        duration_ms = 5000

        await audit_service.log_complete(
            audit_id=audit_id,
            gcs_path=gcs_path,
            duration_ms=duration_ms,
        )

        mock_postgres.execute.assert_called_once()
        call_args = mock_postgres.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "UPDATE audit_logs" in sql
        assert params["status"] == "completed"
        assert params["gcs_path"] == gcs_path
        assert params["duration_ms"] == duration_ms

    @pytest.mark.asyncio
    async def test_log_complete_error_does_not_raise(self, audit_service, mock_postgres):
        """Test that log_complete errors don't propagate (best effort)."""
        mock_postgres.execute.side_effect = Exception("Database error")

        audit_id = uuid4()

        # Should not raise
        await audit_service.log_complete(
            audit_id=audit_id,
            gcs_path="gs://bucket/test.pdf",
            duration_ms=1000,
        )

    @pytest.mark.asyncio
    async def test_log_failure_updates_entry(self, audit_service, mock_postgres):
        """Test that log_failure updates the audit entry."""
        audit_id = uuid4()
        error = "BigQuery timeout"
        duration_ms = 3000

        await audit_service.log_failure(
            audit_id=audit_id,
            error=error,
            duration_ms=duration_ms,
        )

        mock_postgres.execute.assert_called_once()
        call_args = mock_postgres.execute.call_args
        params = call_args[0][1]

        assert params["status"] == "failed"
        assert params["error"] == error
        assert params["duration_ms"] == duration_ms

    @pytest.mark.asyncio
    async def test_log_failure_error_does_not_raise(self, audit_service, mock_postgres):
        """Test that log_failure errors don't propagate."""
        mock_postgres.execute.side_effect = Exception("Database error")

        audit_id = uuid4()

        # Should not raise
        await audit_service.log_failure(
            audit_id=audit_id,
            error="Some error",
            duration_ms=1000,
        )


class TestAuditQuery:
    """Test cases for audit log querying."""

    @pytest.mark.asyncio
    async def test_query_returns_results(self, audit_service, mock_postgres):
        """Test querying audit logs."""
        mock_postgres.fetch.return_value = [
            {
                "id": str(uuid4()),
                "job_id": str(uuid4()),
                "report_id": "ATM",
                "status": "completed",
                "created_at": datetime.utcnow(),
            }
        ]

        results = await audit_service.query()

        assert len(results) == 1
        assert results[0]["report_id"] == "ATM"

    @pytest.mark.asyncio
    async def test_query_filter_by_report_id(self, audit_service, mock_postgres):
        """Test filtering by report_id."""
        await audit_service.query(report_id="ATM")

        call_args = mock_postgres.fetch.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "report_id = $report_id" in sql
        assert params["report_id"] == "ATM"

    @pytest.mark.asyncio
    async def test_query_filter_by_requester(self, audit_service, mock_postgres):
        """Test filtering by requester."""
        await audit_service.query(requester="admin@example.com")

        call_args = mock_postgres.fetch.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "requester = $requester" in sql
        assert params["requester"] == "admin@example.com"

    @pytest.mark.asyncio
    async def test_query_filter_by_status(self, audit_service, mock_postgres):
        """Test filtering by status."""
        await audit_service.query(status="failed")

        call_args = mock_postgres.fetch.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "status = $status" in sql
        assert params["status"] == "failed"

    @pytest.mark.asyncio
    async def test_query_multiple_filters(self, audit_service, mock_postgres):
        """Test combining multiple filters."""
        await audit_service.query(
            report_id="ATM",
            requester="admin",
            status="completed",
        )

        call_args = mock_postgres.fetch.call_args
        sql = call_args[0][0]

        assert "report_id = $report_id" in sql
        assert "requester = $requester" in sql
        assert "status = $status" in sql
        assert "AND" in sql

    @pytest.mark.asyncio
    async def test_query_with_limit(self, audit_service, mock_postgres):
        """Test query respects limit."""
        await audit_service.query(limit=50)

        call_args = mock_postgres.fetch.call_args
        params = call_args[0][1]

        assert params["limit"] == 50

    @pytest.mark.asyncio
    async def test_query_default_limit(self, audit_service, mock_postgres):
        """Test query uses default limit."""
        await audit_service.query()

        call_args = mock_postgres.fetch.call_args
        params = call_args[0][1]

        assert params["limit"] == 100  # Default

    @pytest.mark.asyncio
    async def test_query_error_returns_empty(self, audit_service, mock_postgres):
        """Test that query errors return empty list."""
        mock_postgres.fetch.side_effect = Exception("Database error")

        results = await audit_service.query()

        assert results == []

    @pytest.mark.asyncio
    async def test_query_no_filters(self, audit_service, mock_postgres):
        """Test query with no filters."""
        await audit_service.query()

        call_args = mock_postgres.fetch.call_args
        sql = call_args[0][0]

        # Should not have WHERE clause (except limit)
        assert "WHERE" not in sql or "LIMIT" in sql
