"""BigQuery client for executing queries.

Provides async wrapper around google-cloud-bigquery with:
- Parameterized query support (@param syntax)
- DataFrame result conversion
- Error handling and retries
- Query validation
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional, Dict, Any, List

if TYPE_CHECKING:
    import pandas as pd
    from google.cloud import bigquery
    from google.auth.credentials import Credentials


class BigQueryError(Exception):
    """Raised when BigQuery operation fails."""

    pass


class BigQueryClient:
    """Async BigQuery client wrapper."""

    def __init__(
        self,
        project_id: str,
        credentials: Optional[Credentials] = None,
        max_retries: int = 3
    ):
        """Initialize BigQuery client.

        Args:
            project_id: GCP project ID
            credentials: Optional GCP credentials
            max_retries: Maximum number of retries for failed queries
        """
        self.project_id = project_id
        self.credentials = credentials
        self.max_retries = max_retries
        self._client = None

    def _get_client(self):
        """Get or create BigQuery client.

        Returns:
            BigQuery client instance
        """
        if self._client is None:
            from google.cloud import bigquery

            self._client = bigquery.Client(
                project=self.project_id,
                credentials=self.credentials
            )
        return self._client

    def _build_query_config(
        self,
        params: Optional[Dict[str, Any]] = None
    ):
        """Build query configuration with parameters.

        Args:
            params: Optional dictionary of query parameters

        Returns:
            QueryJobConfig with parameters
        """
        from google.cloud.bigquery import (
            QueryJobConfig,
            ScalarQueryParameter,
            ArrayQueryParameter,
        )

        config = QueryJobConfig()

        if params:
            query_parameters = []
            for key, value in params.items():
                if isinstance(value, list):
                    # Infer element type from first element
                    elem_type = "STRING"
                    if value and isinstance(value[0], int):
                        elem_type = "INT64"
                    elif value and isinstance(value[0], float):
                        elem_type = "FLOAT64"
                    query_parameters.append(
                        ArrayQueryParameter(key, elem_type, value)
                    )
                elif isinstance(value, bool):
                    query_parameters.append(
                        ScalarQueryParameter(key, "BOOL", value)
                    )
                elif isinstance(value, int):
                    query_parameters.append(
                        ScalarQueryParameter(key, "INT64", value)
                    )
                elif isinstance(value, float):
                    query_parameters.append(
                        ScalarQueryParameter(key, "FLOAT64", value)
                    )
                else:
                    query_parameters.append(
                        ScalarQueryParameter(key, "STRING", str(value))
                    )

            config.query_parameters = query_parameters

        return config

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """Execute a BigQuery query and return results as DataFrame.

        Args:
            query: SQL query string (use @param syntax for parameters)
            params: Optional dictionary of query parameters

        Returns:
            Query results as pandas DataFrame

        Raises:
            BigQueryError: If query execution fails
        """
        client = self._get_client()
        config = self._build_query_config(params)

        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                # Run query in executor to avoid blocking
                loop = asyncio.get_event_loop()
                query_job = await loop.run_in_executor(
                    None,
                    lambda: client.query(query, job_config=config)
                )

                # Wait for results
                result = await loop.run_in_executor(
                    None,
                    query_job.result
                )

                # Use REST row fetch path to avoid requiring BigQuery Storage API
                # permissions (bigquery.readsessions.create).
                df = result.to_dataframe(create_bqstorage_client=False)
                return df

            except Exception as e:
                last_error = e
                retries += 1

                if retries <= self.max_retries:
                    # Wait before retrying (exponential backoff)
                    await asyncio.sleep(2 ** retries)
                    continue

        # All retries failed
        raise BigQueryError(
            f"Query execution failed after {self.max_retries} retries: {last_error}"
        )

    async def execute_query_as_dicts(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute a BigQuery query and return results as a list of dicts.

        Lighter alternative to ``execute_query`` that skips the pandas
        DataFrame conversion, useful for custom executors that work with
        raw row dicts.

        Args:
            query: SQL query string (use @param syntax for parameters)
            params: Optional dictionary of query parameters

        Returns:
            Query results as list of row dicts

        Raises:
            BigQueryError: If query execution fails
        """
        client = self._get_client()
        config = self._build_query_config(params)

        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                loop = asyncio.get_event_loop()
                query_job = await loop.run_in_executor(
                    None,
                    lambda: client.query(query, job_config=config),
                )
                result = await loop.run_in_executor(None, query_job.result)
                return [dict(row) for row in result]

            except Exception as e:
                last_error = e
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                    continue

        raise BigQueryError(
            f"Query execution failed after {self.max_retries} retries: {last_error}"
        )

    async def validate_query(self, query: str) -> bool:
        """Validate query syntax without executing it.

        Args:
            query: SQL query string

        Returns:
            True if query is valid, False otherwise
        """
        try:
            client = self._get_client()
            from google.cloud.bigquery import QueryJobConfig

            config = QueryJobConfig(dry_run=True, use_query_cache=False)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.query(query, job_config=config)
            )

            return True
        except Exception:
            return False

    async def get_table_schema(
        self,
        table_id: str
    ) -> list:
        """Get table schema.

        Args:
            table_id: Table ID in format 'project.dataset.table'

        Returns:
            List of schema fields

        Raises:
            BigQueryError: If table doesn't exist
        """
        try:
            client = self._get_client()

            loop = asyncio.get_event_loop()
            table = await loop.run_in_executor(
                None,
                client.get_table,
                table_id
            )

            return table.schema
        except Exception as e:
            if "404" in str(e) or "NotFound" in type(e).__name__:
                raise BigQueryError(f"Table not found: {table_id}")
            raise BigQueryError(f"Failed to get table schema: {e}")

    async def table_exists(self, table_id: str) -> bool:
        """Check if a table exists.

        Args:
            table_id: Table ID in format 'project.dataset.table'

        Returns:
            True if table exists, False otherwise
        """
        try:
            client = self._get_client()

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                client.get_table,
                table_id
            )

            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the BigQuery client."""
        if self._client:
            self._client.close()
            self._client = None
