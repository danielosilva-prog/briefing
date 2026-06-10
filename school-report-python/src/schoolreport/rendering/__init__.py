"""Rendering module for chart and PDF generation."""

from schoolreport.rendering.chart_framework import (
    ChartContext,
    ChartFunction,
    ChartLoader,
    ChartLoadError,
    ChartMetadata,
    ChartRegistry,
    chart,
)
from schoolreport.rendering.charts import ChartGenerator, ChartGeneratorError
from schoolreport.rendering.pdf import PDFRenderer, PDFRendererError

__all__ = [
    # Chart framework
    "chart",
    "ChartContext",
    "ChartFunction",
    "ChartLoader",
    "ChartLoadError",
    "ChartMetadata",
    "ChartRegistry",
    # Chart generator
    "ChartGenerator",
    "ChartGeneratorError",
    # PDF renderer
    "PDFRenderer",
    "PDFRendererError",
]
