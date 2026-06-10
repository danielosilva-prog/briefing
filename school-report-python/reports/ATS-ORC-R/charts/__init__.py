"""Chart generation modules for ATS-02 report.

This package contains chart generators for:
- gauge: Semicircular percentage gauge
- horizontal_bar: Horizontal bar charts (LOA vs Dotação)
- stacked_bar: Stacked bar charts (by budget type)
- grouped_bar: Grouped bar charts (comparative analysis)
- area_line: Combined area + line time series
"""

from .gauge import generate_gauge, generate_gauge_svg
from .horizontal_bar import generate_horizontal_bar
from .stacked_bar import generate_stacked_bar
from .grouped_bar import generate_grouped_bar
from .area_line import generate_area_line

__all__ = [
    "generate_gauge",
    "generate_gauge_svg",
    "generate_horizontal_bar",
    "generate_stacked_bar",
    "generate_grouped_bar",
    "generate_area_line",
]
