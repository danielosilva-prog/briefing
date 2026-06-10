"""Slope chart for Condicionalidade III - desigualdade socioeconomica."""

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
_racial_slope = _load_local_module(
    "atm_eq_grafico_condicionalidade_iii_desigualdade_racial",
    "grafico_condicionalidade_iii_desigualdade_racial.py",
)
ensure_rawline_font_available = _helpers.ensure_rawline_font_available
get_chart_font_family = _helpers.get_chart_font_family
get_image_dimensions = _image_dimensions.get_image_dimensions
plot_two_point_slope_chart = _helpers.plot_two_point_slope_chart
_parse_percent = _racial_slope._parse_percent
_format_percent_label = _racial_slope._format_percent_label
_fit_value_labels_inside_figure = _racial_slope._fit_value_labels_inside_figure


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read reference image dimensions and return figsize in inches."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


_SLOPE_REFERENCE_IMAGE = "template/assets/charts/P3-G2.svg"


def _prepare_values(df: pd.DataFrame, ctx: ChartContext) -> tuple[list[float], list[str]] | None:
    required = {"p3PercentualSocioeconomica2019", "p3PercentualSocioeconomica2023"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes para grafico: {sorted(missing)}")

    row = df.iloc[0]
    value_2019 = _parse_percent(row.get("p3PercentualSocioeconomica2019"))
    value_2023 = _parse_percent(row.get("p3PercentualSocioeconomica2023"))
    if value_2019 is None or value_2023 is None:
        return None

    label_2019 = _format_percent_label(ctx, row.get("p3PercentualSocioeconomica2019"), value_2019)
    label_2023 = _format_percent_label(ctx, row.get("p3PercentualSocioeconomica2023"), value_2023)
    return ([value_2019, value_2023], [label_2019, label_2023])


@chart(
    "graficoCondicionalidadeIIIDesigualdadeSocioeconomica",
    data="p3_condicionalidade_iii_vaar",
    title="Alunos de baixo NSE com aprendizagem adequada (2019-2023)",
    figsize=_designer_figsize_inches(_SLOPE_REFERENCE_IMAGE),
)
def grafico_condicionalidade_iii_desigualdade_socioeconomica(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:  # type: ignore
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
        value_color="#FA7E17",
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
    # Mantem folga inferior para ticks de X e reserva margem esquerda quando eixo Y estiver visivel.
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
    # Borda de depuracao da area util do eixo.
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

    # Borda de depuracao: mostra os limites exatos da figura na exportacao.
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
