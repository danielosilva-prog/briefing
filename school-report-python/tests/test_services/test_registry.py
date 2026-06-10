"""Tests for report registry service."""

import pytest
from pathlib import Path

from schoolreport.models.report import ReportDefinition, ChartType, SourceType, ParameterType
from schoolreport.services.registry import ReportRegistry, ReportNotFoundError


@pytest.fixture
def fixtures_dir():
    """Get path to test fixtures directory."""
    return Path(__file__).parent.parent / "fixtures" / "reports"


@pytest.fixture
def registry(fixtures_dir):
    """Create a registry with test fixtures."""
    return ReportRegistry(reports_dir=fixtures_dir)


class TestReportRegistry:
    """Test cases for ReportRegistry."""

    def test_init_discovers_reports(self, registry, fixtures_dir):
        """Test that registry discovers reports on initialization."""
        # Should find TEST_SIMPLE and TEST_COMPLEX
        assert len(registry._reports) >= 2
        assert "TEST_SIMPLE" in registry._reports
        assert "TEST_COMPLEX" in registry._reports

    def test_get_report_simple(self, registry):
        """Test getting a simple report definition."""
        report = registry.get("TEST_SIMPLE")

        assert report.id == "TEST_SIMPLE"
        assert report.name == "Simple Test Report"
        assert len(report.parameters) == 0
        assert len(report.queries) == 1
        assert len(report.charts) == 0
        assert report.cache.enabled is True
        assert report.cache.ttl_days == 30

    def test_get_report_complex(self, registry):
        """Test getting a complex report definition."""
        report = registry.get("TEST_COMPLEX")

        assert report.id == "TEST_COMPLEX"
        assert report.name == "Complex Test Report"

        # Check parameters
        assert len(report.parameters) == 3
        cod_ibge_param = next(p for p in report.parameters if p.name == "cod_ibge")
        assert cod_ibge_param.type == ParameterType.STRING
        assert cod_ibge_param.required is True
        assert cod_ibge_param.pattern == "^[0-9]{7}$"

        ano_param = next(p for p in report.parameters if p.name == "ano")
        assert ano_param.type == ParameterType.INTEGER
        assert ano_param.default == 2024
        assert ano_param.min == 2020

        # Check queries
        assert len(report.queries) == 3
        assert any(q.name == "municipio" and q.source == SourceType.BIGQUERY for q in report.queries)
        assert any(q.name == "cache_check" and q.source == SourceType.POSTGRES for q in report.queries)

        # Check charts
        assert len(report.charts) == 2
        bar_chart = next(c for c in report.charts if c.name == "matriculas_bar")
        assert bar_chart.type == ChartType.BAR
        assert bar_chart.data == "matriculas"
        assert bar_chart.x == "etapa"
        assert bar_chart.y == "total"

        donut_chart = next(c for c in report.charts if c.name == "demografico_donut")
        assert donut_chart.type == ChartType.DONUT
        assert len(donut_chart.colors) == 3

    def test_get_report_not_found(self, registry):
        """Test getting a non-existent report raises error."""
        with pytest.raises(ReportNotFoundError, match="NONEXISTENT"):
            registry.get("NONEXISTENT")

    def test_list_reports(self, registry):
        """Test listing all available reports."""
        reports = registry.list()

        assert len(reports) >= 2
        assert "TEST_SIMPLE" in reports
        assert "TEST_COMPLEX" in reports

    def test_exists(self, registry):
        """Test checking if report exists."""
        assert registry.exists("TEST_SIMPLE") is True
        assert registry.exists("TEST_COMPLEX") is True
        assert registry.exists("NONEXISTENT") is False

    def test_reload(self, registry, fixtures_dir):
        """Test reloading registry."""
        # Get initial count
        initial_count = len(registry._reports)

        # Reload
        registry.reload()

        # Should have same count
        assert len(registry._reports) == initial_count
        assert "TEST_SIMPLE" in registry._reports

    def test_report_paths_set_correctly(self, registry, fixtures_dir):
        """Test that report paths are set correctly."""
        report = registry.get("TEST_SIMPLE")

        # Check that _report_dir is set
        assert report._report_dir is not None
        assert report._report_dir == fixtures_dir / "TEST_SIMPLE"

        # Check path helpers work
        query_path = report.get_query_path(report.queries[0])
        assert query_path.exists()
        assert query_path.name == "test.sql"

        template_path = report.get_template_path()
        assert template_path == fixtures_dir / "TEST_SIMPLE" / "template" / "main.typ"

    def test_validate_query_files_exist(self, registry):
        """Test that query files exist for TEST_SIMPLE."""
        report = registry.get("TEST_SIMPLE")

        for query in report.queries:
            query_path = report.get_query_path(query)
            assert query_path.exists(), f"Query file not found: {query_path}"

    def test_invalid_report_id_raises_validation_error(self, fixtures_dir, tmp_path):
        """Test that invalid report IDs raise validation errors."""
        # Create a report with lowercase ID
        invalid_yaml = tmp_path / "test_invalid" / "report.yaml"
        invalid_yaml.parent.mkdir()
        invalid_yaml.write_text("""
id: test_invalid
name: Invalid Report
template:
  entry: template/main.typ
""")

        # Create registry with this directory
        with pytest.raises(Exception):  # Should raise validation error
            registry = ReportRegistry(reports_dir=tmp_path)
            registry.get("test_invalid")

    def test_get_reports_by_ids(self, registry):
        """Test getting multiple reports by IDs."""
        reports = registry.get_many(["TEST_SIMPLE", "TEST_COMPLEX"])

        assert len(reports) == 2
        assert reports[0].id == "TEST_SIMPLE"
        assert reports[1].id == "TEST_COMPLEX"

    def test_get_reports_by_ids_with_missing(self, registry):
        """Test getting multiple reports with some missing raises error."""
        with pytest.raises(ReportNotFoundError, match="MISSING"):
            registry.get_many(["TEST_SIMPLE", "MISSING"])

    def test_filter_reports_by_cache_enabled(self, registry):
        """Test filtering reports by cache enabled."""
        # All test reports have cache enabled
        cached_reports = [
            report_id
            for report_id in registry.list()
            if registry.get(report_id).cache.enabled
        ]

        assert "TEST_SIMPLE" in cached_reports
        assert "TEST_COMPLEX" in cached_reports
