"""Utilities to read image dimensions and convert them to inches."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET

DEFAULT_DPI = 120.0
SVG_DPI = 96.0


@dataclass(frozen=True)
class ImageDimensions:
    """Physical and pixel dimensions for a reference image."""

    width_in: float
    height_in: float
    dpi_x: float
    dpi_y: float
    width_px: float
    height_px: float
    path: Path


def _to_inches(raw_value: str, default_px_dpi: float = SVG_DPI) -> float:
    match = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z%]*)\s*$", str(raw_value))
    if not match:
        raise ValueError(f"Dimensao invalida: {raw_value}")

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit in {"", "px"}:
        return value / default_px_dpi
    if unit == "pt":
        return value / 72.0
    if unit == "cm":
        return value / 2.54
    if unit == "mm":
        return value / 25.4
    if unit == "in":
        return value

    raise ValueError(f"Unidade nao suportada: {unit}")


def _svg_dimensions(path: Path) -> ImageDimensions:
    root = ET.parse(path).getroot()
    width_raw = root.attrib.get("width")
    height_raw = root.attrib.get("height")

    if width_raw and height_raw:
        width_in = _to_inches(width_raw, default_px_dpi=SVG_DPI)
        height_in = _to_inches(height_raw, default_px_dpi=SVG_DPI)
        width_px = width_in * SVG_DPI
        height_px = height_in * SVG_DPI
        return ImageDimensions(
            width_in=width_in,
            height_in=height_in,
            dpi_x=SVG_DPI,
            dpi_y=SVG_DPI,
            width_px=width_px,
            height_px=height_px,
            path=path,
        )

    view_box = root.attrib.get("viewBox", "").strip()
    if view_box:
        parts = view_box.replace(",", " ").split()
        if len(parts) == 4:
            width_px = float(parts[2])
            height_px = float(parts[3])
            return ImageDimensions(
                width_in=width_px / SVG_DPI,
                height_in=height_px / SVG_DPI,
                dpi_x=SVG_DPI,
                dpi_y=SVG_DPI,
                width_px=width_px,
                height_px=height_px,
                path=path,
            )

    raise ValueError(f"Não foi possível ler dimensões do SVG: {path}")


def _raster_dimensions(path: Path, default_dpi: float) -> ImageDimensions:
    try:
        from PIL import Image  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Leitura de imagens raster requer Pillow (pip install pillow)."
        ) from exc

    with Image.open(path) as img:
        width_px, height_px = img.size
        dpi = img.info.get("dpi")

    if isinstance(dpi, tuple) and len(dpi) >= 2:
        dpi_x = float(dpi[0]) if dpi[0] else default_dpi
        dpi_y = float(dpi[1]) if dpi[1] else default_dpi
    elif isinstance(dpi, (int, float)) and float(dpi) > 0:
        dpi_x = float(dpi)
        dpi_y = float(dpi)
    else:
        dpi_x = default_dpi
        dpi_y = default_dpi

    return ImageDimensions(
        width_in=float(width_px) / dpi_x,
        height_in=float(height_px) / dpi_y,
        dpi_x=dpi_x,
        dpi_y=dpi_y,
        width_px=float(width_px),
        height_px=float(height_px),
        path=path,
    )


def get_image_dimensions(
    image_path: str | Path,
    *,
    base_dir: str | Path | None = None,
    default_dpi: float = DEFAULT_DPI,
) -> ImageDimensions:
    """
    Read an image and return physical dimensions in inches.

    Mirrors the R helper behavior: if raster DPI metadata is missing,
    falls back to `default_dpi`.
    """
    raw_path = Path(image_path)
    resolved = raw_path if raw_path.is_absolute() else (Path(base_dir or Path.cwd()) / raw_path)
    full_path = resolved.resolve(strict=True)

    suffix = full_path.suffix.lower()
    if suffix == ".svg":
        return _svg_dimensions(full_path)

    return _raster_dimensions(full_path, default_dpi=default_dpi)
