"""Empty-state chart asset for the infraestrutura basica section."""

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
        raise ImportError(f"Nao foi possivel carregar modulo: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_image_dimensions = _load_local_module("atm_eq_image_dimensions", "image_dimensions.py")
get_image_dimensions = _image_dimensions.get_image_dimensions


def _designer_figsize_inches(image_path: str | Path) -> tuple[float, float]:
    """Read designer reference image dimensions and return matplotlib figsize (inches)."""
    reference_image_path = Path(image_path)
    if not reference_image_path.is_absolute():
        reference_image_path = (Path(__file__).parent.parent / reference_image_path).resolve()
    dims = get_image_dimensions(reference_image_path)
    return (dims.width_in, dims.height_in)


@chart(
    "graficoInfraestruturaBasicaEmptyState",
    data=None,
    title="Infraestrutura basica - estado vazio",
    figsize=_designer_figsize_inches("template/assets/charts/P5-G2.svg"),
)
def grafico_infraestrutura_basica_empty_state(
    _: pd.DataFrame,
    __: ChartContext,
) -> plt.Figure | None:
    """Delegate the visual empty state to the central ATM-EQ chart pipeline."""
    return None
