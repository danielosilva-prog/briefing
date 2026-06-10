"""Map chart for municipality and UF capital location."""

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
plot_state_map_with_points = _helpers.plot_state_map_with_points
get_image_dimensions = _image_dimensions.get_image_dimensions


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read designer reference image dimensions and return matplotlib figsize (inches)."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


_MAP_DESIGNER_FIGSIZE = _designer_figsize_inches("template/assets/charts/Map.svg")


def _resolve_map_figsize(ctx: ChartContext) -> tuple[float, float]:
    """
    Resolve map size using designer dimensions as source of truth.

    If context size diverges from the expected designer size, prefer the
    designer reference to preserve layout consistency in the final PDF.
    """
    requested = tuple(float(value) for value in ctx.figsize)
    designer = tuple(float(value) for value in _MAP_DESIGNER_FIGSIZE)
    if len(requested) == 2 and all(abs(req - des) <= 1e-6 for req, des in zip(requested, designer)):
        return requested
    return designer


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize map coordinates used by the map helper."""
    required = {"UF", "municipioLat", "municipioLon", "municipioLatCap", "municipioLonCap"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes para gráfico de mapa: {sorted(missing)}")

    data = df.copy()
    data["UF"] = data["UF"].astype(str).str.strip().str.upper()
    data["municipioNome"] = (
        data.get("municipioNome", pd.Series(index=data.index, dtype="object"))
        .fillna("")
        .astype(str)
        .str.strip()
    )
    data["nomeCapital"] = (
        data.get("nomeCapital", pd.Series(index=data.index, dtype="object"))
        .fillna("")
        .astype(str)
        .str.strip()
    )

    for col in ("municipioLat", "municipioLon", "municipioLatCap", "municipioLonCap"):
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(
        subset=["municipioLat", "municipioLon", "municipioLatCap", "municipioLonCap"]
    )
    data = data[data["UF"] != ""]
    if data.empty:
        return data

    row = data.iloc[[0]].copy()
    row["isCapital"] = (
        row["municipioLat"].astype(float) == row["municipioLatCap"].astype(float)
    ) & (row["municipioLon"].astype(float) == row["municipioLonCap"].astype(float))
    return row


def _build_chart_spec(data: pd.DataFrame, ctx: ChartContext) -> dict[str, object]:
    """Build plot_state_map_with_points kwargs."""
    row = data.iloc[0]
    municipio_label = str(row["municipioNome"]).strip() or None
    capital_label = str(row["nomeCapital"]).strip() or None
    map_figsize = _resolve_map_figsize(ctx)

    return {
        "state_code": str(row["UF"]).strip(),
        "point1_lat": float(row["municipioLat"]),
        "point1_lon": float(row["municipioLon"]),
        "point1_label": municipio_label,
        "point2_lat": float(row["municipioLatCap"]),
        "point2_lon": float(row["municipioLonCap"]),
        "point2_label": capital_label,
        "border_color": "#183EFF",
        "point_size": 7.8,
        "label_size": 26.0,
        "is_capital": bool(row["isCapital"]),
        "figsize": map_figsize,
    }


@chart(
    "graficoMapaMunicipio",
    data="municipio_info",
    title="Mapa do município na UF",
    figsize=_MAP_DESIGNER_FIGSIZE,
)
def grafico_mapa_municipio(
    df: pd.DataFrame,
    ctx: ChartContext,
) -> plt.Figure | None:
    """Map with municipality and UF capital points."""
    if df is None or df.empty:
        return None

    data = _prepare_data(df)
    if data.empty:
        return None

    spec = _build_chart_spec(data, ctx)
    try:
        fig = plot_state_map_with_points(**spec)
    except Exception:
        # O pipeline central converte None em empty-state SVG padronizado.
        return None
    if fig is None:
        return None

    resolved_figsize = _resolve_map_figsize(ctx)
    fig.set_size_inches(*resolved_figsize, forward=True)
    fig.set_dpi(ctx.dpi)
    setattr(fig, "_schoolreport_preserve_svg_size", True)
    setattr(
        fig,
        "_schoolreport_expected_svg_size_inches",
        (float(resolved_figsize[0]), float(resolved_figsize[1])),
    )
    return fig
