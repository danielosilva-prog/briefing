"""Slope chart for Condicionalidade III - desigualdade racial."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from schoolreport.charts import ChartContext, chart


def _load_local_module(module_name: str, relative_path: str):
    """Load local module by path (ATM-EQ folder name has hyphen)."""
    if module_name in sys.modules:
        return sys.modules[module_name]

    module_path = Path(__file__).parent / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao foi possivel carregar modulo: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_helpers = _load_local_module("atm_eq_chart_helpers", "chart_helpers.py")
_image_dimensions = _load_local_module("atm_eq_image_dimensions", "image_dimensions.py")
ensure_rawline_font_available = _helpers.ensure_rawline_font_available
get_chart_font_family = _helpers.get_chart_font_family
get_image_dimensions = _image_dimensions.get_image_dimensions
plot_two_point_slope_chart = _helpers.plot_two_point_slope_chart


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read reference image dimensions and return figsize in inches."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


_SLOPE_REFERENCE_IMAGE = "template/assets/charts/P3-G1.svg"


def _parse_percent(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if text in {"", "-", "-%", "None", "none", "nan"}:
        return None

    normalized = text.replace("%", "").replace(" ", "")
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    else:
        normalized = normalized.replace(",", ".")

    try:
        return float(normalized)
    except ValueError:
        return None


def _format_percent_label(ctx: ChartContext, raw_value: object, parsed_value: float) -> str:
    text = str(raw_value).strip() if raw_value is not None else ""
    if text.endswith("%"):
        return text
    return ctx.format_percent(parsed_value, 2)


def _prepare_values(df: pd.DataFrame, ctx: ChartContext) -> tuple[list[float], list[str]] | None:
    required = {"p3PercentualRacial2019", "p3PercentualRacial2023"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes para grafico: {sorted(missing)}")

    row = df.iloc[0]
    value_2019 = _parse_percent(row.get("p3PercentualRacial2019"))
    value_2023 = _parse_percent(row.get("p3PercentualRacial2023"))
    if value_2019 is None or value_2023 is None:
        return None

    label_2019 = _format_percent_label(ctx, row.get("p3PercentualRacial2019"), value_2019)
    label_2023 = _format_percent_label(ctx, row.get("p3PercentualRacial2023"), value_2023)
    return ([value_2019, value_2023], [label_2019, label_2023])


def _fit_value_labels_inside_figure(
    fig: plt.Figure,
    *,
    top_padding_px: float = 2.0,
    side_padding_px: float = 2.0,
    max_iterations: int = 3,
) -> None:
    """Aplica ajuste mínimo de margens para manter labels de valor visíveis."""
    if not fig.axes:
        return
    ax = fig.axes[0]

    for _ in range(max_iterations):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        fig_bbox = fig.get_window_extent(renderer=renderer)
        fig_width_px = max(1.0, float(fig_bbox.width))
        fig_height_px = max(1.0, float(fig_bbox.height))

        value_texts = [
            text
            for text in ax.texts
            if text.get_visible() and "ATM_EQ_GRAPH_" not in str(text.get_text())
        ]
        if not value_texts:
            return

        text_bboxes = [text.get_window_extent(renderer=renderer) for text in value_texts]
        overflow_top = max(
            0.0,
            max((bbox.y1 + top_padding_px) - fig_bbox.y1 for bbox in text_bboxes),
        )
        overflow_left = max(
            0.0,
            max((fig_bbox.x0 + side_padding_px) - bbox.x0 for bbox in text_bboxes),
        )
        overflow_right = max(
            0.0,
            max(bbox.x1 - (fig_bbox.x1 - side_padding_px) for bbox in text_bboxes),
        )

        if max(overflow_top, overflow_left, overflow_right) < 0.5:
            break

        current_top = float(fig.subplotpars.top)
        current_bottom = float(fig.subplotpars.bottom)
        current_left = float(fig.subplotpars.left)
        current_right = float(fig.subplotpars.right)

        new_top = current_top - (overflow_top / fig_height_px)
        new_left = current_left + (overflow_left / fig_width_px)
        new_right = current_right - (overflow_right / fig_width_px)

        min_top = current_bottom + 0.22
        new_top = max(min_top, min(0.99, new_top))

        min_axis_width = 0.30
        if (new_right - new_left) < min_axis_width:
            center = (new_left + new_right) / 2.0
            half = min_axis_width / 2.0
            new_left = center - half
            new_right = center + half
        new_left = max(0.0, min(0.70, new_left))
        new_right = max(0.30, min(1.0, new_right))

        fig.subplots_adjust(top=new_top, left=new_left, right=new_right)


@chart(
    "graficoCondicionalidadeIIIDesigualdadeRacial",
    data="p3_condicionalidade_iii_vaar",
    title="Alunos pretos, pardos e indigenas com aprendizagem adequada (2019-2023)",
    figsize=_designer_figsize_inches(_SLOPE_REFERENCE_IMAGE),
)
def grafico_condicionalidade_iii_desigualdade_racial(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None: # type: ignore
    if df is None or df.empty:
        return None

    prepared = _prepare_values(df, ctx)
    if prepared is None:
        return None
    values, labels = prepared
    show_y_axis_labels = False

    ensure_rawline_font_available(strict=False)
    fig = plot_two_point_slope_chart(
        y_values=values,
        point_labels=labels,
        year_labels=("2019", "2023"),
        figsize=ctx.figsize,
        font_family=get_chart_font_family(),
        value_color="#725FA9",
        line_color="#333333",
        point_color="#333333",
        year_color="#000000",
        value_fontsize=14.0,
        year_fontsize=9.5,
        point_size=50.0,
        line_width=2.0,
        x_padding=0.34,
        y_padding_ratio=0.10,
        min_y_span=1.2,
        label_x_offsets=(-0.06, 0.0),
        label_y_offsets_ratio=(0.08, 0.08),
        label_horizontal_alignment=("center", "center"),
        x_tick_pad=8.0,
        show_y_axis_labels=show_y_axis_labels,
    )
    if fig is None:
        return None

    fig.set_size_inches(*ctx.figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    # Mantem folga inferior para ticks de X e reserva margem esquerda quando eixo Y estiver visível.
    left_margin = 0.15 if show_y_axis_labels else 0.0
    fig.subplots_adjust(top=0.98, bottom=0.18, left=left_margin, right=0.99)
    _fit_value_labels_inside_figure(fig, top_padding_px=2.0, side_padding_px=2.0)

    # Keep exact SVG dimensions from designer reference fallback.
    setattr(fig, "_schoolreport_preserve_svg_size", True)
    setattr(
        fig,
        "_schoolreport_expected_svg_size_inches",
        (float(ctx.figsize[0]), float(ctx.figsize[1])),
    )
    # Borda de depuração da área útil do eixo.
    if fig.axes:
        fig.axes[0].add_patch(
            Rectangle(
                (0, 0),
                1,
                1,
                transform=fig.axes[0].transAxes,
                fill=False,
                edgecolor="#003CFF00",
                linewidth=0.8,
                zorder=999,
            )
        )

    # Borda de depuração: mostra os limites exatos da figura na exportação.
    fig.add_artist(
        Rectangle(
            (0, 0),
            1,
            1,
            transform=fig.transFigure,
            fill=False,
            edgecolor="#FF000000",
            linewidth=0.8,
            zorder=1000,
        )
    )
    return fig
