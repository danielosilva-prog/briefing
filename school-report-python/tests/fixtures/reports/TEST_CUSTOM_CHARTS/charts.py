"""Custom charts for TEST_CUSTOM_CHARTS report.

This file demonstrates the custom chart definition system using the @chart decorator.
"""

from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd

from schoolreport.charts import ChartContext, chart


@chart("enrollment_bar", data="enrollment")
def enrollment_bar(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    """Custom bar chart showing enrollment by category."""
    fig, ax = plt.subplots(figsize=ctx.figsize, dpi=ctx.dpi)

    # Use context colors
    colors = ctx.get_colors(len(df))
    ax.bar(df["category"], df["count"], color=colors)

    ax.set_title("Enrollment by Category", fontsize=ctx.title_fontsize, fontweight="bold")
    ax.set_xlabel("Category", fontsize=ctx.label_fontsize)
    ax.set_ylabel("Count", fontsize=ctx.label_fontsize)

    # Add value labels
    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(i, row["count"] + 0.5, ctx.format_number(row["count"]), ha="center")

    plt.tight_layout()
    return fig


@chart("demographics_donut", data="demographics")
def demographics_donut(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    """Custom donut chart showing demographic breakdown."""
    fig, ax = plt.subplots(figsize=ctx.figsize, dpi=ctx.dpi)

    colors = ctx.get_colors(len(df))

    wedges, texts, autotexts = ax.pie(
        df["value"],
        labels=df["label"],
        autopct=lambda pct: ctx.format_percent(pct),
        colors=colors,
        startangle=90,
        wedgeprops=dict(width=0.5),
    )

    ax.set_title("Demographics", fontsize=ctx.title_fontsize, fontweight="bold")

    plt.tight_layout()
    return fig


@chart("multi_data_comparison", data=["enrollment", "demographics"])
def multi_data_comparison(data: Dict[str, pd.DataFrame], ctx: ChartContext) -> plt.Figure:
    """Custom chart using multiple data sources."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=ctx.dpi)

    enrollment = data["enrollment"]
    demographics = data["demographics"]

    # Left subplot: enrollment bar
    ax1.bar(enrollment["category"], enrollment["count"], color=ctx.primary_color)
    ax1.set_title("Enrollment", fontsize=ctx.title_fontsize)

    # Right subplot: demographics pie
    ax2.pie(demographics["value"], labels=demographics["label"], colors=ctx.get_colors(len(demographics)))
    ax2.set_title("Demographics", fontsize=ctx.title_fontsize)

    plt.tight_layout()
    return fig


@chart("optional_chart", data="enrollment")
def optional_chart(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure | None:
    """Chart that returns None if data is empty (will be skipped)."""
    if df.empty or df["count"].sum() == 0:
        return None

    fig, ax = plt.subplots(figsize=ctx.figsize, dpi=ctx.dpi)
    ax.bar(df["category"], df["count"], color=ctx.secondary_color)
    ax.set_title("Optional Chart")

    plt.tight_layout()
    return fig


@chart("params_aware_chart", data="enrollment")
def params_aware_chart(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    """Chart that uses report parameters from context."""
    fig, ax = plt.subplots(figsize=ctx.figsize, dpi=ctx.dpi)

    year = ctx.params.get("year", "Unknown")
    ax.bar(df["category"], df["count"], color=ctx.primary_color)
    ax.set_title(f"Enrollment for {year}", fontsize=ctx.title_fontsize)

    plt.tight_layout()
    return fig
