"""Chart for enrollment distribution by race/color."""

from __future__ import annotations

import importlib.util
import math
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
plot_barras_simples = _helpers.plot_barras_simples
get_image_dimensions = _image_dimensions.get_image_dimensions


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read designer reference image dimensions and return matplotlib figsize (inches)."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


_CATEGORIAS_RACIAIS = {"Amarela", "Branca", "Indígena", "Não declarada", "Parda", "Preta"}

_DECIMALS_DISPLAY = 1  # casas decimais exibidas no gráfico


def _largest_remainder(values: list[float], total: float = 100.0, decimals: int = 1) -> list[float]:
    """
    Ajusta percentuais arredondados para somar exatamente `total` usando o
    algoritmo de maior resto (Hamilton), garantindo que nenhum município
    exiba uma soma diferente de 100,0%.

    Funciona para qualquer número de casas decimais.
    """
    scale = 10**decimals
    floored = [math.floor(v * scale) / scale for v in values]
    remainder = round(total - sum(floored), decimals)
    n_adjust = round(remainder * scale)  # quantas unidades de 1/scale adicionar

    if n_adjust == 0:
        return floored

    step = 1.0 / scale
    # Ordena pelos maiores restos fracionários para decidir quem recebe o ajuste.
    fractional = [(v * scale) - math.floor(v * scale) for v in values]
    indices = sorted(range(len(values)), key=lambda i: fractional[i], reverse=(n_adjust > 0))

    result = floored[:]
    for i in range(abs(n_adjust)):
        result[indices[i % len(indices)]] = round(result[indices[i % len(indices)]] + step * (1 if n_adjust > 0 else -1), decimals)

    return result


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate input, normalize dataframe, and apply largest-remainder rounding."""
    required = {"categoria", "percentual"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes para grafico: {sorted(missing)}")

    data = df.copy()
    data["categoria"] = data["categoria"].astype(str)
    data["percentual"] = pd.to_numeric(data["percentual"], errors="coerce").fillna(0.0)

    # Aplica maior-resto às categorias raciais para garantir soma = 100,0%.
    # "Não declarada" é fixada no seu arredondamento natural para manter consistência
    # com o gráfico de declaração racial (que calcula o complemento de nao_declarada).
    # O maior-resto é distribuído apenas pelas outras 5 categorias.
    # Quilombola é métrica paralela (base diferente) e não entra no ajuste.
    mask_racial = data["categoria"].isin(_CATEGORIAS_RACIAIS)
    mask_nao_decl = data["categoria"] == "Não declarada"
    mask_outras = mask_racial & ~mask_nao_decl

    if mask_racial.any():
        scale = 10**_DECIMALS_DISPLAY
        nao_decl_pct = round(
            math.floor(float(data.loc[mask_nao_decl, "percentual"].iloc[0]) * scale) / scale
            if mask_nao_decl.any() else 0.0,
            _DECIMALS_DISPLAY,
        )
        target_outras = round(100.0 - nao_decl_pct, _DECIMALS_DISPLAY)
        outras_pcts = data.loc[mask_outras, "percentual"].tolist()
        if outras_pcts:
            adjusted = _largest_remainder(outras_pcts, total=target_outras, decimals=_DECIMALS_DISPLAY)
            data.loc[mask_outras, "percentual"] = adjusted
        if mask_nao_decl.any():
            data.loc[mask_nao_decl, "percentual"] = nao_decl_pct

    data = data.sort_values("percentual", ascending=True)
    return data


def _build_chart_spec(data: pd.DataFrame, ctx: ChartContext) -> dict[str, object]:
    """Build plotting kwargs and post-render axis settings."""
    max_percentual = float(data["percentual"].max()) if not data.empty else 0.0
    return {
        "data": data,
        "x_col": "categoria",
        "y_col": "percentual",
        "colors": ["#1E88E5"],
        "show_labels": True,
        "label_formatter": lambda v: ctx.format_percent(v, 1),
        "show_y_ticks": False,
        "show_yaxis": True,
        "show_xaxis": False,
        "label_size": 8,
        "bar_width": 0.8,
        "label_color": "#3C3C3C",
        "show_grid": False,
        "smart_labels": False,
        "y_scale_mode": "dynamic",
        "y_expand": (0.0, 0.0),
        "orientation": "horizontal",
        "label_offset": 0.8,
        "xlim": (0, max(100.0, max_percentual * 1.1)),
    }


@chart(
    "graficoDistribuicaoMatriculas",
    data="grafico_distribuicao_matriculas",
    title="Distribuição de matrículas por raça/cor",
    figsize=_designer_figsize_inches("template/assets/charts/P4-G2.svg"),
)
def grafico_distribuicao_matriculas(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Horizontal bar chart for matricula distribution by category."""
    if df is None or df.empty:
        return None

    data = _prepare_data(df)
    spec = _build_chart_spec(data, ctx)

    fig = plot_barras_simples(**spec)
    if fig is None:
        return None

    fig.set_size_inches(*ctx.figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    ax = fig.axes[0]
    ax.set_xlim(spec["xlim"])
    ax.margins(y=0.02)

    # Fine-tune vertical occupancy to calibrate spacing against the SVG canvas.
    fig.subplots_adjust(left=0.14, right=0.99, top=0.992, bottom=0.006)

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
