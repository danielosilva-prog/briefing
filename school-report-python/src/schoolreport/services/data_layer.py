"""Data layer service for executing queries against data sources."""

import asyncio
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from schoolreport.core.bigquery import BigQueryClient
from schoolreport.core.postgres import PostgresClient
from schoolreport.models.report import Query, SourceType

logger = logging.getLogger(__name__)


class DataLayerError(Exception):
    """Raised when data layer operations fail."""

    pass


class DataLayer:
    """
    Data layer for executing queries against multiple data sources.

    Supports BigQuery and PostgreSQL with proper parameterization and
    parallel execution.
    """

    def __init__(
        self,
        bigquery_client: BigQueryClient | None = None,
        postgres_client: PostgresClient | None = None,
    ):
        """
        Initialize the data layer.

        Args:
            bigquery_client: BigQuery client instance
            postgres_client: PostgreSQL client instance
        """
        self._bigquery_client = bigquery_client
        self._postgres_client = postgres_client

    async def execute_query(
        self,
        source: SourceType,
        sql: str,
        params: Dict[str, any],
    ) -> pd.DataFrame:
        """
        Execute a SQL query against a data source.

        Args:
            source: Data source type (BigQuery or PostgreSQL)
            sql: SQL query string with parameterized placeholders
            params: Query parameters

        Returns:
            Query results as pandas DataFrame

        Raises:
            DataLayerError: If query execution fails
        """
        try:
            if source == SourceType.BIGQUERY:
                # BigQuery client returns DataFrame directly
                return await self._bigquery_client.execute_query(sql, params)
            elif source == SourceType.POSTGRES:
                # PostgreSQL client returns list of dicts, convert to DataFrame
                rows = await self._postgres_client.fetch(sql, params)
                return pd.DataFrame(rows) if rows else pd.DataFrame()
            else:
                raise DataLayerError(f"Unsupported source type: {source}")

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise DataLayerError(f"Query execution failed: {e}") from e

    async def execute_query_file(
        self,
        source: SourceType,
        sql_file: Path,
        params: Dict[str, any],
    ) -> pd.DataFrame:
        """
        Execute a SQL query from a file.

        Args:
            source: Data source type
            sql_file: Path to SQL file
            params: Query parameters

        Returns:
            Query results as pandas DataFrame

        Raises:
            DataLayerError: If file not found or query fails
        """
        if not sql_file.exists():
            raise DataLayerError(f"SQL file not found: {sql_file}")

        try:
            sql = sql_file.read_text(encoding="utf-8")
            return await self.execute_query(source, sql, params)
        except DataLayerError:
            raise
        except Exception as e:
            logger.error(f"Failed to execute query from {sql_file}: {e}")
            raise DataLayerError(f"Failed to execute query from {sql_file}: {e}") from e

    async def execute_many(
        self,
        queries: list[Query],
        sql_map: Dict[str, str],
        params: Dict[str, any],
    ) -> Dict[str, pd.DataFrame]:
        """
        Execute multiple queries in parallel.

        Args:
            queries: List of Query definitions
            sql_map: Mapping of query names to SQL strings
            params: Query parameters (shared across all queries)

        Returns:
            Dictionary mapping query names to DataFrames

        Raises:
            DataLayerError: If any query fails
        """
        async def _execute_single(query: Query) -> tuple[str, pd.DataFrame]:
            """Execute a single query and return name + result."""
            try:
                sql = sql_map[query.name]
                result = await self.execute_query(query.source, sql, params)
                logger.debug(f"Executed query '{query.name}': {len(result)} rows")
                return (query.name, result)
            except Exception as e:
                logger.error(f"Failed to execute query '{query.name}': {e}")
                raise DataLayerError(f"Failed to execute query {query.name}: {e}") from e

        # Execute all queries in parallel
        tasks = [_execute_single(query) for query in queries]
        results = await asyncio.gather(*tasks)

        # Convert list of tuples to dict (preserving order)
        return {name: df for name, df in results}

    async def close(self):
        """Close all client connections."""
        try:
            await self._bigquery_client.close()
        except Exception as e:
            logger.warning(f"Error closing BigQuery client: {e}")

        try:
            await self._postgres_client.close()
        except Exception as e:
            logger.warning(f"Error closing PostgreSQL client: {e}")
