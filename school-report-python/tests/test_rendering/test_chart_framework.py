"""Tests for custom chart framework."""

import base64
import tempfile
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from schoolreport.rendering.chart_framework import (
    ChartContext,
    ChartLoader,
    ChartLoadError,
    ChartMetadata,
    ChartRegistry,
    chart,
)
from schoolreport.rendering.charts import ChartGenerator


@pytest.fixture
def sample_enrollment_data():
    """Sample enrollment data for testing."""
    return pd.DataFrame({
        "category": ["A", "B", "C"],
        "count": [100, 200, 150],
    })


@pytest.fixture
def sample_demographics_data():
    """Sample demographics data for testing."""
    return pd.DataFrame({
        "label": ["Group X", "Group Y", "Group Z"],
        "value": [40, 35, 25],
    })


class TestChartContext:
    """Test cases for ChartContext."""

    def test_default_values(self):
        """Test ChartContext has sensible defaults."""
        ctx = ChartContext(chart_name="test", report_id="TEST")

        assert ctx.chart_name == "test"
        assert ctx.report_id == "TEST"
        assert ctx.figsize == (10, 6)
        assert ctx.dpi == 100
        assert ctx.primary_color == "#2E4172"
        assert ctx.font_family == "Rawline"
        assert ctx.locale == "pt_BR"

    def test_format_number(self):
        """Test number formatting."""
        ctx = ChartContext(chart_name="test", report_id="TEST")

        assert ctx.format_number(1234567) == "1.234.567"
        assert ctx.format_number(1234.5, decimals=2) == "1.234,50"
        assert ctx.format_number(0) == "0"

    def test_format_percent(self):
        """Test percentage formatting."""
        ctx = ChartContext(chart_name="test", report_id="TEST")

        assert ctx.format_percent(50.5) == "50,5%"
        assert ctx.format_percent(100.0, decimals=0) == "100%"

    def test_get_colors(self):
        """Test color palette generation."""
        ctx = ChartContext(
            chart_name="test",
            report_id="TEST",
            color_palette=["#AAA", "#BBB", "#CCC"],
        )

        colors = ctx.get_colors(3)
        assert colors == ["#AAA", "#BBB", "#CCC"]

        # Test cycling when requesting more colors than available
        colors = ctx.get_colors(5)
        assert colors == ["#AAA", "#BBB", "#CCC", "#AAA", "#BBB"]

    def test_get_colors_empty_palette(self):
        """Test color generation with empty palette uses matplotlib fallback."""
        ctx = ChartContext(
            chart_name="test",
            report_id="TEST",
            color_palette=[],
        )

        colors = ctx.get_colors(3)
        assert len(colors) == 3

    def test_params_access(self):
        """Test accessing report parameters."""
        ctx = ChartContext(
            chart_name="test",
            report_id="TEST",
            params={"year": 2024, "region": "North"},
        )

        assert ctx.params["year"] == 2024
        assert ctx.params["region"] == "North"


class TestChartRegistry:
    """Test cases for ChartRegistry."""

    def test_empty_registry(self):
        """Test empty registry behavior."""
        registry = ChartRegistry("TEST")

        assert len(registry) == 0
        assert registry.list() == []
        assert registry.get("nonexistent") is None
        assert not registry.has("nonexistent")

    def test_register_and_get(self):
        """Test registering and retrieving chart functions."""
        registry = ChartRegistry("TEST")

        def my_chart(df, ctx):
            return plt.figure()

        metadata = ChartMetadata(name="test_chart", data="query1")
        registry.register("test_chart", my_chart, metadata)

        assert len(registry) == 1
        assert "test_chart" in registry
        assert registry.has("test_chart")

        chart_fn = registry.get("test_chart")
        assert chart_fn is not None
        assert chart_fn.func == my_chart
        assert chart_fn.metadata.name == "test_chart"
        assert chart_fn.metadata.data == "query1"

    def test_list_charts(self):
        """Test listing registered charts."""
        registry = ChartRegistry("TEST")

        def chart_a(df, ctx):
            return plt.figure()

        def chart_b(df, ctx):
            return plt.figure()

        registry.register("chart_b", chart_b, ChartMetadata(name="chart_b", data="q"))
        registry.register("chart_a", chart_a, ChartMetadata(name="chart_a", data="q"))

        # Should be sorted
        assert registry.list() == ["chart_a", "chart_b"]

    def test_all_charts(self):
        """Test getting all charts."""
        registry = ChartRegistry("TEST")

        def my_chart(df, ctx):
            return plt.figure()

        registry.register("test", my_chart, ChartMetadata(name="test", data="q"))

        all_charts = registry.all()
        assert "test" in all_charts
        # Should be a copy
        all_charts["new"] = None
        assert "new" not in registry


class TestChartLoader:
    """Test cases for ChartLoader."""

    def test_load_nonexistent_returns_empty(self, tmp_path):
        """Test loading from dir without charts.py returns empty registry."""
        loader = ChartLoader()
        registry = loader.load(tmp_path, "TEST")

        assert len(registry) == 0
        assert registry.report_id == "TEST"

    def test_load_valid_charts_module(self, tmp_path):
        """Test loading a valid charts.py module."""
        # Create a charts.py file
        charts_code = '''
from schoolreport.charts import chart, ChartContext
import matplotlib.pyplot as plt
import pandas as pd

@chart("my_chart", data="query1")
def my_chart(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    fig, ax = plt.subplots()
    ax.bar([1, 2, 3], [1, 2, 3])
    return fig
'''
        (tmp_path / "charts.py").write_text(charts_code)

        loader = ChartLoader()
        registry = loader.load(tmp_path, "TEST")

        assert len(registry) == 1
        assert registry.has("my_chart")

        chart_fn = registry.get("my_chart")
        assert chart_fn.metadata.data == "query1"

    def test_load_syntax_error_raises(self, tmp_path):
        """Test that syntax errors raise ChartLoadError."""
        # Create invalid Python
        (tmp_path / "charts.py").write_text("def broken(:")

        loader = ChartLoader()

        with pytest.raises(ChartLoadError, match="Syntax error"):
            loader.load(tmp_path, "TEST")

    def test_load_import_error_raises(self, tmp_path):
        """Test that import errors raise ChartLoadError."""
        # Create code with bad import
        (tmp_path / "charts.py").write_text("import nonexistent_module_xyz")

        loader = ChartLoader()

        with pytest.raises(ChartLoadError, match="Import error"):
            loader.load(tmp_path, "TEST")

    def test_get_registry(self, tmp_path):
        """Test getting previously loaded registry."""
        (tmp_path / "charts.py").write_text('''
from schoolreport.charts import chart
import matplotlib.pyplot as plt

@chart("test", data="q")
def test(df, ctx):
    return plt.figure()
''')

        loader = ChartLoader()
        loader.load(tmp_path, "TEST")

        registry = loader.get("TEST")
        assert registry is not None
        assert len(registry) == 1

    def test_get_nonexistent_returns_none(self):
        """Test getting non-loaded registry returns None."""
        loader = ChartLoader()
        assert loader.get("NONEXISTENT") is None


class TestChartDecorator:
    """Test cases for @chart decorator."""

    def test_decorator_stores_metadata_when_no_context(self):
        """Test that decorator stores metadata on function when not loading."""
        @chart("test_chart", data="query1", title="Test Title", figsize=(12, 8))
        def my_chart(df, ctx):
            return plt.figure()

        # When used outside of loading context, metadata is stored on function
        assert hasattr(my_chart, "_chart_metadata")
        assert my_chart._chart_metadata.name == "test_chart"
        assert my_chart._chart_metadata.data == "query1"
        assert my_chart._chart_metadata.title == "Test Title"
        assert my_chart._chart_metadata.figsize == (12, 8)

    def test_decorator_with_list_data(self):
        """Test decorator with multiple data sources."""
        @chart("multi_chart", data=["query1", "query2"])
        def my_chart(data, ctx):
            return plt.figure()

        assert my_chart._chart_metadata.data == ["query1", "query2"]

    def test_decorator_with_no_data(self):
        """Test decorator without data parameter."""
        @chart("static_chart")
        def my_chart(df, ctx):
            return plt.figure()

        assert my_chart._chart_metadata.data is None


class TestChartGeneratorWithCustomCharts:
    """Test ChartGenerator with custom chart functions."""

    @pytest.fixture
    def chart_generator(self):
        """Create ChartGenerator instance."""
        return ChartGenerator()

    @pytest.fixture
    def custom_registry(self):
        """Create registry with custom charts."""
        registry = ChartRegistry("TEST")

        def simple_bar(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
            fig, ax = plt.subplots(figsize=ctx.figsize)
            ax.bar(df["category"], df["count"], color=ctx.primary_color)
            return fig

        def multi_data_chart(data: Dict[str, pd.DataFrame], ctx: ChartContext) -> plt.Figure:
            fig, ax = plt.subplots()
            enrollment = data["enrollment"]
            ax.bar(enrollment["category"], enrollment["count"])
            return fig

        def optional_chart(df: pd.DataFrame, ctx: ChartContext):
            if df.empty:
                return None
            fig, ax = plt.subplots()
            ax.bar(df["category"], df["count"])
            return fig

        registry.register(
            "simple_bar",
            simple_bar,
            ChartMetadata(name="simple_bar", data="enrollment"),
        )
        registry.register(
            "multi_data",
            multi_data_chart,
            ChartMetadata(name="multi_data", data=["enrollment", "demographics"]),
        )
        registry.register(
            "optional",
            optional_chart,
            ChartMetadata(name="optional", data="enrollment"),
        )

        return registry

    @pytest.mark.asyncio
    async def test_generate_custom_chart(
        self,
        chart_generator,
        custom_registry,
        sample_enrollment_data,
        sample_demographics_data,
    ):
        """Test generating a custom chart."""
        data_map = {
            "enrollment": sample_enrollment_data,
            "demographics": sample_demographics_data,
        }

        results = await chart_generator.generate_many(
            charts=[],  # No YAML charts
            data_map=data_map,
            chart_registry=custom_registry,
            report_id="TEST",
        )

        assert "simple_bar" in results
        assert isinstance(results["simple_bar"], str)

        # Verify it's valid base64 SVG
        decoded = base64.b64decode(results["simple_bar"])
        assert b"svg" in decoded.lower()

    @pytest.mark.asyncio
    async def test_generate_multi_data_chart(
        self,
        chart_generator,
        custom_registry,
        sample_enrollment_data,
        sample_demographics_data,
    ):
        """Test generating a chart with multiple data sources."""
        data_map = {
            "enrollment": sample_enrollment_data,
            "demographics": sample_demographics_data,
        }

        results = await chart_generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=custom_registry,
            report_id="TEST",
        )

        assert "multi_data" in results
        assert isinstance(results["multi_data"], str)

    @pytest.mark.asyncio
    async def test_optional_chart_skipped_when_returns_none(
        self,
        chart_generator,
        custom_registry,
    ):
        """Test that charts returning None are skipped."""
        # Create registry with chart that returns None
        registry = ChartRegistry("TEST")

        def skip_chart(df, ctx):
            return None  # Always skip

        registry.register(
            "skip_me",
            skip_chart,
            ChartMetadata(name="skip_me", data="data"),
        )

        data_map = {"data": pd.DataFrame({"x": [1, 2, 3]})}

        results = await chart_generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=registry,
            report_id="TEST",
        )

        # Chart should not be in results
        assert "skip_me" not in results

    @pytest.mark.asyncio
    async def test_custom_chart_receives_params(self, chart_generator, sample_enrollment_data):
        """Test that custom charts receive report parameters."""
        registry = ChartRegistry("TEST")
        received_params = {}

        def param_chart(df, ctx):
            received_params.update(ctx.params)
            fig, ax = plt.subplots()
            ax.bar([1], [1])
            return fig

        registry.register(
            "param_chart",
            param_chart,
            ChartMetadata(name="param_chart", data="enrollment"),
        )

        data_map = {"enrollment": sample_enrollment_data}

        await chart_generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=registry,
            report_id="TEST",
            params={"year": 2024, "region": "North"},
        )

        assert received_params["year"] == 2024
        assert received_params["region"] == "North"

    @pytest.mark.asyncio
    async def test_missing_data_raises_error(self, chart_generator, custom_registry):
        """Test that missing data source raises error."""
        data_map = {}  # No data

        with pytest.raises(Exception, match="not found"):
            await chart_generator.generate_many(
                charts=[],
                data_map=data_map,
                chart_registry=custom_registry,
                report_id="TEST",
            )


class TestIntegrationWithTestFixture:
    """Integration tests using the TEST_CUSTOM_CHARTS fixture."""

    @pytest.fixture
    def fixture_path(self):
        """Path to test fixture."""
        return Path(__file__).parent.parent / "fixtures" / "reports" / "TEST_CUSTOM_CHARTS"

    def test_load_fixture_charts(self, fixture_path):
        """Test loading charts from test fixture."""
        if not fixture_path.exists():
            pytest.skip("Test fixture not found")

        loader = ChartLoader()
        registry = loader.load(fixture_path, "TEST_CUSTOM_CHARTS")

        # Should have all charts defined in the fixture
        assert registry.has("enrollment_bar")
        assert registry.has("demographics_donut")
        assert registry.has("multi_data_comparison")
        assert registry.has("optional_chart")
        assert registry.has("params_aware_chart")

    @pytest.mark.asyncio
    async def test_generate_fixture_charts(self, fixture_path):
        """Test generating charts from fixture."""
        if not fixture_path.exists():
            pytest.skip("Test fixture not found")

        loader = ChartLoader()
        registry = loader.load(fixture_path, "TEST_CUSTOM_CHARTS")

        data_map = {
            "enrollment": pd.DataFrame({
                "category": ["A", "B", "C"],
                "count": [100, 200, 150],
            }),
            "demographics": pd.DataFrame({
                "label": ["X", "Y", "Z"],
                "value": [40, 35, 25],
            }),
        }

        generator = ChartGenerator()
        results = await generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=registry,
            report_id="TEST_CUSTOM_CHARTS",
            params={"year": 2024},
        )

        # All charts should be generated
        assert "enrollment_bar" in results
        assert "demographics_donut" in results
        assert "multi_data_comparison" in results
        assert "params_aware_chart" in results

        # Verify SVG output
        for name, svg in results.items():
            decoded = base64.b64decode(svg)
            assert b"svg" in decoded.lower(), f"Chart {name} did not produce valid SVG"
