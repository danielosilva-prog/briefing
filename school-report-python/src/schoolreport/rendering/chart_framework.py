"""Framework for custom chart definitions using decorators.

This module provides the infrastructure for defining charts as Python functions
instead of declarative YAML configurations. Charts are auto-discovered from
`charts.py` files in report directories.

Example usage in reports/ATM/charts.py:

    from schoolreport.charts import chart, ChartContext
    import matplotlib.pyplot as plt

    @chart("enrollment_bar", data="matriculas", size=(900, 320))
    def enrollment_bar(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
        fig, ax = plt.subplots(figsize=ctx.figsize)
        ax.bar(df["etapa"], df["total"], color=ctx.primary_color)
        return fig
"""

import importlib.util
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Union


logger = logging.getLogger(__name__)

# Thread-local storage for the current registry during module loading
_loading_context = threading.local()

# Default DPI used for pixel → inch conversion.
DEFAULT_DPI = 100


@dataclass
class ChartMetadata:
    """Metadata for a registered chart function."""

    name: str
    data: Union[str, List[str], None]
    title: Optional[str] = None
    size: tuple[int, int] = (1000, 600)
    dpi: int = DEFAULT_DPI
    format: Literal["svg", "png"] = "svg"

    @property
    def figsize(self) -> tuple[float, float]:
        """Convert pixel size to matplotlib figsize (inches)."""
        return (self.size[0] / self.dpi, self.size[1] / self.dpi)


@dataclass
class ChartFunction:
    """A registered chart function with its metadata."""

    func: Callable
    metadata: ChartMetadata


@dataclass
class ChartContext:
    """Context passed to custom chart functions.

    Provides access to report parameters, styling settings, and utility methods.
    """

    # Chart identification
    chart_name: str
    report_id: str

    # Rendering settings (size in pixels, figsize in inches derived from it)
    size: tuple[int, int] = (1000, 600)
    dpi: int = DEFAULT_DPI

    @property
    def figsize(self) -> tuple[float, float]:
        """Matplotlib figsize in inches, derived from pixel size and DPI."""
        return (self.size[0] / self.dpi, self.size[1] / self.dpi)

    # Report parameters (from request)
    params: Dict[str, Any] = field(default_factory=dict)

    # Style/theme settings
    primary_color: str = "#2E4172"
    secondary_color: str = "#FF7F00"
    color_palette: List[str] = field(
        default_factory=lambda: ["#2E4172", "#4A6FA5", "#6B8FC5", "#8DAFE5", "#FF7F00", "#4CAF50"]
    )

    # Font settings
    font_family: str = "Rawline"
    title_fontsize: int = 14
    label_fontsize: int = 12

    # Localization
    locale: str = "pt_BR"

    # Assets path (for custom images, etc.)
    assets_dir: Optional[Path] = None

    def format_number(self, value: float, decimals: int = 0) -> str:
        """Format number with locale-appropriate thousand separators."""
        if decimals == 0:
            return f"{value:,.0f}".replace(",", ".")
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def format_percent(self, value: float, decimals: int = 1) -> str:
        """Format value as percentage."""
        return f"{value:.{decimals}f}%".replace(".", ",")

    def get_colors(self, n: int) -> List[str]:
        """Get n colors from the palette, cycling if needed."""
        if not self.color_palette:
            import matplotlib.pyplot as plt

            # Fallback to matplotlib colormap
            cmap = plt.colormaps.get_cmap("Blues")
            return [cmap(i / max(n - 1, 1)) for i in range(n)]

        # Cycle through palette if n > len(palette)
        return [self.color_palette[i % len(self.color_palette)] for i in range(n)]


class ChartRegistry:
    """Registry of custom chart functions for a single report.

    Stores chart functions registered via the @chart decorator and provides
    methods to retrieve them for rendering.
    """

    def __init__(self, report_id: str):
        """Initialize registry for a report.

        Args:
            report_id: The report identifier (e.g., "ATM")
        """
        self.report_id = report_id
        self._charts: Dict[str, ChartFunction] = {}
        self._module_path: Optional[Path] = None
        self._last_modified: float = 0

    def register(self, name: str, func: Callable, metadata: ChartMetadata) -> None:
        """Register a chart function.

        Args:
            name: Unique chart identifier
            func: The chart function
            metadata: Chart metadata from decorator
        """
        if name in self._charts:
            logger.warning(f"Chart '{name}' already registered in {self.report_id}, overwriting")

        self._charts[name] = ChartFunction(func=func, metadata=metadata)
        logger.debug(f"Registered chart '{name}' for report {self.report_id}")

    def get(self, name: str) -> Optional[ChartFunction]:
        """Get a registered chart function by name.

        Args:
            name: Chart identifier

        Returns:
            ChartFunction if found, None otherwise
        """
        return self._charts.get(name)

    def list(self) -> List[str]:
        """List all registered chart names.

        Returns:
            Sorted list of chart names
        """
        return sorted(self._charts.keys())

    def has(self, name: str) -> bool:
        """Check if a chart is registered.

        Args:
            name: Chart identifier

        Returns:
            True if chart exists
        """
        return name in self._charts

    def all(self) -> Dict[str, ChartFunction]:
        """Get all registered charts.

        Returns:
            Dictionary of chart name to ChartFunction
        """
        return self._charts.copy()

    def __len__(self) -> int:
        return len(self._charts)

    def __contains__(self, name: str) -> bool:
        return name in self._charts


def chart(
    name: str,
    data: Union[str, List[str], None] = None,
    title: Optional[str] = None,
    size: tuple[int, int] = (1000, 600),
    dpi: int = DEFAULT_DPI,
    format: Literal["svg", "png"] = "svg",
    # Deprecated — use `size` instead.
    figsize: Optional[tuple[float, float]] = None,
) -> Callable:
    """Decorator to register a function as a custom chart generator.

    Args:
        name: Unique chart identifier (used in templates and output)
        data: Query name(s) to use for chart data. Can be:
            - str: Single query name (df passed to function)
            - list[str]: Multiple query names (dict[str, df] passed to function)
            - None: No data required (empty df passed)
        title: Default chart title (can be overridden in function)
        size: Chart dimensions in pixels (width, height). This is the
            only size you need to think about — the framework converts
            to matplotlib inches internally.
        format: Output format ("svg" or "png")

    Returns:
        Decorator function

    Example:
        @chart("enrollment_bar", data="matriculas", size=(900, 320))
        def enrollment_bar(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
            fig, ax = plt.subplots(figsize=ctx.figsize)
            ax.bar(df["etapa"], df["total"])
            return fig

        @chart("comparison", data=["current", "previous"], size=(900, 300))
        def comparison(data: dict[str, pd.DataFrame], ctx: ChartContext) -> plt.Figure:
            fig, ax = plt.subplots()
            ax.plot(data["current"]["x"], data["current"]["y"])
            ax.plot(data["previous"]["x"], data["previous"]["y"])
            return fig
    """
    # Support deprecated `figsize` kwarg — convert inches to pixels.
    if figsize is not None:
        resolved_size = (int(figsize[0] * DEFAULT_DPI), int(figsize[1] * DEFAULT_DPI))
    else:
        resolved_size = size

    def decorator(func: Callable) -> Callable:
        # Get the registry from the loading context
        registry = getattr(_loading_context, "registry", None)

        meta = ChartMetadata(
            name=name,
            data=data,
            title=title,
            size=resolved_size,
            format=format,
        )

        if registry is None:
            # Not being loaded via ChartLoader - store metadata on function for later
            # This allows importing charts.py directly for testing
            func._chart_metadata = meta
            logger.debug(f"Chart '{name}' decorated but not registered (no loading context)")
            return func

        # Register the chart
        registry.register(name, func, meta)

        return func

    return decorator


class ChartLoader:
    """Loads charts.py modules from report directories.

    Handles dynamic importing of chart modules and populating their registries.
    """

    def __init__(self):
        """Initialize the chart loader."""
        self._registries: Dict[str, ChartRegistry] = {}

    def load(self, report_dir: Path, report_id: str) -> ChartRegistry:
        """Load charts.py module from a report directory.

        Args:
            report_dir: Path to the report directory
            report_id: Report identifier

        Returns:
            ChartRegistry with all discovered charts (empty if no charts.py)

        Raises:
            ChartLoadError: If module has syntax/import errors
        """
        charts_path = report_dir / "charts.py"

        # Create registry (even if no charts.py exists)
        registry = ChartRegistry(report_id)

        if not charts_path.exists():
            logger.debug(f"No charts.py found for report {report_id}")
            self._registries[report_id] = registry
            return registry

        try:
            # Set up loading context for decorator
            _loading_context.registry = registry

            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                f"schoolreport.reports.{report_id}.charts",
                charts_path,
            )

            if spec is None or spec.loader is None:
                raise ChartLoadError(f"Failed to create module spec for {charts_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Store module info for hot reload
            registry._module_path = charts_path
            registry._last_modified = charts_path.stat().st_mtime

            logger.info(f"Loaded {len(registry)} chart(s) from {charts_path}")

        except SyntaxError as e:
            raise ChartLoadError(
                f"Syntax error in {charts_path}",
                report_id=report_id,
                cause=e,
                suggestion=f"Check line {e.lineno}: {e.text}",
            ) from e

        except ImportError as e:
            raise ChartLoadError(
                f"Import error in {charts_path}",
                report_id=report_id,
                cause=e,
                suggestion="Check that all imported modules are installed",
            ) from e

        except Exception as e:
            raise ChartLoadError(
                f"Failed to load {charts_path}",
                report_id=report_id,
                cause=e,
            ) from e

        finally:
            # Clear loading context
            _loading_context.registry = None

        self._registries[report_id] = registry
        return registry

    def get(self, report_id: str) -> Optional[ChartRegistry]:
        """Get a loaded registry by report ID.

        Args:
            report_id: Report identifier

        Returns:
            ChartRegistry if loaded, None otherwise
        """
        return self._registries.get(report_id)

    def reload(self, report_id: str) -> Optional[ChartRegistry]:
        """Reload a chart module if it has changed.

        Args:
            report_id: Report identifier

        Returns:
            Updated ChartRegistry if reloaded, None if unchanged or not found
        """
        registry = self._registries.get(report_id)
        if registry is None or registry._module_path is None:
            return None

        current_mtime = registry._module_path.stat().st_mtime
        if current_mtime <= registry._last_modified:
            return None  # No changes

        logger.info(f"Reloading charts.py for {report_id}")
        return self.load(registry._module_path.parent, report_id)


class ChartLoadError(Exception):
    """Raised when loading a charts.py module fails."""

    def __init__(
        self,
        message: str,
        report_id: Optional[str] = None,
        cause: Optional[Exception] = None,
        suggestion: Optional[str] = None,
    ):
        self.report_id = report_id
        self.cause = cause
        self.suggestion = suggestion

        full_message = message
        if report_id:
            full_message = f"[{report_id}] {message}"
        if cause:
            full_message += f": {cause}"
        if suggestion:
            full_message += f"\n  Suggestion: {suggestion}"

        super().__init__(full_message)
