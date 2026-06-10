"""Chart for approval rates by school profile."""

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
        raise ImportError(f"Não foi possível carregar módulo: {module_path}")
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

SCHOOL_PROFILE_ORDER = [
    "Maioria PPI",
    "Maioria não PPI",
    "Escolas quilombolas",
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
    required = {"grupoEscola", "taxaAprovacaoAnosIniciais", "taxaAprovacaoAnosFinais"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes para gráfico: {sorted(missing)}")

    data = df.copy()
    data["grupoEscola"] = data["grupoEscola"].astype(str).replace(
        {
            "PPI >= 60%": "Maioria PPI",
            "PPI < 60%": "Maioria não PPI",
            "Quilombola": "Escolas quilombolas",
        }
    )
    data = pd.DataFrame({"grupoEscola": SCHOOL_PROFILE_ORDER}).merge(
        data,
        on="grupoEscola",
        how="left",
    )
    data["grupoEscola"] = pd.Categorical(
        data["grupoEscola"],
        categories=SCHOOL_PROFILE_ORDER,
        ordered=True,
    )
    data["taxaAprovacaoAnosIniciais"] = pd.to_numeric(
        data["taxaAprovacaoAnosIniciais"], errors="coerce"
    )
    data["taxaAprovacaoAnosFinais"] = pd.to_numeric(
        data["taxaAprovacaoAnosFinais"], errors="coerce"
    )
    # Preserva semântica: ausência de dado (NaN original) é diferente de valor 0 real.
    data["is_missing_iniciais"] = data["taxaAprovacaoAnosIniciais"].isna()
    data["is_missing_finais"] = data["taxaAprovacaoAnosFinais"].isna()
    data["taxaAprovacaoAnosIniciais"] = data["taxaAprovacaoAnosIniciais"].fillna(0.0)
    data["taxaAprovacaoAnosFinais"] = data["taxaAprovacaoAnosFinais"].fillna(0.0)
    if data.empty:
        return data

    plot_data = data.melt(
        id_vars=["grupoEscola", "is_missing_iniciais", "is_missing_finais"],
        value_vars=["taxaAprovacaoAnosIniciais", "taxaAprovacaoAnosFinais"],
        var_name="etapa",
        value_name="percentual",
    )
    plot_data["is_missing_original"] = plot_data["is_missing_finais"]
    iniciais_mask = plot_data["etapa"] == "taxaAprovacaoAnosIniciais"
    plot_data.loc[iniciais_mask, "is_missing_original"] = plot_data.loc[
        iniciais_mask, "is_missing_iniciais"
    ]
    plot_data["is_missing_original"] = plot_data["is_missing_original"].astype(bool)
    plot_data["etapa"] = plot_data["etapa"].replace(
        {
            "taxaAprovacaoAnosIniciais": "Anos Iniciais",
            "taxaAprovacaoAnosFinais": "Anos Finais",
        }
    )
    plot_data["etapa"] = pd.Categorical(
        plot_data["etapa"],
        categories=["Anos Iniciais", "Anos Finais"],
        ordered=True,
    )
    return plot_data.sort_values(["etapa", "grupoEscola"]).drop(
        columns=["is_missing_iniciais", "is_missing_finais"]
    )


def _build_chart_spec(data: pd.DataFrame, ctx: ChartContext) -> dict[str, object]:
    """Build plot_barras_agrupadas kwargs."""
    colors = {
        "Maioria PPI": "#2E7D32",
        "Maioria não PPI": "#607D8B",
        "Escolas quilombolas": "#8C4A2F",
    }

    # O helper global envia apenas o valor numérico para o formatter.
    # Para manter a distinção entre ausência e 0 real, precomputamos um
    # sequenciamento de "is_missing_original" na mesma ordem de desenho das barras.
    x_order = list(dict.fromkeys(data["etapa"].astype(str).tolist()))
    present_groups = set(data["grupoEscola"].astype(str).tolist())
    group_order = [group for group in colors if group in present_groups]
    data_with_keys = data.assign(
        etapa_key=data["etapa"].astype(str),
        grupo_key=data["grupoEscola"].astype(str),
    )
    missing_by_pair = (
        data_with_keys.groupby(["etapa_key", "grupo_key"], as_index=True, observed=False)[
            "is_missing_original"
        ]
        .all()
        .to_dict()
    )
    missing_sequence = iter(
        bool(missing_by_pair.get((etapa, group), False))
        for group in group_order
        for etapa in x_order
    )

    def _format_percent_or_missing(value: float) -> str:
        # Ausência de dado vira "-", enquanto 0 real mantém formatação percentual.
        if next(missing_sequence, False):
            return "-"
        return ctx.format_percent(float(value), 1)

    return {
        "data": data,
        "x_col": "etapa",
        "y_col": "percentual",
        "group_col": "grupoEscola",
        "colors": colors,
        "show_yaxis": False,
        "show_y_ticks": False,
        "show_xaxis": True,
        "show_x_ticks": False,
        "show_legend": True,
        "legend_position": "bottom",
        "legend_bbox": (0.5, -0.5),
        "legend_fontsize": AXIS_SIZE + 3,
        "show_labels": True,
        "axis_text_size": AXIS_SIZE + 3,
        "label_size": LABEL_SIZE + 7,
        "label_formatter": _format_percent_or_missing,
        "label_threshold": 0.0,
        "label_offset": 1.0,
        "label_color": "#3C3C3C",
        "label_shadow": False,
        "bar_width": 0.6,
        "dodge_width": 0.65,
        "y_expand": (0.0, 0.0),
        "x_tick_rotation": 0.0,
        "x_tick_ha": "center",
        "y_floor": 100.0,
        "label_headroom_pct": 0.12,# folga extra para evitar corte de rotulo quando barra chega a 100%
        "show_grid": False,
    }


@chart(
    "graficoTaxaRendimento",
    data="grafico_taxa_rendimento",
    title="Taxa média de aprovação no ensino fundamental por perfil das escolas",
    figsize=_designer_figsize_inches("template/assets/charts/P5-G3.svg"),
)
def grafico_taxa_rendimento(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Grouped bars for approval rates in the two EF stages by school profile."""
    if df is None or df.empty:
        return None

    data = _prepare_data(df)
    if data.empty:
        return None

    spec = _build_chart_spec(data, ctx)
    fig = plot_barras_agrupadas(**spec)
    if fig is None:
        return None

    fig.set_size_inches(*ctx.figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    ax = fig.axes[0]
    ax.set_xlabel("")
    ax.set_ylabel("")

    fig.subplots_adjust(left=0.05, right=0.98, top=0.96, bottom=0.30)

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
