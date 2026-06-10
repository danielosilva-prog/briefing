"""Gráfico de crescimento da complementação VAAR/FUNDEB (2023-2026)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd

from schoolreport.charts import ChartContext, chart


def _load_local_module(module_name: str, relative_path: str):
    """Carrega módulo local por caminho (a pasta ATM-EQ possui hífen no nome)."""
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
plot_barras_simples = _helpers.plot_barras_simples
AXIS_SIZE = _helpers.AXIS_SIZE
LABEL_SIZE = _helpers.LABEL_SIZE
get_image_dimensions = _image_dimensions.get_image_dimensions


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Lê dimensões da imagem de referência e retorna figsize em polegadas."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


_DESIGNER_FIGSIZE = _designer_figsize_inches("template/assets/charts/P1-G1.svg")


def _format_number_br(value: float, decimals: int) -> str:
    """Formata número no padrão brasileiro (milhar='.' e decimal=',')."""
    return f"{value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _format_brl_full(value: float) -> str:
    """Formata valores monetários completos em reais, sem centavos e com truncamento."""
    value_truncado = int(float(value))
    return f"R$ {_format_number_br(value_truncado, 0)}"


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Valida, normaliza e prepara o dataframe para o plot_barras_simples."""
    required = {"anoReferencia", "valorNominalVaar"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes para gráfico: {sorted(missing)}")

    data = df.copy()
    data["anoReferencia"] = pd.to_numeric(data["anoReferencia"], errors="coerce")
    data["valorNominalVaar"] = pd.to_numeric(data["valorNominalVaar"], errors="coerce").fillna(0.0)
    data = data.dropna(subset=["anoReferencia"]).sort_values("anoReferencia")
    if data.empty:
        return data

    return pd.DataFrame(
        {
            "ano": data["anoReferencia"].astype(int).astype(str),
            "valor": data["valorNominalVaar"].to_numpy(dtype=float),
        }
    )


def _build_chart_spec(data: pd.DataFrame, _: ChartContext) -> dict[str, object]:
    """Monta os parâmetros de chamada do plot_barras_simples."""
    return {
        "data": data,
        "x_col": "ano",
        "y_col": "valor",
        "colors": ["#FA7E17"],
        "show_labels": True,
        "label_formatter": _format_brl_full,
        "label_size": LABEL_SIZE + 5,
        "label_color": "#3C3C3C",
        "show_yaxis": False,
        "show_y_ticks": False,
        "show_x_ticks": False,
        "show_grid": False,
        "bar_width": 1.2,
        "category_spacing": 1.3,
        "y_expand": (0.0, 0.20),
        "smart_labels": False,
        "y_scale_mode": "dynamic",
        "axis_text_x_size": AXIS_SIZE - 1,
        "axis_text_y_size": AXIS_SIZE,
        "ticklabel_format_style": "plain",
    }


@chart(
    "graficoCrescimentoVaarFundeb",
    data="grafico_crescimento_vaar_fundeb_2023_2026",
    title="Crescimento da complementação VAAR/FUNDEB (2023-2026)",
    figsize=_DESIGNER_FIGSIZE,
)
def grafico_crescimento_vaar_fundeb(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Gera barras verticais do crescimento nominal do VAAR/FUNDEB no Brasil (2023-2026)."""
    if df is None or df.empty:
        return None

    data = _prepare_data(df)
    if data.empty:
        return None

    spec = _build_chart_spec(data, ctx)
    fig = plot_barras_simples(**spec)
    if fig is None:
        return None

    fig.set_size_inches(*_DESIGNER_FIGSIZE, forward=True)
    fig.set_dpi(ctx.dpi)
    fig.subplots_adjust(top=1, bottom=0.10, left=0.0, right=1)
    # Garante que o SVG final preserve exatamente o canvas configurado da figura.
    setattr(fig, "_schoolreport_preserve_svg_size", True)
    setattr(
        fig,
        "_schoolreport_expected_svg_size_inches",
        (float(_DESIGNER_FIGSIZE[0]), float(_DESIGNER_FIGSIZE[1])),
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
