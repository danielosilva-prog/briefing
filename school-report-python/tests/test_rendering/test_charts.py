"""Tests for chart generation service."""

import pytest
import pandas as pd
import base64
from io import BytesIO
import matplotlib.pyplot as plt

from schoolreport.models.report import Chart, ChartType
from schoolreport.rendering.charts import ChartGenerator, ChartGeneratorError


@pytest.fixture
def chart_generator():
    """Create ChartGenerator instance."""
    return ChartGenerator()


@pytest.fixture
def sample_bar_data():
    """Sample data for bar chart."""
    return pd.DataFrame({
        "etapa": ["Fundamental I", "Fundamental II", "Médio"],
        "total": [1200, 800, 450]
    })


@pytest.fixture
def sample_donut_data():
    """Sample data for donut chart."""
    return pd.DataFrame({
        "category": ["Urbana", "Rural"],
        "count": [15000, 3500]
    })


class TestChartGenerator:
    """Test cases for ChartGenerator."""

    def test_generate_bar_chart(self, chart_generator, sample_bar_data):
        """Test generating a bar chart."""
        chart_def = Chart(
            name="matriculas_bar",
            type=ChartType.BAR,
            data="matriculas",
            x="etapa",
            y="total",
            title="Matrículas por Etapa",
            color="#2E4172"
        )

        result = chart_generator.generate(chart_def, sample_bar_data)

        # Should return base64-encoded SVG
        assert isinstance(result, str)
        assert len(result) > 0

        # Verify it's valid base64
        try:
            decoded = base64.b64decode(result)
            assert b"<svg" in decoded or b"svg" in decoded.lower()
        except Exception as e:
            pytest.fail(f"Invalid base64: {e}")

    def test_generate_donut_chart(self, chart_generator, sample_donut_data):
        """Test generating a donut chart."""
        chart_def = Chart(
            name="location_donut",
            type=ChartType.DONUT,
            data="location",
            values="count",
            labels="category",
            colors=["#2E4172", "#FF7F00"]
        )

        result = chart_generator.generate(chart_def, sample_donut_data)

        assert isinstance(result, str)
        assert len(result) > 0

        # Verify it's valid base64 SVG
        decoded = base64.b64decode(result)
        assert b"svg" in decoded.lower()

    def test_generate_line_chart(self, chart_generator):
        """Test generating a line chart."""
        data = pd.DataFrame({
            "year": [2020, 2021, 2022, 2023, 2024],
            "value": [100, 120, 115, 135, 150]
        })

        chart_def = Chart(
            name="trend_line",
            type=ChartType.LINE,
            data="trend",
            x="year",
            y="value",
            title="Tendência ao Longo do Tempo"
        )

        result = chart_generator.generate(chart_def, data)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_stacked_bar_chart(self, chart_generator):
        """Test generating a stacked bar chart."""
        data = pd.DataFrame({
            "region": ["Norte", "Nordeste", "Sul", "Sudeste", "Centro-Oeste"],
            "urbano": [1000, 2000, 1500, 3000, 800],
            "rural": [500, 1200, 300, 600, 400]
        })

        chart_def = Chart(
            name="regional_stacked",
            type=ChartType.STACKED_BAR,
            data="regional",
            x="region",
            y="urbano",  # Will use multiple y columns
            stack="type"
        )

        result = chart_generator.generate(chart_def, data)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_missing_required_column_raises_error(self, chart_generator):
        """Test that missing required columns raise error."""
        data = pd.DataFrame({
            "wrong_col": [1, 2, 3]
        })

        chart_def = Chart(
            name="test",
            type=ChartType.BAR,
            data="test",
            x="etapa",  # This column doesn't exist
            y="total"   # This column doesn't exist
        )

        with pytest.raises(ChartGeneratorError, match="Missing required column"):
            chart_generator.generate(chart_def, data)

    def test_empty_dataframe_raises_error(self, chart_generator):
        """Test that empty DataFrame raises error."""
        data = pd.DataFrame()

        chart_def = Chart(
            name="test",
            type=ChartType.BAR,
            data="test",
            x="x",
            y="y"
        )

        with pytest.raises(ChartGeneratorError, match="No data"):
            chart_generator.generate(chart_def, data)

    def test_custom_colors_applied(self, chart_generator, sample_bar_data):
        """Test that custom colors are applied."""
        chart_def = Chart(
            name="colored_bar",
            type=ChartType.BAR,
            data="test",
            x="etapa",
            y="total",
            color="#FF0000"  # Red color
        )

        result = chart_generator.generate(chart_def, sample_bar_data)

        # Just verify it generates without error
        # Actual color verification would require parsing SVG
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_many_parallel(self, chart_generator, sample_bar_data, sample_donut_data):
        """Test generating multiple charts in parallel."""
        charts = [
            Chart(
                name="chart1",
                type=ChartType.BAR,
                data="data1",
                x="etapa",
                y="total"
            ),
            Chart(
                name="chart2",
                type=ChartType.DONUT,
                data="data2",
                values="count",
                labels="category"
            )
        ]

        data_map = {
            "data1": sample_bar_data,
            "data2": sample_donut_data
        }

        results = await chart_generator.generate_many(charts, data_map)

        assert isinstance(results, dict)
        assert len(results) == 2
        assert "chart1" in results
        assert "chart2" in results

        # Both should be base64 strings
        assert isinstance(results["chart1"], str)
        assert isinstance(results["chart2"], str)

    @pytest.mark.asyncio
    async def test_generate_many_with_error_propagates(self, chart_generator):
        """Test that errors in parallel generation are propagated."""
        charts = [
            Chart(
                name="bad_chart",
                type=ChartType.BAR,
                data="missing_data",
                x="x",
                y="y"
            )
        ]

        data_map = {}  # Empty - will cause error

        with pytest.raises(ChartGeneratorError):
            await chart_generator.generate_many(charts, data_map)

    def test_svg_is_valid_xml(self, chart_generator, sample_bar_data):
        """Test that generated SVG is valid XML."""
        chart_def = Chart(
            name="test",
            type=ChartType.BAR,
            data="test",
            x="etapa",
            y="total"
        )

        result = chart_generator.generate(chart_def, sample_bar_data)
        decoded = base64.b64decode(result)

        # Basic XML validity checks
        assert decoded.count(b"<svg") == decoded.count(b"</svg")
        assert b"xmlns" in decoded  # Should have XML namespace

    def test_markers_promoted_from_comments_to_text_nodes(self, chart_generator):
        """Graph markers should be emitted as searchable text nodes in SVG."""
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.text(
            1.0,
            1.0,
            "<<ATM_EQ_GRAPH_START:id=unit_test_graph>>",
            alpha=0.0,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=1,
        )
        ax.text(
            0.0,
            0.0,
            "<<ATM_EQ_GRAPH_END:id=unit_test_graph>>",
            alpha=0.0,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=1,
        )

        svg = chart_generator._fig_to_svg(fig).decode("utf-8")
        plt.close(fig)

        assert 'data-atm-marker="true"' in svg
        assert "&lt;&lt;ATM_EQ_GRAPH_START:id=unit_test_graph&gt;&gt;" in svg
        assert "&lt;&lt;ATM_EQ_GRAPH_END:id=unit_test_graph&gt;&gt;" in svg
        assert "<!-- &lt;&lt;ATM_EQ_GRAPH_START:id=unit_test_graph&gt;&gt; -->" not in svg
        assert "<!-- &lt;&lt;ATM_EQ_GRAPH_END:id=unit_test_graph&gt;&gt; -->" not in svg

    def test_marker_promotion_uses_original_svg_coordinates(self):
        """Promoted text markers should preserve source marker coordinates when available."""
        input_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="380">
  <g id="text_1">
    <!-- &lt;&lt;ATM_EQ_GRAPH_START:id=coord_test&gt;&gt; -->
    <g style="fill: #262626; opacity: 0" transform="translate(468.107031 7.57) scale(0.01 -0.01)">
    </g>
  </g>
  <g id="text_2">
    <!-- &lt;&lt;ATM_EQ_GRAPH_END:id=coord_test&gt;&gt; -->
    <g style="fill: #262626; opacity: 0" transform="translate(15.270000 361.020000) scale(0.01 -0.01)">
    </g>
  </g>
</svg>
"""
        promoted = ChartGenerator._promote_graph_markers(input_svg)

        assert 'data-atm-marker="true"' in promoted
        assert 'x="468.107031" y="7.570000"' in promoted
        assert 'x="15.270000" y="361.020000"' in promoted
        assert "<!-- &lt;&lt;ATM_EQ_GRAPH_START:id=coord_test&gt;&gt; -->" not in promoted
        assert "<!-- &lt;&lt;ATM_EQ_GRAPH_END:id=coord_test&gt;&gt; -->" not in promoted
