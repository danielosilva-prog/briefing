"""Utilities for writing chart SVGs to disk for Typst templates.

Custom executors generate charts as base64-encoded SVGs.  These need to be
decoded and persisted as files so that Typst ``image()`` calls can reference
them.  This module provides reusable helpers for that workflow, plus
placeholder generation for charts referenced in Typst pages but not yet
generated (e.g. because the underlying data was unavailable).
"""

import base64
import logging
import re
from pathlib import Path
from typing import Dict, Set

logger = logging.getLogger(__name__)

PLACEHOLDER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="280" viewBox="0 0 900 280">'
    '<rect width="900" height="280" fill="#F5F7FA"/>'
    '<rect x="20" y="20" width="860" height="240" fill="none" stroke="#D0D7DE" stroke-width="2"/>'
    '<text x="450" y="130" text-anchor="middle" font-family="Rawline, Arial, sans-serif" '
    'font-size="22" fill="#51606D">Gráfico indisponível</text>'
    '<text x="450" y="165" text-anchor="middle" font-family="Rawline, Arial, sans-serif" '
    'font-size="14" fill="#7A8693">Dados não fornecidos para esta visualização</text>'
    "</svg>"
)

_CHART_REF_PATTERN = re.compile(r"\.\./assets/charts/([A-Za-z0-9\-_]+\.(svg|png))")


def chart_key_to_filename(key: str) -> str:
    """Convert a chart data key to the SVG filename expected by Typst.

    Examples:
        >>> chart_key_to_filename("p1_g2")
        'P1-G2.svg'
        >>> chart_key_to_filename("p5_g_aux")
        'P5-G-AUX.svg'
    """
    return key.upper().replace("_", "-") + ".svg"


def write_charts_to_assets(
    charts: Dict[str, str],
    assets_dir: Path,
) -> Set[str]:
    """Decode base64 chart SVGs and write them to the assets/charts directory.

    Args:
        charts: Mapping of chart key to base64-encoded SVG string.
        assets_dir: Path to the report's ``template/assets`` directory.

    Returns:
        Set of filenames that were successfully written.
    """
    charts_dir = assets_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    written: Set[str] = set()
    for key, b64 in charts.items():
        filename = chart_key_to_filename(key)
        try:
            (charts_dir / filename).write_bytes(base64.b64decode(b64))
            written.add(filename)
            logger.debug(f"Wrote chart asset: {filename}")
        except Exception as exc:
            logger.warning(f"Failed to write chart {key} to {filename}: {exc}")

    return written


def ensure_placeholder_charts(
    pages_dir: Path,
    assets_dir: Path,
    generated: Set[str],
) -> None:
    """Scan Typst pages for chart references and create placeholders for missing ones.

    This prevents Typst compilation errors when a chart image is referenced
    but no data was available to generate it.

    Args:
        pages_dir: Path to the report's ``template/pages`` directory.
        assets_dir: Path to the report's ``template/assets`` directory.
        generated: Set of filenames that were already generated (skip these).
    """
    charts_dir = assets_dir / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    if not pages_dir.exists():
        return

    for page_file in pages_dir.glob("*.typ"):
        content = page_file.read_text(encoding="utf-8")
        for match in _CHART_REF_PATTERN.finditer(content):
            filename = match.group(1)
            svg_name = re.sub(r"\.(svg|png)$", ".svg", filename, flags=re.IGNORECASE)
            if svg_name in generated:
                continue
            svg_path = charts_dir / svg_name
            if svg_path.exists():
                continue
            svg_path.write_text(PLACEHOLDER_SVG, encoding="utf-8")
            logger.debug(f"Created placeholder chart asset: {svg_name}")
