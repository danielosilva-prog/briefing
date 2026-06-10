"""Chart generation service using matplotlib and seaborn."""

from __future__ import annotations

import asyncio
import base64
import html
import importlib.util
import logging
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from schoolreport.models.report import Chart, ChartType
from schoolreport.rendering.chart_framework import ChartContext, ChartRegistry

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

_matplotlib_initialized = False


def _ensure_matplotlib():
    """Initialize matplotlib with Agg backend on first use."""
    global _matplotlib_initialized
    if not _matplotlib_initialized:
        import matplotlib

        matplotlib.use("Agg")
        _matplotlib_initialized = True


logger = logging.getLogger(__name__)

_GRAPH_MARKER_COMMENT_PATTERN = re.compile(
    r"<!--\s*&lt;&lt;(ATM(?:_EQ)?_GRAPH_(?:START|END):id=[^&<>]+)&gt;&gt;\s*-->"
)
_GRAPH_MARKER_WITH_TRANSFORM_PATTERN = re.compile(
    r"<!--\s*&lt;&lt;(ATM(?:_EQ)?_GRAPH_(?:START|END):id=[^&<>]+)&gt;&gt;\s*-->\s*"
    r"<g[^>]*transform=[\"']translate\(([-+0-9.eE]+)\s+([-+0-9.eE]+)\)[^\"']*[\"']",
    re.DOTALL,
)
_SVG_DIMENSION_PATTERN = re.compile(
    r"<svg[^>]*\swidth=[\"']([^\"']+)[\"'][^>]*\sheight=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)


class ChartGeneratorError(Exception):
    """Raised when chart generation fails."""

    pass


class ChartGenerator:
    """
    Generate charts using matplotlib/seaborn and export as base64 SVG.

    Supports bar charts, donut charts, line charts, stacked bars, and maps.
    """

    def __init__(self, dpi: int = 200, figsize: tuple[float, float] = (10, 6)):
        """
        Initialize chart generator.

        Args:
            dpi: Dots per inch for rendering
            figsize: Figure size in inches (width, height)
        """
        self.dpi = dpi
        self.figsize = figsize

        _ensure_matplotlib()
        import seaborn as sns

        sns.set_theme(style="whitegrid")

    def generate(self, chart_def: Chart, data: pd.DataFrame) -> str:
        """
        Generate a single chart and return as base64-encoded SVG.

        Args:
            chart_def: Chart definition
            data: DataFrame with chart data

        Returns:
            Base64-encoded SVG string

        Raises:
            ChartGeneratorError: If chart generation fails
        """
        import matplotlib.pyplot as plt

        try:
            # Validate data
            if data.empty:
                raise ChartGeneratorError(f"No data provided for chart '{chart_def.name}'")

            # Generate chart based on type
            if chart_def.type == ChartType.BAR:
                fig = self._generate_bar(chart_def, data)
            elif chart_def.type == ChartType.DONUT:
                fig = self._generate_donut(chart_def, data)
            elif chart_def.type == ChartType.LINE:
                fig = self._generate_line(chart_def, data)
            elif chart_def.type == ChartType.STACKED_BAR:
                fig = self._generate_stacked_bar(chart_def, data)
            elif chart_def.type == ChartType.MAP:
                fig = self._generate_map(chart_def, data)
            else:
                raise ChartGeneratorError(f"Unsupported chart type: {chart_def.type}")

            # Convert to SVG and encode as base64
            svg_bytes = self._fig_to_svg(fig)
            fig.clf()

            return base64.b64encode(svg_bytes).decode("utf-8")

        except ChartGeneratorError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate chart '{chart_def.name}': {e}")
            raise ChartGeneratorError(f"Failed to generate chart '{chart_def.name}': {e}") from e

    def _generate_bar(self, chart_def: Chart, data: pd.DataFrame) -> "plt.Figure":
        """Generate a bar chart."""
        from matplotlib.figure import Figure

        self._validate_columns(data, [chart_def.x, chart_def.y])

        fig = Figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111)

        # Create bar chart
        color = chart_def.color or "#2E4172"
        ax.bar(data[chart_def.x], data[chart_def.y], color=color)

        # Set labels and title
        if chart_def.title:
            ax.set_title(chart_def.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(chart_def.x.replace("_", " ").title())
        ax.set_ylabel(chart_def.y.replace("_", " ").title())

        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        return fig

    def _generate_donut(self, chart_def: Chart, data: pd.DataFrame) -> "plt.Figure":
        """Generate a donut/pie chart."""
        import seaborn as sns
        from matplotlib.figure import Figure

        self._validate_columns(data, [chart_def.values, chart_def.labels])

        fig = Figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111)

        # Create donut chart
        colors = chart_def.colors or sns.color_palette("husl", len(data))

        wedges, texts, autotexts = ax.pie(
            data[chart_def.values],
            labels=data[chart_def.labels],
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.5),  # Makes it a donut
        )

        # Improve text styling
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        if chart_def.title:
            ax.set_title(chart_def.title, fontsize=14, fontweight="bold")

        fig.tight_layout()
        return fig

    def _generate_line(self, chart_def: Chart, data: pd.DataFrame) -> "plt.Figure":
        """Generate a line chart."""
        from matplotlib.figure import Figure

        self._validate_columns(data, [chart_def.x, chart_def.y])

        fig = Figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111)

        # Create line chart
        color = chart_def.color or "#2E4172"
        ax.plot(data[chart_def.x], data[chart_def.y], color=color, marker="o", linewidth=2)

        # Set labels and title
        if chart_def.title:
            ax.set_title(chart_def.title, fontsize=14, fontweight="bold")
        ax.set_xlabel(chart_def.x.replace("_", " ").title())
        ax.set_ylabel(chart_def.y.replace("_", " ").title())

        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        return fig

    def _generate_stacked_bar(self, chart_def: Chart, data: pd.DataFrame) -> "plt.Figure":
        """Generate a stacked bar chart."""
        import seaborn as sns
        from matplotlib.figure import Figure

        # For stacked bar, we need multiple value columns
        # Use all numeric columns except the x column
        numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()

        if chart_def.x in numeric_cols:
            numeric_cols.remove(chart_def.x)

        if not numeric_cols:
            raise ChartGeneratorError("No numeric columns found for stacked bar chart")

        fig = Figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.add_subplot(111)

        # Create stacked bar chart
        colors = chart_def.colors or sns.color_palette("husl", len(numeric_cols))

        data.set_index(chart_def.x)[numeric_cols].plot(
            kind="bar", stacked=True, ax=ax, color=colors
        )

        if chart_def.title:
            ax.set_title(chart_def.title, fontsize=14, fontweight="bold")

        ax.legend(title=chart_def.stack or "Category", bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        return fig

    def _generate_map(self, chart_def: Chart, data: pd.DataFrame) -> plt.Figure:
        """Generate a geographic map chart."""
        # Placeholder for map generation
        # Would require geopandas and geographic data
        raise ChartGeneratorError("Map charts not yet implemented")

    def _validate_columns(self, data: pd.DataFrame, required_cols: list[str]) -> None:
        """
        Validate that required columns exist in DataFrame.

        Args:
            data: DataFrame to validate
            required_cols: List of required column names

        Raises:
            ChartGeneratorError: If any required column is missing
        """
        missing = [col for col in required_cols if col and col not in data.columns]
        if missing:
            raise ChartGeneratorError(
                f"Missing required columns: {missing}. Available columns: {list(data.columns)}"
            )

    @staticmethod
    def _svg_length_to_points(raw_value: str) -> Optional[float]:
        """Convert SVG length strings (pt/px/in/cm/mm) to points."""
        match = re.match(
            r"^\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*([a-zA-Z]*)\s*$",
            str(raw_value),
        )
        if not match:
            return None
        value = float(match.group(1))
        unit = match.group(2).lower()
        if unit in {"", "pt"}:
            return value
        if unit == "px":
            return value * (72.0 / 96.0)
        if unit == "in":
            return value * 72.0
        if unit == "cm":
            return value * (72.0 / 2.54)
        if unit == "mm":
            return value * (72.0 / 25.4)
        return None

    @classmethod
    def _extract_svg_dimensions_points(cls, svg_content: str) -> Optional[tuple[float, float]]:
        match = _SVG_DIMENSION_PATTERN.search(svg_content)
        if match is None:
            return None
        width_pt = cls._svg_length_to_points(match.group(1))
        height_pt = cls._svg_length_to_points(match.group(2))
        if width_pt is None or height_pt is None:
            return None
        return (float(width_pt), float(height_pt))

    def _fig_to_svg(self, fig) -> bytes:
        """
        Convert matplotlib figure to SVG bytes.

        Args:
            fig: Matplotlib figure

        Returns:
            SVG as bytes
        """
        buffer = BytesIO()
        preserve_exact_size = bool(getattr(fig, "_schoolreport_preserve_svg_size", False))
        expected_size_inches = getattr(fig, "_schoolreport_expected_svg_size_inches", None)

        save_kwargs: dict[str, Any] = {"format": "svg"}
        if preserve_exact_size:
            # Map charts must keep the exact designer dimensions in the SVG root.
            save_kwargs["dpi"] = (
                float(fig.get_dpi()) if hasattr(fig, "get_dpi") else float(self.dpi)
            )
            save_kwargs["bbox_inches"] = None
            save_kwargs["pad_inches"] = 0.0
        else:
            save_kwargs["dpi"] = self.dpi
            save_kwargs["bbox_inches"] = "tight"

        fig.savefig(buffer, **save_kwargs)
        buffer.seek(0)
        svg_content = buffer.read().decode("utf-8")
        if (
            preserve_exact_size
            and isinstance(expected_size_inches, tuple)
            and len(expected_size_inches) == 2
        ):
            dims = self._extract_svg_dimensions_points(svg_content)
            if dims is not None:
                expected_w_pt = float(expected_size_inches[0]) * 72.0
                expected_h_pt = float(expected_size_inches[1]) * 72.0
                logger.debug(
                    "Map SVG dimensions (pt): expected=(%.2f, %.2f), actual=(%.2f, %.2f)",
                    expected_w_pt,
                    expected_h_pt,
                    float(dims[0]),
                    float(dims[1]),
                )
        svg_content = self._promote_graph_markers(svg_content)
        return svg_content.encode("utf-8")

    @staticmethod
    def _promote_graph_markers(svg_content: str) -> str:
        """
        Promote graph markers from SVG comments to tiny invisible text nodes.

        Matplotlib can serialize hidden marker texts as comments when text is
        converted to paths in SVG. Comments do not survive downstream PDF
        generation, so we transform marker comments into real <text> nodes that
        remain searchable while staying visually imperceptible.
        """
        marker_payloads = _GRAPH_MARKER_COMMENT_PATTERN.findall(svg_content)
        if not marker_payloads:
            return svg_content

        # Keep first occurrence order, drop duplicates.
        marker_payloads = list(dict.fromkeys(marker_payloads))

        marker_positions: dict[str, tuple[float, float]] = {}
        for payload, x_str, y_str in _GRAPH_MARKER_WITH_TRANSFORM_PATTERN.findall(svg_content):
            if payload in marker_positions:
                continue
            try:
                marker_positions[payload] = (float(x_str), float(y_str))
            except ValueError:
                continue

        # Remove marker comments to avoid relying on comment propagation.
        svg_without_marker_comments = _GRAPH_MARKER_COMMENT_PATTERN.sub("", svg_content)

        if 'data-atm-marker="true"' in svg_without_marker_comments:
            return svg_without_marker_comments

        marker_nodes: list[str] = []
        base_x = 0.1
        base_y = 0.2
        step_y = 0.2
        for idx, payload in enumerate(marker_payloads):
            marker_text = html.escape(f"<<{payload}>>")
            if payload in marker_positions:
                x, y = marker_positions[payload]
            else:
                x = base_x
                y = base_y + (idx * step_y)
            marker_nodes.append(
                (
                    '<text data-atm-marker="true" x="{x:.6f}" y="{y:.6f}" '
                    'style="font-size: 0.1px; fill: #000000; fill-opacity: 0.001; '
                    'font-family: Rawline, DejaVu Sans, Arial, sans-serif;">'
                    "{text}</text>"
                ).format(x=x, y=y, text=marker_text)
            )

        insert_at = svg_without_marker_comments.rfind("</svg>")
        if insert_at < 0:
            return svg_without_marker_comments

        insertion = "\n  " + "\n  ".join(marker_nodes) + "\n"
        return (
            svg_without_marker_comments[:insert_at]
            + insertion
            + svg_without_marker_comments[insert_at:]
        )

    def _build_context(
        self,
        chart_name: str,
        report_id: str,
        metadata: Optional["ChartMetadata"] = None,
        params: Optional[Dict[str, Any]] = None,
        assets_dir: Optional[Path] = None,
    ) -> ChartContext:
        """
        Build a ChartContext for a custom chart function.

        Args:
            chart_name: Name of the chart being generated
            report_id: Report identifier
            metadata: Chart metadata (size comes from here if provided)
            params: Report parameters from request
            assets_dir: Path to assets directory

        Returns:
            ChartContext instance
        """
        size = (
            metadata.size
            if metadata
            else (int(self.figsize[0] * self.dpi), int(self.figsize[1] * self.dpi))
        )
        dpi = metadata.dpi if metadata else self.dpi
        return ChartContext(
            chart_name=chart_name,
            report_id=report_id,
            size=size,
            dpi=dpi,
            params=params or {},
            assets_dir=assets_dir,
        )

    @staticmethod
    def _load_atm_eq_empty_state_factory(assets_dir: Optional[Path]):
        """Load the ATM-EQ empty-state figure factory from local chart helpers."""
        helper_module = sys.modules.get("atm_eq_chart_helpers")
        if helper_module is not None:
            factory = getattr(helper_module, "build_empty_state_figure", None)
            if callable(factory):
                return factory

        if assets_dir is None:
            return None

        helper_path = assets_dir.parent.parent / "charts" / "chart_helpers.py"
        if not helper_path.exists():
            return None

        spec = importlib.util.spec_from_file_location("atm_eq_chart_helpers", helper_path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules["atm_eq_chart_helpers"] = module
        spec.loader.exec_module(module)
        factory = getattr(module, "build_empty_state_figure", None)
        return factory if callable(factory) else None

    def _build_empty_state_svg_bytes(
        self,
        *,
        chart_name: str,
        report_id: str,
        ctx: ChartContext,
        assets_dir: Optional[Path],
    ) -> Optional[bytes]:
        """Build an empty-state SVG for custom charts that intentionally return None."""
        if report_id != "ATM-EQ":
            return None

        fig = None
        factory = self._load_atm_eq_empty_state_factory(assets_dir=assets_dir)
        try:
            if factory is not None:
                fig = factory(figsize=ctx.figsize, dpi=ctx.dpi)
            else:
                import matplotlib.pyplot as plt
                from matplotlib.patches import FancyBboxPatch

                fig = plt.figure(figsize=ctx.figsize, dpi=ctx.dpi)
                ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
                fig.patch.set_facecolor("none")
                fig.patch.set_alpha(0.0)
                ax.set_facecolor("none")
                ax.set_xlim(0.0, 1.0)
                ax.set_ylim(0.0, 1.0)
                ax.axis("off")
                ax.add_patch(
                    FancyBboxPatch(
                        (0.02, 0.08),
                        0.96,
                        0.84,
                        boxstyle="round,pad=0.02,rounding_size=0.03",
                        linewidth=0.0,
                        facecolor="#E7E7E7",
                        edgecolor="none",
                        transform=ax.transAxes,
                        zorder=1,
                    )
                )
                ax.add_patch(
                    FancyBboxPatch(
                        (0.31, 0.36),
                        0.38,
                        0.28,
                        boxstyle="round,pad=0.015,rounding_size=0.035",
                        linewidth=0.0,
                        facecolor="#A7A7A7",
                        edgecolor="none",
                        transform=ax.transAxes,
                        zorder=2,
                    )
                )
                ax.text(
                    0.5,
                    0.5,
                    "AUS\u00caNCIA DE dados suficientes",
                    ha="center",
                    va="center",
                    color="#FFFFFF",
                    fontsize=14.0,
                    fontfamily="Rawline",
                    fontweight="bold",
                    transform=ax.transAxes,
                    zorder=3,
                )
                setattr(fig, "_schoolreport_preserve_svg_size", True)
                setattr(
                    fig,
                    "_schoolreport_expected_svg_size_inches",
                    (float(ctx.figsize[0]), float(ctx.figsize[1])),
                )
        except Exception as exc:
            logger.warning(
                "Falha ao construir empty-state do chart '%s' para %s: %s",
                chart_name,
                report_id,
                exc,
            )
            return None

        try:
            return self._fig_to_svg(fig)
        finally:
            if fig is not None:
                fig.clf()

    def _resolve_data(
        self,
        data_spec: Union[str, List[str], None],
        data_map: Dict[str, pd.DataFrame],
        chart_name: str,
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Resolve data for a chart based on its data specification.

        Args:
            data_spec: Data specification (single query name, list of names, or None)
            data_map: Dictionary mapping query names to DataFrames
            chart_name: Chart name for error messages

        Returns:
            Single DataFrame or dict of DataFrames

        Raises:
            ChartGeneratorError: If required data is not found
        """
        if data_spec is None:
            import pandas as pd

            return pd.DataFrame()

        if isinstance(data_spec, str):
            if data_spec not in data_map:
                raise ChartGeneratorError(
                    f"Data '{data_spec}' not found for chart '{chart_name}'. "
                    f"Available: {list(data_map.keys())}"
                )
            return data_map[data_spec]

        # List of data sources
        result = {}
        for name in data_spec:
            if name not in data_map:
                raise ChartGeneratorError(
                    f"Data '{name}' not found for chart '{chart_name}'. "
                    f"Available: {list(data_map.keys())}"
                )
            result[name] = data_map[name]
        return result

    async def generate_one(
        self,
        chart_name: str,
        is_custom: bool,
        data_map: Dict[str, pd.DataFrame],
        chart_registry: Optional[ChartRegistry] = None,
        yaml_charts: Optional[Dict[str, Chart]] = None,
        report_id: str = "",
        params: Optional[Dict[str, Any]] = None,
        assets_dir: Optional[Path] = None,
    ) -> tuple[str, str]:
        """
        Generate a single chart and return (name, base64_svg).

        Args:
            chart_name: Chart identifier
            is_custom: True if chart comes from the Python registry
            data_map: Dictionary mapping query names to DataFrames
            chart_registry: Optional registry of custom chart functions
            yaml_charts: Lookup of YAML chart definitions
            report_id: Report identifier (for context)
            params: Report parameters from request
            assets_dir: Path to assets directory

        Returns:
            Tuple of (chart_name, base64-encoded SVG). SVG is empty string
            if the chart opted to skip.

        Raises:
            ChartGeneratorError: If chart generation fails
        """
        try:
            loop = asyncio.get_event_loop()

            if is_custom and chart_registry:
                # Use custom chart function
                chart_fn = chart_registry.get(chart_name)
                if chart_fn is None:
                    raise ChartGeneratorError(f"Custom chart '{chart_name}' not found in registry")

                # Build context with per-chart size from metadata
                ctx = self._build_context(
                    chart_name=chart_name,
                    report_id=report_id,
                    metadata=chart_fn.metadata,
                    params=params,
                    assets_dir=assets_dir,
                )

                # Resolve data based on chart's data specification
                data = self._resolve_data(chart_fn.metadata.data, data_map, chart_name)

                # Run custom function in thread pool
                def _run_custom():
                    fig = chart_fn.func(data, ctx)
                    if fig is None:
                        empty_state_svg = self._build_empty_state_svg_bytes(
                            chart_name=chart_name,
                            report_id=report_id,
                            ctx=ctx,
                            assets_dir=assets_dir,
                        )
                        if empty_state_svg is None:
                            return None  # Chart opted to skip
                        return base64.b64encode(empty_state_svg).decode("utf-8")
                    svg_bytes = self._fig_to_svg(fig)
                    fig.clf()
                    return base64.b64encode(svg_bytes).decode("utf-8")

                result = await loop.run_in_executor(None, _run_custom)

                if result is None:
                    logger.debug(f"Chart '{chart_name}' returned None, skipping")
                    return (chart_name, "")

                logger.debug(f"Generated custom chart '{chart_name}'")
                return (chart_name, result)

            else:
                # Use YAML-defined chart with built-in generator
                yaml_charts = yaml_charts or {}
                chart_def = yaml_charts.get(chart_name)
                if chart_def is None:
                    raise ChartGeneratorError(f"Chart definition not found: {chart_name}")

                if chart_def.data not in data_map:
                    raise ChartGeneratorError(
                        f"Data '{chart_def.data}' not found for chart '{chart_name}'"
                    )

                data = data_map[chart_def.data]
                result = await loop.run_in_executor(None, self.generate, chart_def, data)

                logger.debug(f"Generated YAML chart '{chart_name}'")
                return (chart_name, result)

        except ChartGeneratorError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate chart '{chart_name}': {e}")
            raise ChartGeneratorError(f"Failed to generate chart '{chart_name}': {e}") from e

    async def generate_many(
        self,
        charts: list[Chart],
        data_map: Dict[str, pd.DataFrame],
        chart_registry: Optional[ChartRegistry] = None,
        report_id: str = "",
        params: Optional[Dict[str, Any]] = None,
        assets_dir: Optional[Path] = None,
    ) -> Dict[str, str]:
        """
        Generate multiple charts in parallel.

        Supports both YAML-defined charts and custom Python chart functions.
        Custom charts from the registry take precedence over YAML definitions.

        Args:
            charts: List of chart definitions from YAML
            data_map: Dictionary mapping query names to DataFrames
            chart_registry: Optional registry of custom chart functions
            report_id: Report identifier (for context)
            params: Report parameters from request
            assets_dir: Path to assets directory

        Returns:
            Dictionary mapping chart names to base64-encoded SVGs

        Raises:
            ChartGeneratorError: If any chart generation fails
        """
        # Collect all charts to generate (custom + YAML-defined)
        charts_to_generate: List[tuple[str, bool]] = []  # (name, is_custom)

        # Add custom charts from registry
        if chart_registry:
            for name in chart_registry.list():
                charts_to_generate.append((name, True))

        # Add YAML-defined charts (skip if already in registry)
        custom_names = {name for name, _ in charts_to_generate}
        for chart in charts:
            if chart.name not in custom_names:
                charts_to_generate.append((chart.name, False))

        # Create lookup for YAML chart definitions
        yaml_charts = {chart.name: chart for chart in charts}

        # Generate all charts in parallel using generate_one
        tasks = [
            self.generate_one(
                chart_name=name,
                is_custom=is_custom,
                data_map=data_map,
                chart_registry=chart_registry,
                yaml_charts=yaml_charts,
                report_id=report_id,
                params=params,
                assets_dir=assets_dir,
            )
            for name, is_custom in charts_to_generate
        ]
        results = await asyncio.gather(*tasks)

        # Convert list of tuples to dict, filtering out empty results
        return {name: svg for name, svg in results if svg}
