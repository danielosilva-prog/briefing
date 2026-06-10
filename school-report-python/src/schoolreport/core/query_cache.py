"""Local disk cache for BigQuery query results.

Provides fast caching for development and repeated report generation,
avoiding redundant BigQuery calls for the same queries.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Default cache directory (relative to user's home)
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "schoolreport" / "queries"

# Default TTL: 30 days — cache invalidates automatically when SQL content changes
# (the cache key is a hash of the normalized SQL + params)
DEFAULT_TTL_SECONDS = 2592000


class QueryCache:
    """
    Disk-based cache for BigQuery query results.

    Uses diskcache for fast, persistent caching of DataFrames.
    Ideal for development workflows where the same queries are run repeatedly.
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        enabled: bool = True,
        size_limit: int = 1024 * 1024 * 1024,  # 1GB default
    ):
        """
        Initialize the query cache.

        Args:
            cache_dir: Directory for cache storage. Defaults to ~/.cache/schoolreport/queries
            ttl_seconds: Time-to-live for cache entries in seconds. Default 1 hour.
            enabled: Whether caching is enabled. Default True.
            size_limit: Maximum cache size in bytes. Default 1GB.
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled
        self.size_limit = size_limit
        self._cache = None

        # Stats for logging
        self._hits = 0
        self._misses = 0

    @property
    def cache(self):
        """Lazy-load the cache instance."""
        if self._cache is None:
            from diskcache import Cache

            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache = Cache(
                str(self.cache_dir),
                size_limit=self.size_limit,
                eviction_policy="least-recently-used",
            )
        return self._cache

    def _generate_key(self, sql: str, params: Optional[dict] = None) -> str:
        """
        Generate a cache key from SQL query and parameters.

        Args:
            sql: The SQL query string
            params: Optional query parameters

        Returns:
            SHA256 hash of the query + params
        """
        # Normalize SQL (strip whitespace, lowercase)
        normalized_sql = " ".join(sql.split()).lower()

        # Sort params for consistent hashing
        params_str = json.dumps(params or {}, sort_keys=True, default=str)

        # Create hash
        content = f"{normalized_sql}:{params_str}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, sql: str, params: Optional[dict] = None) -> Optional[pd.DataFrame]:
        """
        Get cached query result if available.

        Args:
            sql: The SQL query string
            params: Optional query parameters

        Returns:
            DataFrame if cached and not expired, None otherwise
        """
        if not self.enabled:
            return None

        key = self._generate_key(sql, params)

        try:
            result = self.cache.get(key)
            if result is not None:
                self._hits += 1
                logger.debug(f"Cache HIT for query (key={key[:8]}...)")
                return result
            else:
                self._misses += 1
                logger.debug(f"Cache MISS for query (key={key[:8]}...)")
                return None
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    def set(
        self,
        sql: str,
        params: Optional[dict],
        result: pd.DataFrame,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Store query result in cache.

        Args:
            sql: The SQL query string
            params: Optional query parameters
            result: DataFrame to cache
            ttl: Optional custom TTL in seconds

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False

        key = self._generate_key(sql, params)
        expire = ttl if ttl is not None else self.ttl_seconds

        try:
            self.cache.set(key, result, expire=expire)
            logger.debug(
                f"Cached query result (key={key[:8]}..., rows={len(result)}, ttl={expire}s)"
            )
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False

    def invalidate(self, sql: str, params: Optional[dict] = None) -> bool:
        """
        Invalidate a specific cache entry.

        Args:
            sql: The SQL query string
            params: Optional query parameters

        Returns:
            True if entry was removed, False otherwise
        """
        if not self.enabled:
            return False

        key = self._generate_key(sql, params)

        try:
            return self.cache.delete(key)
        except Exception as e:
            logger.warning(f"Cache invalidate failed: {e}")
            return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        try:
            count = len(self.cache)
            self.cache.clear()
            logger.info(f"Cleared {count} cache entries")
            return count
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
            return 0

    def stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with hit/miss counts and cache info
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 1),
            "entries": len(self.cache) if self._cache else 0,
            "size_bytes": self.cache.volume() if self._cache else 0,
            "enabled": self.enabled,
        }

    def info(self) -> str:
        """Return a human-readable summary of the cache state."""
        if not self.enabled:
            return "Query cache: disabled"

        entries = len(self.cache) if self._cache else 0
        volume = self.cache.volume() if self._cache else 0

        if volume < 1024:
            size_str = f"{volume} B"
        elif volume < 1024 * 1024:
            size_str = f"{volume / 1024:.1f} KB"
        else:
            size_str = f"{volume / (1024 * 1024):.1f} MB"

        return f"Query cache: {entries} entries, {size_str} in {self.cache_dir}"

    def close(self) -> None:
        """Close the cache."""
        if self._cache:
            self._cache.close()
            self._cache = None


# Global cache instance (lazy-loaded)
_query_cache: Optional[QueryCache] = None


def get_query_cache(
    cache_dir: Optional[Path] = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    enabled: bool = True,
) -> QueryCache:
    """
    Get the global query cache instance.

    Args:
        cache_dir: Optional cache directory override
        ttl_seconds: Cache TTL in seconds
        enabled: Whether caching is enabled

    Returns:
        QueryCache instance
    """
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache(
            cache_dir=cache_dir,
            ttl_seconds=ttl_seconds,
            enabled=enabled,
        )
    return _query_cache


def reset_query_cache() -> None:
    """Reset the global query cache (useful for testing)."""
    global _query_cache
    if _query_cache:
        _query_cache.close()
    _query_cache = None
