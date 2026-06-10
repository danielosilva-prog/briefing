"""Tests for CLI generate command."""

import pytest
import json
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
        description="Report for municipalities",
        version="1.0.0",
        parameters=[
            Parameter(name="cod_ibge", type=ParameterType.STRING, required=True, pattern=r"^\d{7}$"),
            Parameter(name="ano", type=ParameterType.INTEGER, required=False, default=2024),
        ],
        queries=[
            Query(name="municipio", source=SourceType.BIGQUERY, file="queries/municipio.sql"),
        ],
        charts=[],
        template=Template(entry="template/main.typ"),
    )


class TestGenerateCommand:
    """Tests for generate command."""

    def test_generate_creates_pdf(self, tmp_path, sample_report):
        """Test generate creates PDF file."""
        output_file = tmp_path / "output.pdf"

        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.return_value = output_file
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                    "--output", str(output_file),
                ])

                assert result.exit_code == 0
                mock_executor.execute.assert_called_once()

    def test_generate_with_parameters(self, tmp_path, sample_report):
        """Test generate parses parameters correctly."""
        output_file = tmp_path / "output.pdf"

        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.return_value = output_file
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                    "ano=2023",
                    "--output", str(output_file),
                ])

                assert result.exit_code == 0

                # Check parameters were passed correctly
                call_args = mock_executor.execute.call_args
                params = call_args.kwargs.get("params") or call_args[1].get("params")
                assert params["cod_ibge"] == "2304400"
                assert params["ano"] == "2023"

    def test_generate_missing_required_parameter(self, sample_report):
        """Test generate fails when required parameter is missing."""
        with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            result = runner.invoke(app, [
                "generate", "ATM",
                # Missing cod_ibge
            ])

            assert result.exit_code != 0
            assert "required" in result.stdout.lower() or "cod_ibge" in result.stdout

    def test_generate_default_output_path(self, tmp_path, sample_report):
        """Test generate uses default output path."""
        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.return_value = Path("./output/ATM-2304400.pdf")
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code == 0
                # Default output should be ./output/{ID}-{params}.pdf
                call_args = mock_executor.execute.call_args
                output = call_args.kwargs.get("output") or call_args[1].get("output")
                assert "ATM" in str(output) or "output" in str(output)

    def test_generate_report_not_found(self):
        """Test generate with unknown report ID."""
        with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
            from schoolreport.services.registry import ReportNotFoundError
            mock_registry.return_value.get.side_effect = ReportNotFoundError("UNKNOWN")

            result = runner.invoke(app, ["generate", "UNKNOWN"])

            assert result.exit_code != 0
            assert "not found" in result.stdout.lower()

    def test_generate_data_only(self, tmp_path, sample_report):
        """Test generate with --data-only outputs JSON."""
        output_file = tmp_path / "data.json"

        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute_data_only.return_value = {
                "municipio": [{"nome": "Fortaleza", "cod_ibge": "2304400"}]
            }
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                    "--data-only",
                    "--output", str(output_file),
                ])

                assert result.exit_code == 0
                mock_executor.execute_data_only.assert_called_once()

    def test_generate_with_upload(self, tmp_path, sample_report):
        """Test generate with --upload flag."""
        output_file = tmp_path / "output.pdf"
        output_file.write_bytes(b"%PDF-1.4 test")

        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.return_value = output_file
            mock_executor.upload.return_value = "gs://bucket/ATM/2304400.pdf"
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                    "--upload",
                    "--output", str(output_file),
                ])

                assert result.exit_code == 0
                mock_executor.upload.assert_called_once()
                assert "gs://" in result.stdout

    def test_generate_shows_progress(self, tmp_path, sample_report):
        """Test generate shows progress during execution."""
        output_file = tmp_path / "output.pdf"

        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.return_value = output_file
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                    "--output", str(output_file),
                ])

                # Should show some progress indication
                assert result.exit_code == 0
                # Progress indicators vary, just check command completed
                assert "ATM" in result.stdout or "saved" in result.stdout.lower()

    def test_generate_handles_bigquery_error(self, sample_report):
        """Test generate handles BigQuery errors gracefully."""
        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.side_effect = Exception("BigQuery connection failed")
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code != 0
                assert "error" in result.stdout.lower() or "failed" in result.stdout.lower()

    def test_generate_handles_typst_error(self, sample_report):
        """Test generate handles Typst rendering errors."""
        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.side_effect = Exception("Typst compilation failed")
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                result = runner.invoke(app, [
                    "generate", "ATM",
                    "cod_ibge=2304400",
                ])

                assert result.exit_code != 0

    def test_generate_invalid_parameter_format(self, sample_report):
        """Test generate fails with invalid parameter format."""
        with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_report

            result = runner.invoke(app, [
                "generate", "ATM",
                "invalid_format_no_equals",
            ])

            assert result.exit_code != 0
            assert "invalid" in result.stdout.lower() or "format" in result.stdout.lower()

    def test_generate_with_open_flag(self, tmp_path, sample_report):
        """Test generate with --open flag opens the PDF."""
        output_file = tmp_path / "output.pdf"
        output_file.write_bytes(b"%PDF-1.4 test")

        with patch("schoolreport.cli.commands.generate.LocalExecutor") as MockExecutor:
            mock_executor = AsyncMock()
            mock_executor.execute.return_value = output_file
            MockExecutor.return_value = mock_executor

            with patch("schoolreport.cli.commands.generate.get_registry") as mock_registry:
                mock_registry.return_value.get.return_value = sample_report

                with patch("schoolreport.cli.commands.generate.open_file") as mock_open:
                    result = runner.invoke(app, [
                        "generate", "ATM",
                        "cod_ibge=2304400",
                        "--open",
                        "--output", str(output_file),
                    ])

                    assert result.exit_code == 0
                    mock_open.assert_called_once_with(output_file)


class TestLocalExecutor:
    """Tests for LocalExecutor used by generate command."""

    @pytest.mark.asyncio
    async def test_executor_runs_queries(self, sample_report, tmp_path):
        """Test executor runs all queries."""
        from schoolreport.cli.executor import LocalExecutor

        with patch.object(LocalExecutor, "_run_queries") as mock_queries:
            mock_queries.return_value = {"municipio": [{"nome": "Test"}]}

            with patch.object(LocalExecutor, "_generate_charts") as mock_charts:
                mock_charts.return_value = {}

                with patch.object(LocalExecutor, "_render_pdf") as mock_render:
                    mock_render.return_value = tmp_path / "output.pdf"
                    (tmp_path / "output.pdf").write_bytes(b"%PDF")

                    executor = LocalExecutor()
                    result = await executor.execute(
                        report=sample_report,
                        params={"cod_ibge": "2304400"},
                        output=tmp_path / "output.pdf",
                    )

                    mock_queries.assert_called_once()
                    assert result.exists()

    @pytest.mark.asyncio
    async def test_executor_generates_charts(self, sample_report, tmp_path):
        """Test executor generates charts when defined."""
        from schoolreport.cli.executor import LocalExecutor

        # Add a chart to the report
        from schoolreport.models.report import Chart, ChartType
        sample_report.charts = [
            Chart(name="test_chart", type=ChartType.BAR, data="municipio", x="nome", y="total")
        ]

        with patch.object(LocalExecutor, "_run_queries") as mock_queries:
            mock_queries.return_value = {"municipio": [{"nome": "Test", "total": 100}]}

            with patch.object(LocalExecutor, "_generate_charts") as mock_charts:
                mock_charts.return_value = {"test_chart": "base64_svg"}

                with patch.object(LocalExecutor, "_render_pdf") as mock_render:
                    mock_render.return_value = tmp_path / "output.pdf"
                    (tmp_path / "output.pdf").write_bytes(b"%PDF")

                    executor = LocalExecutor()
                    await executor.execute(
                        report=sample_report,
                        params={"cod_ibge": "2304400"},
                        output=tmp_path / "output.pdf",
                    )

                    mock_charts.assert_called_once()

    @pytest.mark.asyncio
    async def test_executor_data_only_mode(self, sample_report, tmp_path):
        """Test executor data-only mode returns JSON."""
        from schoolreport.cli.executor import LocalExecutor

        with patch.object(LocalExecutor, "_run_queries") as mock_queries:
            mock_queries.return_value = {"municipio": [{"nome": "Fortaleza"}]}

            executor = LocalExecutor()
            result = await executor.execute_data_only(
                report=sample_report,
                params={"cod_ibge": "2304400"},
            )

            assert "municipio" in result
            assert result["municipio"][0]["nome"] == "Fortaleza"

    @pytest.mark.asyncio
    async def test_executor_upload(self, sample_report, tmp_path):
        """Test executor upload functionality."""
        from schoolreport.cli.executor import LocalExecutor

        pdf_file = tmp_path / "output.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 test content")

        with patch("schoolreport.cli.executor.GCSClient") as MockGCS:
            mock_gcs = AsyncMock()
            mock_gcs.upload.return_value = "gs://bucket/ATM/report.pdf"
            MockGCS.return_value = mock_gcs

            executor = LocalExecutor()
            result = await executor.upload(
                local_path=pdf_file,
                report_id="ATM",
                params={"cod_ibge": "2304400"},
            )

            assert result.startswith("gs://")
            mock_gcs.upload.assert_called_once()
