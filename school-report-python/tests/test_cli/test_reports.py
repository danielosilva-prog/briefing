"""Tests for CLI reports commands."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
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
def sample_reports():
    """Create sample report definitions."""
    return [
        ReportDefinition(
            id="ATM",
            name="Aqui Tem MEC 2",
            description="Report for municipalities",
            version="1.0.0",
            parameters=[
                Parameter(name="cod_ibge", type=ParameterType.STRING, required=True),
                Parameter(name="ano", type=ParameterType.INTEGER, required=False, default=2024),
            ],
            queries=[
                Query(name="municipio", source=SourceType.BIGQUERY, file="queries/municipio.sql"),
                Query(name="matriculas", source=SourceType.BIGQUERY, file="queries/matriculas.sql"),
            ],
            charts=[],
            template=Template(entry="template/main.typ"),
        ),
        ReportDefinition(
            id="ATSBR",
            name="Aqui Tem Superior Brasil",
            description="National higher education report",
            version="1.0.0",
            parameters=[],  # No parameters
            queries=[
                Query(name="dados", source=SourceType.BIGQUERY, file="queries/dados.sql"),
            ],
            charts=[],
            template=Template(entry="template/main.typ"),
        ),
    ]


class TestReportsList:
    """Tests for reports list command."""

    def test_list_shows_all_reports(self, sample_reports):
        """Test list displays all available reports."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get_all.return_value = {r.id: r for r in sample_reports}

            result = runner.invoke(app, ["reports", "list"])

            assert result.exit_code == 0
            assert "ATM" in result.stdout
            assert "ATSBR" in result.stdout
            assert "Aqui Tem MEC" in result.stdout

    def test_list_shows_parameters(self, sample_reports):
        """Test list shows parameter count or names."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get_all.return_value = {r.id: r for r in sample_reports}

            result = runner.invoke(app, ["reports", "list"])

            assert result.exit_code == 0
            # Should indicate ATM has parameters
            assert "cod_ibge" in result.stdout or "2 param" in result.stdout.lower()

    def test_list_empty_reports(self):
        """Test list when no reports are available."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get_all.return_value = {}

            result = runner.invoke(app, ["reports", "list"])

            assert result.exit_code == 0
            assert "no reports" in result.stdout.lower() or result.stdout.strip() == ""

    def test_list_with_format_json(self, sample_reports):
        """Test list with JSON output format."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get_all.return_value = {r.id: r for r in sample_reports}

            result = runner.invoke(app, ["reports", "list", "--format", "json"])

            assert result.exit_code == 0
            # Should be valid JSON
            import json
            data = json.loads(result.stdout)
            assert len(data) == 2
            assert data[0]["id"] == "ATM"


class TestReportsShow:
    """Tests for reports show command."""

    def test_show_displays_report_details(self, sample_reports):
        """Test show displays full report details."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_reports[0]

            result = runner.invoke(app, ["reports", "show", "ATM"])

            assert result.exit_code == 0
            assert "ATM" in result.stdout
            assert "Aqui Tem MEC" in result.stdout
            assert "cod_ibge" in result.stdout
            assert "municipio" in result.stdout  # Query name

    def test_show_displays_parameters(self, sample_reports):
        """Test show displays parameter details."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_reports[0]

            result = runner.invoke(app, ["reports", "show", "ATM"])

            assert result.exit_code == 0
            assert "cod_ibge" in result.stdout
            assert "required" in result.stdout.lower()
            assert "ano" in result.stdout

    def test_show_displays_queries(self, sample_reports):
        """Test show displays query list."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_reports[0]

            result = runner.invoke(app, ["reports", "show", "ATM"])

            assert result.exit_code == 0
            assert "municipio" in result.stdout
            assert "matriculas" in result.stdout

    def test_show_report_not_found(self):
        """Test show with unknown report ID."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            from schoolreport.services.registry import ReportNotFoundError
            mock_registry.return_value.get.side_effect = ReportNotFoundError("UNKNOWN")

            result = runner.invoke(app, ["reports", "show", "UNKNOWN"])

            assert result.exit_code != 0
            assert "not found" in result.stdout.lower()

    def test_show_with_format_json(self, sample_reports):
        """Test show with JSON output."""
        with patch("schoolreport.cli.commands.reports.get_registry") as mock_registry:
            mock_registry.return_value.get.return_value = sample_reports[0]

            result = runner.invoke(app, ["reports", "show", "ATM", "--format", "json"])

            assert result.exit_code == 0
            import json
            data = json.loads(result.stdout)
            assert data["id"] == "ATM"
            assert len(data["parameters"]) == 2


class TestReportsValidate:
    """Tests for reports validate command."""

    def test_validate_valid_report(self, tmp_path):
        """Test validate passes for valid report."""
        # Create valid report structure
        report_dir = tmp_path / "reports" / "TEST"
        report_dir.mkdir(parents=True)

        (report_dir / "report.yaml").write_text("""
id: TEST
name: Test Report
parameters: []
queries:
  - name: data
    source: bigquery
    file: queries/data.sql
template:
  entry: template/main.typ
""")

        queries_dir = report_dir / "queries"
        queries_dir.mkdir()
        (queries_dir / "data.sql").write_text("SELECT 1")

        template_dir = report_dir / "template"
        template_dir.mkdir()
        (template_dir / "main.typ").write_text("= Report")

        with patch("schoolreport.cli.commands.reports.get_reports_dir", return_value=tmp_path / "reports"):
            result = runner.invoke(app, ["reports", "validate", "TEST"])

            assert result.exit_code == 0
            assert "valid" in result.stdout.lower() or "✓" in result.stdout

    def test_validate_missing_sql_file(self, tmp_path):
        """Test validate fails when SQL file is missing."""
        report_dir = tmp_path / "reports" / "TEST"
        report_dir.mkdir(parents=True)

        (report_dir / "report.yaml").write_text("""
id: TEST
name: Test Report
parameters: []
queries:
  - name: data
    source: bigquery
    file: queries/missing.sql
template:
  entry: template/main.typ
""")

        with patch("schoolreport.cli.commands.reports.get_reports_dir", return_value=tmp_path / "reports"):
            result = runner.invoke(app, ["reports", "validate", "TEST"])

            assert result.exit_code != 0
            assert "missing" in result.stdout.lower() or "not found" in result.stdout.lower()

    def test_validate_invalid_yaml(self, tmp_path):
        """Test validate fails with invalid YAML."""
        report_dir = tmp_path / "reports" / "TEST"
        report_dir.mkdir(parents=True)

        (report_dir / "report.yaml").write_text("invalid: yaml: syntax:")

        with patch("schoolreport.cli.commands.reports.get_reports_dir", return_value=tmp_path / "reports"):
            result = runner.invoke(app, ["reports", "validate", "TEST"])

            assert result.exit_code != 0

    def test_validate_missing_template(self, tmp_path):
        """Test validate fails when template is missing."""
        report_dir = tmp_path / "reports" / "TEST"
        report_dir.mkdir(parents=True)

        (report_dir / "report.yaml").write_text("""
id: TEST
name: Test Report
parameters: []
queries: []
template:
  entry: template/missing.typ
""")

        with patch("schoolreport.cli.commands.reports.get_reports_dir", return_value=tmp_path / "reports"):
            result = runner.invoke(app, ["reports", "validate", "TEST"])

            assert result.exit_code != 0
            assert "template" in result.stdout.lower()

    def test_validate_report_not_found(self, tmp_path):
        """Test validate with unknown report."""
        report_dir = tmp_path / "report"
        report_dir.mkdir(parents=True)

        with patch("schoolreport.cli.commands.reports.get_reports_dir", return_value=report_dir):
            result = runner.invoke(app, ["reports", "validate", "NONEXISTENT"])

            assert result.exit_code != 0
            assert "not found" in result.stdout.lower()

    def test_validate_all_reports(self, tmp_path):
        """Test validate all reports at once."""
        report_dir = tmp_path / "report"

        # Create two valid reports
        for report_id in ["TEST1", "TEST2"]:
            rd = report_dir / report_id
            rd.mkdir(parents=True)
            (rd / "report.yaml").write_text(f"""
id: {report_id}
name: Test Report {report_id}
parameters: []
queries: []
template:
  entry: template/main.typ
""")
            (rd / "template").mkdir()
            (rd / "template" / "main.typ").write_text("= Report")

        with patch("schoolreport.cli.commands.reports.get_reports_dir", return_value=report_dir):
            result = runner.invoke(app, ["reports", "validate", "--all"])

            assert result.exit_code == 0
            assert "TEST1" in result.stdout
            assert "TEST2" in result.stdout
