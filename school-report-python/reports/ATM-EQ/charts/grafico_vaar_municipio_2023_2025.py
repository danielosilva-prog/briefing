# Todos os comentários devem ser mantidos em português (pt-BR) para padronização do projeto.
"""Gráfico de valores previstos do VAAR pelo município (2023-2026)."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
from typing import Callable

from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
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
    """
    Formata valores monetários completos em reais, sem abreviações e sem centavos.

    Por decisão de negócio, os centavos são ocultados nos rótulos.
    Não há arredondamento: apenas truncamento visual da parte decimal.
    """
    value_truncado = int(float(value))
    return f"R$ {_format_number_br(value_truncado, 0)}"


def _format_brl_label(value: float) -> str:
    """
    Formata rótulos monetários em escala dinâmica para evitar perda de informação.

    O comportamento anterior sempre forçava milhões e podia transformar valores
    relevantes, como 48.262,8, em "R$ 0,0 mi". Este formatter escolhe escala
    por magnitude: bi/mi/mil/valor completo.
    """
    abs_value = abs(float(value))

    if abs_value >= 1_000_000_000:  # 1 bi ou mais
        return f"R$ {_format_number_br(value / 1_000_000_000, 1)} bi"

    if abs_value >= 1_000_000:  # 1 mi ou mais
        return f"R$ {_format_number_br(value / 1_000_000, 1)} mi"

    if abs_value >= 1_000:  # 1 mil ou mais
        scaled = value / 1_000
        decimals = 0 if math.isclose(scaled, round(scaled), abs_tol=1e-9) else 1
        return f"R$ {_format_number_br(scaled, decimals)} mil"

    # Menos de 1 mil: mostra valor completo com 1 casa decimal quando necessário.
    decimals = 0 if math.isclose(value, round(value), abs_tol=1e-9) else 1
    return f"R$ {_format_number_br(value, decimals)}"


def _format_brl_million_legacy(value: float) -> str:
    """Formatter legado mantido para comparação de tamanho de rótulo."""
    return f"R$ {value / 1_000_000:.1f} mi".replace(".", ",")


def _has_label_overlap_risk(
    data: pd.DataFrame,
    label_size: float,
    ctx: ChartContext,
    label_formatter: Callable[[float], str] = _format_brl_label,
) -> bool:
    """
    Estima risco de sobreposição quando os rótulos ficam mais longos.

    Reduzimos o tamanho da fonte apenas se:
    1) os rótulos atuais forem maiores que o legado; e
    2) a largura estimada do texto se aproximar do espaço por barra.
    """
    if data.empty or len(data) <= 1:
        return False

    values = data["valor"].to_numpy(dtype=float)
    current_labels = [label_formatter(v) for v in values]
    legacy_labels = [_format_brl_million_legacy(v) for v in values]

    has_longer_current_label = any(
        len(current_label) > len(legacy_label)
        for current_label, legacy_label in zip(current_labels, legacy_labels)
    )
    if not has_longer_current_label:
        return False

    current_max_len = max((len(label) for label in current_labels), default=0)
    fig_width_px = float(ctx.figsize[0]) * float(ctx.dpi)
    axis_width_px = fig_width_px * 0.93  # Espelha fig.subplots_adjust(left=0.05, right=0.98).
    slot_width_px = axis_width_px / float(len(data))

    # Estimativa aproximada da largura do texto em pixels.
    est_label_width_px = current_max_len * float(label_size) * (float(ctx.dpi) / 72.0) * 0.56
    return est_label_width_px >= (slot_width_px * 0.9)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Valida, normaliza e prepara o dataframe para o plot_barras_simples."""
    required = {"anoReferencia", "valorPrevistoComplementacaoVAARMunicipio"}
    legacy_required = {"anoReferencia", "valorRepassadoComplementacaoVAARMunicipio"}
    missing = required - set(df.columns)
    if missing and not legacy_required.issubset(set(df.columns)):
        raise ValueError(f"Colunas obrigatórias ausentes para gráfico: {sorted(missing)}")

    data = df.copy()
    data["anoReferencia"] = pd.to_numeric(data["anoReferencia"], errors="coerce")
    value_column = (
        "valorPrevistoComplementacaoVAARMunicipio"
        if "valorPrevistoComplementacaoVAARMunicipio" in data.columns
        else "valorRepassadoComplementacaoVAARMunicipio"
    )
    data[value_column] = pd.to_numeric(data[value_column], errors="coerce").fillna(0.0)
    data = data.dropna(subset=["anoReferencia"]).sort_values("anoReferencia")
    if data.empty:
        return data

    return pd.DataFrame(
        {
            "ano": data["anoReferencia"].astype(int).astype(str),
            "valor": data[value_column].to_numpy(dtype=float),
        }
    )


def _build_chart_spec(data: pd.DataFrame, ctx: ChartContext) -> dict[str, object]:
    """Monta os parâmetros de chamada do plot_barras_simples."""
    max_value = float(data["valor"].max()) if not data.empty else 0.0
    label_formatter = _format_brl_full

    label_size = LABEL_SIZE + 6
    if _has_label_overlap_risk(
        data,
        label_size=label_size,
        ctx=ctx,
        label_formatter=label_formatter,
    ):
        label_size -= 1

    return {
        "data": data,
        "x_col": "ano",
        "y_col": "valor",
        "colors": ["#FA7E17"],
        "show_labels": max_value > 0,
        "label_formatter": label_formatter,
        "label_size": label_size,
        "label_color": "#3C3C3C",
        "show_yaxis": False,
        "show_y_ticks": False,
        "show_x_ticks": False,
        "show_grid": False,
        # Barras ligeiramente mais espessas para acomodar rótulos completos.
        "bar_width": 0.61,
        "y_expand": (0.0, 0.18),
        "smart_labels": False,
        "y_scale_mode": "dynamic",
        "axis_text_x_size": AXIS_SIZE,
        "axis_text_y_size": AXIS_SIZE,
        "ticklabel_format_style": "plain",
        "empty_value_message": (
            "Sem valor previsto de VAAR em 2023-2026 para este município" if max_value <= 0 else None
        ),
        "empty_value_message_xy": (0.5, 0.52),
        "empty_value_message_size": 10,
        "empty_value_message_color": "#3C3C3C",
    }


@chart(
    "graficoValoresPrevistosVaarMunicipio",
    data="grafico_vaar_municipio_2023_2025",
    title="Valores previstos do VAAR pelo município (2023-2026)",
    figsize=_designer_figsize_inches("template/assets/charts/P1-G1.svg"),
)
def grafico_valores_previstos_vaar_municipio(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Gera gráfico de barras dos valores previstos do VAAR pelo município."""
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
    fig.subplots_adjust(top=0.93, bottom=0.15, left=0.02, right=0.98)
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
