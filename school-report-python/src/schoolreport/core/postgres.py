"""PostgreSQL client using asyncpg with connection pooling."""

import asyncio
from typing import Optional, Dict, Any, List
import asyncpg
from asyncpg import Pool


class PostgresError(Exception):
    """Raised when PostgreSQL operation fails."""

    pass


class PostgresClient:
    """Async PostgreSQL client with connection pooling."""

    def __init__(
        self,
        dsn: str,
        min_size: int = 10,
        max_size: int = 20
    ):
        """Initialize PostgreSQL client.

        Args:
            dsn: PostgreSQL connection string
            min_size: Minimum number of connections in pool
            max_size: Maximum number of connections in pool
        """
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool: Optional[Pool] = None

    async def connect(self) -> None:
        """Create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.dsn,
                min_size=self.min_size,
                max_size=self.max_size
            )

    async def execute(
        self,
        query: str,
        *args,
        **kwargs
    ) -> str:
        """Execute a query that doesn't return results.

        Args:
            query: SQL query
            *args: Positional parameters
            **kwargs: Named parameters

        Returns:
            Query status string

        Raises:
            PostgresError: If query execution fails
        """
        if not self._pool:
            await self.connect()

        try:
            async with self._pool.acquire() as conn:
                result = await conn.execute(query, *args, **kwargs)
                return result
        except Exception as e:
            raise PostgresError(f"Query execution failed: {e}")

    async def fetch(
        self,
        query: str,
        *args,
        **kwargs
    ) -> List[asyncpg.Record]:
        """Fetch multiple rows.

        Args:
            query: SQL query
            *args: Positional parameters
            **kwargs: Named parameters

        Returns:
            List of records

        Raises:
            PostgresError: If query execution fails
        """
        if not self._pool:
            await self.connect()

        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *args, **kwargs)
                return rows
        except Exception as e:
            raise PostgresError(f"Query execution failed: {e}")

    async def fetchrow(
        self,
        query: str,
        *args,
        **kwargs
    ) -> Optional[asyncpg.Record]:
        """Fetch a single row.

        Args:
            query: SQL query
            *args: Positional parameters
            **kwargs: Named parameters

        Returns:
            Single record or None

        Raises:
            PostgresError: If query execution fails
        """
        if not self._pool:
            await self.connect()

        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(query, *args, **kwargs)
                return row
        except Exception as e:
            raise PostgresError(f"Query execution failed: {e}")

    async def fetchval(
        self,
        query: str,
        *args,
        column: int = 0,
        **kwargs
    ) -> Any:
        """Fetch a single value.

        Args:
            query: SQL query
            *args: Positional parameters
            column: Column index to return
            **kwargs: Named parameters

        Returns:
            Single value

        Raises:
            PostgresError: If query execution fails
        """
        if not self._pool:
            await self.connect()

        try:
            async with self._pool.acquire() as conn:
                value = await conn.fetchval(query, *args, column=column, **kwargs)
                return value
        except Exception as e:
            raise PostgresError(f"Query execution failed: {e}")

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def is_connected(self) -> bool:
        """Check if connection pool is active.

        Returns:
            True if connected, False otherwise
        """
        return self._pool is not None
