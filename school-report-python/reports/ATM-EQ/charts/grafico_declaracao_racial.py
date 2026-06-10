"""Chart for historical racial declaration series."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Callable

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
        raise ImportError(f"Nao foi possivel carregar modulo: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_helpers = _load_local_module("atm_eq_chart_helpers", "chart_helpers.py")
_image_dimensions = _load_local_module("atm_eq_image_dimensions", "image_dimensions.py")
plot_serie_temporal_multiplas_linhas = _helpers.plot_serie_temporal_multiplas_linhas
AXIS_SIZE = _helpers.AXIS_SIZE
LABEL_SIZE = _helpers.LABEL_SIZE
ensure_rawline_font_available = _helpers.ensure_rawline_font_available
get_chart_font_family = _helpers.get_chart_font_family
get_image_dimensions = _image_dimensions.get_image_dimensions


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read designer reference image dimensions and return matplotlib figsize (inches)."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize data for racial declaration time-series chart."""
    required = {"anoReferencia", "percentualDeclaracaoRacial"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes para grafico: {sorted(missing)}")

    data = df.copy()
    data["anoReferencia"] = pd.to_numeric(data["anoReferencia"], errors="coerce")
    data["percentualDeclaracaoRacial"] = pd.to_numeric(
        data["percentualDeclaracaoRacial"], errors="coerce"
    ).fillna(0.0)
    data = data.dropna(subset=["anoReferencia"]).sort_values("anoReferencia")
    if data.empty:
        return data
    data["anoReferencia"] = data["anoReferencia"].astype(int)
    return data


def _build_chart_spec(
    data: pd.DataFrame,
    label_formatter: Callable[[float], str],
) -> dict[str, object]:
    """Build helper spec for the time-series line + filled area rendering."""
    plot_data = data.copy()
    plot_data["serie"] = "DeclaracaoRacial"
    return {
        "data": plot_data,
        "x_col": "anoReferencia",
        "y_col": "percentualDeclaracaoRacial",
        "group_col": "serie",
        "colors": {"DeclaracaoRacial": "#00695C"},
        "y_limits": (0, 100),
        "legend_position": "none",
        "label_strategy": "none",
        "label_formatter": label_formatter,
        "label_offset": 2.0,
        "label_colors": {"DeclaracaoRacial": "#00352E"},
        "label_fontfamily": get_chart_font_family(),
        "show_x_axis": True,
        "show_y_axis": False,
        "axis_text_size": AXIS_SIZE,
        "label_size": LABEL_SIZE + 4,
        "show_grid": False,
        "point_size": 2.5,
        "marker_alpha": 0.85,
        "line_size": 2.2,
        "fill_between": True,
        "fill_between_colors": {"DeclaracaoRacial": "#26A69A"},
        "fill_between_alpha": 0.15,
        "x_tick_stride": 1,
        "expand_y_for_labels": False,
    }


@chart(
    "graficoDeclaracaoRacial",
    data="grafico_declaracao_racial",
    title="Série histórica do percentual de declaração racial",
    figsize=_designer_figsize_inches("template/assets/charts/P4-G3.svg"),
)
def grafico_declaracao_racial(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Line chart for historical racial declaration percentage."""
    if df is None or df.empty:
        return None

    data = _prepare_data(df)
    if data.empty:
        return None

    def custom_percent_formatter(value: float) -> str:
        numeric_value = float(value)
        # Rótulos em 100% com ",0" tendem a ocupar mais largura e sobrepor elementos.
        # Mantemos "100%" para legibilidade sem alterar o formatter global do contexto.
        # A tolerância evita erro de comparação com float (ex.: 99.9999999998).
        if abs(numeric_value - 100.0) < 1e-6:
            return "100%"
        return ctx.format_percent(numeric_value, 1)

    ensure_rawline_font_available(strict=False)
    spec = _build_chart_spec(data, custom_percent_formatter)
    fig = plot_serie_temporal_multiplas_linhas(**spec)
    if fig is None:
        return None

    fig.set_size_inches(*ctx.figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    ax = fig.axes[0]
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title("")
    ax.grid(False)
    ax.set_xticks(data["anoReferencia"].to_numpy(dtype=int))
    ax.set_yticks([])
    ax.tick_params(
        axis="x",
        bottom=False,
        top=False,
        labelbottom=True,
    )
    ax.tick_params(
        axis="y",
        left=False,
        right=False,
        labelleft=False,
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    selected_years = {2007, 2011, 2015, 2019, 2022, 2024, 2025}
    label_rows = data[data["anoReferencia"].isin(selected_years)].copy()
    for _, row in label_rows.iterrows():
        ax.text(
            float(row["anoReferencia"]),
            float(row["percentualDeclaracaoRacial"]) + 2.0,
            custom_percent_formatter(float(row["percentualDeclaracaoRacial"])),
            color="#00352E",
            fontsize=LABEL_SIZE + 4,
            fontfamily=get_chart_font_family(),
            ha="center",
            va="bottom",
        )
    fig.tight_layout()
    return fig
