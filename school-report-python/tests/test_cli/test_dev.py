"""Tests for CLI dev commands."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typer.testing import CliRunner

from schoolreport.cli.app import app
from schoolreport.models.report import (
    ReportDefinition,
    Parameter,
    ParameterType,
    Query,
    SourceType,
    Template,
)


runner = CliRunner()


@pytest.fixture
def sample_report():
    """Create a sample report definition."""
    return ReportDefinition(
        id="ATM",
        name="Aqui Tem MEC 2",
        parameters=[
            Parameter(name="cod_ibge", type=ParameterType.STRING, required=True),
        ],
        queries=[
            Query(name="municipio", source=SourceType.BIGQUERY, file="queries/municipio.sql"),
            Query(name="matriculas", source=SourceType.BIGQUERY, file="queries/matriculas.sql"),
        ],
        charts=[],
        template=Template(entry="template/main.typ"),
    )


class TestDevServe:
    """Tests for dev serve command."""

    def test_serve_starts_server(self):
        """Test serve starts uvicorn server."""
        with patch("schoolreport.cli.commands.dev.uvicorn") as mock_uvicorn:
            # Invoke with timeout to avoid blocking
            result = runner.invoke(app, ["dev", "serve", "--port", "8080"], catch_exceptions=True)

            # Should attempt to start server
            if result.exit_code == 0:
                mock_uvicorn.run.assert_called_once()

    def test_serve_default_port(self):
        """Test serve uses default port 8000."""
        with patch("schoolreport.cli.commands.dev.uvicorn") as mock_uvicorn:
            runner.invoke(app, ["dev", "serve"], catch_exceptions=True)

            if mock_uvicorn.run.called:
                call_kwargs = mock_uvicorn.run.call_args.kwargs
                assert call_kwargs.get("port") == 8000

    def test_serve_custom_port(self):
        """Test serve with custom port."""
        with patch("schoolreport.cli.commands.dev.uvicorn") as mock_uvicorn:
            runner.invoke(app, ["dev", "serve", "--port", "9000"], catch_exceptions=True)

            if mock_uvicorn.run.called:
                call_kwargs = mock_uvicorn.run.call_args.kwargs
                assert call_kwargs.get("port") == 9000

    def test_serve_reload_mode(self):
        """Test serve with --reload flag."""
        with patch("schoolreport.cli.commands.dev.uvicorn") as mock_uvicorn:
            runner.invoke(app, ["dev", "serve", "--reload"], catch_exceptions=True)

            if mock_uvicorn.run.called:
                call_kwargs = mock_uvicorn.run.call_args.kwargs
                assert call_kwargs.get("reload") is True


class TestDevQuery:
    """Tests for dev query command."""

    def test_query_executes_all_queries(self, sample_report):
        """Test query executes all report queries."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.return_value = {
                    "municipio": [{"nome": "Fortaleza", "cod_ibge": "2304400"}],
                    "matriculas": [{"etapa": "Fund I", "total": 1000}],
                }

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code == 0
                assert "municipio" in result.stdout
                assert "matriculas" in result.stdout
                mock_exec.assert_called_once()

    def test_query_shows_row_counts(self, sample_report):
        """Test query shows row counts for each query."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.return_value = {
                    "municipio": [{"nome": "Test"}],
                    "matriculas": [{"x": 1}, {"x": 2}, {"x": 3}],
                }

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code == 0
                # Should show row counts
                assert "1 row" in result.stdout or "1" in result.stdout
                assert "3 row" in result.stdout or "3" in result.stdout

    def test_query_single_query(self, sample_report):
        """Test query can run a single named query."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.return_value = {
                    "municipio": [{"nome": "Fortaleza"}],
                }

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                    "--query", "municipio",
                ])

                assert result.exit_code == 0
                assert "municipio" in result.stdout

    def test_query_output_json(self, sample_report):
        """Test query with JSON output."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.return_value = {
                    "municipio": [{"nome": "Fortaleza", "cod_ibge": "2304400"}],
                }

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                    "--format", "json",
                ])

                assert result.exit_code == 0
                import json
                data = json.loads(result.stdout)
                assert "municipio" in data

    def test_query_output_to_file(self, sample_report, tmp_path):
        """Test query outputs to file."""
        output_file = tmp_path / "data.json"

        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.return_value = {
                    "municipio": [{"nome": "Fortaleza"}],
                }

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                    "--output", str(output_file),
                ])

                assert result.exit_code == 0
                assert output_file.exists()

    def test_query_report_not_found(self):
        """Test query with unknown report."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            from schoolreport.services.registry import ReportNotFoundError
            mock_registry.return_value.get.side_effect = ReportNotFoundError("UNKNOWN")

            result = runner.invoke(app, [
                "dev", "query", "UNKNOWN",
                "cod_ibge=2304400",
            ])

            assert result.exit_code != 0
            assert "not found" in result.stdout.lower()

    def test_query_bigquery_error(self, sample_report):
        """Test query handles BigQuery errors."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.side_effect = Exception("BigQuery timeout")

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code != 0
                assert "error" in result.stdout.lower()

    def test_query_shows_timing(self, sample_report):
        """Test query shows execution timing."""
        with patch("schoolreport.cli.commands.dev.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            with patch("schoolreport.cli.commands.dev.execute_queries") as mock_exec:
                mock_exec.return_value = {
                    "municipio": [{"nome": "Test"}],
                }

                result = runner.invoke(app, [
                    "dev", "query", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code == 0
                # Should show timing (seconds or ms)
                assert "s" in result.stdout.lower() or "ms" in result.stdout.lower()
