"""Redis client wrapper for connection management."""

import asyncio
from typing import Optional
import redis.asyncio as redis


class RedisError(Exception):
    """Raised when Redis operation fails."""

    pass


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self, url: str):
        """Initialize Redis client.

        Args:
            url: Redis connection URL (e.g., "redis://localhost:6379/0")
        """
        self.url = url
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._client is None:
            self._client = await redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True
            )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> Optional[str]:
        """Get value by key.

        Args:
            key: Key to get

        Returns:
            Value or None if key doesn't exist

        Raises:
            RedisError: If operation fails
        """
        if not self._client:
            await self.connect()

        try:
            return await self._client.get(key)
        except Exception as e:
            raise RedisError(f"Get operation failed: {e}")

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set key to value.

        Args:
            key: Key to set
            value: Value to set
            expire: Optional expiration time in seconds

        Returns:
            True if successful

        Raises:
            RedisError: If operation fails
        """
        if not self._client:
            await self.connect()

        try:
            await self._client.set(key, value, ex=expire)
            return True
        except Exception as e:
            raise RedisError(f"Set operation failed: {e}")

    async def delete(self, key: str) -> int:
        """Delete key.

        Args:
            key: Key to delete

        Returns:
            Number of keys deleted

        Raises:
            RedisError: If operation fails
        """
        if not self._client:
            await self.connect()

        try:
            return await self._client.delete(key)
        except Exception as e:
            raise RedisError(f"Delete operation failed: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: Key to check

        Returns:
            True if key exists, False otherwise

        Raises:
            RedisError: If operation fails
        """
        if not self._client:
            await self.connect()

        try:
            result = await self._client.exists(key)
            return result > 0
        except Exception as e:
            raise RedisError(f"Exists operation failed: {e}")

    async def ping(self) -> bool:
        """Check if Redis is responding.

        Returns:
            True if Redis is responding, False otherwise
        """
        if not self._client:
            try:
                await self.connect()
            except Exception:
                return False

        try:
            response = await self._client.ping()
            return response is True
        except Exception:
            return False

    async def is_connected(self) -> bool:
        """Check if client is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._client is not None
