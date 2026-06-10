"""Tests for BigQuery client module."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
from schoolreport.core.bigquery import (
    BigQueryClient,
    BigQueryError,
)


class TestBigQueryClient:
    """Test BigQueryClient class."""

    @pytest.fixture
    def mock_credentials(self):
        """Mock GCP credentials."""
        return Mock()

    @pytest.fixture
    def mock_bq_client(self):
        """Mock BigQuery client."""
        return Mock()

    def test_init_with_credentials(self, mock_credentials):
        """Test initialization with credentials."""
        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        assert client.project_id == "test-project"
        assert client.credentials == mock_credentials

    def test_init_without_credentials(self):
        """Test initialization without credentials."""
        client = BigQueryClient(project_id="test-project")

        assert client.project_id == "test-project"
        assert client.credentials is None

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_execute_query_success(self, mock_client_class, mock_credentials):
        """Test successful query execution."""
        # Mock query result
        mock_result = Mock()
        mock_result.to_dataframe.return_value = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"]
        })

        # Mock client
        mock_client = Mock()
        mock_client.query.return_value.result.return_value = mock_result
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        query = "SELECT * FROM `project.dataset.table`"
        df = await client.execute_query(query)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["col1", "col2"]
        # Verify query was called (with job_config parameter)
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert call_args[0][0] == query  # First positional arg is the query

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_execute_query_with_params(self, mock_client_class, mock_credentials):
        """Test query execution with parameters."""
        mock_result = Mock()
        mock_result.to_dataframe.return_value = pd.DataFrame({"result": [1]})

        mock_client = Mock()
        mock_client.query.return_value.result.return_value = mock_result
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        query = "SELECT * FROM table WHERE id = @id AND year = @year"
        params = {"id": "123", "year": 2024}

        df = await client.execute_query(query, params)

        assert isinstance(df, pd.DataFrame)
        # Verify query was called
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args
        assert query in str(call_args)

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_execute_query_error(self, mock_client_class, mock_credentials):
        """Test query execution with error."""
        mock_client = Mock()
        mock_client.query.side_effect = Exception("Query failed")
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        query = "SELECT * FROM invalid_table"

        with pytest.raises(BigQueryError, match="Query execution failed"):
            await client.execute_query(query)

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_execute_query_with_retry(self, mock_client_class, mock_credentials):
        """Test query execution with retry on transient failure."""
        mock_result = Mock()
        mock_result.to_dataframe.return_value = pd.DataFrame({"result": [1]})

        # First call fails, second succeeds
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.result.side_effect = [
            Exception("Transient error"),
            mock_result
        ]
        mock_client.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials,
            max_retries=2
        )

        query = "SELECT * FROM table"
        df = await client.execute_query(query)

        assert isinstance(df, pd.DataFrame)
        assert mock_query_job.result.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_query_empty_result(self, mock_credentials):
        """Test query execution with empty result."""
        with patch("schoolreport.core.bigquery.bigquery.Client") as mock_client_class:
            mock_result = Mock()
            mock_result.to_dataframe.return_value = pd.DataFrame()

            mock_client = Mock()
            mock_client.query.return_value.result.return_value = mock_result
            mock_client_class.return_value = mock_client

            client = BigQueryClient(
                project_id="test-project",
                credentials=mock_credentials
            )

            query = "SELECT * FROM table WHERE 1=0"
            df = await client.execute_query(query)

            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_validate_query_syntax_valid(self, mock_client_class, mock_credentials):
        """Test query syntax validation for valid query."""
        mock_client = Mock()
        mock_client.query.return_value.dry_run = True
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        query = "SELECT * FROM `project.dataset.table`"
        is_valid = await client.validate_query(query)

        assert is_valid is True

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_validate_query_syntax_invalid(self, mock_client_class, mock_credentials):
        """Test query syntax validation for invalid query."""
        mock_client = Mock()
        mock_client.query.side_effect = Exception("Syntax error")
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        query = "SELECT * FROM INVALID SYNTAX"
        is_valid = await client.validate_query(query)

        assert is_valid is False

    def test_build_query_config_no_params(self):
        """Test building query config without parameters."""
        client = BigQueryClient(project_id="test-project")

        config = client._build_query_config()

        assert config is not None

    def test_build_query_config_with_params(self):
        """Test building query config with parameters."""
        client = BigQueryClient(project_id="test-project")

        params = {"id": "123", "year": 2024, "active": True}
        config = client._build_query_config(params)

        assert config is not None

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_get_table_schema(self, mock_client_class, mock_credentials):
        """Test getting table schema."""
        mock_schema_field = Mock()
        mock_schema_field.name = "col1"
        mock_schema_field.field_type = "STRING"

        mock_table = Mock()
        mock_table.schema = [mock_schema_field]

        mock_client = Mock()
        mock_client.get_table.return_value = mock_table
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        schema = await client.get_table_schema("project.dataset.table")

        assert len(schema) == 1
        assert schema[0].name == "col1"
        assert schema[0].field_type == "STRING"

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_table_exists_true(self, mock_client_class, mock_credentials):
        """Test checking if table exists (true case)."""
        mock_client = Mock()
        mock_client.get_table.return_value = Mock()
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        exists = await client.table_exists("project.dataset.table")

        assert exists is True

    @pytest.mark.asyncio
    @patch("schoolreport.core.bigquery.bigquery.Client")
    async def test_table_exists_false(self, mock_client_class, mock_credentials):
        """Test checking if table exists (false case)."""
        from google.cloud.exceptions import NotFound

        mock_client = Mock()
        mock_client.get_table.side_effect = NotFound("Table not found")
        mock_client_class.return_value = mock_client

        client = BigQueryClient(
            project_id="test-project",
            credentials=mock_credentials
        )

        exists = await client.table_exists("project.dataset.nonexistent")

        assert exists is False
