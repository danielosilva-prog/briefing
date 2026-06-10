"""Chart for teachers' education level distribution."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import matplotlib.pyplot as plt
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
    required = {"grupoEscola", "percentualEdInfantilAdequada", "percentualAnosIniciaisAdequada"}
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
    data["percentualEdInfantilAdequada"] = pd.to_numeric(
        data["percentualEdInfantilAdequada"], errors="coerce"
    ).fillna(0.0)
    data["percentualAnosIniciaisAdequada"] = pd.to_numeric(
        data["percentualAnosIniciaisAdequada"], errors="coerce"
    ).fillna(0.0)
    if data.empty:
        return data

    plot_data = data.melt(
        id_vars="grupoEscola",
        value_vars=["percentualEdInfantilAdequada", "percentualAnosIniciaisAdequada"],
        var_name="etapa",
        value_name="percentual",
    )
    plot_data["etapa"] = plot_data["etapa"].replace(
        {
            "percentualEdInfantilAdequada": "Educação Infantil",
            "percentualAnosIniciaisAdequada": "Anos Iniciais",
        }
    )
    return plot_data.sort_values("grupoEscola")


def _build_chart_spec(data: pd.DataFrame, ctx: ChartContext) -> dict[str, object]:
    """Build plot_barras_agrupadas kwargs."""
    def _format_percent_or_absence(value: float) -> str:
        numeric_value = float(value)
        # Neste grafico, 0 representa ausencia de ocorrencia (nao apenas "0%"),
        # por isso mostramos "-" para diferenciar de percentuais validos.
        if abs(numeric_value) < 1e-9:
            return "-"
        return ctx.format_percent(numeric_value, 1)

    return {
        "data": data,
        "x_col": "grupoEscola",
        "y_col": "percentual",
        "group_col": "etapa",
        "colors": {
            "Educação Infantil": "#2E7D32",
            "Anos Iniciais": "#8C4A2F",
        },
        "show_yaxis": False,
        "show_y_ticks": False,
        "show_xaxis": True,
        "show_x_ticks": False,
        "show_legend": True,
        "legend_position": "bottom",
        "legend_bbox": (0.5, -0.44),
        "legend_fontsize": AXIS_SIZE,
        "show_labels": True,
        "axis_text_size": AXIS_SIZE,
        "label_size": LABEL_SIZE + 5,
        "label_formatter": _format_percent_or_absence,
        "label_threshold": 0.0,
        "label_offset": 0.8,# quanto maior, mais proximo do topo da barra o rotulo fica
        "label_color": "#3C3C3C",
        "label_shadow": False,
        "bar_width": 0.42,
        "dodge_width": 0.45,# quanto mais proximo de 1.0, mais espacadas as barras dos grupos ficam (0.5 = sem espaco, 1.0 = sem agrupamento)
        "group_spacing": 0.68,# distancia entre os centros de cada grupo no eixo x (1.0 = padrao)
        "y_expand": (0.0, 0.0),
        "x_tick_rotation": 0.0,
        "x_tick_ha": "center",
        "y_floor": 100.0,
        "label_headroom_pct": 0.06,
        "show_grid": False,
    }


@chart(
    "graficoNivelFormacaoProfessores",
    data="grafico_nivel_formacao_professores",
    title="DOCENTES COM FORMAÇÃO ADEQUADA POR PERFIL DA ESCOLA",
    figsize=_designer_figsize_inches("template/assets/charts/P5-G1.svg"),
)
def grafico_nivel_formacao_professores(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Grouped bars for school groups in the municipality."""
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

    fig.subplots_adjust(left=0.05, right=0.98, top=0.96, bottom=0.28)
    return fig
