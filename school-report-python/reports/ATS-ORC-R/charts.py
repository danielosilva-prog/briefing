"""ATS-ORC-R custom charts registered via schoolreport chart decorators.

Input contract:
  budget_data.chart_data.<chart_id> -> tabular dataset for that chart.
Each chart function receives its own dataset by matching `data=<chart_id>`.
"""

from typing import Callable, Optional

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Wedge
from matplotlib.ticker import FuncFormatter

from schoolreport.charts import ChartContext, chart

FONT_TICK_SIZE = 16
FONT_TEXT_SIZE = 16


def _get_shared_ylim(ctx: ChartContext) -> Optional[float]:
    """Retrieve shared ylim for a chart based on its pair.

    Automatically determines which pair (G1/G2, G3/G4, G5/G6) the chart belongs to
    and returns the shared ylim for that pair.

    Args:
        ctx: Chart context with params

    Returns:
        Shared ylim or None if not found
    """
    shared_ylims = ctx.params.get("shared_ylims", {})
    if not shared_ylims:
        return None

    # Extract page prefix and graph suffix from chart name (e.g. "p1_g1" -> "p1", "g1")
    chart_name = ctx.chart_name.lower()
    parts = chart_name.split("_")
    if len(parts) < 2:
        return None

    page_prefix = parts[0]  # e.g. "p1"
    graph_suffix = parts[1]  # e.g. "g1", "g2", "g3", etc.

    # Map graph suffix to its pair
    PAIR_MAP = {
        "g1": "g1_g2",
        "g2": "g1_g2",
        "g3": "g3_g4",
        "g4": "g3_g4",
        "g5": "g5_g6",
        "g6": "g5_g6",
    }

    pair_suffix = PAIR_MAP.get(graph_suffix)
    if not pair_suffix:
        return None

    pair_key = f"{page_prefix}_{pair_suffix}"
    return shared_ylims.get(pair_key)


CHART_RATIO_BY_NAME = {
    # P01: Normalized G1/G2 ratio = (2.7833 + 2.6907) / 2 = 2.7370
    "p1_g1": 2.7370,
    "p1_g2": 2.7370,
    "p1_g3": 3.1065,
    # P02: use same ratio as P01 for consistent chart height
    "p2_g1": 2.7370,
    "p2_g2": 2.7370,
    # P03: Normalized G1/G2 ratio = (2.9509 + 2.8754) / 2 = 2.9132
    "p3_g1": 2.9132,
    "p3_g2": 2.9132,
    "p3_g3": 2.9859,
    # P04: Normalized G1/G2 ratio = (2.9509 + 3.1524) / 2 = 3.0517
    "p4_g1": 3.0517,
    "p4_g2": 3.0517,
    "p4_g3": 3.1328,
    # P05: Using same ratio for G1/G2
    "p5_g1": 2.9509,
    "p5_g2": 2.9509,
    # P06: Using same ratio for G1/G2
    "p6_g1": 2.9509,
    "p6_g2": 2.9509,
    # P07: Using same ratio for G1/G2
    "p7_g1": 2.9509,
    "p7_g2": 2.9509,
    # Other pages
    # P09: Normalized G1/G2 ratio = (2.4949 + 2.7417) / 2 = 2.6183
    "p9_g1": 2.6183,
    "p9_g2": 2.6183,
    "p9_g3": 2.8367,
    # P10: G1 only
    "p10_g1": 2.8923,
    "p10_g2": 2.8923,
    # P12: Normalized G1/G2 ratio = (3.0071 + 3.1062) / 2 = 3.0567
    "p12_g1": 3.0567,
    "p12_g2": 3.0567,
    "p12_g3": 3.1407,
    # P13: G1 only
    "p13_g1": 3.0836,
    "p13_g2": 3.0836,
    # Shared pages
    "p15_g3": 2.8367,
    "p18_g3": 2.8367,
}

DUAL_AREA_STYLE_BY_CHART = {
    # P01, P02 - Removed: use single column bar (creditos_totais only)
    # They will use the fallback _register_column_single() with colors from _G1_FALLBACK_COLORS

    # P10, P13 - Blue theme
    "p10_g1": {
        "top_fill": "#9BD6F4",
        "base_fill": "#D9D9D9",
        "top_line": "#0095DA",
        "base_line": "#A1A1A1",
        "top_label_color": "#006699",
        "base_label_color": "#646464",
    },
    "p13_g1": {
        "top_fill": "#9BD6F4",
        "base_fill": "#D9D9D9",
        "top_line": "#0095DA",
        "base_line": "#A1A1A1",
        "top_label_color": "#006699",
        "base_label_color": "#646464",
    },
    # Legacy entries kept for compatibility with other report types
    "p9_g1": {
        "top_fill": "#183EFF",
        "base_fill": "#D9D9D9",
        "top_line": "#0059DA",
        "base_line": "#A1A1A1",
        "top_label_color": "#003366",
        "base_label_color": "#646464",
    },
    "p12_g1": {
        "top_fill": "#183EFF",
        "base_fill": "#D9D9D9",
        "top_line": "#0059DA",
        "base_line": "#A1A1A1",
        "top_label_color": "#003366",
        "base_label_color": "#646464",
    },
}

STACKED_PALETTE_BY_CHART = {
    "p1_g2": ["#11B880", "#FF7D00", "#FFC769"],
    "p1_g3": ["#11B880", "#FF7D00", "#FFC769"],
    "p9_g2": ["#11B880", "#FF7D00", "#FFC769"],
    "p9_g3": ["#65CCF2", "#A4DBA4", "#A1E0F7"],
    "p12_g3": ["#65CCF2", "#A4DBA4", "#A1E0F7"],
    "p12_g2": ["#11B880", "#FF7D00", "#FFC769"],
}

GROUPED_PALETTE_BY_CHART = {
    "p2_g2": ["#11B880", "#0095DA", "#F9C620"],
    "p1_g3": ["#008F00", "#A4DBA4", "#FFAE61"],
    "p9_g3": ["#65CCF2", "#A4DBA4", "#A1E0F7"],
    "p15_g3": ["#0095DA", "#183EFF", "#A9DBF2"],
    "p18_g3": ["#0095DA", "#183EFF", "#A9DBF2"],
}


def _as_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _figsize_for(chart_name: str, default: tuple[float, float]) -> tuple[float, float]:
    ratio = CHART_RATIO_BY_NAME.get(chart_name.lower())
    if not ratio:
        return default
    width = default[0]
    return (width, width / ratio)


def _create_figure(ctx: ChartContext, default: tuple[float, float]) -> tuple[Figure, plt.Axes]:
    figsize = _figsize_for(ctx.chart_name, default)
    fig = Figure(figsize=figsize, dpi=ctx.dpi)
    ax = fig.add_subplot(111)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    return fig, ax


def _hide_axes_frame(ax: plt.Axes) -> None:
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(
        axis="x", which="both", bottom=False, top=False, length=0, labelsize=FONT_TICK_SIZE
    )
    ax.tick_params(
        axis="y",
        which="both",
        left=False,
        right=False,
        length=0,
        labelleft=False,
        labelsize=FONT_TICK_SIZE,
    )
    ax.xaxis.set_ticks_position("none")
    ax.yaxis.set_ticks_position("none")


def _hide_y_axis_labels(ax: plt.Axes) -> None:
    ax.set_yticks([])
    ax.set_yticklabels([])


def _format_brl(value: float) -> str:
    # Format value in pt-BR currency style for point labels.
    s = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def _format_compact(value: float) -> str:
    """Format large numbers compactly in pt-BR style: 1,23Bi / 1,23Mi / 1,23mil."""
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}Bi".replace(".", ",")
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}Mi".replace(".", ",")
    if abs(value) >= 1_000:
        return f"{value / 1_000:.2f}mil".replace(".", ",")
    return f"{value:.0f}"


def _format_compact_brl(value: float) -> str:
    """Compact currency label: 'R$ 1,23Bi', 'R$ 456,78Mi', etc."""
    return f"R$ {_format_compact(value)}"


def _apply_compact_brl_y_axis(ax: plt.Axes) -> None:
    """Show compact BRL labels (Mi/Bi) on the Y-axis tick marks."""
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: _format_compact_brl(y)))


def _style_axes_like_mock(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#3C3C3C")
    ax.spines["bottom"].set_linewidth(1.0)
    ax.tick_params(axis="x", colors="#646464", labelsize=FONT_TICK_SIZE, length=0)
    ax.tick_params(axis="y", which="both", left=False, length=0, labelleft=False)
    ax.yaxis.set_ticks_position("none")
    ax.set_yticks([])
    ax.grid(which="both", visible=False)


def _plot_mock_single_series(
    df: pd.DataFrame, ctx: ChartContext, color: str, aggregate: str = "first"
) -> plt.Figure:
    if df.empty:
        return None

    # Common shape: [label, series...]
    if df.shape[1] >= 2:
        labels = df.iloc[:, 0].astype(str).tolist()
        numeric_df = pd.DataFrame({col: _as_numeric(df[col]) for col in df.columns[1:]})
    else:
        # Fallback for payloads like [{"valor": 88.4}]
        labels = ["Atual"] * len(df)
        numeric_df = pd.DataFrame({"valor": _as_numeric(df.iloc[:, 0])})

    if numeric_df.empty:
        return None
    if aggregate == "sum":
        values = numeric_df.sum(axis=1).tolist()
    else:
        values = numeric_df.iloc[:, 0].tolist()

    x = list(range(len(labels)))
    fig, ax = _create_figure(ctx, (9, 3.3))
    bars = ax.bar(x, values, width=0.62, color=color, edgecolor="none", zorder=2)

    # Determine ylim: use shared if available, otherwise calculate local
    max_v = max(values) if values else 0
    shared_ylim = _get_shared_ylim(ctx)
    if shared_ylim:
        max_v = shared_ylim

    pad = max_v * 0.08 if max_v > 0 else 1.0
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (pad * 0.12),
            _format_compact_brl(float(v)),
            ha="center",
            va="bottom",
            fontsize=FONT_TEXT_SIZE,
            color="#646464",
            zorder=3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max_v + pad)
    _apply_compact_brl_y_axis(ax)
    _style_axes_like_mock(ax)
    fig.subplots_adjust(left=0.13, right=0.995, top=0.93, bottom=0.2)
    return fig


def _plot_mock_area_single(
    df: pd.DataFrame, ctx: ChartContext, color: str, aggregate: str = "first"
) -> plt.Figure:
    if df.empty:
        return None

    if df.shape[1] >= 2:
        labels = df.iloc[:, 0].astype(str).tolist()
        numeric_df = pd.DataFrame({col: _as_numeric(df[col]) for col in df.columns[1:]})
    else:
        labels = ["Atual"] * len(df)
        numeric_df = pd.DataFrame({"valor": _as_numeric(df.iloc[:, 0])})

    if numeric_df.empty:
        return None
    values = (
        numeric_df.sum(axis=1).tolist() if aggregate == "sum" else numeric_df.iloc[:, 0].tolist()
    )

    x = list(range(len(labels)))
    fig, ax = _create_figure(ctx, (9, 3.3))
    ax.fill_between(x, values, color=color, alpha=0.98, zorder=2)

    # Determine ylim: use shared if available, otherwise calculate local
    max_v = max(values) if values else 0
    shared_ylim = _get_shared_ylim(ctx)
    if shared_ylim:
        max_v = shared_ylim

    pad = max_v * 0.12 if max_v > 0 else 1.0
    for xi, v in zip(x, values):
        ax.text(
            xi,
            v + (pad * 0.08),
            _format_compact_brl(float(v)),
            ha="center",
            va="bottom",
            fontsize=FONT_TEXT_SIZE,
            color="#646464",
            zorder=3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max_v + pad)
    _apply_compact_brl_y_axis(ax)
    _style_axes_like_mock(ax)
    fig.subplots_adjust(left=0.13, right=0.995, top=0.93, bottom=0.2)
    return fig


def _plot_horizontal(df: pd.DataFrame, ctx: ChartContext, label1: str, label2: str) -> plt.Figure:
    if df.shape[1] < 3:
        return None
    labels = df.iloc[:, 0].astype(str).tolist()
    values1 = _as_numeric(df.iloc[:, 1]).tolist()
    values2 = _as_numeric(df.iloc[:, 2]).tolist()

    fig, ax = _create_figure(ctx, (9, 3.3))
    y_pos = list(range(len(labels)))
    bar_height = 0.35
    ax.barh([i - bar_height / 2 for i in y_pos], values1, bar_height, label=label1, color="#2E4172")
    ax.barh([i + bar_height / 2 for i in y_pos], values2, bar_height, label=label2, color="#0095DA")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    _hide_axes_frame(ax)
    plt.tight_layout()
    return fig


def _plot_stacked(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    if df.shape[1] < 2:
        return None
    labels = df.iloc[:, 0].astype(str).tolist()
    series_cols = list(df.columns[1:])
    fig, ax = _create_figure(ctx, (9, 3.3))
    cumulative = pd.Series([0.0] * len(labels))
    palette = STACKED_PALETTE_BY_CHART.get(
        ctx.chart_name.lower(), ["#2E4172", "#0095DA", "#00C7B1", "#FFB81C", "#E63946"]
    )

    values_df = pd.DataFrame({col: _as_numeric(df[col]) for col in series_cols})
    totals = values_df.sum(axis=1).replace(0, 1)
    deferred_labels: list = []

    # Minimum visual bar height: 0.8% of the tallest bar, ensures tiny segments are visible
    max_bar_h = float(values_df.sum(axis=1).max())
    min_bar_h = max_bar_h * 0.03 if max_bar_h > 0 else 0.0

    for i, col in enumerate(series_cols):
        values = _as_numeric(df[col])
        # Apply minimum visual height for rendering only; stacking uses real values
        render_values = values.where(values <= 0, values.clip(lower=min_bar_h))
        ax.bar(labels, render_values, bottom=cumulative, label=str(col), color=palette[i % len(palette)])
        percentages = (values / totals) * 100.0
        for j, (v, pct) in enumerate(zip(values.tolist(), percentages.tolist())):
            if v <= 0:
                continue
            if pct < 6:
                deferred_labels.append({
                    "j": j,
                    "segment_center": float(cumulative.iloc[j] + v / 2.0),
                    "text": _format_compact_brl(v),
                })
            else:
                ax.text(
                    j,
                    float(cumulative.iloc[j] + (v / 2.0)),
                    _format_compact_brl(v),
                    ha="center",
                    va="center",
                    fontsize=FONT_TEXT_SIZE,
                    color="#1F1F1F",
                    zorder=5,
                )
        cumulative += values

    # Render deferred small-segment labels above the bar with connector lines
    bar_heights = values_df.sum(axis=1)
    if deferred_labels:
        from collections import defaultdict

        by_bar: dict = defaultdict(list)
        for lbl in deferred_labels:
            by_bar[lbl["j"]].append(lbl)

        max_bar_h = float(bar_heights.max()) if float(bar_heights.max()) > 0 else 1.0
        spacing = max_bar_h * 0.10

        for j, lbls in by_bar.items():
            bar_h = float(bar_heights.iloc[j])
            for k, lbl in enumerate(lbls):
                label_y = bar_h + (k + 0.5) * spacing
                ax.annotate(
                    lbl["text"],
                    xy=(lbl["j"], lbl["segment_center"]),
                    xytext=(lbl["j"], label_y),
                    ha="center",
                    va="bottom",
                    fontsize=FONT_TEXT_SIZE,
                    color="#1F1F1F",
                    arrowprops=dict(arrowstyle="-", color="#888888", lw=0.8),
                    zorder=5,
                )

        # Ensure ylim has room for the highest deferred label
        max_label_y = max(
            float(bar_heights.iloc[lbl["j"]]) + (k + 1) * spacing
            for j, lbls in by_bar.items()
            for k, lbl in enumerate(lbls)
        )
        min_ylim_needed = max_label_y * 1.05
        current_top = ax.get_ylim()[1]
        if min_ylim_needed > current_top:
            ax.set_ylim(0, min_ylim_needed)
    else:
        min_ylim_needed = 0.0

    # Set shared ylim if available (BEFORE styling to prevent tick recreation)
    # Use max() to avoid truncating space reserved for small-segment labels above bars
    shared_ylim = _get_shared_ylim(ctx)
    if shared_ylim:
        ax.set_ylim(0, max(shared_ylim, min_ylim_needed))

    plt.xticks(rotation=0)
    _style_axes_like_mock(ax)
    plt.tight_layout()
    return fig


def _plot_stacked_100(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    if df.shape[1] < 2:
        return None
    labels = df.iloc[:, 0].astype(str).tolist()
    series_cols = list(df.columns[1:])
    fig, ax = _create_figure(ctx, (9, 3.3))
    palette = STACKED_PALETTE_BY_CHART.get(
        ctx.chart_name.lower(), ["#2E4172", "#0095DA", "#00C7B1", "#FFB81C", "#E63946"]
    )

    values_df = pd.DataFrame({col: _as_numeric(df[col]) for col in series_cols})
    totals = values_df.sum(axis=1).replace(0, 1)
    pct_df = values_df.div(totals, axis=0) * 100.0

    cumulative = pd.Series([0.0] * len(labels))
    for i, col in enumerate(series_cols):
        values = pct_df[col]
        color = palette[i % len(palette)]
        ax.barh(labels, values, left=cumulative, label=str(col), color=color)

        # Center label in each segment with the displayed percentage value.
        for j, value in enumerate(values.tolist()):
            if value <= 0:
                continue
            x_center = float(cumulative.iloc[j] + (value / 2.0))
            if value < 7:
                continue
            label = f"{value:.1f}%".replace(".", ",")
            ax.text(
                x_center,
                labels[j],
                label,
                ha="center",
                va="center",
                fontsize=FONT_TEXT_SIZE,
                color="#1F1F1F",
            )
        cumulative += values

    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    _style_axes_like_mock(ax)
    plt.tight_layout()
    return fig


def _plot_grouped(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    if df.shape[1] < 3:
        return None
    labels = df.iloc[:, 0].astype(str).tolist()
    series_cols = list(df.columns[1:])
    fig, ax = _create_figure(ctx, (9, 3.0))
    x = list(range(len(labels)))
    total_width = 0.8
    n = len(series_cols)
    bar_width = total_width / max(n, 1)
    offsets = [-(total_width - bar_width) / 2 + i * bar_width for i in range(n)]
    palette = GROUPED_PALETTE_BY_CHART.get(
        ctx.chart_name.lower(), ["#2E4172", "#0095DA", "#00C7B1", "#FFB81C", "#E63946"]
    )

    # Collect all values to determine max for padding
    all_values = []
    for i, col in enumerate(series_cols):
        values = _as_numeric(df[col]).tolist()
        all_values.extend(values)
        bars = ax.bar(
            [xi + offsets[i] for xi in x],
            values,
            bar_width * 0.9,
            label=str(col),
            color=palette[i % len(palette)],
        )

        # Add labels above each bar
        max_v = max(all_values) if all_values else 0
        pad = max_v * 0.08 if max_v > 0 else 1.0
        for bar, v in zip(bars, values):
            if v > 0:  # Only show label if value is positive
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + (pad * 0.15),
                    _format_compact_brl(float(v)),
                    ha="center",
                    va="bottom",
                    fontsize=FONT_TEXT_SIZE - 5,
                    color="#646464",
                    zorder=5,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    ax.grid(axis="x", visible=False)
    _hide_y_axis_labels(ax)
    _hide_axes_frame(ax)
    plt.tight_layout()
    return fig


def _plot_grouped_horizontal(df: pd.DataFrame, ctx: ChartContext) -> plt.Figure:
    if df.shape[1] < 3:
        return None
    labels = df.iloc[:, 0].astype(str).tolist()
    series_cols = list(df.columns[1:])
    fig, ax = _create_figure(ctx, (9, 3.0))
    y = list(range(len(labels)))
    total_height = 0.8
    n = len(series_cols)
    bar_height = total_height / max(n, 1)
    offsets = [-(total_height - bar_height) / 2 + i * bar_height for i in range(n)]
    palette = GROUPED_PALETTE_BY_CHART.get(
        ctx.chart_name.lower(), ["#2E4172", "#0095DA", "#00C7B1", "#FFB81C", "#E63946"]
    )

    for i, col in enumerate(series_cols):
        values = _as_numeric(df[col]).tolist()
        ax.barh(
            [yi + offsets[i] for yi in y],
            values,
            bar_height * 0.9,
            label=str(col),
            color=palette[i % len(palette)],
        )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    ax.grid(axis="y", visible=False)
    _hide_axes_frame(ax)
    plt.tight_layout()
    return fig


def _plot_horizontal_single(df: pd.DataFrame, ctx: ChartContext, color: str) -> plt.Figure:
    if df.empty:
        return None
    if df.shape[1] >= 2:
        labels = df.iloc[:, 0].astype(str).tolist()
        numeric_df = pd.DataFrame({col: _as_numeric(df[col]) for col in df.columns[1:]})
    else:
        labels = ["Atual"] * len(df)
        numeric_df = pd.DataFrame({"valor": _as_numeric(df.iloc[:, 0])})

    if numeric_df.empty:
        return None
    values = numeric_df.sum(axis=1).tolist()

    fig, ax = _create_figure(ctx, (9, 3.0))
    y = list(range(len(labels)))
    bars = ax.barh(y, values, color=color, edgecolor="none")
    max_v = max(values) if values else 0
    pad = max_v * 0.08 if max_v > 0 else 1.0

    for i, (bar, value) in enumerate(zip(bars, values)):
        ax.text(
            bar.get_width() + (pad * 0.15),
            i,
            _format_brl(float(value)),
            va="center",
            ha="left",
            fontsize=FONT_TEXT_SIZE,
            color="#646464",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, max_v + pad)
    _hide_y_axis_labels(ax)
    _style_axes_like_mock(ax)
    fig.subplots_adjust(left=0.06, right=0.995, top=0.93, bottom=0.2)
    return fig


def _plot_dual_area_currency(
    df: pd.DataFrame,
    ctx: ChartContext,
    label_top: str = "LOA",
    label_base: str = "Dotação Atualizada",
    top_fill: str = "#9BD6F4",
    base_fill: str = "#C7CDD4",
    top_line: str = "#4AA9D8",
    base_line: str = "#8D98A5",
    top_label_color: str = "#2A6F90",
    base_label_color: str = "#5E6771",
) -> plt.Figure:
    if df.shape[1] < 3:
        return None

    labels = df.iloc[:, 0].astype(str).tolist()
    top_values = _as_numeric(df.iloc[:, 1]).tolist()
    base_values = _as_numeric(df.iloc[:, 2]).tolist()
    x = list(range(len(labels)))

    fig, ax = _create_figure(ctx, (9, 3.3))

    # Base area (gray) + top area (light blue), both from zero.
    ax.fill_between(x, base_values, color=base_fill, alpha=0.95, label=label_base, zorder=1)
    ax.fill_between(x, top_values, color=top_fill, alpha=0.8, label=label_top, zorder=2)

    # Edge lines improve readability of overlapping areas.
    ax.plot(x, base_values, color=base_line, linewidth=1.4, marker="o", markersize=3.2, zorder=3)
    ax.plot(x, top_values, color=top_line, linewidth=1.6, marker="o", markersize=3.2, zorder=4)

    for xi, y in enumerate(top_values):
        ax.text(
            xi,
            y,
            _format_compact_brl(y),
            ha="center",
            va="bottom",
            fontsize=FONT_TEXT_SIZE,
            color=top_label_color,
            zorder=5,
        )

    # Set shared ylim if available (BEFORE hiding axes to prevent tick recreation)
    shared_ylim = _get_shared_ylim(ctx)
    if shared_ylim:
        ax.set_ylim(0, shared_ylim)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=False)
    ax.set_yticks([])
    _hide_axes_frame(ax)
    plt.tight_layout()
    return fig


def _plot_gauge(df: pd.DataFrame, ctx: ChartContext, color: str) -> plt.Figure:
    if df.empty:
        return None

    # First numeric value from the row.
    numeric = _as_numeric(df.iloc[0])
    value = float(numeric.iloc[0]) if len(numeric) > 0 else 0.0
    max_value = 100.0
    percent = max(0.0, min(value / max_value, 1.0))

    fig, ax = _create_figure(ctx, (3.2, 1.6))
    ax.add_patch(Wedge((0, 0), 1.0, 0, 180, width=0.27, facecolor="#D9D9D9", edgecolor="none"))
    ax.add_patch(
        Wedge(
            (0, 0), 1.0, 180 - (180 * percent), 180, width=0.27, facecolor=color, edgecolor="none"
        )
    )
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig


def _register_horizontal(
    name: str, label1: str = "LOA", label2: str = "Dotação Atualizada"
) -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.3)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_horizontal(df, ctx, label1=label1, label2=label2)

    return _fn


def _register_dual_area_currency(
    name: str,
    label_top: str = "LOA",
    label_base: str = "Dotação Atualizada",
    top_fill: str = "#9BD6F4",
    base_fill: str = "#C7CDD4",
    top_line: str = "#4AA9D8",
    base_line: str = "#8D98A5",
    top_label_color: str = "#2A6F90",
    base_label_color: str = "#5E6771",
) -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.3)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_dual_area_currency(
            df,
            ctx,
            label_top=label_top,
            label_base=label_base,
            top_fill=top_fill,
            base_fill=base_fill,
            top_line=top_line,
            base_line=base_line,
            top_label_color=top_label_color,
            base_label_color=base_label_color,
        )

    return _fn


def _register_stacked(name: str, data_name: str | None = None) -> Callable:
    dataset = data_name or name

    @chart(name, data=dataset, figsize=_figsize_for(name, (9, 3.3)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_stacked(df, ctx)

    return _fn


def _register_stacked_100(name: str, data_name: str | None = None) -> Callable:
    dataset = data_name or name

    @chart(name, data=dataset, figsize=_figsize_for(name, (9, 3.3)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_stacked_100(df, ctx)

    return _fn


def _register_grouped(name: str) -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.0)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_grouped(df, ctx)

    return _fn


def _register_grouped_horizontal(name: str) -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.0)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_grouped_horizontal(df, ctx)

    return _fn


def _register_horizontal_single(name: str, color: str) -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.0)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_horizontal_single(df, ctx, color=color)

    return _fn


def _register_gauge(name: str, color: str) -> Callable:
    @chart(name, data=name, figsize=(3.2, 1.6), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_gauge(df, ctx, color=color)

    return _fn


def _register_mock_single_series(name: str, color: str, aggregate: str = "first") -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.3)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_mock_single_series(df, ctx, color=color, aggregate=aggregate)

    return _fn


def _register_mock_area_single(name: str, color: str, aggregate: str = "first") -> Callable:
    @chart(name, data=name, figsize=_figsize_for(name, (9, 3.3)), format="svg")
    def _fn(df: pd.DataFrame, ctx: ChartContext):
        return _plot_mock_area_single(df, ctx, color=color, aggregate=aggregate)

    return _fn


# Stacked
_register_stacked_100("p9_g2")
_register_stacked_100("p12_g2")

# Stacked 100% (G3 series)
_register_stacked("p9_g3")
_register_stacked("p15_g3", data_name="p9_g3")
_register_stacked("p18_g3", data_name="p9_g3")
_register_stacked("p12_g3")

_register_dual_area_currency("p10_g1", **DUAL_AREA_STYLE_BY_CHART["p10_g1"])
_register_dual_area_currency("p13_g1", **DUAL_AREA_STYLE_BY_CHART["p13_g1"])

# Gauges (p7_g1 is NOT a gauge in ATS-02 — it belongs to another report type)
# _register_gauge("p7_g1", "#FFCF00")  # removed: conflicts with ATS-02 P07 dual-area chart
_register_gauge("p8_g1", "#ED2129")
_register_gauge("p8_g2", "#F28705")
_register_gauge("p10_g2", "#0D2186")

# ATS-ORC-R template (P1..P2): force dynamic generation for all G1..G6.
_register_column_single = _register_mock_single_series

_G1_FALLBACK_COLORS = {
    1: "#65CCF2",
    2: "#FFE799",
}

_G2_FALLBACK_COLORS = {
    1: "#0097CD",
    2: "#F9C620",
}

_G3_COLORS = ["#FFC769", "#11B880", "#FF7D00"]

_G4_COLORS = {
    1: ["#FFC769", "#11B880", "#FF7D00"],
    2: ["#FFC769", "#11B880", "#FF7D00"],
}

_G5_COLORS = {
    1: ["#0095DA", "#FFD000", "#88D088"],
    2: ["#0095DA", "#FFD000", "#88D088"],
}

_G6_COLORS = {
    1: ["#0095DA", "#FFD000", "#88D088"],
    2: ["#0095DA", "#FFD000", "#88D088"],
}

# Padroniza o tamanho de todos os gráficos de barra empilhada (G3..G6).
_STACKED_BAR_RATIO = 3.1065
for _p_ratio in range(1, 3):
    for _g_ratio in range(3, 7):
        CHART_RATIO_BY_NAME[f"p{_p_ratio}_g{_g_ratio}"] = _STACKED_BAR_RATIO

for _p in range(1, 3):
    _g1 = f"p{_p}_g1"
    _g2 = f"p{_p}_g2"
    _g3 = f"p{_p}_g3"
    _g4 = f"p{_p}_g4"
    _g5 = f"p{_p}_g5"
    _g6 = f"p{_p}_g6"

    # G1: dual area if style defined, area+line if area-line style, else mock area
    if _g1 in DUAL_AREA_STYLE_BY_CHART:
        _s = DUAL_AREA_STYLE_BY_CHART[_g1]
        _register_dual_area_currency(
            _g1,
            top_fill=_s["top_fill"],
            base_fill=_s["base_fill"],
            top_line=_s["top_line"],
            base_line=_s["base_line"],
            top_label_color=_s["top_label_color"],
            base_label_color=_s["base_label_color"],
        )
    else:
        _register_column_single(_g1, color=_G1_FALLBACK_COLORS[_p], aggregate="first")

    # G2: dual area if style defined, else column
    if _g2 in DUAL_AREA_STYLE_BY_CHART:
        _s = DUAL_AREA_STYLE_BY_CHART[_g2]
        _register_dual_area_currency(
            _g2,
            top_fill=_s["top_fill"],
            base_fill=_s["base_fill"],
            top_line=_s["top_line"],
            base_line=_s["base_line"],
            top_label_color=_s["top_label_color"],
            base_label_color=_s["base_label_color"],
        )
    else:
        _register_column_single(_g2, color=_G2_FALLBACK_COLORS[_p], aggregate="sum")

    # G3: barra única (destaque_recebido CE) para P02, stacked para demais
    if _p == 2:
        _register_column_single(_g3, color=_G1_FALLBACK_COLORS[_p], aggregate="first")
    else:
        STACKED_PALETTE_BY_CHART[_g3] = _G3_COLORS
        _register_stacked(_g3)

    # G4: barra única (destaque_recebido CE) para P02, stacked para demais
    if _p == 2:
        _register_column_single(_g4, color=_G2_FALLBACK_COLORS[_p], aggregate="first")
    else:
        STACKED_PALETTE_BY_CHART[_g4] = _G4_COLORS[_p]
        _register_stacked(_g4)

    # G5: barra empilhada (Grupo Despesa período 1)
    STACKED_PALETTE_BY_CHART[_g5] = _G5_COLORS[_p]
    _register_stacked(_g5)

    # G6: barra empilhada (Grupo Despesa período 2)
    STACKED_PALETTE_BY_CHART[_g6] = _G6_COLORS[_p]
    _register_stacked(_g6)
