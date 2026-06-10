"""Convenience module for chart definitions.

This module provides a clean import path for defining custom charts:

    from schoolreport.charts import chart, ChartContext

Example usage in reports/ATM/charts.py:

    from schoolreport.charts import chart, ChartContext
    import matplotlib.pyplot as plt
    import pandas as pd

    @chart("enrollment_bar", data="matriculas", size=(900, 320))
    def enrollment_bar(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
        fig, ax = plt.subplots(figsize=ctx.figsize)
        ax.bar(df["etapa"], df["total"], color=ctx.primary_color)
        ax.set_title("Matrículas por Etapa")
        return fig
"""

from schoolreport.rendering.chart_framework import (
    ChartContext,
    ChartFunction,
    ChartMetadata,
    ChartRegistry,
    chart,
)

__all__ = [
    "chart",
    "ChartContext",
    "ChartFunction",
    "ChartMetadata",
    "ChartRegistry",
]
