"""Chart for daycare and preschool attendance by race/color."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd

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
plot_barras_agrupadas = _helpers.plot_barras_agrupadas
get_image_dimensions = _image_dimensions.get_image_dimensions
AXIS_SIZE = _helpers.AXIS_SIZE
LABEL_SIZE = _helpers.LABEL_SIZE
ensure_rawline_font_available = _helpers.ensure_rawline_font_available
get_chart_font_family = _helpers.get_chart_font_family

CATEGORIA_ORDER = [
    "Branca",
    "Preta",
    "Parda",
    "Amarela",
    "Indígena",
]
ETAPA_ORDER = [
    "Creche",
    "Pré-Escola",
]


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read designer reference image dimensions and return matplotlib figsize (inches)."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate, normalize and reshape source dataframe for grouped bars helper."""
    required = {"etapa", "categoria", "percentual"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes para grafico: {sorted(missing)}")

    data = df.copy()
    data["etapa"] = (
        data["etapa"]
        .astype(str)
        .str.strip()
        .replace(
            {
                "Pre-Escola": "Pré-Escola",
                "PrÃ©-Escola": "Pré-Escola",
                "PrÃƒÂ©-Escola": "Pré-Escola",
            }
        )
    )
    data["categoria"] = (
        data["categoria"]
        .astype(str)
        .str.strip()
        .replace(
            {
                "Indigena": "Indígena",
                "IndÃ­gena": "Indígena",
                "IndÃƒÂ­gena": "Indígena",
            }
        )
    )
    data["percentual"] = pd.to_numeric(data["percentual"], errors="coerce").fillna(0.0)

    complete_index = pd.MultiIndex.from_product(
        [ETAPA_ORDER, CATEGORIA_ORDER],
        names=["etapa", "categoria"],
    )
    plot_data = (
        data.groupby(["etapa", "categoria"], as_index=False)["percentual"]
        .sum()
        .set_index(["etapa", "categoria"])
        .reindex(complete_index, fill_value=0.0)
        .reset_index()
    )

    non_zero_categories = (
        plot_data.groupby("categoria", as_index=False)["percentual"]
        .sum()
        .loc[lambda d: d["percentual"] > 0.0, "categoria"]
        .tolist()
    )
    if not non_zero_categories:
        return pd.DataFrame(columns=["etapa", "categoria", "percentual"])

    plot_data = plot_data[plot_data["categoria"].isin(non_zero_categories)].copy()
    plot_data["etapa"] = pd.Categorical(
        plot_data["etapa"],
        categories=ETAPA_ORDER,
        ordered=True,
    )
    plot_data["categoria"] = pd.Categorical(
        plot_data["categoria"],
        categories=[categoria for categoria in CATEGORIA_ORDER if categoria in non_zero_categories],
        ordered=True,
    )
    return plot_data.sort_values(["etapa", "categoria"])


def _format_percent_compacto(ctx: ChartContext, value: float) -> str:
    """Format percent labels without forcing trailing ',0' for integer values."""
    rounded = round(float(value), 1)
    if abs(rounded - round(rounded)) < 1e-9:
        return ctx.format_percent(rounded, 0)
    return ctx.format_percent(rounded, 1)


def _build_chart_spec(data: pd.DataFrame, ctx: ChartContext) -> dict[str, object]:
    """Build plot_barras_agrupadas kwargs."""
    return {
        "data": data,
        # Keep helper geometry computations aligned with the final chart size.
        "figsize": ctx.figsize,
        "x_col": "etapa",
        "y_col": "percentual",
        "group_col": "categoria",
        "colors": {
            "Branca": "#118D45",
            "Preta": "#9A1915",
            "Parda": "#FA7E17",
            "Amarela": "#265793",
            "Indígena": "#8D6E63",
        },
        "show_yaxis": False,
        "show_y_ticks": False,
        "show_xaxis": True,
        "show_x_ticks": False,
        "show_legend": True,
        "legend_position": "bottom",
        "legend_bbox": (0.5, -0.48),
        "legend_fontsize": LABEL_SIZE + 6,# = 10,
        "label_size": LABEL_SIZE + 7,# = 11,
        "show_labels": True,
        "axis_text_size": AXIS_SIZE + 3,# = 7,        
        # Local formatter keeps "100%" instead of "100,0%" without changing
        # ChartContext global behavior.
        "label_formatter": lambda v: _format_percent_compacto(ctx, v),
        "label_threshold": 0.0,
        "label_offset": 0.7, # distancia da barra com relacao ao valor da barra (em unidades de y, ou seja, percentual)
        "label_color": "#3C3C3C",
        "label_fontfamily": get_chart_font_family(),
        "label_shadow": False,
        # Light spacing increase to reduce visual crowding while preserving proportions.
        "bar_width": 0.72,
        "dodge_width": 0.88,
        "group_spacing": 1.5,
        "y_expand": (0.0, 0.0),
        "x_tick_rotation": 0.0,
        "x_tick_ha": "center",
        "y_floor": 100.0,
        "label_headroom_pct": 0.08,
        "show_grid": False,
    }

@chart(
    "graficoAtendimentoCrechePreEscola",
    data="grafico_atendimento_creche_pre_escola",
    title="Atendimento em creche e pré-escola por raça/cor (CadÚnico)",
    figsize=_designer_figsize_inches("template/assets/charts/P4-G1.svg"),
)
def grafico_atendimento_creche_pre_escola(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    
    if df is None or df.empty:
        return None

    data = _prepare_data(df)
    if data.empty:
        return None

    ensure_rawline_font_available(strict=False)
    spec = _build_chart_spec(data, ctx)
    fig = plot_barras_agrupadas(**spec)
    if fig is None:
        return None

    fig.set_size_inches(*ctx.figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    ax = fig.axes[0]
    ax.set_xlabel("")
    ax.set_ylabel("")

    fig.subplots_adjust(left=0.08, right=0.99, top=0.96, bottom=0.30)

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
