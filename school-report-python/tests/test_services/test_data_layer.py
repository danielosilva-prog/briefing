"""Tests for data layer service."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from schoolreport.models.report import Query, SourceType
from schoolreport.services.data_layer import DataLayer, DataLayerError


@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client."""
    client = AsyncMock()
    client.execute_query = AsyncMock(return_value=pd.DataFrame({"col1": [1, 2, 3]}))
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_postgres_client():
    """Mock PostgreSQL client."""
    client = AsyncMock()
    client.fetch = AsyncMock(return_value=[{"col2": 4}, {"col2": 5}, {"col2": 6}])
    client.close = AsyncMock()
    return client


@pytest.fixture
def data_layer(mock_bigquery_client, mock_postgres_client):
    """Create DataLayer with mocked clients."""
    return DataLayer(bigquery_client=mock_bigquery_client, postgres_client=mock_postgres_client)


class TestDataLayer:
    """Test cases for DataLayer."""

    @pytest.mark.asyncio
    async def test_execute_bigquery_query(self, data_layer, mock_bigquery_client):
        """Test executing a BigQuery query."""
        sql = "SELECT * FROM table WHERE id = @id"
        params = {"id": 123}

        result = await data_layer.execute_query(
            source=SourceType.BIGQUERY,
            sql=sql,
            params=params
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        mock_bigquery_client.execute_query.assert_called_once_with(sql, params)

    @pytest.mark.asyncio
    async def test_execute_postgres_query(self, data_layer, mock_postgres_client):
        """Test executing a PostgreSQL query."""
        sql = "SELECT * FROM table WHERE id = :id"
        params = {"id": 456}

        result = await data_layer.execute_query(
            source=SourceType.POSTGRES,
            sql=sql,
            params=params
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "col2" in result.columns
        mock_postgres_client.fetch.assert_called_once_with(sql, params)

    @pytest.mark.asyncio
    async def test_execute_query_from_file(self, data_layer, tmp_path, mock_bigquery_client):
        """Test executing query from SQL file."""
        # Create temp SQL file
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT * FROM table WHERE id = @id")

        params = {"id": 789}

        result = await data_layer.execute_query_file(
            source=SourceType.BIGQUERY,
            sql_file=sql_file,
            params=params
        )

        assert isinstance(result, pd.DataFrame)
        mock_bigquery_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_file_not_found(self, data_layer):
        """Test executing query from non-existent file raises error."""
        with pytest.raises(DataLayerError, match="SQL file not found"):
            await data_layer.execute_query_file(
                source=SourceType.BIGQUERY,
                sql_file=Path("/nonexistent.sql"),
                params={}
            )

    @pytest.mark.asyncio
    async def test_execute_many_queries_parallel(self, data_layer, mock_bigquery_client, mock_postgres_client):
        """Test executing multiple queries in parallel."""
        # Setup different return values for each query
        mock_bigquery_client.execute_query.side_effect = [
            pd.DataFrame({"a": [1, 2]}),
            pd.DataFrame({"b": [3, 4]})
        ]
        mock_postgres_client.fetch.return_value = [{"c": 5}, {"c": 6}]

        queries = [
            Query(name="q1", source=SourceType.BIGQUERY, file="q1.sql"),
            Query(name="q2", source=SourceType.BIGQUERY, file="q2.sql"),
            Query(name="q3", source=SourceType.POSTGRES, file="q3.sql"),
        ]

        sql_map = {
            "q1": "SELECT * FROM t1",
            "q2": "SELECT * FROM t2",
            "q3": "SELECT * FROM t3",
        }

        params = {"year": 2024}

        result = await data_layer.execute_many(queries, sql_map, params)

        assert isinstance(result, dict)
        assert len(result) == 3
        assert "q1" in result
        assert "q2" in result
        assert "q3" in result

        assert isinstance(result["q1"], pd.DataFrame)
        assert isinstance(result["q2"], pd.DataFrame)
        assert isinstance(result["q3"], pd.DataFrame)

        # All queries should have been called with params
        assert mock_bigquery_client.execute_query.call_count == 2
        assert mock_postgres_client.fetch.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_many_handles_errors(self, data_layer, mock_bigquery_client):
        """Test that execute_many properly propagates errors."""
        # Make one query fail
        mock_bigquery_client.execute_query.side_effect = Exception("Query failed")

        queries = [
            Query(name="q1", source=SourceType.BIGQUERY, file="q1.sql"),
        ]

        sql_map = {"q1": "SELECT * FROM t1"}

        with pytest.raises(DataLayerError, match="Failed to execute query q1"):
            await data_layer.execute_many(queries, sql_map, {})

    @pytest.mark.asyncio
    async def test_parameter_binding_bigquery(self, data_layer, mock_bigquery_client):
        """Test that BigQuery parameters use @ syntax."""
        sql = "SELECT * FROM table WHERE cod_ibge = @cod_ibge AND ano = @ano"
        params = {"cod_ibge": "2304400", "ano": 2024}

        await data_layer.execute_query(SourceType.BIGQUERY, sql, params)

        # Verify params were passed correctly
        call_args = mock_bigquery_client.execute_query.call_args
        assert call_args[0][0] == sql
        assert call_args[0][1] == params

    @pytest.mark.asyncio
    async def test_parameter_binding_postgres(self, data_layer, mock_postgres_client):
        """Test that PostgreSQL parameters use : syntax."""
        sql = "SELECT * FROM table WHERE cod_ibge = :cod_ibge AND ano = :ano"
        params = {"cod_ibge": "2304400", "ano": 2024}

        await data_layer.execute_query(SourceType.POSTGRES, sql, params)

        # Verify params were passed correctly
        call_args = mock_postgres_client.fetch.call_args
        assert call_args[0][0] == sql
        assert call_args[0][1] == params

    @pytest.mark.asyncio
    async def test_empty_params_allowed(self, data_layer, mock_bigquery_client):
        """Test that queries with no parameters work."""
        sql = "SELECT * FROM table"
        params = {}

        result = await data_layer.execute_query(SourceType.BIGQUERY, sql, params)

        assert isinstance(result, pd.DataFrame)
        mock_bigquery_client.execute_query.assert_called_once_with(sql, params)

    @pytest.mark.asyncio
    async def test_execute_many_preserves_order(self, data_layer, mock_bigquery_client):
        """Test that execute_many returns results in query name order."""
        mock_bigquery_client.execute_query.side_effect = [
            pd.DataFrame({"a": [1]}),
            pd.DataFrame({"b": [2]}),
            pd.DataFrame({"c": [3]}),
        ]

        queries = [
            Query(name="query_1", source=SourceType.BIGQUERY, file="q1.sql"),
            Query(name="query_2", source=SourceType.BIGQUERY, file="q2.sql"),
            Query(name="query_3", source=SourceType.BIGQUERY, file="q3.sql"),
        ]

        sql_map = {
            "query_1": "SELECT 1",
            "query_2": "SELECT 2",
            "query_3": "SELECT 3",
        }

        result = await data_layer.execute_many(queries, sql_map, {})

        # Check keys are present
        assert list(result.keys()) == ["query_1", "query_2", "query_3"]
