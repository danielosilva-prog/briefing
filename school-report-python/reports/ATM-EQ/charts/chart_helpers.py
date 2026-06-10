"""
ATM chart helpers converted from the R plotting-helpers.R module.

This module provides reusable plotting helpers with a matplotlib-first API.
Most functions return a matplotlib Figure or None when input data is invalid.
"""

from __future__ import annotations

import json
import math
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional, Sequence

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.colors import to_rgba
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch
from matplotlib.transforms import Bbox

FONT_PADRAO = "Rawline"
LABEL_SIZE = 4
AXIS_SIZE = 9
TITLE_SIZE = 11
_FONT_FAMILY_IN_USE = FONT_PADRAO
_RAWLINE_DIR = Path(__file__).resolve().parent.parent / "template" / "assets" / "Rawline"

VALID_STATE_CODES = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}

_STATE_GEOMETRY_CACHE: Dict[str, Any] = {}
_MUNICIPALITY_POINT_CACHE: Dict[str, tuple[float, float]] = {}
_GEOBR_RELEASE_BASE_URL = "https://github.com/ipeaGIT/geobr/releases/download/v1.7.0/"
_GEOBR_METADATA_MIRROR_URL = f"{_GEOBR_RELEASE_BASE_URL}metadata_1.7.0_gpkg.csv"
_GEOBR_CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache" / "geobr"
_MAP_LABEL_BBOX_STYLE = {"facecolor": "white", "edgecolor": "none", "alpha": 0.9}
_MAP_LABEL_PROXIMITY_M = 150_000.0
_MAP_LABEL_PROXIMITY_PX = 140.0
_MAP_LABEL_MAX_OVERLAP_PX2 = 1.0
_MAP_LABEL_MAX_OUTSIDE_PX2 = 32.0
_MAP_LABEL_VISIBLE_OUTSIDE_PX2 = 1.0
_MAP_LABEL_VISIBLE_OVERLAP_PX2 = 1.0
_MAP_LABEL_MAX_FONT_REDUCTION = 2.0
_MAP_LABEL_MARGIN_ATTEMPTS = 4
_MAP_MUNICIPALITY_COLOR = "#E65100"
_MAP_CAPITAL_POINT_COLOR = "#183EFF"
_MAP_CAPITAL_LABEL_COLOR = "#183EFF"
_MAP_STATE_FILL_COLOR = "#183EFF"
_MAP_CAPITAL_COLOR_FALLBACK = "#6A1B9A"
_MAP_BACKGROUND_COLOR = "#F4F6FB00"
_EMPTY_STATE_DEFAULT_MESSAGE = "Aus\u00eancia de dados suficientes"
_EMPTY_STATE_OUTER_FILL = "#E7E7E7"
_EMPTY_STATE_INNER_FILL = "#A7A7A7"
_EMPTY_STATE_TEXT_COLOR = "#FFFFFF"
_EMPTY_STATE_DEFAULT_FIGSIZE = (9.0, 2.8)
_EMPTY_STATE_TEXT_BBOX_STYLE = "round,pad=0.6"


def _ensure_geobr_cache_dir() -> Path:
    _GEOBR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _GEOBR_CACHE_DIR


def _state_geometry_cache_path(state_code: str, year: int) -> Path:
    return _ensure_geobr_cache_dir() / f"state_{state_code.upper()}_{year}.pkl"


def _municipality_point_cache_path(code_muni: str | int, year: int) -> Path:
    code = str(code_muni).strip()
    return _ensure_geobr_cache_dir() / f"municipality_point_{code}_{year}.json"


def _rawline_font_candidates() -> list[Path]:
    """Return Rawline font files from the official ATM-EQ fonts directory."""
    if not _RAWLINE_DIR.exists():
        return []

    # Prioriza os nomes canônicos da Rawline e depois inclui os demais arquivos de fonte.
    preferred = sorted(_RAWLINE_DIR.glob("rawline-*.ttf")) + sorted(
        _RAWLINE_DIR.glob("rawline-*.otf")
    )
    all_fonts = sorted(_RAWLINE_DIR.glob("*.ttf")) + sorted(_RAWLINE_DIR.glob("*.otf"))

    seen: set[Path] = set()
    ordered: list[Path] = []
    for candidate in preferred + all_fonts:
        if candidate not in seen:
            ordered.append(candidate)
            seen.add(candidate)
    return ordered


def ensure_rawline_font_available(strict: bool = False) -> bool:
    """Ensure matplotlib can resolve Rawline. Returns True when available."""
    global _FONT_FAMILY_IN_USE
    try:
        font_manager.findfont(FontProperties(family=FONT_PADRAO), fallback_to_default=False)
        plt.rcParams["font.family"] = FONT_PADRAO
        _FONT_FAMILY_IN_USE = FONT_PADRAO
        return True
    except Exception:
        pass

    for candidate in _rawline_font_candidates():
        if candidate.exists():
            try:
                font_manager.fontManager.addfont(str(candidate))
            except Exception:
                continue

    try:
        font_manager.findfont(FontProperties(family=FONT_PADRAO), fallback_to_default=False)
        plt.rcParams["font.family"] = FONT_PADRAO
        _FONT_FAMILY_IN_USE = FONT_PADRAO
        return True
    except Exception:
        message = (
            "Fonte Rawline nao encontrada no ambiente/matplotlib. "
            "Instale/registre a Rawline para manter o padrao visual do projeto."
        )
        if strict:
            raise RuntimeError(message)
        _FONT_FAMILY_IN_USE = "DejaVu Sans"
        plt.rcParams["font.family"] = _FONT_FAMILY_IN_USE
        warnings.warn(message, stacklevel=2)
        return False


def get_chart_font_family() -> str:
    """Return the effective font family currently used by charts."""
    return _FONT_FAMILY_IN_USE


def _to_dataframe(data: Any) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data.copy()
    return pd.DataFrame(data)


def _format_number_br(value: float, decimals: int = 0) -> str:
    return f"{value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _format_label(value: float, label_format: str, decimal_places: int = 0) -> str:
    if label_format == "integer":
        return _format_number_br(round(value), 0)
    if label_format == "decimal":
        return _format_number_br(value, decimal_places)
    if label_format == "percent":
        return f"{_format_number_br(value, decimal_places)}%"
    return str(value)


def build_empty_state_figure(
    figsize: tuple[float, float] = _EMPTY_STATE_DEFAULT_FIGSIZE,
    *,
    dpi: int = 100,
    message: str = _EMPTY_STATE_DEFAULT_MESSAGE,
) -> plt.Figure:
    """Build the standard ATM-EQ empty-state chart figure."""
    ensure_rawline_font_available(strict=False)

    resolved_figsize = (max(1.0, float(figsize[0])), max(0.8, float(figsize[1])))
    fig = plt.figure(figsize=resolved_figsize, dpi=dpi)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    fig.patch.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    outer_patch = FancyBboxPatch(
        (0.02, 0.08),
        0.96,
        0.84,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=0.0,
        facecolor=_EMPTY_STATE_OUTER_FILL,
        edgecolor="none",
        transform=ax.transAxes,
        zorder=1,
    )
    ax.add_patch(outer_patch)

    text_size = max(10.0, min(20.0, 8.0 + (resolved_figsize[1] * 4.5)))
    ax.text(
        0.5,
        0.5,
        str(message),
        ha="center",
        va="center",
        color=_EMPTY_STATE_TEXT_COLOR,
        fontsize=text_size,
        fontfamily=get_chart_font_family(),
        fontweight="bold",
        transform=ax.transAxes,
        clip_on=False,
        bbox={
            "boxstyle": _EMPTY_STATE_TEXT_BBOX_STYLE,
            "facecolor": _EMPTY_STATE_INNER_FILL,
            "edgecolor": "none",
        },
        zorder=3,
    )

    setattr(fig, "_schoolreport_preserve_svg_size", True)
    setattr(
        fig,
        "_schoolreport_expected_svg_size_inches",
        (float(resolved_figsize[0]), float(resolved_figsize[1])),
    )
    return fig


def save_empty_state_svg(
    output_path: str | Path,
    *,
    figsize: tuple[float, float] = _EMPTY_STATE_DEFAULT_FIGSIZE,
    dpi: int = 100,
    message: str = _EMPTY_STATE_DEFAULT_MESSAGE,
) -> None:
    """Persist the standard ATM-EQ empty-state chart as SVG."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig = build_empty_state_figure(figsize=figsize, dpi=dpi, message=message)
    try:
        fig.savefig(
            path,
            format="svg",
            transparent=True,
            dpi=dpi,
            bbox_inches=None,
            pad_inches=0.0,
        )
    finally:
        plt.close(fig)


def _ensure_nonempty_or_empty_svg(output_path: str | Path) -> None:
    save_empty_state_svg(output_path)


def is_data_valid(data: Any, output_path: str | Path | None = None) -> bool:
    df = _to_dataframe(data)
    if df.empty:
        if output_path is not None:
            _ensure_nonempty_or_empty_svg(output_path)
        return False
    return True


def theme_atm_base(ax: plt.Axes, base_size: int = TITLE_SIZE) -> plt.Axes:
    ax.set_facecolor("none")
    fig = ax.figure
    fig.patch.set_alpha(0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", labelsize=base_size)
    ax.title.set_fontsize(TITLE_SIZE)
    ax.title.set_fontweight("bold")
    ax.title.set_fontfamily(get_chart_font_family())
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontfamily(get_chart_font_family())
    return ax


def theme_atm_void(ax: plt.Axes) -> plt.Axes:
    ax.set_facecolor("none")
    fig = ax.figure
    fig.patch.set_alpha(0)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def geom_atm_label(
    ax: plt.Axes, x: float, y: float, text: str, size: float = LABEL_SIZE, **kwargs: Any
) -> None:
    kwargs.setdefault("fontsize", size)
    kwargs.setdefault("fontfamily", get_chart_font_family())
    ax.text(x, y, text, **kwargs)


def geom_atm_shadow_label(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    size: float = LABEL_SIZE,
    bg_colour: str = "white",
    bg_r: float = 0.05,
    **kwargs: Any,
) -> None:
    kwargs.setdefault("fontsize", size)
    kwargs.setdefault("fontfamily", get_chart_font_family())
    txt = ax.text(x, y, text, **kwargs)
    txt.set_path_effects([pe.withStroke(linewidth=max(0.5, bg_r * 20), foreground=bg_colour)])


def scale_y_dinamico(
    valores: Iterable[float],
    expand_top: float = 0.10,
    expand_bottom: float = 0.0,
) -> tuple[float, float]:
    arr = np.asarray(list(valores), dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        max_val = 1.0
    else:
        max_val = float(np.nanmax(arr))
    low = 0.0 - (max_val * expand_bottom)
    high = max_val + (max_val * expand_top)
    return low, high


def add_graph_markers(ax: plt.Axes, graph_id: str) -> plt.Axes:
    ax.text(
        1.0,
        1.0,
        f"<<ATM_EQ_GRAPH_START:id={graph_id}>>",
        alpha=0.0,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=1,
    )
    ax.text(
        0.0,
        0.0,
        f"<<ATM_EQ_GRAPH_END:id={graph_id}>>",
        alpha=0.0,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=1,
    )
    return ax


def apply_grid_theme(ax: plt.Axes, show_grid: bool = True) -> plt.Axes:
    if show_grid:
        ax.grid(True, axis="both", color="#E0E0E0", linewidth=0.4)
    else:
        ax.grid(False)
    return ax


def _coerce_pair(
    values: Sequence[float] | None,
    default: tuple[float, float],
) -> tuple[float, float]:
    """Normaliza uma configuração numérica de dois elementos.

    Retorna `default` quando `values` é `None`. Caso informado, `values`
    precisa ter exatamente dois itens, convertidos para `float`.
    """
    if values is None:
        return default
    if len(values) != 2:
        raise ValueError("Expected exactly two values for pair configuration.")
    return (float(values[0]), float(values[1]))


def _coerce_label_pair(
    values: Sequence[str] | None,
    default: tuple[str, str],
) -> tuple[str, str]:
    """Normaliza uma configuração textual de dois elementos.

    Retorna `default` quando `values` é `None`. Caso informado, `values`
    precisa ter exatamente dois itens, convertidos para `str`.
    """
    if values is None:
        return default
    if len(values) != 2:
        raise ValueError("Expected exactly two labels for pair configuration.")
    return (str(values[0]), str(values[1]))


def plot_two_point_slope_chart(
    *,
    graph_id: str = "slope_chart",
    y_values: Sequence[float],
    point_labels: Sequence[str],
    year_labels: Sequence[str] = ("2019", "2023"),
    figsize: tuple[float, float] = (3.1, 1.58),
    font_family: str = FONT_PADRAO,
    value_color: str = "#725FA9",
    line_color: str = "#333333",
    point_color: str = "#333333",
    year_color: str = "#000000",
    value_fontsize: float = 22.0,
    year_fontsize: float = 15.0,
    value_fontweight: str = "bold",
    year_fontweight: str = "black",
    point_size: float = 110.0,
    line_width: float = 2.0,
    x_padding: float = 0.34,
    y_padding_ratio: float = 0.10,
    min_y_span: float = 2.0,
    label_x_offsets: Sequence[float] | None = (-0.06, 0.0),
    label_y_offsets_ratio: Sequence[float] | None = (0.08, 0.08),
    label_horizontal_alignment: Sequence[str] | None = ("center", "center"),
    x_tick_pad: float = 10.0,
    show_y_axis_labels: bool = False,
) -> plt.Figure | None:
    """Plota um slope chart minimalista com dois pontos no padrão ATM-EQ.

    O helper foi desenhado para comparações pontuais entre dois anos
    (ex.: 2019 e 2023), com foco em linha de ligação, pontos destacados,
    rótulos de valor e eixo Y visualmente neutro.

    Args:
        y_values: Valores numéricos dos dois pontos no eixo Y.
        point_labels: Rótulos de texto exibidos próximos aos pontos.
        year_labels: Rótulos do eixo X para os dois pontos (ex.: "2019", "2023").
        figsize: Tamanho da figura em polegadas (largura, altura).
        font_family: Família tipográfica usada em rótulos e ticks do eixo X.
        value_color: Cor dos rótulos de valor.
        line_color: Cor da linha que conecta os dois pontos.
        point_color: Cor dos marcadores dos pontos.
        year_color: Cor dos rótulos do eixo X (anos).
        value_fontsize: Tamanho da fonte dos rótulos de valor.
        year_fontsize: Tamanho da fonte dos rótulos de ano no eixo X.
        value_fontweight: Peso da fonte dos rótulos de valor, ou seja, "light", "normal", "bold", etc.
        year_fontweight: Peso da fonte dos rótulos de ano.
        point_size: Tamanho dos pontos (escala do `scatter`).
        line_width: Espessura da linha de ligação.
        x_padding: Margem horizontal extra para evitar cortes laterais.
        y_padding_ratio: Fator auxiliar de segurança para microajustes anti-corte.
            Mantido para compatibilidade e aplicado apenas em folgas mínimas.
        min_y_span: Span mínimo do eixo Y para evitar compressão visual.
        label_x_offsets: Deslocamentos horizontais dos rótulos de valor.
        label_y_offsets_ratio: Deslocamentos verticais relativos dos rótulos.
        label_horizontal_alignment: Alinhamento horizontal dos rótulos de valor.
        x_tick_pad: Espaçamento entre eixo X e rótulos de ano.
        show_y_axis_labels: Quando `True`, exibe ticks e rótulos do eixo Y.
            Quando `False` (padrão), oculta ticks e rótulos do eixo Y.

    Returns:
        Figura Matplotlib pronta para exportação, ou `None` quando os dados são
        inválidos (quantidade diferente de dois pontos ou presença de `NaN`).
    """
    if len(y_values) != 2 or len(point_labels) != 2:
        return None

    y = np.asarray(list(y_values), dtype=float)
    if np.isnan(y).any():
        return None

    years = _coerce_label_pair(year_labels, ("2019", "2023"))
    x = np.asarray([0.0, 1.0], dtype=float)

    x_offsets = _coerce_pair(label_x_offsets, (-0.06, 0.0))
    y_offsets_ratio = _coerce_pair(label_y_offsets_ratio, (0.08, 0.08))
    h_align = _coerce_label_pair(label_horizontal_alignment, ("center", "center"))

    min_val = float(np.min(y))
    max_val = float(np.max(y))
    delta = max(0.0, max_val - min_val)

    # Regra principal: eixo ancorado nos próprios dados.
    y_low = min_val
    y_high = max_val

    # Caso degenerado (valores iguais): garante faixa mínima.
    if delta <= 1e-9:
        y_high = y_low + float(min_y_span)

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    ax.plot(
        x,
        y,
        color=line_color,
        linewidth=line_width,
        solid_capstyle="round",
        zorder=2,
    )
    ax.scatter(
        x,
        y,
        s=point_size,
        color=point_color,
        zorder=3,
    )

    ax.set_xlim(-float(x_padding), 1.0 + float(x_padding))
    ax.set_ylim(y_low, y_high)

    # Microajustes apenas quando houver risco real de corte de marker/labels.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax_bbox = ax.get_window_extent(renderer=renderer)
    span = max(1e-6, y_high - y_low)

    marker_radius_pt = math.sqrt(max(0.0, float(point_size)) / math.pi)
    marker_radius_px = marker_radius_pt * (float(fig.dpi) / 72.0)
    data_per_px = span / max(1.0, float(ax_bbox.height))
    marker_margin = (marker_radius_px + 1.0) * data_per_px

    if (min_val - y_low) < marker_margin:
        y_low = min_val - marker_margin
    if (y_high - max_val) < marker_margin:
        y_high = max_val + marker_margin

    max_up_ratio = max(0.0, max(y_offsets_ratio))
    max_down_ratio = max(0.0, -min(y_offsets_ratio))
    for _ in range(2):
        span = max(1e-6, y_high - y_low)
        safety = max(0.01 * span, float(y_padding_ratio) * 0.1 * span)
        changed = False
        if max_up_ratio > 0.0:
            top_anchor = max_val + (max_up_ratio * span)
            if top_anchor >= y_high:
                y_high = top_anchor + safety
                changed = True
        if max_down_ratio > 0.0:
            bottom_anchor = min_val - (max_down_ratio * span)
            if bottom_anchor <= y_low:
                y_low = bottom_anchor - safety
                changed = True
        if not changed:
            break

    ax.set_ylim(y_low, y_high)
    y_total_span = max(1e-6, y_high - y_low)

    for idx, label in enumerate(point_labels):
        ax.text(
            x[idx] + x_offsets[idx],
            y[idx] + (y_offsets_ratio[idx] * y_total_span),
            str(label),
            color=value_color,
            fontsize=value_fontsize,
            fontfamily=font_family,
            fontweight=value_fontweight,
            ha=h_align[idx],
            va="bottom",
            clip_on=False,
            zorder=4,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.tick_params(
        axis="x",
        bottom=False,
        top=False,
        labelbottom=True,
        length=0,
        pad=float(x_tick_pad),
    )
    for tick in ax.get_xticklabels():
        tick.set_fontfamily(font_family)
        tick.set_fontsize(year_fontsize)
        tick.set_fontweight(year_fontweight)
        tick.set_color(year_color)

    if not show_y_axis_labels:
        ax.set_yticks([])
        ax.set_yticklabels([])
        ax.tick_params(axis="y", left=False, right=False, labelleft=False)
    else:
        ax.tick_params(axis="y", left=True, right=False, labelleft=True, labelsize=AXIS_SIZE)
        for tick in ax.get_yticklabels():
            tick.set_fontfamily(font_family)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    add_graph_markers(ax, graph_id)
    return fig


def _fit_left_margin_for_ylabels(
    fig: plt.Figure,
    ax: plt.Axes,
    *,
    target_left_padding_px: float = 8.0,
    min_left_margin: float = 0.05,
    max_left_margin: float = 0.50,
) -> None:
    """Adjust subplot left margin so y tick labels stay visible and near the edge."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = [
        tick for tick in ax.get_yticklabels() if tick.get_visible() and tick.get_text().strip()
    ]
    if not labels:
        return

    min_x = min(label.get_window_extent(renderer=renderer).x0 for label in labels)
    fig_width_px = float(fig.bbox.width)
    if fig_width_px <= 0.0:
        return

    delta_px = float(target_left_padding_px) - float(min_x)
    if abs(delta_px) < 0.5:
        return

    current_left = float(fig.subplotpars.left)
    proposed_left = current_left + (delta_px / fig_width_px)
    bounded_left = max(float(min_left_margin), min(float(max_left_margin), proposed_left))
    if abs(bounded_left - current_left) < 1e-4:
        return
    fig.subplots_adjust(left=bounded_left)


def plot_ideb_linhas(
    data: Any,
    x_col: str = "ano",
    y_col: str = "valor",
    group_col: str = "tipo",
    colors: Optional[Dict[str, str]] = None,
    show_xaxis: bool = True,
    show_yaxis: bool = False,
    show_legend: bool = False,
    axis_text_size: float = AXIS_SIZE,
    label_size: float = LABEL_SIZE,
    line_size: float = 1.0,
    point_size: float = 3.0,
    y_expand: tuple[float, float] = (0.1, 0.1),
    path_if_empty: str | Path | None = None,
) -> Optional[plt.Figure]:
    if not is_data_valid(data, path_if_empty):
        return None

    df = _to_dataframe(data)
    colors = colors or {"Resultado": "#0095DA", "Meta": "#FF8C00"}
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
    df = df.dropna(subset=[x_col, y_col, group_col])
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    for grp in colors.keys():
        subset = df[df[group_col].astype(str) == grp].sort_values(x_col)
        if subset.empty:
            continue
        ax.plot(
            subset[x_col],
            subset[y_col],
            marker="o",
            linewidth=line_size,
            markersize=point_size,
            color=colors[grp],
            label=grp,
        )
        for _, row in subset.iterrows():
            geom_atm_label(
                ax,
                float(row[x_col]),
                float(row[y_col]) + 0.03,
                _format_number_br(float(row[y_col]), 1),
                size=label_size,
                color=colors[grp],
                ha="center",
                va="bottom",
            )

    y_max = max(1.0, float(df[y_col].max()))
    ax.set_ylim(0, y_max * (1 + y_expand[1]))
    ax.tick_params(axis="x", labelsize=axis_text_size, labelbottom=show_xaxis)
    ax.tick_params(axis="y", labelsize=axis_text_size, labelleft=show_yaxis)
    if not show_legend:
        leg = ax.get_legend()
        if leg:
            leg.remove()
    else:
        ax.legend(loc="lower center", ncol=2, frameon=False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    # Preserva o tamanho de fonte de ticks definido pelo chamador, sem forçar TITLE_SIZE.
    theme_atm_base(ax, base_size=axis_text_size)
    return fig


def plot_barras_agrupadas(
    data: Any,
    x_col: str = "ano",
    y_col: str = "valor",
    group_col: str = "categoria",
    colors: Optional[Dict[str, str]] = None,
    show_xaxis: bool = True,
    show_yaxis: bool = True,
    show_x_ticks: bool = True,
    show_y_ticks: bool = True,
    show_legend: bool = True,
    legend_position: str = "bottom",
    legend_bbox: Optional[tuple[float, float]] = None,
    legend_fontsize: Optional[float] = None,
    show_labels: bool = True,
    label_format: str = "integer",
    axis_text_size: float = AXIS_SIZE,
    label_size: float = LABEL_SIZE,
    bar_width: float = 0.6,
    dodge_width: float = 0.55,
    group_spacing: float = 1.0,
    y_expand: tuple[float, float] = (0.0, 0.15),
    shadow_bg_colour: str = "white",
    shadow_bg_r: float = 0.05,
    show_grid: bool = False,
    value_suffix: Optional[str] = None,
    label_formatter: Optional[Callable[[float], str]] = None,
    label_threshold: float = float("-inf"),
    small_label_outside_threshold: float = 5.0,
    small_label_min_width_px: float = 24.0,
    small_label_padding_px: float = 4.0,
    small_label_overlap_shift_px: float = 6.0,
    outside_label_color: Optional[str] = None,
    label_offset: Optional[float] = None,
    label_color: str = "black",
    label_fontfamily: Optional[str] = None,
    label_shadow: bool = True,
    x_tick_rotation: float = 0.0,
    x_tick_ha: str = "center",
    y_floor: Optional[float] = None,
    label_headroom_pct: Optional[float] = None,
    x_axis_text_size: Optional[float] = None,
    y_axis_text_size: Optional[float] = None,
    stacked: bool = False,
    orientation: str = "vertical",
    category_spacing: float = 1.0,
    figsize: tuple[float, float] = (10, 5),
    graph_id: str = "barras_agrupadas",
    ax: Optional[plt.Axes] = None,
    path_if_empty: str | Path | None = None,
    x_tick_pad: Optional[float] = None,
    y_tick_pad: Optional[float] = None,
    category_outer_margin: Optional[float] = None,
    auto_fit_ylabels_left: bool = False,
    ylabels_left_padding_px: float = 8.0,
    min_left_margin: float = 0.05,
    max_left_margin: float = 0.50,
) -> Optional[plt.Figure]:
    """Renderiza barras agrupadas (ou empilhadas) no padrão visual do ATM-EQ.

    Este helper é usado no pipeline de gráficos do ATM-EQ para padronizar
    barras, rótulos, legenda, eixos e marcadores do gráfico. A função aceita
    entrada tabular flexível (`DataFrame`, dict-like, list-like), converte os
    valores para numérico e retorna uma figura Matplotlib pronta para exportação.

    Fluxo de execução:
        1. Valida os dados com `is_data_valid`; opcionalmente gera um SVG
           placeholder via `path_if_empty` e retorna `None` para dados vazios.
        2. Resolve os tamanhos de texto dos eixos e, quando `stacked=True`,
           delega a renderização para `plot_barras_empilhadas` com formatter de
           rótulo adaptado.
        3. Converte os dados com `_to_dataframe`, normaliza `y_col` para
           numérico e monta as barras por categoria (`group_col`).
        4. Adiciona rótulos com `geom_atm_label` ou `geom_atm_shadow_label`,
           configura ticks/legenda e aplica limites de eixo.
        5. Aplica helpers visuais compartilhados (`theme_atm_base`,
           `apply_grid_theme`, `add_graph_markers` e, opcionalmente,
           `_fit_left_margin_for_ylabels`).

    Args:
        data (Any): Dados tabulares contendo ao menos `x_col`, `y_col` e
            `group_col`. Entradas aceitas são convertidas por `_to_dataframe`.
        x_col (str): Nome da coluna usada nas categorias do eixo X
            (padrão: `"ano"`).
        y_col (str): Nome da coluna usada nos valores das barras
            (padrão: `"valor"`).
        group_col (str): Nome da coluna usada para separar séries/categorias
            dentro de cada grupo do eixo X (padrão: `"categoria"`).
        colors (Optional[Dict[str, str]]): Mapeamento `{grupo: cor_hex}`. Se
            omitido, o helper usa cores padrão internas.
        show_xaxis (bool): Se `True`, mantém os rótulos do eixo X visíveis.
        show_yaxis (bool): Se `True`, mantém os rótulos do eixo Y visíveis.
        show_x_ticks (bool): Se `True`, desenha os ticks do eixo X.
        show_y_ticks (bool): Se `True`, desenha os ticks do eixo Y.
        show_legend (bool): Se `True`, renderiza a legenda.
        legend_position (str): Posição predefinida da legenda. Valores
            suportados: `"bottom"`, `"top"`, `"right"`, `"left"`.
        legend_bbox (Optional[tuple[float, float]]): `bbox_to_anchor` explícito
            para posicionamento da legenda. Se `None`, usa padrão conforme
            `legend_position`.
        legend_fontsize (Optional[float]): Tamanho do texto da legenda. Se
            `None`, usa padrão do Matplotlib.
        show_labels (bool): Se `True`, renderiza rótulos de valor nas barras.
        label_format (str): Formato padrão de rótulo quando `label_formatter`
            não é informado. Valores suportados: `"integer"`, `"decimal"`,
            `"percent"`.
        axis_text_size (float): Tamanho base dos textos de tick usado nos
            helpers de tema.
        label_size (float): Tamanho da fonte dos rótulos de valor.
        bar_width (float): Largura total disponível para as barras em cada
            posição de X.
        dodge_width (float): Largura usada para distribuir categorias dentro de
            cada grupo.
        group_spacing (float): Fator de espaçamento horizontal entre grupos no
            eixo X. Deve ser maior que `0`.
        y_expand (tuple[float, float]): Tupla de expansão de eixo
            `(expand_base, expand_topo)`. No modo agrupado, apenas o valor de
            topo é aplicado.
        shadow_bg_colour (str): Cor do contorno/sombra usada por
            `geom_atm_shadow_label`.
        shadow_bg_r (float): Fator do traço de sombra passado para
            `geom_atm_shadow_label`.
        show_grid (bool): Se `True`, aplica estilo de grade via
            `apply_grid_theme`.
        value_suffix (Optional[str]): Sufixo opcional anexado ao texto do
            rótulo (por exemplo, `"%"` ou `" mi"`).
        label_formatter (Optional[Callable[[float], str]]): Formatter
            customizado para os valores dos rótulos. Sobrescreve
            `label_format`.
        label_threshold (float): Valor mínimo necessário para exibir rótulo.
        small_label_outside_threshold (float): Valor abaixo do qual, no modo
            empilhado horizontal, o rótulo é movido para fora do segmento.
        small_label_min_width_px (float): Largura mínima do segmento (em px)
            para manter rótulo interno no modo empilhado horizontal.
        small_label_padding_px (float): Espaçamento em px entre o fim da barra
            e o rótulo externo (modo empilhado horizontal).
        small_label_overlap_shift_px (float): Deslocamento incremental em px
            usado para evitar sobreposição entre rótulos externos.
        outside_label_color (Optional[str]): Cor do texto para rótulos
            externos no modo empilhado horizontal. Quando `None`, usa cor
            automaticamente baseada no contraste.
        label_offset (Optional[float]): Offset vertical acima de cada barra. Se
            `None`, é calculado automaticamente com base na faixa de valores.
        label_color (str): Cor do texto dos rótulos.
        label_fontfamily (Optional[str]): Família de fonte dos rótulos. Se
            `None`, usa a fonte padrão dos gráficos.
        label_shadow (bool): Se `True`, desenha rótulos com contorno/sombra
            para melhorar legibilidade.
        x_tick_rotation (float): Ângulo de rotação (graus) dos rótulos do eixo
            X.
        x_tick_ha (str): Alinhamento horizontal dos rótulos do eixo X
            (`"center"`, `"left"`, `"right"`, etc., conforme Matplotlib).
        y_floor (Optional[float]): Piso opcional para o cálculo do limite
            superior do eixo Y antes da expansão.
        label_headroom_pct (Optional[float]): Percentual extra de headroom para
            garantir visibilidade dos rótulos acima das barras.
        x_axis_text_size (Optional[float]): Tamanho explícito dos rótulos de
            tick do eixo X. Se `None`, usa `axis_text_size`.
        y_axis_text_size (Optional[float]): Tamanho explícito dos rótulos de
            tick do eixo Y. Se `None`, usa `axis_text_size`.
        stacked (bool): Se `True`, delega a renderização para
            `plot_barras_empilhadas` (barras empilhadas) em vez de barras
            agrupadas.
        orientation (str): Orientação das barras repassada ao modo empilhado
            (`"vertical"` ou `"horizontal"` na semântica do helper).
        category_spacing (float): Espaçamento repassado ao modo empilhado. Deve
            ser maior que `0` quando `stacked=True`.
        figsize (tuple[float, float]): Tamanho solicitado da figura em
            polegadas. É aplicado tanto no modo agrupado quanto no empilhado.
        graph_id (str): Identificador do gráfico usado por `add_graph_markers`.
        ax (Optional[plt.Axes]): Eixo de destino no modo empilhado. No modo
            agrupado, a implementação atual cria um novo eixo.
        path_if_empty (str | Path | None): Caminho opcional usado por
            `is_data_valid` para salvar um SVG placeholder quando os dados estão
            vazios.
        x_tick_pad (Optional[float]): Padding dos ticks do eixo X (em pontos).
        y_tick_pad (Optional[float]): Padding dos ticks do eixo Y (em pontos).
        category_outer_margin (Optional[float]): Margem externa adicional no
            eixo X aplicada com `ax.margins(x=...)`, quando informada.
        auto_fit_ylabels_left (bool): Se `True`, ajusta automaticamente a
            margem esquerda para evitar corte de rótulos no eixo Y.
        ylabels_left_padding_px (float): Padding alvo, em pixels, usado por
            `_fit_left_margin_for_ylabels`.
        min_left_margin (float): Margem esquerda mínima permitida no auto-fit.
        max_left_margin (float): Margem esquerda máxima permitida no auto-fit.

    Returns:
        Optional[plt.Figure]: `matplotlib.figure.Figure` configurada quando os
        dados são válidos; caso contrário, `None`. O retorno é `None` quando os
        dados são vazios/inválidos segundo `is_data_valid` (e um SVG placeholder
        pode ser gerado quando `path_if_empty` é informado).

    Raises:
        KeyError: Se colunas obrigatórias (`x_col`, `y_col`, `group_col`)
            estiverem ausentes na entrada.
        ValueError: Se `group_spacing <= 0`. Também pode ser propagado por
            `plot_barras_empilhadas` (por exemplo, `category_spacing <= 0`
            quando `stacked=True`).

    Notes:
        - Esta função depende de helpers visuais do projeto para manter o
          padrão do ATM-EQ (fonte, fundo transparente, grade, marcadores e
          renderização de rótulos).
        - Os parâmetros `orientation` e `category_spacing` só têm efeito no
          modo empilhado (`stacked=True`).
        - No modo agrupado, o helper instancia internamente `Figure/Axes` e
          aplica o `figsize` informado.
        - O parâmetro `ax` só é respeitado no modo empilhado.
    """
    if not is_data_valid(data, path_if_empty):
        return None

    x_tick_size = float(x_axis_text_size) if x_axis_text_size is not None else float(axis_text_size)
    y_tick_size = float(y_axis_text_size) if y_axis_text_size is not None else float(axis_text_size)

    if stacked:

        def _stacked_label_formatter(value: float) -> str:
            base_label = (
                label_formatter(float(value))
                if label_formatter is not None
                else _format_label(float(value), label_format, 1)
            )
            if value_suffix:
                return f"{base_label}{value_suffix}"
            return base_label

        return plot_barras_empilhadas(
            data=data,
            x_col=x_col,
            y_col=y_col,
            group_col=group_col,
            colors=colors,
            show_labels=show_labels,
            label_formatter=_stacked_label_formatter,
            label_threshold=label_threshold,
            small_label_outside_threshold=small_label_outside_threshold,
            small_label_min_width_px=small_label_min_width_px,
            small_label_padding_px=small_label_padding_px,
            small_label_overlap_shift_px=small_label_overlap_shift_px,
            outside_label_color=outside_label_color,
            show_yaxis=show_yaxis,
            show_xaxis=show_xaxis,
            show_y_ticks=show_y_ticks,
            show_x_ticks=show_x_ticks,
            show_legend=show_legend,
            legend_position=legend_position,
            legend_bbox=legend_bbox,
            legend_fontsize=legend_fontsize,
            axis_text_size=axis_text_size,
            x_axis_text_size=x_tick_size,
            y_axis_text_size=y_tick_size,
            x_tick_pad=x_tick_pad,
            y_tick_pad=y_tick_pad,
            label_size=label_size,
            label_color=label_color,
            bar_width=bar_width,
            category_spacing=category_spacing,
            category_outer_margin=category_outer_margin,
            auto_fit_ylabels_left=auto_fit_ylabels_left,
            ylabels_left_padding_px=ylabels_left_padding_px,
            min_left_margin=min_left_margin,
            max_left_margin=max_left_margin,
            y_expand=y_expand,
            shadow_bg_colour=shadow_bg_colour,
            show_grid=show_grid,
            shadow_bg_r=shadow_bg_r,
            label_shadow=label_shadow,
            label_fontfamily=label_fontfamily,
            orientation=orientation,
            figsize=figsize,
            graph_id=graph_id,
            path_if_empty=path_if_empty,
            ax=ax,
        )

    df = _to_dataframe(data)
    colors = colors or {"Categoria1": "#808080", "Categoria2": "#0095DA"}
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
    df = df.dropna(subset=[x_col, group_col])

    x_vals = list(dict.fromkeys(df[x_col].tolist()))
    groups = [g for g in colors.keys() if g in df[group_col].astype(str).unique()]
    if not groups:
        groups = list(dict.fromkeys(df[group_col].astype(str).tolist()))
    spacing = float(group_spacing)
    if spacing <= 0:
        raise ValueError("group_spacing must be greater than 0.")

    x_base = np.arange(len(x_vals), dtype=float)
    x_center = (len(x_vals) - 1) / 2 if x_vals else 0.0
    # Comprime/expande os centros dos grupos em torno do ponto médio para que
    # o group_spacing não desloque o gráfico para um lado.
    x_idx = (x_base - x_center) * spacing + x_center
    step = dodge_width / max(1, len(groups))

    fig, ax = plt.subplots(figsize=figsize)
    max_val = float(np.nanmax(df[y_col])) if not df.empty else 0.0
    computed_offset = float(label_offset) if label_offset is not None else max(0.2, max_val * 0.01)
    max_label_anchor: Optional[float] = None
    for i, grp in enumerate(groups):
        sub = df[df[group_col].astype(str) == grp]
        vals = [float(sub[sub[x_col] == x][y_col].sum()) for x in x_vals]
        offset = (i - (len(groups) - 1) / 2) * step
        bars = ax.bar(
            x_idx + offset,
            vals,
            width=bar_width / max(1, len(groups)),
            color=colors.get(grp, "#0095DA"),
            label=grp,
        )
        if show_labels:
            for bar, val in zip(bars, vals):
                if float(val) < float(label_threshold):
                    continue
                label = (
                    label_formatter(float(val))
                    if label_formatter is not None
                    else _format_label(float(val), label_format, 1)
                )
                if value_suffix:
                    label = f"{label}{value_suffix}"
                label_x = bar.get_x() + bar.get_width() / 2
                label_y = bar.get_height() + computed_offset
                max_label_anchor = (
                    float(label_y)
                    if max_label_anchor is None
                    else max(float(max_label_anchor), float(label_y))
                )
                if label_shadow:
                    geom_atm_shadow_label(
                        ax,
                        label_x,
                        label_y,
                        label,
                        size=label_size,
                        bg_colour=shadow_bg_colour,
                        bg_r=shadow_bg_r,
                        color=label_color,
                        fontfamily=label_fontfamily,
                        ha="center",
                        va="bottom",
                    )
                else:
                    geom_atm_label(
                        ax,
                        label_x,
                        label_y,
                        label,
                        size=label_size,
                        color=label_color,
                        fontfamily=label_fontfamily,
                        ha="center",
                        va="bottom",
                    )

    ax.set_xticks(x_idx)
    ax.set_xticklabels(x_vals, fontsize=x_tick_size)
    # Mantém a largura percebida das barras estável quando group_spacing < 1,
    # preservando ao menos a amplitude padrão do eixo X (spacing == 1).
    if x_vals:
        half_span_default = ((len(x_vals) - 1) / 2) + 0.5
        half_span_scaled = (((len(x_vals) - 1) * spacing) / 2) + 0.5
        half_span = max(half_span_default, half_span_scaled)
        ax.set_xlim(x_center - half_span, x_center + half_span)
    for tick in ax.get_xticklabels():
        tick.set_rotation(x_tick_rotation)
        tick.set_ha(x_tick_ha)
    x_tick_kwargs: Dict[str, Any] = {
        "axis": "x",
        "labelsize": x_tick_size,
        "labelbottom": show_xaxis,
        "bottom": show_xaxis and show_x_ticks,
    }
    y_tick_kwargs: Dict[str, Any] = {
        "axis": "y",
        "labelsize": y_tick_size,
        "labelleft": show_yaxis,
        "left": show_y_ticks,
    }
    if x_tick_pad is not None:
        x_tick_kwargs["pad"] = float(x_tick_pad)
    if y_tick_pad is not None:
        y_tick_kwargs["pad"] = float(y_tick_pad)
    ax.tick_params(**x_tick_kwargs)
    ax.tick_params(**y_tick_kwargs)
    if not show_y_ticks:
        ax.set_yticks([])
    y_max = max(1.0, float(df[y_col].max()))
    base_max = max(y_max, float(y_floor)) if y_floor is not None else y_max
    y_top = base_max * (1 + y_expand[1])
    if show_labels and max_label_anchor is not None:
        label_headroom = (
            base_max * max(0.0, float(label_headroom_pct))
            if label_headroom_pct is not None
            else 0.0
        )
        # Converte altura de texto (em pontos) para unidades de dados para que
        # rótulos próximos ao topo permaneçam visíveis mesmo em canvases baixos.
        fig_height_px = float(fig.get_size_inches()[1] * fig.get_dpi())
        axis_height_px = max(1.0, fig_height_px * float(ax.get_position().height))
        label_height_px = max(1.0, float(label_size)) * (float(fig.get_dpi()) / 72.0)
        # Mantém uma pequena folga de segurança, pois o chamador pode ajustar
        # subplots após o retorno (reduzindo a altura útil do eixo).
        label_text_headroom_data = (
            ((label_height_px + 2.0) / axis_height_px)
            * max(base_max, float(max_label_anchor), 1.0)
            * 1.25
        )
        y_top = max(
            y_top,
            float(max_label_anchor) + max(label_headroom, label_text_headroom_data),
        )
    ax.set_ylim(0, y_top)
    if show_legend:
        loc_map = {
            "bottom": "lower center",
            "top": "upper center",
            "right": "center left",
            "left": "center right",
        }
        bbox = legend_bbox
        if bbox is None and legend_position == "right":
            bbox = (1.02, 0.5)
        legend = ax.legend(
            loc=loc_map.get(legend_position, "lower center"),
            bbox_to_anchor=bbox,
            ncol=1 if legend_position in {"left", "right"} else max(1, len(groups)),
            frameon=False,
            fontsize=legend_fontsize,
        )
        for text in legend.get_texts():
            text.set_fontfamily(get_chart_font_family())
            if legend_fontsize is not None:
                text.set_fontsize(legend_fontsize)
    # Preserva o tamanho de fonte de ticks definido pelo chamador, sem forçar TITLE_SIZE.
    theme_atm_base(ax, base_size=axis_text_size)
    # O theme_atm_base pode uniformizar os eixos; reaplica tamanhos explícitos.
    ax.tick_params(axis="x", labelsize=x_tick_size)
    ax.tick_params(axis="y", labelsize=y_tick_size)
    if x_tick_pad is not None:
        ax.tick_params(axis="x", pad=float(x_tick_pad))
    if y_tick_pad is not None:
        ax.tick_params(axis="y", pad=float(y_tick_pad))
    if category_outer_margin is not None:
        margin = max(0.0, float(category_outer_margin))
        ax.margins(x=margin)
    for tick in ax.get_xticklabels():
        tick.set_fontsize(x_tick_size)
    for tick in ax.get_yticklabels():
        tick.set_fontsize(y_tick_size)
    if auto_fit_ylabels_left and show_yaxis:
        _fit_left_margin_for_ylabels(
            fig,
            ax,
            target_left_padding_px=ylabels_left_padding_px,
            min_left_margin=min_left_margin,
            max_left_margin=max_left_margin,
        )
    apply_grid_theme(ax, show_grid)
    add_graph_markers(ax, graph_id)
    return fig


def plot_barras_empilhadas(
    data: Any,
    x_col: str = "ano",
    y_col: str = "valor",
    group_col: str = "categoria",
    colors: Optional[Dict[str, str]] = None,
    show_labels: bool = True,
    label_formatter: Optional[Callable[[float], str]] = None,
    label_threshold: float = 5.0,
    small_label_outside_threshold: float = 5.0,
    small_label_min_width_px: float = 24.0,
    small_label_padding_px: float = 4.0,
    small_label_overlap_shift_px: float = 6.0,
    outside_label_color: Optional[str] = None,
    show_yaxis: bool = True,
    show_legend: bool = True,
    legend_position: str = "bottom",
    axis_text_size: float = 12,
    label_size: float = 6.5,
    label_color: str = "black",
    bar_width: float = 0.7,
    category_spacing: float = 1.0,
    y_expand: tuple[float, float] = (0.0, 0.15),
    shadow_bg_colour: str = "white",
    show_grid: bool = False,
    shadow_bg_r: float = 0.02,
    label_shadow: bool = True,
    label_fontfamily: Optional[str] = None,
    orientation: str = "vertical",
    figsize: tuple[float, float] = (10, 5),
    graph_id: str = "barras_empilhadas",
    show_xaxis: bool = True,
    show_x_ticks: bool = True,
    show_y_ticks: bool = True,
    legend_bbox: Optional[tuple[float, float]] = None,
    legend_fontsize: Optional[float] = None,
    x_axis_text_size: Optional[float] = None,
    y_axis_text_size: Optional[float] = None,
    path_if_empty: str | Path | None = None,
    ax: Optional[plt.Axes] = None,
    x_tick_pad: Optional[float] = None,
    y_tick_pad: Optional[float] = None,
    category_outer_margin: Optional[float] = None,
    auto_fit_ylabels_left: bool = False,
    ylabels_left_padding_px: float = 8.0,
    min_left_margin: float = 0.05,
    max_left_margin: float = 0.50,
) -> Optional[plt.Figure]:
    if not is_data_valid(data, path_if_empty):
        return None
    df = _to_dataframe(data)
    colors = colors or {"Categoria1": "#0095DA", "Categoria2": "#FF8C00", "Categoria3": "#808080"}
    formatter = label_formatter or (lambda x: _format_number_br(x, 1))
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
    df = df.dropna(subset=[x_col, group_col])
    x_vals = list(dict.fromkeys(df[x_col].tolist()))
    groups = [g for g in colors.keys() if g in df[group_col].astype(str).unique()] or list(
        dict.fromkeys(df[group_col].astype(str).tolist())
    )
    x_tick_size = float(x_axis_text_size) if x_axis_text_size is not None else float(axis_text_size)
    y_tick_size = float(y_axis_text_size) if y_axis_text_size is not None else float(axis_text_size)
    spacing = float(category_spacing)
    if spacing <= 0:
        raise ValueError("category_spacing must be greater than 0.")
    x_idx = np.arange(len(x_vals), dtype=float) * spacing

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    bottom = np.zeros(len(x_vals), dtype=float)
    label_entries: list[Dict[str, Any]] = []
    for grp in groups:
        vals = np.array(
            [
                float(df[(df[x_col] == x) & (df[group_col].astype(str) == grp)][y_col].sum())
                for x in x_vals
            ],
            dtype=float,
        )
        if orientation == "horizontal":
            bars = ax.barh(
                x_idx,
                vals,
                left=bottom,
                height=bar_width,
                color=colors.get(grp, "#0095DA"),
                label=grp,
            )
        else:
            bars = ax.bar(
                x_idx,
                vals,
                bottom=bottom,
                width=bar_width,
                color=colors.get(grp, "#0095DA"),
                label=grp,
            )
        if show_labels:
            for i, bar in enumerate(bars):
                value = float(vals[i])
                if value <= float(label_threshold):
                    continue
                label_text = str(formatter(value)).strip()
                if not label_text:
                    continue
                segment_start = float(bottom[i])
                segment_end = segment_start + value
                if orientation == "horizontal":
                    x_text = segment_start + (value / 2.0)
                    y_text = float(bar.get_y() + bar.get_height() / 2.0)
                else:
                    x_text = float(bar.get_x() + bar.get_width() / 2.0)
                    y_text = segment_start + (value / 2.0)
                label_entries.append(
                    {
                        "text": label_text,
                        "value": value,
                        "x": x_text,
                        "y": y_text,
                        "segment_start": segment_start,
                        "segment_end": segment_end,
                    }
                )
        bottom += vals

    ymax = max(1.0, float(bottom.max()))
    if orientation == "horizontal":
        ax.set_yticks(x_idx)
        if show_yaxis:
            ax.set_yticklabels(x_vals, fontsize=y_tick_size)
        else:
            ax.set_yticklabels([])
        y_tick_kwargs: Dict[str, Any] = {
            "axis": "y",
            "labelsize": y_tick_size,
            "labelleft": show_yaxis,
            "left": show_y_ticks,
        }
        x_tick_kwargs: Dict[str, Any] = {
            "axis": "x",
            "labelsize": x_tick_size,
            "labelbottom": show_xaxis,
            "bottom": show_x_ticks,
        }
        if y_tick_pad is not None:
            y_tick_kwargs["pad"] = float(y_tick_pad)
        if x_tick_pad is not None:
            x_tick_kwargs["pad"] = float(x_tick_pad)
        ax.tick_params(**y_tick_kwargs)
        ax.tick_params(**x_tick_kwargs)
        if category_outer_margin is not None:
            ax.margins(y=max(0.0, float(category_outer_margin)))
        ax.set_xlim(0, ymax * (1 + y_expand[1]))
    else:
        ax.set_xticks(x_idx)
        ax.set_xticklabels(x_vals, fontsize=x_tick_size)
        x_tick_kwargs = {
            "axis": "x",
            "labelsize": x_tick_size,
            "labelbottom": show_xaxis,
            "bottom": show_x_ticks,
        }
        y_tick_kwargs = {
            "axis": "y",
            "labelsize": y_tick_size,
            "labelleft": show_yaxis,
            "left": show_y_ticks,
        }
        if x_tick_pad is not None:
            x_tick_kwargs["pad"] = float(x_tick_pad)
        if y_tick_pad is not None:
            y_tick_kwargs["pad"] = float(y_tick_pad)
        ax.tick_params(**x_tick_kwargs)
        ax.tick_params(**y_tick_kwargs)
        if category_outer_margin is not None:
            ax.margins(x=max(0.0, float(category_outer_margin)))
        ax.set_ylim(0, ymax * (1 + y_expand[1]))
    if show_legend:
        loc_map = {
            "bottom": "lower center",
            "top": "upper center",
            "right": "center left",
            "left": "center right",
        }
        bbox = legend_bbox
        if bbox is None and legend_position == "right":
            bbox = (1.02, 0.5)
        legend = ax.legend(
            loc=loc_map.get(legend_position, "lower center"),
            bbox_to_anchor=bbox,
            frameon=False,
            ncol=1 if legend_position in {"left", "right"} else max(1, len(groups)),
            fontsize=legend_fontsize if legend_fontsize is not None else axis_text_size,
        )
        for text in legend.get_texts():
            text.set_fontfamily(get_chart_font_family())
            if legend_fontsize is not None:
                text.set_fontsize(legend_fontsize)
            else:
                text.set_fontsize(axis_text_size)
    # Mantém axis_text_size efetivo após a aplicação do tema.
    theme_atm_base(ax, base_size=axis_text_size)
    ax.tick_params(axis="x", labelsize=x_tick_size)
    ax.tick_params(axis="y", labelsize=y_tick_size)
    if x_tick_pad is not None:
        ax.tick_params(axis="x", pad=float(x_tick_pad))
    if y_tick_pad is not None:
        ax.tick_params(axis="y", pad=float(y_tick_pad))
    for tick in ax.get_xticklabels():
        tick.set_fontsize(x_tick_size)
    for tick in ax.get_yticklabels():
        tick.set_fontsize(y_tick_size)
    if orientation == "horizontal" and auto_fit_ylabels_left and show_yaxis:
        _fit_left_margin_for_ylabels(
            fig,
            ax,
            target_left_padding_px=ylabels_left_padding_px,
            min_left_margin=min_left_margin,
            max_left_margin=max_left_margin,
        )
    apply_grid_theme(ax, show_grid)

    def _draw_value_label(
        x_pos: float,
        y_pos: float,
        text: str,
        *,
        color: str,
        ha: str,
        va: str,
        clip_on: bool = True,
    ) -> None:
        if label_shadow:
            geom_atm_shadow_label(
                ax,
                x_pos,
                y_pos,
                text,
                size=label_size,
                bg_colour=shadow_bg_colour,
                bg_r=shadow_bg_r,
                color=color,
                fontfamily=label_fontfamily,
                ha=ha,
                va=va,
                clip_on=clip_on,
            )
        else:
            geom_atm_label(
                ax,
                x_pos,
                y_pos,
                text,
                size=label_size,
                color=color,
                fontfamily=label_fontfamily,
                ha=ha,
                va=va,
                clip_on=clip_on,
            )

    if show_labels and label_entries:
        if orientation == "horizontal":
            resolved_outside_color = outside_label_color
            if resolved_outside_color is None:
                normalized = str(label_color).strip().lower()
                if normalized in {"white", "#fff", "#ffffff", "#ffffffff", "w"}:
                    resolved_outside_color = "#3C3C3C"
                else:
                    resolved_outside_color = label_color

            inside_color = "white"
            right_guard_px = 1.5

            def _measure_label_bbox(
                x_pos: float,
                y_pos: float,
                text: str,
                *,
                ha: str,
                renderer: Any,
            ) -> Bbox:
                temp = ax.text(
                    x_pos,
                    y_pos,
                    text,
                    fontsize=label_size,
                    color=resolved_outside_color,
                    fontfamily=label_fontfamily or get_chart_font_family(),
                    ha=ha,
                    va="center",
                    alpha=0.0,
                    clip_on=False,
                )
                try:
                    return temp.get_window_extent(renderer=renderer).expanded(1.02, 1.12)
                finally:
                    temp.remove()

            def _build_horizontal_label_layout() -> tuple[list[Dict[str, Any]], float, float]:
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
                ax_bbox = ax.get_window_extent(renderer=renderer)
                x_min, x_max = ax.get_xlim()
                x_span = max(1.0, float(x_max) - float(x_min))
                axis_width_px = max(1.0, float(ax_bbox.width))
                data_per_px = x_span / axis_width_px
                offset_data = max(0.0, float(small_label_padding_px)) * data_per_px
                overlap_step_data = max(1.0, float(small_label_overlap_shift_px)) * data_per_px
                min_inside_width_px = max(0.0, float(small_label_min_width_px))
                small_value_threshold = float(small_label_outside_threshold)

                layout: list[Dict[str, Any]] = []
                outside_bboxes: list[Bbox] = []
                max_overflow_px = 0.0

                ordered_entries = sorted(
                    label_entries,
                    key=lambda entry: (float(entry["y"]), float(entry["segment_end"])),
                )
                for entry in ordered_entries:
                    x0_px = ax.transData.transform(
                        (float(entry["segment_start"]), float(entry["y"]))
                    )[0]
                    x1_px = ax.transData.transform(
                        (float(entry["segment_end"]), float(entry["y"]))
                    )[0]
                    segment_width_px = abs(float(x1_px) - float(x0_px))
                    render_outside = (
                        float(entry["value"]) <= small_value_threshold
                        or segment_width_px < min_inside_width_px
                    )

                    if not render_outside:
                        layout.append(
                            {
                                "x": float(entry["x"]),
                                "y": float(entry["y"]),
                                "text": str(entry["text"]),
                                "color": inside_color,
                                "ha": "center",
                                "clip_on": True,
                            }
                        )
                        continue

                    x_text = float(entry["segment_end"]) + offset_data
                    y_text = float(entry["y"])
                    bbox = _measure_label_bbox(
                        x_text,
                        y_text,
                        str(entry["text"]),
                        ha="left",
                        renderer=renderer,
                    )
                    for _ in range(120):
                        if any(bbox.overlaps(prev) for prev in outside_bboxes):
                            x_text += overlap_step_data
                            bbox = _measure_label_bbox(
                                x_text,
                                y_text,
                                str(entry["text"]),
                                ha="left",
                                renderer=renderer,
                            )
                            continue
                        break

                    overflow_px = max(0.0, float(bbox.x1) - (float(ax_bbox.x1) - right_guard_px))
                    max_overflow_px = max(max_overflow_px, overflow_px)
                    outside_bboxes.append(bbox)
                    layout.append(
                        {
                            "x": x_text,
                            "y": y_text,
                            "text": str(entry["text"]),
                            "color": str(resolved_outside_color),
                            "ha": "left",
                            "clip_on": False,
                        }
                    )

                return layout, max_overflow_px, data_per_px

            final_layout: list[Dict[str, Any]] = []
            for _ in range(3):
                final_layout, overflow_px, data_per_px = _build_horizontal_label_layout()
                if overflow_px <= 0.5:
                    break
                x_min, x_max = ax.get_xlim()
                extra_data = (overflow_px + max(1.0, float(small_label_padding_px))) * data_per_px
                ax.set_xlim(float(x_min), float(x_max) + extra_data)

            for item in final_layout:
                _draw_value_label(
                    float(item["x"]),
                    float(item["y"]),
                    str(item["text"]),
                    color=str(item["color"]),
                    ha=str(item["ha"]),
                    va="center",
                    clip_on=bool(item["clip_on"]),
                )
        else:
            for entry in label_entries:
                _draw_value_label(
                    float(entry["x"]),
                    float(entry["y"]),
                    str(entry["text"]),
                    color=label_color,
                    ha="center",
                    va="center",
                )

    add_graph_markers(ax, graph_id)
    return fig


def plot_barras_empilhadas_com_media(
    *args: Any,
    mean_value: float = math.nan,
    mean_label: Optional[str] = None,
    mean_line_color: str = "black",
    mean_line_type: str = "dashed",
    mean_line_width: float = 0.8,
    mean_label_hjust: float = -0.1,
    mean_label_vjust: float = -0.5,
    mean_label_size: float = 4.5,
    mean_label_color: str = "black",
    **kwargs: Any,
) -> Optional[plt.Figure]:
    fig = plot_barras_empilhadas(*args, **kwargs)
    if fig is None:
        return None
    ax = fig.axes[0]
    if not math.isnan(mean_value):
        ax.axhline(
            mean_value, color=mean_line_color, linewidth=mean_line_width, linestyle=mean_line_type
        )
        if mean_label:
            ax.text(
                0.99 + mean_label_hjust * 0.01,
                mean_value + mean_label_vjust * 0.01 * max(1.0, ax.get_ylim()[1]),
                mean_label,
                transform=ax.get_yaxis_transform(),
                ha="right",
                va="bottom",
                fontsize=mean_label_size,
                color=mean_label_color,
            )
    return fig


def plot_barras_simples(
    data: Any,
    x_col: str = "ano",
    y_col: str = "valor",
    colors: Optional[Sequence[str] | Dict[str, str]] = None,
    show_labels: bool = True,
    label_format: str = "decimal",
    label_decimal_places: int = 0,
    label_formatter: Optional[Callable[[float], str]] = None,
    show_yaxis: bool = True,
    show_xaxis: bool = True,
    show_y_ticks: bool = True,
    show_x_ticks: bool = True,
    y_label: Optional[str] = None,
    axis_text_size: float = AXIS_SIZE,
    axis_text_x_size: float = AXIS_SIZE,
    axis_text_y_size: float = AXIS_SIZE,
    label_size: float = LABEL_SIZE,
    label_vjust: float = -0.5,
    label_color: str = "black",
    bar_width: float = 0.7,
    category_spacing: float = 1.0,
    show_grid: bool = False,
    y_expand: tuple[float, float] = (0.0, 0.1),
    smart_labels: bool = True,
    smart_threshold: float = 0.92,
    y_scale_mode: str = "fixed_100",
    ticklabel_format_style: Optional[str] = None,
    path_if_empty: str | Path | None = None,
    orientation: str = "vertical",
    label_offset: float = 0.0,
    xlim: tuple[float, float] | None = None,
    empty_value_message: Optional[str] = None,
    empty_value_message_xy: tuple[float, float] = (0.5, 0.52),
    empty_value_message_size: float = 10.0,
    empty_value_message_color: str = "#3C3C3C",
) -> Optional[plt.Figure]:
    """Renderiza gráfico de barras simples (vertical ou horizontal) no padrão ATM-EQ.

    Parâmetros:
        data: Estrutura tabular de entrada (DataFrame, lista de dicts, etc.).
        x_col: Nome da coluna categórica usada no eixo X (ou eixo Y no modo horizontal).
        y_col: Nome da coluna numérica usada como valor das barras.
        colors: Cores das barras. Aceita lista/tupla (por posição) ou dict
            mapeando categoria (`x_col`) para cor.
        show_labels: Define se os rótulos de valor devem ser desenhados nas barras.
        label_format: Formato padrão dos rótulos quando `label_formatter` não é informado.
        label_decimal_places: Casas decimais usadas com `label_format`.
        label_formatter: Função customizada para formatar o texto do rótulo.
            Quando informado, sobrescreve `label_format` e `label_decimal_places`.
        show_yaxis: Exibe ou oculta os rótulos do eixo Y.
        show_xaxis: Exibe ou oculta os rótulos do eixo X.
        show_y_ticks: Exibe ou oculta as marcas (ticks) do eixo Y.
        show_x_ticks: Exibe ou oculta as marcas (ticks) do eixo X.
        y_label: Texto do rótulo do eixo de valores
            (`ylabel` no vertical, `xlabel` no horizontal).
        axis_text_size: Tamanho base de fonte para textos dos eixos.
        axis_text_x_size: Tamanho específico dos textos do eixo X
            (sobrescreve `axis_text_size` para esse eixo).
        axis_text_y_size: Tamanho específico dos textos do eixo Y
            (sobrescreve `axis_text_size` para esse eixo).
        label_size: Tamanho da fonte dos rótulos das barras.
        label_vjust: Parâmetro legado mantido por compatibilidade; não é aplicado
            diretamente na posição dos rótulos nesta implementação.
        label_color: Cor dos rótulos das barras quando posicionados fora da barra.
        bar_width: Espessura da barra (`width` no vertical e `height` no horizontal).
            Não controla distância entre categorias.
        category_spacing: Fator de espaçamento entre categorias no eixo categórico.
            Atua apenas na posição dos centros (`np.arange(...) * category_spacing`).
            `1.0` mantém o comportamento original; maior que `1.0` afasta as barras;
            entre `0` e `1.0` aproxima.
        show_grid: Ativa ou desativa a grade de fundo.
        y_expand: Tupla de expansão da escala do eixo de valores.
            Nesta função, usa-se apenas `y_expand[1]` para expansão superior.
        smart_labels: Ativa lógica de contraste/posicionamento interno para rótulos
            em barras altas.
        smart_threshold: Percentual do valor máximo que define quando o rótulo é
            considerado "alto" para a regra de `smart_labels`.
        y_scale_mode: Modo de escala do eixo de valores.
            `fixed_100` fixa referência em 100; `dynamic` usa máximo dos dados.
        ticklabel_format_style: Estilo numérico aplicado via `ax.ticklabel_format`
            no eixo de valores.
        path_if_empty: Caminho opcional para gerar placeholder quando `data` estiver vazio.
        orientation: Orientação do gráfico. Aceita `vertical` ou `horizontal`.
        label_offset: Distância adicional do rótulo em relação ao topo/fim da barra
            quando o rótulo fica fora dela.
        xlim: Limites explícitos do eixo X. Quando informado, sobrescreve o limite
            automático ao final da montagem.
        empty_value_message: Mensagem exibida no centro do gráfico quando todos os
            valores são menores ou iguais a zero.
        empty_value_message_xy: Posição da mensagem em coordenadas do eixo (0 a 1).
        empty_value_message_size: Tamanho da fonte da mensagem de vazio.
        empty_value_message_color: Cor da mensagem de vazio.

    Retorno:
        Figure matplotlib pronta para exportação, ou `None` quando não há dados válidos.
    """
    if not is_data_valid(data, path_if_empty):
        return None
    orientation_normalized = orientation.lower().strip()
    if orientation_normalized not in {"vertical", "horizontal"}:
        raise ValueError("orientation deve ser 'vertical' ou 'horizontal'")
    spacing = float(category_spacing)
    if spacing <= 0:
        raise ValueError("category_spacing deve ser maior que 0.")

    df = _to_dataframe(data)
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
    df = df.dropna(subset=[x_col])
    x_vals = df[x_col].astype(str).tolist()
    y_vals = df[y_col].to_numpy(dtype=float)

    color_values: list[str]
    if colors is None:
        color_values = ["#0095DA"] * len(df)
    elif isinstance(colors, dict):
        color_values = [colors.get(x, "#0095DA") for x in x_vals]
    else:
        c = list(colors)
        color_values = c if len(c) == len(df) else [c[0]] * len(df)

    fig, ax = plt.subplots(figsize=(10, 5))
    # category_spacing altera apenas a distância entre centros das barras.
    axis_indexes = np.arange(len(df), dtype=float) * spacing
    if orientation_normalized == "horizontal":
        bars = ax.barh(axis_indexes, y_vals, color=color_values, height=bar_width)
    else:
        bars = ax.bar(axis_indexes, y_vals, color=color_values, width=bar_width)

    max_val = max(1.0, float(np.nanmax(y_vals)))
    threshold_value = (100.0 if y_scale_mode == "fixed_100" else max_val) * smart_threshold
    if show_labels:
        for bar, val in zip(bars, y_vals):
            inside = smart_labels and (val >= threshold_value) and (val < max_val)
            color = "white" if inside else label_color
            label = (
                label_formatter(float(val))
                if label_formatter is not None
                else _format_label(float(val), label_format, label_decimal_places)
            )
            if orientation_normalized == "horizontal":
                if inside:
                    x_pos = val - (val * 0.05)
                    ha = "right"
                else:
                    x_pos = val + label_offset
                    ha = "left"
                geom_atm_label(
                    ax,
                    x_pos,
                    bar.get_y() + bar.get_height() / 2,
                    label,
                    size=label_size,
                    color=color,
                    ha=ha,
                    va="center",
                )
            else:
                y_pos = val - (val * 0.05) if inside else val + label_offset
                va = "top" if inside else "bottom"
                geom_atm_label(
                    ax,
                    bar.get_x() + bar.get_width() / 2,
                    y_pos,
                    label,
                    size=label_size,
                    color=color,
                    ha="center",
                    va=va,
                )
    if y_scale_mode == "fixed_100":
        value_limit = 100 * (1 + y_expand[1])
    elif y_scale_mode == "dynamic":
        value_limit = max_val * (1 + y_expand[1])
    else:
        raise ValueError("y_scale_mode deve ser 'dynamic' ou 'fixed_100'")

    if orientation_normalized == "horizontal":
        ax.set_xlim(0, value_limit)
        ax.set_yticks(axis_indexes)
        ax.set_yticklabels(x_vals, fontsize=axis_text_x_size or axis_text_size)
        if axis_indexes.size > 0:
            margem = max(float(bar_width) / 2.0, 0.05)
            y_min = float(axis_indexes.min()) - margem
            y_max = float(axis_indexes.max()) + margem
            if y_min == y_max:
                y_min -= 0.5
                y_max += 0.5
            ax.set_ylim(y_min, y_max)
        ax.tick_params(
            axis="y",
            labelsize=axis_text_x_size or axis_text_size,
            labelleft=show_yaxis,
            left=show_y_ticks,
        )
        ax.tick_params(
            axis="x",
            labelsize=axis_text_y_size or axis_text_size,
            labelbottom=show_xaxis,
            bottom=show_xaxis and show_x_ticks,
        )
        ax.set_xlabel("" if y_label is None else y_label)
    else:
        ax.set_ylim(0, value_limit)
        ax.set_xticks(axis_indexes)
        ax.set_xticklabels(x_vals, fontsize=axis_text_x_size or axis_text_size)
        if axis_indexes.size > 0:
            margem = max(float(bar_width) / 2.0, 0.05)
            x_min = float(axis_indexes.min()) - margem
            x_max = float(axis_indexes.max()) + margem
            if x_min == x_max:
                x_min -= 0.5
                x_max += 0.5
            ax.set_xlim(x_min, x_max)
        ax.tick_params(
            axis="x",
            labelsize=axis_text_x_size or axis_text_size,
            labelbottom=show_xaxis,
            bottom=show_xaxis and show_x_ticks,
        )
        ax.tick_params(
            axis="y",
            labelsize=axis_text_y_size or axis_text_size,
            labelleft=show_yaxis,
            left=show_y_ticks,
        )
        ax.set_ylabel("" if y_label is None else y_label)

    if not show_x_ticks:
        ax.tick_params(axis="x", length=0)
    if not show_y_ticks:
        ax.tick_params(axis="y", length=0)

    if ticklabel_format_style is not None:
        axis_name = "x" if orientation_normalized == "horizontal" else "y"
        ax.ticklabel_format(style=ticklabel_format_style, axis=axis_name)

    if xlim is not None:
        ax.set_xlim(xlim)

    if empty_value_message is not None and float(np.nanmax(y_vals)) <= 0.0:
        ax.text(
            empty_value_message_xy[0],
            empty_value_message_xy[1],
            empty_value_message,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=empty_value_message_size,
            color=empty_value_message_color,
        )

    theme_atm_base(ax, base_size=axis_text_size)
    if orientation_normalized == "horizontal":
        ax.tick_params(
            axis="y",
            labelsize=axis_text_x_size or axis_text_size,
            labelleft=show_yaxis,
            left=show_y_ticks,
        )
        ax.tick_params(
            axis="x",
            labelsize=axis_text_y_size or axis_text_size,
            labelbottom=show_xaxis,
            bottom=show_xaxis and show_x_ticks,
        )
    else:
        ax.tick_params(
            axis="x",
            labelsize=axis_text_x_size or axis_text_size,
            labelbottom=show_xaxis,
            bottom=show_xaxis and show_x_ticks,
        )
        ax.tick_params(
            axis="y",
            labelsize=axis_text_y_size or axis_text_size,
            labelleft=show_yaxis,
            left=show_y_ticks,
        )
    if not show_x_ticks:
        ax.tick_params(axis="x", length=0)
    if not show_y_ticks:
        ax.tick_params(axis="y", length=0)
    apply_grid_theme(ax, show_grid)
    add_graph_markers(ax, "barras_simples")
    return fig


def plot_donut(
    data: Any,
    value_col: str = "valor",
    category_col: str = "categoria",
    colors: Optional[Dict[str, str]] = None,
    show_legend: bool = True,
    legend_position: str = "bottom",
    label_size: float = 4,
    shadow_bg_colour: str = "#ffffff00",
    shadow_bg_r: float = 0.05,
    path_if_empty: str | Path | None = None,
) -> Optional[plt.Figure]:
    if not is_data_valid(data, path_if_empty):
        return None
    df = _to_dataframe(data)
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)
    df = df[df[value_col] > 0]
    if df.empty:
        return None
    colors = colors or {
        "Categoria1": "#0095DA",
        "Categoria2": "#FF8C00",
        "Categoria3": "#808080",
        "Categoria4": "#4CAF50",
    }

    cat = df[category_col].astype(str).tolist()
    vals = df[value_col].to_numpy(dtype=float)
    slice_colors = [colors.get(c, "#0095DA") for c in cat]
    total = float(vals.sum())

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _ = ax.pie(
        vals, colors=slice_colors, startangle=90, wedgeprops={"width": 0.45, "edgecolor": "white"}
    )

    for wedge, value in zip(wedges, vals):
        angle = (wedge.theta1 + wedge.theta2) / 2
        r = 0.75
        x = r * math.cos(math.radians(angle))
        y = r * math.sin(math.radians(angle))
        pct = (value / total) * 100
        geom_atm_shadow_label(
            ax,
            x,
            y,
            f"{_format_number_br(pct, 1)}%",
            size=label_size,
            bg_colour=shadow_bg_colour,
            bg_r=shadow_bg_r,
            color="black",
            ha="center",
            va="center",
        )

    theme_atm_void(ax)
    if show_legend:
        loc_map = {
            "bottom": "lower center",
            "top": "upper center",
            "right": "center right",
            "left": "center left",
        }
        ax.legend(
            wedges, cat, loc=loc_map.get(legend_position, "lower center"), frameon=False, ncol=2
        )
    return fig


def validate_state_code(state_code: str) -> None:
    if not isinstance(state_code, str):
        raise TypeError("state_code must be a single character string")
    code = state_code.upper()
    if code not in VALID_STATE_CODES:
        raise ValueError(
            f"Invalid state code: '{state_code}'. Valid codes are: {', '.join(sorted(VALID_STATE_CODES))}"
        )


def validate_coordinates(lat: float, lon: float, point_name: str = "point") -> None:
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise TypeError(f"{point_name}: lat and lon must be numeric")
    if lat < -34 or lat > 6:
        warnings.warn(
            f"{point_name}: latitude {lat} is outside Brazil bounds (-34 to 6)", stacklevel=2
        )
    if lon < -75 or lon > -33:
        warnings.warn(
            f"{point_name}: longitude {lon} is outside Brazil bounds (-75 to -33)", stacklevel=2
        )


def ensure_geobr_network_resilience() -> None:
    """
    Patch geobr network resolution to avoid hanging on unstable IPEA endpoints.

    Strategy:
    - Prioritize official geobr GitHub release mirror by file id.
    - Enforce request timeout for every geobr HTTP call.
    - Use GitHub metadata mirror as default metadata source.
    """
    import geobr.utils as geobr_utils  # type: ignore

    if getattr(geobr_utils, "_schoolreport_network_patch", False):
        return

    def _url_solver_with_timeout(url: str):
        file_id = str(url).split("/")[-1]
        candidates = [f"{_GEOBR_RELEASE_BASE_URL}{file_id}", str(url)]

        for mirror in getattr(geobr_utils, "MIRRORS", []):
            candidate = f"{mirror}{file_id}"
            if candidate not in candidates:
                candidates.append(candidate)

        last_error: Exception | None = None
        for candidate in candidates:
            try:
                response = geobr_utils.requests.get(candidate, timeout=(5, 30))
                if response.status_code == 200:
                    return response
            except Exception as exc:
                last_error = exc
                continue

        if last_error is not None:
            raise ConnectionError(
                "No geobr mirrors responded successfully. "
                "Please report to https://github.com/ipeaGIT/geobr/issues"
            ) from last_error

        raise ConnectionError(
            "No geobr mirrors are active. "
            "Please report to https://github.com/ipeaGIT/geobr/issues"
        )

    geobr_utils.url_solver = _url_solver_with_timeout

    # download_metadata usa lru_cache: atualiza a URL padrão de metadados e limpa o cache.
    try:
        geobr_utils.download_metadata.__wrapped__.__defaults__ = (_GEOBR_METADATA_MIRROR_URL,)
    except Exception:
        pass
    try:
        geobr_utils.download_metadata.cache_clear()
    except Exception:
        pass

    geobr_utils._schoolreport_network_patch = True


def get_cached_state_geometry(
    state_code: str, year: int = 2020, show_progress: bool = False
) -> Any:
    validate_state_code(state_code)
    code = state_code.upper()
    key = f"{code}_{year}"
    if key in _STATE_GEOMETRY_CACHE:
        return _STATE_GEOMETRY_CACHE[key]

    disk_cache_path = _state_geometry_cache_path(code, year)
    if disk_cache_path.exists():
        state_geom = pd.read_pickle(disk_cache_path)
        _STATE_GEOMETRY_CACHE[key] = state_geom
        return state_geom

    try:
        import geobr  # type: ignore
    except Exception as exc:
        raise ImportError("Map plotting requires the 'geobr' Python package.") from exc

    ensure_geobr_network_resilience()

    try:
        state_geom = geobr.read_state(
            code_state=code, year=year, simplified=False, showProgress=show_progress
        )
    except TypeError:
        state_geom = geobr.read_state(code_state=code, year=year, simplified=False)
    state_geom.to_pickle(disk_cache_path)
    _STATE_GEOMETRY_CACHE[key] = state_geom
    return state_geom


def get_municipality_point(
    code_muni: str | int, state_code: str, year: int = 2020
) -> tuple[float, float]:
    """
    Resolve municipality representative point (lat, lon) from geobr.

    Falls back to the state representative point when municipality geometry
    cannot be loaded for any reason.
    """
    validate_state_code(state_code)
    code = str(code_muni).strip()
    cache_key = f"{code}_{year}"
    if cache_key in _MUNICIPALITY_POINT_CACHE:
        return _MUNICIPALITY_POINT_CACHE[cache_key]

    disk_cache_path = _municipality_point_cache_path(code, year)
    if disk_cache_path.exists():
        cached = json.loads(disk_cache_path.read_text(encoding="utf-8"))
        point = (float(cached["lat"]), float(cached["lon"]))
        _MUNICIPALITY_POINT_CACHE[cache_key] = point
        return point

    try:
        import geobr  # type: ignore
    except Exception as exc:
        raise ImportError("Map plotting requires the 'geobr' Python package.") from exc

    ensure_geobr_network_resilience()

    try:
        muni = geobr.read_municipality(code_muni=int(code), year=year)
        if muni is None or len(muni) == 0:
            raise ValueError("Municipality geometry returned empty result.")
        muni = muni.to_crs(4326)
        pt = muni.geometry.representative_point().iloc[0]
        point = (float(pt.y), float(pt.x))
    except Exception:
        state_geom = get_cached_state_geometry(
            state_code=state_code, year=year, show_progress=False
        ).to_crs(4326)
        pt = state_geom.geometry.representative_point().iloc[0]
        point = (float(pt.y), float(pt.x))

    disk_cache_path.write_text(
        json.dumps({"lat": point[0], "lon": point[1]}),
        encoding="utf-8",
    )
    _MUNICIPALITY_POINT_CACHE[cache_key] = point
    return point


def clear_state_geometry_cache() -> None:
    _STATE_GEOMETRY_CACHE.clear()
    _MUNICIPALITY_POINT_CACHE.clear()


def _mark_figure_for_exact_svg_export(fig: plt.Figure) -> None:
    """Mark map figures so SVG export preserves exact width/height from figsize."""
    fig_width_in, fig_height_in = fig.get_size_inches()
    setattr(fig, "_schoolreport_preserve_svg_size", True)
    setattr(
        fig,
        "_schoolreport_expected_svg_size_inches",
        (float(fig_width_in), float(fig_height_in)),
    )


def plot_state_map(
    state_code: str,
    fill_color: str = "#183EFF",
    border_color: str = "#183EFF",
    border_width: float = 0.8,
    year: int = 2020,
    show_progress: bool = False,
) -> plt.Figure:
    state_geom = get_cached_state_geometry(state_code, year, show_progress)
    fig, ax = plt.subplots(figsize=(8, 6))
    _mark_figure_for_exact_svg_export(fig)
    state_geom.to_crs(4326).plot(
        ax=ax, color=fill_color, edgecolor=border_color, linewidth=border_width
    )
    theme_atm_void(ax)
    return fig


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _bbox_area(bbox: Bbox) -> float:
    return max(0.0, float(bbox.width)) * max(0.0, float(bbox.height))


def _bbox_overlap_area(bbox1: Bbox, bbox2: Bbox) -> float:
    x0 = max(float(bbox1.x0), float(bbox2.x0))
    y0 = max(float(bbox1.y0), float(bbox2.y0))
    x1 = min(float(bbox1.x1), float(bbox2.x1))
    y1 = min(float(bbox1.y1), float(bbox2.y1))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _bbox_outside_area(inner: Bbox, outer: Bbox) -> float:
    overlap_x0 = max(float(inner.x0), float(outer.x0))
    overlap_y0 = max(float(inner.y0), float(outer.y0))
    overlap_x1 = min(float(inner.x1), float(outer.x1))
    overlap_y1 = min(float(inner.y1), float(outer.y1))
    if overlap_x1 <= overlap_x0 or overlap_y1 <= overlap_y0:
        return _bbox_area(inner)
    inside = (overlap_x1 - overlap_x0) * (overlap_y1 - overlap_y0)
    return max(0.0, _bbox_area(inner) - inside)


def _bbox_contains_point(bbox: Bbox, point: tuple[float, float], margin_px: float = 6.0) -> bool:
    x, y = point
    return (
        float(bbox.x0) - margin_px <= x <= float(bbox.x1) + margin_px
        and float(bbox.y0) - margin_px <= y <= float(bbox.y1) + margin_px
    )


def _direction_component(value: float) -> float:
    if value > 0:
        return 1.0
    if value < 0:
        return -1.0
    return 0.0


def _normalize_map_label_text(text: str) -> str:
    return " ".join(str(text).replace("\n", " ").split())


def _suggest_map_label_wrap_width(label_size: float) -> int:
    width = int(34.0 - (max(0.0, float(label_size)) * 0.55))
    return max(16, min(30, width))


def _wrap_map_label_text(text: str, label_size: float) -> str:
    normalized = _normalize_map_label_text(text)
    if not normalized:
        return normalized

    max_width = _suggest_map_label_wrap_width(label_size)
    if len(normalized) <= max_width:
        return normalized

    words = normalized.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        word_clean = word.strip()
        if not word_clean:
            continue
        if not current:
            current = word_clean
            continue
        if len(current) + 1 + len(word_clean) <= max_width:
            current = f"{current} {word_clean}"
            continue
        lines.append(current)
        current = word_clean
    if current:
        lines.append(current)
    return "\n".join(lines) if lines else normalized


def _map_label_size_attempts(label_size: float) -> list[float]:
    attempts: list[float] = []
    for reduction in (0.0, 1.0, 2.0):
        if reduction > float(_MAP_LABEL_MAX_FONT_REDUCTION):
            continue
        size = max(3.0, float(label_size) - reduction)
        if all(abs(size - existing) > 1e-6 for existing in attempts):
            attempts.append(size)
    return attempts


def _map_label_text_variants(
    labels: list[tuple[str, float, float, str]],
    label_sizes: dict[str, float],
) -> list[dict[str, str]]:
    base: dict[str, str] = {
        point_name: _normalize_map_label_text(text) for point_name, _, _, text in labels
    }
    wrapped: dict[str, str] = {
        point_name: _wrap_map_label_text(text, label_size=label_sizes.get(point_name, LABEL_SIZE))
        for point_name, _, _, text in labels
    }
    if wrapped != base:
        return [base, wrapped]
    return [base]


def _compute_map_axis_padding_ratios(
    label_texts: Sequence[str], label_size: float
) -> tuple[float, float]:
    normalized = []
    for text in label_texts:
        normalized_text = _normalize_map_label_text(text)
        if normalized_text:
            normalized.append(normalized_text)
    longest = max((len(text) for text in normalized), default=0)
    line_count = max((text.count("\n") + 1 for text in label_texts if text), default=1)
    size_factor = max(0.0, min(1.6, (float(label_size) - 12.0) / 10.0))
    length_factor = max(0.0, min(1.8, (float(longest) - 16.0) / 18.0))
    line_factor = max(0.0, min(1.0, float(line_count - 1)))
    x_ratio = min(0.42, 0.08 + (0.08 * size_factor) + (0.13 * length_factor))
    y_ratio = min(0.30, 0.06 + (0.05 * size_factor) + (0.04 * length_factor) + (0.05 * line_factor))
    return x_ratio, y_ratio


def _set_map_axes_limits_with_padding(
    ax: plt.Axes,
    base_limits: tuple[float, float, float, float],
    *,
    x_pad_ratio: float,
    y_pad_ratio: float,
) -> None:
    base_x_min, base_x_max, base_y_min, base_y_max = base_limits
    x_span = max(1e-6, float(base_x_max) - float(base_x_min))
    y_span = max(1e-6, float(base_y_max) - float(base_y_min))
    ax.set_xlim(
        float(base_x_min) - (x_span * float(x_pad_ratio)),
        float(base_x_max) + (x_span * float(x_pad_ratio)),
    )
    ax.set_ylim(
        float(base_y_min) - (y_span * float(y_pad_ratio)),
        float(base_y_max) + (y_span * float(y_pad_ratio)),
    )


def _prepare_map_axes_for_labels(
    fig: plt.Figure,
    ax: plt.Axes,
    label_texts: Sequence[str],
    label_size: float,
) -> tuple[tuple[float, float, float, float], float, float]:
    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.03)
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    base_limits = (float(x_min), float(x_max), float(y_min), float(y_max))
    x_ratio, y_ratio = _compute_map_axis_padding_ratios(
        label_texts=label_texts, label_size=label_size
    )
    _set_map_axes_limits_with_padding(
        ax=ax,
        base_limits=base_limits,
        x_pad_ratio=x_ratio,
        y_pad_ratio=y_ratio,
    )
    return base_limits, x_ratio, y_ratio


def _build_map_label_candidates(
    lon: float,
    lat: float,
    label: str,
    x_span: float,
    y_span: float,
    label_size: float,
    preferred_direction: Optional[tuple[float, float]] = None,
    spread_multiplier: float = 1.0,
) -> list[dict[str, Any]]:
    # O deslocamento escala com a área do mapa e o tamanho do texto para manter legibilidade.
    safe_x_span = max(1e-6, float(x_span))
    safe_y_span = max(1e-6, float(y_span))
    size_factor = max(1.0, float(label_size) / 12.0)
    text_factor = min(2.6, max(1.0, len(_normalize_map_label_text(label)) / 15.0))
    base_dx = safe_x_span * 0.022 * size_factor * (0.95 + 0.22 * text_factor) * spread_multiplier
    base_dy = safe_y_span * 0.020 * size_factor * (0.9 + 0.12 * text_factor) * spread_multiplier

    vectors: list[tuple[float, float, float]] = [
        (1.0, 1.0, 1.0),
        (-1.0, 1.0, 1.0),
        (1.0, -1.0, 1.0),
        (-1.0, -1.0, 1.0),
        (1.0, 0.0, 1.1),
        (-1.0, 0.0, 1.1),
        (0.0, 1.0, 1.1),
        (0.0, -1.0, 1.1),
        (1.0, 1.0, 1.6),
        (-1.0, 1.0, 1.6),
        (1.0, -1.0, 1.6),
        (-1.0, -1.0, 1.6),
        (1.0, 0.0, 1.8),
        (-1.0, 0.0, 1.8),
        (0.0, 1.0, 1.8),
        (0.0, -1.0, 1.8),
        (1.0, 1.0, 2.2),
        (-1.0, 1.0, 2.2),
        (1.0, -1.0, 2.2),
        (-1.0, -1.0, 2.2),
        (1.0, 0.0, 2.4),
        (-1.0, 0.0, 2.4),
    ]

    candidates: list[dict[str, Any]] = []
    pref_x = preferred_direction[0] if preferred_direction is not None else 0.0
    pref_y = preferred_direction[1] if preferred_direction is not None else 0.0
    for idx, (vx, vy, scale) in enumerate(vectors):
        ha = "center"
        va = "center"
        if vx > 0:
            ha = "left"
        elif vx < 0:
            ha = "right"
        if vy > 0:
            va = "bottom"
        elif vy < 0:
            va = "top"

        preference = (vx * pref_x) + (vy * pref_y)
        cardinal_penalty = 0.2 if vx == 0.0 or vy == 0.0 else 0.0
        rank = float(idx) + cardinal_penalty - (2.5 * preference)
        candidates.append(
            {
                "x": float(lon) + (vx * base_dx * scale),
                "y": float(lat) + (vy * base_dy * scale),
                "ha": ha,
                "va": va,
                "rank": rank,
            }
        )
    return sorted(candidates, key=lambda item: float(item["rank"]))


def _measure_map_label_bbox(
    ax: plt.Axes,
    renderer: Any,
    text: str,
    candidate: dict[str, Any],
    label_size: float,
    label_color: str,
) -> Bbox:
    temp = ax.text(
        float(candidate["x"]),
        float(candidate["y"]),
        text,
        fontsize=label_size,
        color=label_color,
        fontfamily=get_chart_font_family(),
        ha=str(candidate["ha"]),
        va=str(candidate["va"]),
        zorder=6,
        alpha=0.0,
        clip_on=False,
        linespacing=1.05,
        bbox=_MAP_LABEL_BBOX_STYLE,
    )
    try:
        return temp.get_window_extent(renderer=renderer).expanded(1.05, 1.15)
    finally:
        temp.remove()


def _build_measured_map_label_candidates(
    ax: plt.Axes,
    renderer: Any,
    lon: float,
    lat: float,
    label: str,
    x_span: float,
    y_span: float,
    label_size: float,
    label_color: str,
    preferred_direction: Optional[tuple[float, float]] = None,
    spread_multiplier: float = 1.0,
) -> list[dict[str, Any]]:
    measured: list[dict[str, Any]] = []
    raw_candidates = _build_map_label_candidates(
        lon=lon,
        lat=lat,
        label=label,
        x_span=x_span,
        y_span=y_span,
        label_size=label_size,
        preferred_direction=preferred_direction,
        spread_multiplier=spread_multiplier,
    )
    for candidate in raw_candidates:
        measured.append(
            {
                **candidate,
                "bbox": _measure_map_label_bbox(
                    ax=ax,
                    renderer=renderer,
                    text=label,
                    candidate=candidate,
                    label_size=label_size,
                    label_color=label_color,
                ),
            }
        )
    return measured


def _pick_best_single_map_label_candidate(
    candidates: list[dict[str, Any]],
    ax_bbox: Bbox,
    avoid_point: Optional[tuple[float, float]] = None,
) -> Optional[dict[str, Any]]:
    best: Optional[dict[str, Any]] = None
    for candidate in candidates:
        outside = _bbox_outside_area(candidate["bbox"], ax_bbox)
        covers_point = bool(
            avoid_point is not None and _bbox_contains_point(candidate["bbox"], avoid_point)
        )
        penalty = (outside * 4.0) + (12000.0 if covers_point else 0.0) + float(candidate["rank"])
        if best is None or penalty < float(best["penalty"]):
            best = {
                "candidate": candidate,
                "outside_area": outside,
                "covers_point": covers_point,
                "penalty": penalty,
            }
    return best


def _pick_best_pair_map_label_candidates(
    point1_candidates: list[dict[str, Any]],
    point2_candidates: list[dict[str, Any]],
    ax_bbox: Bbox,
    point1_display: tuple[float, float],
    point2_display: tuple[float, float],
) -> Optional[dict[str, Any]]:
    best: Optional[dict[str, Any]] = None
    for candidate1 in point1_candidates:
        for candidate2 in point2_candidates:
            overlap = _bbox_overlap_area(candidate1["bbox"], candidate2["bbox"])
            outside = _bbox_outside_area(candidate1["bbox"], ax_bbox) + _bbox_outside_area(
                candidate2["bbox"], ax_bbox
            )
            covers_points = int(_bbox_contains_point(candidate1["bbox"], point2_display)) + int(
                _bbox_contains_point(candidate2["bbox"], point1_display)
            )
            penalty = (
                (overlap * 40.0)
                + (outside * 3.0)
                + (covers_points * 30000.0)
                + float(candidate1["rank"])
                + float(candidate2["rank"])
            )
            if best is None or penalty < float(best["penalty"]):
                best = {
                    "candidate1": candidate1,
                    "candidate2": candidate2,
                    "overlap_area": overlap,
                    "outside_area": outside,
                    "covers_points": covers_points,
                    "penalty": penalty,
                }
    return best


def _translate_bbox(bbox: Bbox, dx_px: float, dy_px: float) -> Bbox:
    return Bbox.from_extents(
        float(bbox.x0) + float(dx_px),
        float(bbox.y0) + float(dy_px),
        float(bbox.x1) + float(dx_px),
        float(bbox.y1) + float(dy_px),
    )


def _nudge_map_label_candidate_inside_axes(
    ax: plt.Axes,
    candidate: dict[str, Any],
    ax_bbox: Bbox,
    padding_px: float = 2.0,
) -> dict[str, Any]:
    bbox = candidate.get("bbox")
    if not isinstance(bbox, Bbox):
        return candidate

    dx_px = 0.0
    dy_px = 0.0
    if float(bbox.x0) < float(ax_bbox.x0):
        dx_px += float(ax_bbox.x0) - float(bbox.x0) + float(padding_px)
    if float(bbox.x1) > float(ax_bbox.x1):
        dx_px -= float(bbox.x1) - float(ax_bbox.x1) + float(padding_px)
    if float(bbox.y0) < float(ax_bbox.y0):
        dy_px += float(ax_bbox.y0) - float(bbox.y0) + float(padding_px)
    if float(bbox.y1) > float(ax_bbox.y1):
        dy_px -= float(bbox.y1) - float(ax_bbox.y1) + float(padding_px)

    if abs(dx_px) < 1e-3 and abs(dy_px) < 1e-3:
        return candidate

    anchor_display = ax.transData.transform((float(candidate["x"]), float(candidate["y"])))
    nudged_data = ax.transData.inverted().transform(
        (float(anchor_display[0]) + dx_px, float(anchor_display[1]) + dy_px)
    )
    updated = dict(candidate)
    updated["x"] = float(nudged_data[0])
    updated["y"] = float(nudged_data[1])
    updated["bbox"] = _translate_bbox(bbox, dx_px=dx_px, dy_px=dy_px)
    return updated


def _map_layout_is_fully_visible(layout: dict[str, Any]) -> bool:
    outside_area = float(layout.get("outside_area", 0.0))
    if outside_area > float(_MAP_LABEL_VISIBLE_OUTSIDE_PX2):
        return False

    if int(layout.get("covers_points", 0)) > 0:
        return False

    if str(layout.get("kind")) == "pair":
        overlap_area = float(layout.get("overlap_area", 0.0))
        if overlap_area > float(_MAP_LABEL_VISIBLE_OVERLAP_PX2):
            return False
    return True


def _infer_map_label_bbox_background_rgb(state_fill_color: str) -> tuple[float, float, float]:
    # Cor percebida do bbox: branco translúcido sobre o fundo do estado.
    bbox_face_rgba = to_rgba(str(_MAP_LABEL_BBOX_STYLE.get("facecolor", "white")))
    state_rgba = to_rgba(str(state_fill_color))
    bbox_alpha = max(0.0, min(1.0, float(_MAP_LABEL_BBOX_STYLE.get("alpha", 1.0))))
    effective_alpha = float(bbox_face_rgba[3]) * bbox_alpha
    return (
        (float(bbox_face_rgba[0]) * effective_alpha)
        + (float(state_rgba[0]) * (1.0 - effective_alpha)),
        (float(bbox_face_rgba[1]) * effective_alpha)
        + (float(state_rgba[1]) * (1.0 - effective_alpha)),
        (float(bbox_face_rgba[2]) * effective_alpha)
        + (float(state_rgba[2]) * (1.0 - effective_alpha)),
    )


def _relative_luminance(rgb: tuple[float, float, float]) -> float:
    def _to_linear(channel: float) -> float:
        channel = max(0.0, min(1.0, float(channel)))
        if channel <= 0.04045:
            return channel / 12.92
        return ((channel + 0.055) / 1.055) ** 2.4

    r_lin = _to_linear(rgb[0])
    g_lin = _to_linear(rgb[1])
    b_lin = _to_linear(rgb[2])
    return (0.2126 * r_lin) + (0.7152 * g_lin) + (0.0722 * b_lin)


def _default_capital_label_color(state_fill_color: str) -> str:
    # Se o bbox percebido estiver claro (caso comum), prefere texto mais escuro.
    perceived_bbox_rgb = _infer_map_label_bbox_background_rgb(state_fill_color)
    if _relative_luminance(perceived_bbox_rgb) >= 0.55:
        return _MAP_CAPITAL_LABEL_COLOR
    return _MAP_CAPITAL_POINT_COLOR


def _resolve_map_role_colors(
    *,
    point_color: Optional[str],
    label_color: Optional[str],
    state_fill_color: str,
    municipality_point_color: Optional[str],
    municipality_label_color: Optional[str],
    capital_point_color: Optional[str],
    capital_label_color: Optional[str],
) -> dict[str, str]:
    # Resolve paleta por papel (municipio/capital) com fallback para parametros legados.
    def _pick_color(value: Optional[str], fallback: str) -> str:
        candidate = str(value).strip() if value is not None else ""
        return candidate or str(fallback).strip()

    resolved_municipality_point = _pick_color(
        municipality_point_color,
        _pick_color(point_color, _MAP_MUNICIPALITY_COLOR),
    )
    resolved_municipality_label = _pick_color(
        municipality_label_color,
        _pick_color(label_color, resolved_municipality_point),
    )
    resolved_capital_point = _pick_color(capital_point_color, _MAP_CAPITAL_POINT_COLOR)
    resolved_capital_label = _pick_color(
        capital_label_color,
        _default_capital_label_color(state_fill_color),
    )

    # Garante contraste sem deixar capital e municipio com a mesma cor.
    if resolved_capital_point.lower() == resolved_municipality_point.lower():
        resolved_capital_point = (
            _MAP_CAPITAL_COLOR_FALLBACK
            if resolved_municipality_point.lower() == _MAP_CAPITAL_POINT_COLOR.lower()
            else _MAP_CAPITAL_POINT_COLOR
        )
    if resolved_capital_label.lower() == resolved_municipality_label.lower():
        resolved_capital_label = (
            resolved_capital_point
            if resolved_capital_point.lower() != resolved_municipality_label.lower()
            else _MAP_CAPITAL_COLOR_FALLBACK
        )

    return {
        "point1_point": resolved_municipality_point,
        "point1_label": resolved_municipality_label,
        "point2_point": resolved_capital_point,
        "point2_label": resolved_capital_label,
    }


def _build_map_label_layout_attempt(
    *,
    ax: plt.Axes,
    renderer: Any,
    labels: list[tuple[str, float, float, str]],
    label_texts: dict[str, str],
    point1_lat: float,
    point1_lon: float,
    point2_lat: float,
    point2_lon: float,
    label_sizes: dict[str, float],
    base_label_sizes: dict[str, float],
    label_colors: dict[str, str],
    spread_multiplier: float,
    is_capital: bool,
    style_penalty: float = 0.0,
) -> Optional[dict[str, Any]]:
    ax_bbox = ax.get_window_extent(renderer=renderer)
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    x_span = abs(float(x_max) - float(x_min))
    y_span = abs(float(y_max) - float(y_min))

    point1_display = tuple(ax.transData.transform((float(point1_lon), float(point1_lat))))
    point2_display = tuple(ax.transData.transform((float(point2_lon), float(point2_lat))))
    wrap_penalty = float(sum(text.count("\n") for text in label_texts.values())) * 180.0
    font_penalty = (
        float(
            sum(
                max(0.0, float(base_label_sizes.get(point_name, size)) - float(size))
                for point_name, size in label_sizes.items()
            )
        )
        * 220.0
    )

    if len(labels) == 2:
        point1_text = label_texts.get("point1", labels[0][3])
        point2_text = label_texts.get("point2", labels[1][3])
        point1_label_size = float(label_sizes.get("point1", LABEL_SIZE))
        point2_label_size = float(label_sizes.get("point2", LABEL_SIZE))
        max_pair_size = max(point1_label_size, point2_label_size)
        distance_m = _haversine_distance_m(point1_lat, point1_lon, point2_lat, point2_lon)
        distance_px = float(np.linalg.norm(np.asarray(point1_display) - np.asarray(point2_display)))
        close_points = distance_m <= _MAP_LABEL_PROXIMITY_M or distance_px <= max(
            _MAP_LABEL_PROXIMITY_PX, max_pair_size * 8.0
        )
        direction_x = _direction_component(point2_lon - point1_lon)
        direction_y = _direction_component(point2_lat - point1_lat)
        preferred_for_point1 = (-direction_x, -direction_y)
        preferred_for_point2 = (direction_x, direction_y)
        spread = (1.45 if close_points else 1.0) * float(spread_multiplier)

        point1_candidates = _build_measured_map_label_candidates(
            ax=ax,
            renderer=renderer,
            lon=float(point1_lon),
            lat=float(point1_lat),
            label=point1_text,
            x_span=x_span,
            y_span=y_span,
            label_size=point1_label_size,
            label_color=str(label_colors.get("point1", _MAP_MUNICIPALITY_COLOR)),
            preferred_direction=preferred_for_point1,
            spread_multiplier=spread,
        )
        point2_candidates = _build_measured_map_label_candidates(
            ax=ax,
            renderer=renderer,
            lon=float(point2_lon),
            lat=float(point2_lat),
            label=point2_text,
            x_span=x_span,
            y_span=y_span,
            label_size=point2_label_size,
            label_color=str(label_colors.get("point2", _MAP_CAPITAL_POINT_COLOR)),
            preferred_direction=preferred_for_point2,
            spread_multiplier=spread,
        )
        best_pair = _pick_best_pair_map_label_candidates(
            point1_candidates=point1_candidates,
            point2_candidates=point2_candidates,
            ax_bbox=ax_bbox,
            point1_display=point1_display,
            point2_display=point2_display,
        )
        if best_pair is None:
            return None

        adjusted_candidate1 = _nudge_map_label_candidate_inside_axes(
            ax=ax,
            candidate=best_pair["candidate1"],
            ax_bbox=ax_bbox,
        )
        adjusted_candidate2 = _nudge_map_label_candidate_inside_axes(
            ax=ax,
            candidate=best_pair["candidate2"],
            ax_bbox=ax_bbox,
        )
        bbox1 = adjusted_candidate1["bbox"]
        bbox2 = adjusted_candidate2["bbox"]
        overlap_area = _bbox_overlap_area(bbox1, bbox2)
        outside_area = _bbox_outside_area(bbox1, ax_bbox) + _bbox_outside_area(bbox2, ax_bbox)
        covers_points = int(_bbox_contains_point(bbox1, point2_display)) + int(
            _bbox_contains_point(bbox2, point1_display)
        )
        placement_penalty = (
            (overlap_area * 40.0)
            + (outside_area * 3.0)
            + (covers_points * 30000.0)
            + float(adjusted_candidate1["rank"])
            + float(adjusted_candidate2["rank"])
        )
        return {
            "kind": "pair",
            "label_size": float(max_pair_size),
            "overlap_area": float(overlap_area),
            "outside_area": float(outside_area),
            "covers_points": int(covers_points),
            "penalty": float(placement_penalty)
            + wrap_penalty
            + font_penalty
            + float(style_penalty),
            "placements": [
                {
                    "point_name": "point1",
                    "text": point1_text,
                    "candidate": adjusted_candidate1,
                    "label_size": point1_label_size,
                },
                {
                    "point_name": "point2",
                    "text": point2_text,
                    "candidate": adjusted_candidate2,
                    "label_size": point2_label_size,
                },
            ],
        }

    if len(labels) != 1:
        return None

    point_name, lon, lat, original_text = labels[0]
    text = label_texts.get(point_name, original_text)
    point_label_size = float(label_sizes.get(point_name, LABEL_SIZE))
    avoid_point = point2_display if point_name == "point1" and not is_capital else None
    preferred: Optional[tuple[float, float]] = None
    if point_name == "point1" and not is_capital:
        preferred = (
            -_direction_component(point2_lon - point1_lon),
            -_direction_component(point2_lat - point1_lat),
        )
    elif point_name == "point2" and not is_capital:
        preferred = (
            _direction_component(point2_lon - point1_lon),
            _direction_component(point2_lat - point1_lat),
        )

    candidates = _build_measured_map_label_candidates(
        ax=ax,
        renderer=renderer,
        lon=lon,
        lat=lat,
        label=text,
        x_span=x_span,
        y_span=y_span,
        label_size=point_label_size,
        label_color=str(label_colors.get(point_name, _MAP_MUNICIPALITY_COLOR)),
        preferred_direction=preferred,
        spread_multiplier=spread_multiplier,
    )
    best_single = _pick_best_single_map_label_candidate(
        candidates=candidates,
        ax_bbox=ax_bbox,
        avoid_point=avoid_point,
    )
    if best_single is None:
        return None

    adjusted_candidate = _nudge_map_label_candidate_inside_axes(
        ax=ax,
        candidate=best_single["candidate"],
        ax_bbox=ax_bbox,
    )
    adjusted_bbox = adjusted_candidate["bbox"]
    outside_area = _bbox_outside_area(adjusted_bbox, ax_bbox)
    covers_points = int(
        bool(avoid_point is not None and _bbox_contains_point(adjusted_bbox, avoid_point))
    )
    placement_penalty = (
        (outside_area * 4.0)
        + (12000.0 if covers_points else 0.0)
        + float(adjusted_candidate["rank"])
    )
    return {
        "kind": "single",
        "label_size": point_label_size,
        "outside_area": float(outside_area),
        "covers_points": int(covers_points),
        "penalty": float(placement_penalty) + wrap_penalty + font_penalty + float(style_penalty),
        "placements": [
            {
                "point_name": point_name,
                "text": text,
                "candidate": adjusted_candidate,
                "label_size": point_label_size,
            }
        ],
    }


def _draw_map_layout(
    ax: plt.Axes,
    layout: dict[str, Any],
    label_colors: dict[str, str],
) -> list[Any]:
    artists: list[Any] = []
    for placement in layout.get("placements", []):
        point_name = str(placement.get("point_name", "point1"))
        artists.append(
            _draw_map_label(
                ax=ax,
                text=str(placement["text"]),
                candidate=placement["candidate"],
                label_size=float(placement.get("label_size", layout["label_size"])),
                label_color=str(label_colors.get(point_name, _MAP_MUNICIPALITY_COLOR)),
                path_effects_style=_map_label_path_effects(point_name),
            )
        )
    return artists


def _map_label_path_effects(point_name: str) -> list[Any]:
    # Reforca contraste do texto da capital contra o bbox translúcido.
    if str(point_name) == "point2":
        return [pe.withStroke(linewidth=1.2, foreground="white", alpha=0.95)]
    return []


def _draw_map_label(
    ax: plt.Axes,
    text: str,
    candidate: dict[str, Any],
    label_size: float,
    label_color: str,
    path_effects_style: Optional[list[Any]] = None,
) -> Any:
    artist = ax.text(
        float(candidate["x"]),
        float(candidate["y"]),
        text,
        fontsize=label_size,
        color=label_color,
        fontfamily=get_chart_font_family(),
        ha=str(candidate["ha"]),
        va=str(candidate["va"]),
        zorder=6,
        clip_on=False,
        linespacing=1.05,
        bbox=_MAP_LABEL_BBOX_STYLE,
    )
    if path_effects_style:
        artist.set_path_effects(path_effects_style)
    return artist


def _shift_text_artist_in_display_space(
    ax: plt.Axes,
    text_artist: Any,
    *,
    dx_px: float = 0.0,
    dy_px: float = 0.0,
) -> None:
    if abs(dx_px) < 1e-6 and abs(dy_px) < 1e-6:
        return
    current_x, current_y = text_artist.get_position()
    anchor_display = ax.transData.transform((float(current_x), float(current_y)))
    shifted = ax.transData.inverted().transform(
        (float(anchor_display[0]) + float(dx_px), float(anchor_display[1]) + float(dy_px))
    )
    text_artist.set_position((float(shifted[0]), float(shifted[1])))


def _nudge_drawn_text_artist_inside_axes(
    ax: plt.Axes,
    text_artist: Any,
    renderer: Any,
    ax_bbox: Bbox,
    *,
    padding_px: float = 2.0,
) -> bool:
    text_bbox = text_artist.get_window_extent(renderer=renderer)
    dx_px = 0.0
    dy_px = 0.0
    if float(text_bbox.x0) < float(ax_bbox.x0):
        dx_px += float(ax_bbox.x0) - float(text_bbox.x0) + float(padding_px)
    if float(text_bbox.x1) > float(ax_bbox.x1):
        dx_px -= float(text_bbox.x1) - float(ax_bbox.x1) + float(padding_px)
    if float(text_bbox.y0) < float(ax_bbox.y0):
        dy_px += float(ax_bbox.y0) - float(text_bbox.y0) + float(padding_px)
    if float(text_bbox.y1) > float(ax_bbox.y1):
        dy_px -= float(text_bbox.y1) - float(ax_bbox.y1) + float(padding_px)
    if abs(dx_px) < 1e-6 and abs(dy_px) < 1e-6:
        return False
    _shift_text_artist_in_display_space(ax, text_artist, dx_px=dx_px, dy_px=dy_px)
    return True


def _resolve_drawn_map_labels_visibility(
    fig: plt.Figure,
    ax: plt.Axes,
    text_artists: list[Any],
    *,
    max_iterations: int = 6,
) -> None:
    if not text_artists:
        return

    for _ in range(max_iterations):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        ax_bbox = ax.get_window_extent(renderer=renderer)
        moved = False

        # Primeiro: garante que cada rótulo fique totalmente dentro da área visível.
        for text_artist in text_artists:
            moved = (
                _nudge_drawn_text_artist_inside_axes(
                    ax=ax,
                    text_artist=text_artist,
                    renderer=renderer,
                    ax_bbox=ax_bbox,
                    padding_px=1.5,
                )
                or moved
            )

        # Segundo: separa rótulos caso ainda exista sobreposição relevante.
        if len(text_artists) > 1:
            bboxes = [artist.get_window_extent(renderer=renderer) for artist in text_artists]
            for idx in range(len(text_artists) - 1):
                for jdx in range(idx + 1, len(text_artists)):
                    overlap_area = _bbox_overlap_area(bboxes[idx], bboxes[jdx])
                    if overlap_area <= float(_MAP_LABEL_VISIBLE_OVERLAP_PX2):
                        continue
                    delta = min(
                        18.0,
                        max(6.0, min(float(bboxes[idx].height), float(bboxes[jdx].height)) * 0.35),
                    )
                    if float(bboxes[idx].y0) <= float(bboxes[jdx].y0):
                        _shift_text_artist_in_display_space(ax, text_artists[idx], dy_px=-delta)
                        _shift_text_artist_in_display_space(ax, text_artists[jdx], dy_px=delta)
                    else:
                        _shift_text_artist_in_display_space(ax, text_artists[idx], dy_px=delta)
                        _shift_text_artist_in_display_space(ax, text_artists[jdx], dy_px=-delta)
                    moved = True
        if not moved:
            break
    fig.canvas.draw()


def plot_state_map_with_points(
    state_code: str,
    point1_lat: float,
    point1_lon: float,
    point1_label: Optional[str] = None,
    point2_lat: float = 0.0,
    point2_lon: float = 0.0,
    point2_label: Optional[str] = None,
    map_background_color: str = _MAP_BACKGROUND_COLOR,
    state_fill_color: str = _MAP_STATE_FILL_COLOR,
    border_color: str = "#183EFF",
    border_width: float = 0.8,
    point_color: str = _MAP_MUNICIPALITY_COLOR,
    point_size: float = 3,
    line_color: str = "white",
    line_width: float = 1,
    line_type: str = "solid",
    label_size: float = 4,
    label_color: str = _MAP_MUNICIPALITY_COLOR,
    municipality_point_color: Optional[str] = None,
    municipality_label_color: Optional[str] = None,
    capital_point_color: Optional[str] = None,
    capital_label_color: Optional[str] = None,
    show_distance: bool = False,
    distance_unit: str = "km",
    year: int = 2020,
    show_progress: bool = False,
    is_capital: bool = False,
    figsize: tuple[float, float] = (8.0, 6.0),
    fill_color: Optional[str] = None,
) -> plt.Figure:
    """
    Plota o mapa de uma UF com destaque para o municipio de interesse e, quando
    aplicavel, para a capital estadual. O helper aplica ajuste dinamico de margem,
    reposicionamento de rótulos por bounding box e correcoes finais apos renderizacao
    para evitar truncamento de texto.

    Parametros:
        state_code (str): Sigla da UF (ex.: "AC", "SP").
        point1_lat (float): Latitude do municipio analisado.
        point1_lon (float): Longitude do municipio analisado.
        point1_label (Optional[str]): Nome do municipio analisado.
        point2_lat (float): Latitude da capital (quando diferente do municipio).
        point2_lon (float): Longitude da capital (quando diferente do municipio).
        point2_label (Optional[str]): Nome da capital.
        map_background_color (str): Cor de fundo da área do mapa (axes).
        state_fill_color (str): Cor de preenchimento da geometria do estado.
        border_color (str): Cor da borda do estado.
        border_width (float): Espessura da borda do estado.
        point_color (str): Cor legada do ponto do municipio (fallback).
        point_size (float): Tamanho base dos pontos.
        line_color (str): Cor da linha entre municipio e capital.
        line_width (float): Espessura da linha entre municipio e capital.
        line_type (str): Estilo da linha entre municipio e capital.
        label_size (float): Tamanho base da fonte dos rótulos.
        label_color (str): Cor legada do rótulo do municipio (fallback).
        municipality_point_color (Optional[str]): Cor do ponto do municipio.
        municipality_label_color (Optional[str]): Cor do rótulo do municipio.
        capital_point_color (Optional[str]): Cor do ponto da capital.
        capital_label_color (Optional[str]): Cor do rótulo da capital.
        show_distance (bool): Se True, mostra a distancia entre os pontos.
        distance_unit (str): Unidade da distancia exibida ("km" ou "m").
        year (int): Ano da malha geográfica usada no geobr.
        show_progress (bool): Se True, mostra progresso do carregamento geobr.
        is_capital (bool): Indica se o municipio analisado ja e a capital.
        figsize (tuple[float, float]): Tamanho da figura em polegadas.
        fill_color (Optional[str]): Alias legado (deprecated) para
            `map_background_color`.

    Retorno:
        plt.Figure: Figura matplotlib pronta para exportacao.
    """
    # 1) Validacoes basicas de coordenadas para evitar estados invalidos no plot.
    validate_coordinates(point1_lat, point1_lon, "point1")
    if not is_capital:
        validate_coordinates(point2_lat, point2_lon, "point2")

    # Compatibilidade legada: fill_color agora e alias de map_background_color.
    resolved_map_background_color = str(map_background_color).strip() or _MAP_BACKGROUND_COLOR
    if fill_color is not None and str(fill_color).strip():
        warnings.warn(
            "Parametro `fill_color` esta deprecated; use `map_background_color`.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Se o chamador nao sobrescreveu a nova opcao, prioriza o alias legado.
        if str(map_background_color).strip() in {"", _MAP_BACKGROUND_COLOR}:
            resolved_map_background_color = str(fill_color).strip()

    resolved_state_fill_color = str(state_fill_color).strip() or _MAP_STATE_FILL_COLOR

    # 2) Base cartografica do estado.
    state_geom = get_cached_state_geometry(state_code, year, show_progress).to_crs(4326)
    fig, ax = plt.subplots(figsize=figsize)
    _mark_figure_for_exact_svg_export(fig)
    state_geom.plot(
        ax=ax,
        color=resolved_state_fill_color,
        edgecolor=border_color,
        linewidth=border_width,
    )

    # 3) Resolve paleta por papel (municipio/capital), centralizada no helper.
    role_colors = _resolve_map_role_colors(
        point_color=point_color,
        label_color=label_color,
        state_fill_color=resolved_state_fill_color,
        municipality_point_color=municipality_point_color,
        municipality_label_color=municipality_label_color,
        capital_point_color=capital_point_color,
        capital_label_color=capital_label_color,
    )
    point_colors_by_point = {
        "point1": role_colors["point1_point"],
        "point2": role_colors["point2_point"],
    }
    label_colors_by_point = {
        "point1": role_colors["point1_label"],
        "point2": role_colors["point2_label"],
    }

    # 4) Define quais rótulos entram no layout e tamanhos base por ponto.
    #    Regra visual: quando nao e capital, a capital fica 6pt menor para destacar o municipio.
    labels: list[tuple[str, float, float, str]] = []
    label_base_sizes: dict[str, float] = {}
    if point1_label:
        labels.append(("point1", float(point1_lon), float(point1_lat), str(point1_label)))
        label_base_sizes["point1"] = float(label_size)
    if not is_capital and point2_label:
        labels.append(("point2", float(point2_lon), float(point2_lat), str(point2_label)))
        label_base_sizes["point2"] = max(3.0, float(label_size) - 6.0)

    # 5) Reservar area util para textos antes de posicionar os labels.
    base_limits: tuple[float, float, float, float] | None = None
    base_x_ratio = 0.0
    base_y_ratio = 0.0
    if labels:
        max_base_label_size = max(label_base_sizes.values(), default=float(label_size))
        base_limits, base_x_ratio, base_y_ratio = _prepare_map_axes_for_labels(
            fig=fig,
            ax=ax,
            label_texts=[text for _, _, _, text in labels],
            label_size=max_base_label_size,
        )

    # 6) Camadas do mapa: pontos de interesse, conexao e distancia opcional.
    ax.scatter(
        [point1_lon],
        [point1_lat],
        color=point_colors_by_point["point1"],
        s=point_size * 15,
        zorder=4,
    )
    if not is_capital:
        ax.scatter(
            [point2_lon],
            [point2_lat],
            color=point_colors_by_point["point2"],
            s=point_size * 15,
            edgecolors="white",
            linewidths=1.5,
            zorder=4.2,
        )
        ax.plot(
            [point1_lon, point2_lon],
            [point1_lat, point2_lat],
            color=line_color,
            linewidth=line_width,
            linestyle=line_type,
            zorder=3,
        )
        if show_distance:
            dist_m = _haversine_distance_m(point1_lat, point1_lon, point2_lat, point2_lon)
            if distance_unit == "km":
                label = f"{dist_m / 1000:.1f} km"
            else:
                label = f"{dist_m:.0f} m"
            mx = (point1_lon + point2_lon) / 2
            my = (point1_lat + point2_lat) / 2
            ax.text(
                mx,
                my,
                label,
                fontsize=label_size * 0.8,
                color=label_colors_by_point["point1"],
                ha="center",
                va="center",
                clip_on=False,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.95},
            )

    # 7) Busca iterativa do melhor layout de rótulos (margem, offset, wrap e fonte).
    drawn_label_artists: list[Any] = []
    if labels:
        best_layout: Optional[dict[str, Any]] = None
        drawn = False
        text_attempts: list[tuple[dict[str, float], dict[str, str]]] = []

        reference_base_size = max(label_base_sizes.values(), default=float(label_size))
        for attempted_reference_size in _map_label_size_attempts(reference_base_size):
            size_reduction = max(0.0, reference_base_size - float(attempted_reference_size))
            attempted_label_sizes = {
                point_name: max(3.0, float(base_size) - size_reduction)
                for point_name, base_size in label_base_sizes.items()
            }
            for variant in _map_label_text_variants(
                labels=labels, label_sizes=attempted_label_sizes
            ):
                text_attempts.append((attempted_label_sizes, variant))

        for attempt_idx, (attempted_label_sizes, variant) in enumerate(text_attempts):
            if drawn:
                break
            for margin_step in range(_MAP_LABEL_MARGIN_ATTEMPTS):
                if base_limits is not None:
                    _set_map_axes_limits_with_padding(
                        ax=ax,
                        base_limits=base_limits,
                        x_pad_ratio=base_x_ratio + (0.05 * margin_step),
                        y_pad_ratio=base_y_ratio + (0.03 * margin_step),
                    )
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
                attempt = _build_map_label_layout_attempt(
                    ax=ax,
                    renderer=renderer,
                    labels=labels,
                    label_texts=variant,
                    point1_lat=point1_lat,
                    point1_lon=point1_lon,
                    point2_lat=point2_lat,
                    point2_lon=point2_lon,
                    label_sizes=attempted_label_sizes,
                    base_label_sizes=label_base_sizes,
                    label_colors=label_colors_by_point,
                    spread_multiplier=1.0 + (0.20 * margin_step),
                    is_capital=is_capital,
                    style_penalty=float(attempt_idx * 120) + float(margin_step * 35),
                )
                if attempt is None:
                    continue
                if best_layout is None or float(attempt["penalty"]) < float(best_layout["penalty"]):
                    best_layout = attempt
                if _map_layout_is_fully_visible(attempt):
                    drawn_label_artists = _draw_map_layout(
                        ax=ax, layout=attempt, label_colors=label_colors_by_point
                    )
                    drawn = True
                    break

        if not drawn:
            if best_layout is not None:
                drawn_label_artists = _draw_map_layout(
                    ax=ax, layout=best_layout, label_colors=label_colors_by_point
                )
            else:
                for point_name, lon, lat, text in labels:
                    drawn_label_artists.append(
                        _draw_map_label(
                            ax=ax,
                            text=_normalize_map_label_text(text),
                            candidate={"x": lon, "y": lat, "ha": "left", "va": "bottom"},
                            label_size=label_base_sizes.get(point_name, float(label_size)),
                            label_color=str(
                                label_colors_by_point.get(point_name, _MAP_MUNICIPALITY_COLOR)
                            ),
                            path_effects_style=_map_label_path_effects(point_name),
                        )
                    )

        # 8) Ajuste final pos-render: garante rótulos dentro da area visivel e sem sobreposicao forte.
        if drawn_label_artists:
            _resolve_drawn_map_labels_visibility(fig=fig, ax=ax, text_artists=drawn_label_artists)

    # 9) Tema e marcadores tecnicos do grafico.
    theme_atm_void(ax)
    # 10) Fundo dedicado somente ao mapa; SVG externo permanece transparente.
    ax.set_facecolor(resolved_map_background_color)
    fig.patch.set_facecolor("none")
    fig.patch.set_alpha(0.0)
    add_graph_markers(ax, "state_map")
    return fig


def plot_serie_temporal_multiplas_linhas(
    data: Any,
    x_col: str = "ano",
    y_col: str = "valor",
    group_col: str = "categoria",
    colors: Optional[Dict[str, str]] = None,
    caption_text: Optional[str] = None,
    y_limits: tuple[float, float] = (0, 100),
    path_if_empty: str | Path | None = None,
    legend_position: str = "right",
    custom_legend_labels: Optional[Dict[str, str]] = None,
    label_strategy: str = "none",
    label_format: str = "percent",
    label_decimal_places: int = 0,
    show_x_axis: bool = True,
    show_y_axis: bool = True,
    axis_text_size: float = AXIS_SIZE,
    label_size: float = LABEL_SIZE,
    show_grid: bool = False,
    point_size: float = 2.5,
    marker_alpha: float = 1.0,
    line_size: float = 1.2,
    vjust: float = -0.6,
    label_offset: float = 0.5,
    label_formatter: Optional[Callable[[float], str]] = None,
    label_colors: Optional[Dict[str, str]] = None,
    label_fontfamily: Optional[str] = None,
    fill_between: bool = False,
    fill_between_colors: Optional[Dict[str, str]] = None,
    fill_between_alpha: float = 0.15,
    fill_between_y2: float = 0.0,
    x_tick_stride: int | None = None,
    expand_y_for_labels: bool = True,
) -> Optional[plt.Figure]:
    if not is_data_valid(data, path_if_empty):
        return None
    df = _to_dataframe(data)
    df[x_col] = pd.to_numeric(df[x_col], errors="coerce")
    df[y_col] = pd.to_numeric(df[y_col], errors="coerce")
    df = df.dropna(subset=[x_col, group_col])
    if df.empty:
        return None

    years = sorted(df[x_col].dropna().unique().tolist())
    if x_tick_stride is not None:
        stride = max(1, int(x_tick_stride))
        breaks_x = years[::stride]
    else:
        breaks_x = years[::2] if len(years) > 10 else years
    groups = list(dict.fromkeys(df[group_col].astype(str).tolist()))
    palette = colors or {grp: None for grp in groups}
    label_palette = label_colors or {}
    label_family = label_fontfamily or get_chart_font_family()
    fill_palette = fill_between_colors or {}

    fig, ax = plt.subplots(figsize=(10, 5))
    for grp in groups:
        sub = df[df[group_col].astype(str) == grp].sort_values(x_col)
        color = palette.get(grp)
        label_color = label_palette.get(grp, color if color is not None else "black")
        (line,) = ax.plot(
            sub[x_col],
            sub[y_col],
            linewidth=line_size,
            marker="o",
            markersize=point_size,
            label=(custom_legend_labels or {}).get(grp, grp),
            color=color,
        )
        marker_alpha_clamped = max(0.0, min(1.0, float(marker_alpha)))
        if marker_alpha_clamped < 1.0:
            marker_rgba = to_rgba(line.get_color(), alpha=marker_alpha_clamped)
            line.set_markerfacecolor(marker_rgba)
            line.set_markeredgecolor(marker_rgba)
        if fill_between and not sub.empty:
            area_color = fill_palette.get(grp, color if color is not None else "#0095DA")
            ax.fill_between(
                sub[x_col].to_numpy(dtype=float),
                sub[y_col].to_numpy(dtype=float),
                fill_between_y2,
                color=area_color,
                alpha=fill_between_alpha,
            )

        if label_strategy == "last" and not sub.empty:
            row = sub.loc[sub[x_col].idxmax()]
            formatted_value = (
                label_formatter(float(row[y_col]))
                if label_formatter is not None
                else _format_label(float(row[y_col]), label_format, label_decimal_places)
            )
            ax.text(
                float(row[x_col]),
                float(row[y_col]) + vjust,
                formatted_value,
                color=label_color,
                fontsize=label_size,
                fontfamily=label_family,
                ha="center",
            )
        elif label_strategy == "all":
            for _, row in sub.dropna(subset=[y_col]).iterrows():
                formatted_value = (
                    label_formatter(float(row[y_col]))
                    if label_formatter is not None
                    else _format_label(float(row[y_col]), label_format, label_decimal_places)
                )
                ax.text(
                    float(row[x_col]),
                    float(row[y_col]) + label_offset,
                    formatted_value,
                    color=label_color,
                    fontsize=label_size,
                    fontfamily=label_family,
                    ha="center",
                )

    ax.set_ylim(*y_limits)
    ax.set_xticks(breaks_x)
    if label_strategy != "none" and expand_y_for_labels:
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, ymax * 1.12)
    ax.tick_params(axis="x", labelsize=axis_text_size, labelbottom=show_x_axis)
    ax.tick_params(axis="y", labelsize=axis_text_size, labelleft=show_y_axis)
    apply_grid_theme(ax, show_grid)
    theme_atm_base(ax, base_size=axis_text_size)

    loc_map = {
        "right": "center right",
        "left": "center left",
        "top": "upper center",
        "bottom": "lower center",
        "none": None,
    }
    loc = loc_map.get(legend_position, "center right")
    if loc is None:
        leg = ax.get_legend()
        if leg:
            leg.remove()
    else:
        ax.legend(loc=loc, frameon=False)

    if caption_text:
        fig.text(0.5, 0.02, caption_text, ha="center", va="bottom", fontsize=AXIS_SIZE)

    add_graph_markers(ax, "serie_temporal_multiplas_linhas")
    return fig
