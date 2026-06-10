"""Charts de condicionalidades do relatorio ATM-EQ."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd

from schoolreport.charts import ChartContext, chart


CONDICIONALIDADE_LABELS = {
    "1": "Seleção por critérios técnicos do cargo de diretor escolar",
    "2": "Participação (>=80%) no Sistema de Avaliação da Educação Básica - Saeb",
    "3": "Redução das desigualdades",
    "4": "Regulamentação do ICMS Educacional no estado",
    "5": "Referenciais curriculares alinhados à Base Nacional Comum Curricular",
}
CONDICIONALIDADE_ORDER = ["1", "2", "3", "4", "5"]
STATUS_ORDER = ["true", "false", "pendente"]
STATUS_LABELS = {
    "true": "Atendido",
    "false": "N\u00e3o atendido",
    "pendente": "Pendente",
}
STATUS_COLORS = {
    "Atendido": "#048838",
    "N\u00e3o atendido": "#C62828",
    "Pendente": "#616161",
}


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
plot_barras_agrupadas = _helpers.plot_barras_agrupadas
AXIS_SIZE = _helpers.AXIS_SIZE
LABEL_SIZE = _helpers.LABEL_SIZE
ensure_rawline_font_available = _helpers.ensure_rawline_font_available
get_image_dimensions = _image_dimensions.get_image_dimensions


def _designer_figsize_inches(image_path: str | Path | None = None) -> tuple[float, float]:
    """Read designer reference image dimensions and return matplotlib figsize (inches)."""
    reference_image_path = (
        Path(image_path)
        if image_path is not None
        else Path(__file__).parent.parent / "template" / "assets" / "charts" / "Map.svg"
    )
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


def _prepare_data(
    df: pd.DataFrame,
    col_cond: str,
    col_att: str,
    col_pct: str,
    *,
    label_wrap: int,
) -> pd.DataFrame:
    """Validate, normalize and reshape condicionalidades data for the chart helper."""
    required = {col_cond, col_att, col_pct}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes para gráfico: {sorted(missing)}")

    data = df.copy()
    data[col_cond] = data[col_cond].astype(str)
    data[col_att] = data[col_att].astype(str).str.lower()
    data[col_pct] = pd.to_numeric(data[col_pct], errors="coerce").fillna(0.0)
    data = data.groupby([col_cond, col_att], as_index=False)[col_pct].sum()

    base = pd.MultiIndex.from_product(
        [CONDICIONALIDADE_ORDER, STATUS_ORDER],
        names=[col_cond, col_att],
    ).to_frame(index=False)
    merged = base.merge(data, on=[col_cond, col_att], how="left")
    merged[col_pct] = pd.to_numeric(merged[col_pct], errors="coerce").fillna(0.0)

    merged[col_cond] = pd.Categorical(
        merged[col_cond],
        categories=CONDICIONALIDADE_ORDER,
        ordered=True,
    )
    merged[col_att] = pd.Categorical(
        merged[col_att],
        categories=STATUS_ORDER,
        ordered=True,
    )
    merged = merged.sort_values([col_cond, col_att])

    def _wrap_label_max_two_lines(label: str, width: int) -> str:
        normalized = " ".join(str(label).split())
        wrapped = fill(normalized, width=width).splitlines()
        if len(wrapped) <= 2:
            return "\n".join(wrapped)

        words = normalized.split(" ")
        if len(words) <= 1:
            return normalized

        target = max(1, int(width))
        best_split = 1
        best_cost: tuple[int, int, int] | None = None
        for idx in range(1, len(words)):
            line1 = " ".join(words[:idx])
            line2 = " ".join(words[idx:])
            overflow = max(0, len(line1) - target) + max(0, len(line2) - target)
            balance = abs(len(line1) - len(line2))
            max_len = max(len(line1), len(line2))
            cost = (overflow, balance, max_len)
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_split = idx

        return " ".join(words[:best_split]) + "\n" + " ".join(words[best_split:])

    merged["status"] = merged[col_att].astype(str).map(STATUS_LABELS).fillna("Pendente")
    pending_label = STATUS_LABELS.get("pendente", "Pendente")
    pending_total = float(merged.loc[merged["status"] == pending_label, col_pct].sum())
    if pending_total <= 0.0:
        merged = merged.loc[merged["status"] != pending_label].copy()

    merged["cond_label"] = merged[col_cond].astype(str).map(
        lambda code: _wrap_label_max_two_lines(
            CONDICIONALIDADE_LABELS.get(code, f"Condicionalidade {code}"),
            width=label_wrap,
        )
    )

    return merged[["cond_label", "status", col_pct]].rename(columns={col_pct: "percentual"})


def _build_chart_spec(
    data: pd.DataFrame,
    ctx: ChartContext,
    level_label: str,
    category_text_size: float,
    max_label_lines: int,
) -> dict[str, object]:
    """Build plot_barras_agrupadas kwargs."""
    def _percent_label(value: float) -> str:
        label = ctx.format_percent(value, 0)
        return "" if label.strip() == "0%" else label

    spacing = min(1.70, max(1.18, 1.10 + ((max(1, max_label_lines) - 1) * 0.22)))
    y_tick_text_size = max(6.0, category_text_size - 1.0)
    return {
        "data": data,
        "x_col": "cond_label",
        "y_col": "percentual",
        "group_col": "status",
        "colors": STATUS_COLORS,
        "show_xaxis": False,
        "show_yaxis": True,
        "show_x_ticks": False,
        "show_y_ticks": False,
        "show_legend": True,
        "legend_position": "bottom",
        "legend_bbox": (0.0, -0.34),
        "legend_fontsize": category_text_size,
        "show_labels": True,
        "axis_text_size": category_text_size,  # Fallback size for axis texts.
        "x_axis_text_size": max(6.0, category_text_size - 1.0),
        # Keep y-label font size independent from bar geometry tuning.
        "y_axis_text_size": y_tick_text_size - 1,
        "y_tick_pad": 2.0,
        "label_size": LABEL_SIZE + 2,
        "label_formatter": _percent_label,
        "label_threshold": 0.0,
        "small_label_outside_threshold": 6.0,
        "small_label_min_width_px": 0.0,
        "small_label_padding_px": 3.0,
        "small_label_overlap_shift_px": 6.0,
        "outside_label_color": "#3C3C3C",
        "label_color": "white",
        "label_shadow": False,
        "bar_width": 1.10,
        "category_spacing": spacing,
        "category_outer_margin": 0.01,
        "auto_fit_ylabels_left": False,
        "ylabels_left_padding_px": 6.0,
        "min_left_margin": 0.10,
        "max_left_margin": 0.48,
        "y_expand": (0.0, 0.05),
        "show_grid": False,
        "stacked": True,
        "orientation": "horizontal",
        "graph_id": f"condicionalidades_percentual_{level_label.lower()}",
    }


def _render_condicionalidades_percentual(
    df: pd.DataFrame,
    ctx: ChartContext,
    *,
    level_label: str,
    col_cond: str,
    col_att: str,
    col_pct: str,
    label_font_size: float | None,
) -> plt.Figure | None:
    """Render condicionalidades chart using only data prep + helper spec."""
    if df is None or df.empty:
        return None

    ensure_rawline_font_available(strict=False)
    category_text_size = (
        float(label_font_size)
        if label_font_size is not None
        else float(max(6.0, AXIS_SIZE - 1))
    )

    label_area_ratio = 0.50
    fig_width_in = float(ctx.figsize[0]) if ctx.figsize and len(ctx.figsize) >= 1 else 10.0
    label_width_in = max(1.4, fig_width_in * label_area_ratio * 1.05)
    chars_per_inch = max(6.0, 14.5 - (category_text_size * 0.50))
    label_wrap = max(34, min(72, int(round(label_width_in * chars_per_inch))))

    data = _prepare_data(
        df=df,
        col_cond=col_cond,
        col_att=col_att,
        col_pct=col_pct,
        label_wrap=label_wrap,
    )
    if data.empty:
        return None
    max_label_lines = int(data["cond_label"].astype(str).str.count("\n").max()) + 1

    spec = _build_chart_spec(
        data=data,
        ctx=ctx,
        level_label=level_label,
        category_text_size=category_text_size,
        max_label_lines=max_label_lines,
    )
    fig = plot_barras_agrupadas(**spec)
    if fig is None:
        return None

    fig.set_size_inches(*ctx.figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    ax = fig.axes[0]
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Reserve exactly half of figure width for y labels and half for the chart area.
    fig.subplots_adjust(left=label_area_ratio, right=0.99, top=0.96, bottom=0.22)

    # Debug border: shows the exact figure/canvas limits in the exported image.
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


@chart(
    "graficoCondicionalidadesUfPercentual",
    data="grafico_condicionalidades_uf",
    title="Condicionalidades por UF - Atendimento (%)",
    figsize=_designer_figsize_inches("template/assets/charts/P1-G3.svg"),
)
def grafico_condicionalidades_uf_percentual(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Horizontal stacked bars for UF."""
    return _render_condicionalidades_percentual(
        df=df,
        ctx=ctx,
        level_label="UF",
        col_cond="condicionalidadeUf",
        col_att="atendimentoUf",
        col_pct="percentualUf",
        label_font_size=8.0,
    )


@chart(
    "graficoCondicionalidadesBrasilPercentual",
    data="grafico_condicionalidades_brasil",
    title="Condicionalidades no Brasil - Atendimento (%)",
    figsize=_designer_figsize_inches("template/assets/charts/P1-G2.svg"),
)
def grafico_condicionalidades_brasil_percentual(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Horizontal stacked bars for Brasil."""
    return _render_condicionalidades_percentual(
        df=df,
        ctx=ctx,
        level_label="Brasil",
        col_cond="condicionalidadeBrasil",
        col_att="atendimentoBrasil",
        col_pct="percentualBrasil",
        label_font_size=8.0,
    )
