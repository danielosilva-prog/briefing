"""Cache service for report results."""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from schoolreport.core.postgres import PostgresClient

logger = logging.getLogger(__name__)


class CacheService:
    """
    Manage report caching using PostgreSQL backend.

    Implements 30-day TTL caching with hash-based keys.
    """

    def __init__(self, postgres_client: PostgresClient, ttl_days: int = 30):
        """
        Initialize cache service.

        Args:
            postgres_client: PostgreSQL client
            ttl_days: Cache TTL in days
        """
        self.postgres = postgres_client
        self.ttl_days = ttl_days

    def _generate_key(self, report_id: str, params: dict) -> str:
        """Generate cache key from report ID and parameters."""
        # Sort params for consistent hashing
        params_str = json.dumps(params, sort_keys=True)
        hash_value = hashlib.sha256(params_str.encode()).hexdigest()[:16]
        return f"{report_id}:{hash_value}"

    async def get(self, report_id: str, params: dict) -> Optional[str]:
        """
        Get cached report path if available and not expired.

        Args:
            report_id: Report identifier
            params: Report parameters

        Returns:
            GCS path if cached, None otherwise
        """
        cache_key = self._generate_key(report_id, params)

        try:
            result = await self.postgres.fetchrow(
                """
                SELECT gcs_path, expires_at
                FROM report_cache
                WHERE cache_key = $1 AND expires_at > NOW()
                """,
                {"cache_key": cache_key}
            )

            if result:
                logger.info(f"Cache hit for {report_id}: {result['gcs_path']}")
                return result["gcs_path"]

            logger.debug(f"Cache miss for {report_id}")
            return None

        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")
            return None

    async def set(
        self,
        report_id: str,
        params: dict,
        gcs_path: str,
        ttl_days: Optional[int] = None
    ) -> None:
        """
        Store report in cache.

        Args:
            report_id: Report identifier
            params: Report parameters
            gcs_path: GCS path to PDF
            ttl_days: Optional custom TTL (defaults to instance TTL)
        """
        cache_key = self._generate_key(report_id, params)
        ttl = ttl_days or self.ttl_days
        expires_at = datetime.utcnow() + timedelta(days=ttl)

        try:
            await self.postgres.execute(
                """
                INSERT INTO report_cache (cache_key, report_id, parameters, gcs_path, expires_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (cache_key) DO UPDATE
                SET gcs_path = EXCLUDED.gcs_path,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = NOW()
                """,
                {
                    "cache_key": cache_key,
                    "report_id": report_id,
                    "parameters": json.dumps(params),
                    "gcs_path": gcs_path,
                    "expires_at": expires_at
                }
            )

            logger.info(f"Cached report {report_id} at {gcs_path}")

        except Exception as e:
            logger.error(f"Failed to cache report: {e}")
            # Don't raise - caching is not critical

    async def invalidate(self, report_id: str, params: Optional[dict] = None) -> int:
        """
        Invalidate cache entries.

        Args:
            report_id: Report identifier
            params: Optional specific params to invalidate (None = all)

        Returns:
            Number of entries invalidated
        """
        try:
            if params:
                cache_key = self._generate_key(report_id, params)
                result = await self.postgres.execute(
                    "DELETE FROM report_cache WHERE cache_key = $1",
                    {"cache_key": cache_key}
                )
            else:
                result = await self.postgres.execute(
                    "DELETE FROM report_cache WHERE report_id = $1",
                    {"report_id": report_id}
                )

            count = result.split()[-1] if result else "0"
            logger.info(f"Invalidated {count} cache entries for {report_id}")
            return int(count)

        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return 0

    async def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        try:
            result = await self.postgres.execute(
                "DELETE FROM report_cache WHERE expires_at < NOW()"
            )

            count = result.split()[-1] if result else "0"
            logger.info(f"Cleaned up {count} expired cache entries")
            return int(count)

        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return 0
