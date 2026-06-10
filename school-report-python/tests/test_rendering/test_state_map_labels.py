"""Regression tests for map label readability in ATM-EQ chart helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import pytest

from schoolreport.rendering.charts import ChartGenerator


def _load_atm_eq_chart_helpers():
    module_path = (
        Path(__file__).resolve().parents[2] / "reports" / "ATM-EQ" / "charts" / "chart_helpers.py"
    )
    spec = importlib.util.spec_from_file_location("atm_eq_chart_helpers_for_tests", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load chart helpers: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeStateGeometry:
    """Simple geometry stub used to avoid geobr dependency in unit tests."""

    def to_crs(self, _epsg: int):
        return self

    def plot(self, ax, color=None, edgecolor=None, linewidth=None):  # noqa: ANN001
        del color, edgecolor, linewidth
        ax.set_xlim(-50.0, -40.0)
        ax.set_ylim(-20.0, -10.0)
        return ax


def _overlap_area(bbox1, bbox2) -> float:  # noqa: ANN001
    x0 = max(float(bbox1.x0), float(bbox2.x0))
    y0 = max(float(bbox1.y0), float(bbox2.y0))
    x1 = min(float(bbox1.x1), float(bbox2.x1))
    y1 = min(float(bbox1.y1), float(bbox2.y1))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _outside_area(inner: Bbox, outer: Bbox) -> float:
    overlap_x0 = max(float(inner.x0), float(outer.x0))
    overlap_y0 = max(float(inner.y0), float(outer.y0))
    overlap_x1 = min(float(inner.x1), float(outer.x1))
    overlap_y1 = min(float(inner.y1), float(outer.y1))
    if overlap_x1 <= overlap_x0 or overlap_y1 <= overlap_y0:
        return max(0.0, float(inner.width)) * max(0.0, float(inner.height))
    inside = (overlap_x1 - overlap_x0) * (overlap_y1 - overlap_y0)
    return max(0.0, (max(0.0, float(inner.width)) * max(0.0, float(inner.height))) - inside)


def _normalize_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def _svg_length_to_points(raw_value: str) -> float | None:
    match = re.match(
        r"^\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*([a-zA-Z]*)\s*$",
        str(raw_value),
    )
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).lower()
    if unit in {"", "pt"}:
        return value
    if unit == "px":
        return value * (72.0 / 96.0)
    if unit == "in":
        return value * 72.0
    if unit == "cm":
        return value * (72.0 / 2.54)
    if unit == "mm":
        return value * (72.0 / 25.4)
    return None


def _extract_svg_dimensions_points(svg_content: str) -> tuple[float, float]:
    match = re.search(
        r"<svg[^>]*\swidth=[\"']([^\"']+)[\"'][^>]*\sheight=[\"']([^\"']+)[\"']",
        svg_content,
        re.IGNORECASE,
    )
    assert match is not None, "SVG width/height not found."
    width_pt = _svg_length_to_points(match.group(1))
    height_pt = _svg_length_to_points(match.group(2))
    assert width_pt is not None, f"Unsupported SVG width unit: {match.group(1)}"
    assert height_pt is not None, f"Unsupported SVG height unit: {match.group(2)}"
    return (float(width_pt), float(height_pt))


def _find_text_artist(ax, expected_text: str):  # noqa: ANN001
    normalized_expected = _normalize_text(expected_text)
    for text_artist in ax.texts:
        if _normalize_text(text_artist.get_text()) == normalized_expected:
            return text_artist
    return None


def _color_to_hex(color: object) -> str:
    return str(mcolors.to_hex(mcolors.to_rgba(color), keep_alpha=False)).lower()


def _find_point_collection(
    ax, lon: float, lat: float, tol: float = 1e-6
) -> tuple[object, int] | None:  # noqa: ANN001
    for collection in ax.collections:
        offsets = collection.get_offsets()
        if offsets is None or len(offsets) == 0:
            continue
        facecolors = collection.get_facecolors()
        if facecolors is None or len(facecolors) == 0:
            continue
        for idx, offset in enumerate(offsets):
            if (
                abs(float(offset[0]) - float(lon)) <= tol
                and abs(float(offset[1]) - float(lat)) <= tol
            ):
                color_idx = min(idx, len(facecolors) - 1)
                return (collection, color_idx)
    return None


def _find_point_color_hex(
    ax, lon: float, lat: float, tol: float = 1e-6
) -> str | None:  # noqa: ANN001
    match = _find_point_collection(ax=ax, lon=lon, lat=lat, tol=tol)
    if match is None:
        return None
    collection, color_idx = match
    return _color_to_hex(collection.get_facecolors()[color_idx])


def _find_point_edge_color_hex(
    ax, lon: float, lat: float, tol: float = 1e-6
) -> str | None:  # noqa: ANN001
    match = _find_point_collection(ax=ax, lon=lon, lat=lat, tol=tol)
    if match is None:
        return None
    collection, color_idx = match
    edgecolors = collection.get_edgecolors()
    if edgecolors is None or len(edgecolors) == 0:
        return None
    edge_idx = min(color_idx, len(edgecolors) - 1)
    return _color_to_hex(edgecolors[edge_idx])


def _find_point_linewidth(
    ax, lon: float, lat: float, tol: float = 1e-6
) -> float | None:  # noqa: ANN001
    match = _find_point_collection(ax=ax, lon=lon, lat=lat, tol=tol)
    if match is None:
        return None
    collection, color_idx = match
    linewidths = collection.get_linewidths()
    if linewidths is None or len(linewidths) == 0:
        return None
    width_idx = min(color_idx, len(linewidths) - 1)
    return float(linewidths[width_idx])


@pytest.fixture
def helpers():
    return _load_atm_eq_chart_helpers()


def _assert_label_fully_visible(fig, ax, label_text: str):  # noqa: ANN001
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    artist = _find_text_artist(ax, label_text)
    assert artist is not None, f"Label '{label_text}' was not rendered."
    assert _normalize_text(artist.get_text()) == _normalize_text(label_text)
    assert artist.get_clip_on() is False
    outside = _outside_area(
        artist.get_window_extent(renderer=renderer),
        ax.get_window_extent(renderer=renderer),
    )
    assert outside <= 1.0
    return artist


def test_map_labels_use_dynamic_offsets_to_avoid_overlap(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    municipio_label = "Municipio Teste"
    capital_label = "Capital Teste"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-15.0,
        point1_lon=-46.0,
        point1_label=municipio_label,
        point2_lat=-15.08,
        point2_lon=-45.92,
        point2_label=capital_label,
        label_size=20.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        capital_artist = _assert_label_fully_visible(fig, ax, capital_label)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        overlap = _overlap_area(
            municipio_artist.get_window_extent(renderer=renderer),
            capital_artist.get_window_extent(renderer=renderer),
        )
        assert overlap <= 1.0
    finally:
        plt.close(fig)


def test_map_labels_keep_both_labels_visible_for_very_long_names(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    municipio_label = "Municipio Pesquisado Com Nome Muito Extenso Para Um Mapa Pequeno"
    capital_label = "Capital Com Nome Muito Extenso Em Area De Forte Sobreposicao"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-10.10,
        point1_lon=-40.12,
        point1_label=municipio_label,
        point2_lat=-10.11,
        point2_lon=-40.10,
        point2_label=capital_label,
        label_size=26.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        capital_artist = _assert_label_fully_visible(fig, ax, capital_label)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        overlap = _overlap_area(
            municipio_artist.get_window_extent(renderer=renderer),
            capital_artist.get_window_extent(renderer=renderer),
        )
        assert overlap <= 1.0
    finally:
        plt.close(fig)


@pytest.mark.parametrize(
    (
        "code_muni",
        "municipio_label",
        "point1_lat",
        "point1_lon",
        "point2_lat",
        "point2_lon",
    ),
    [
        ("5105507", "Vila Bela da Santíssima Trindade", -18.70, -49.70, -12.20, -41.20),
        ("5101837", "Boa Esperança do Norte - MT", -10.60, -45.80, -17.40, -41.00),
        ("3166600", "Serra da Saudade", -19.30, -40.80, -12.20, -48.00),
        ("1200328", "Jordão - AC", -12.50, -49.30, -18.00, -41.30),
        ("3305158", "São José do Vale do Rio Preto", -15.10, -40.50, -11.20, -48.50),
    ],
    ids=[
        "5105507_vila_bela_da_santissima_trindade",
        "5101837_boa_esperanca_do_norte_mt",
        "3166600_serra_da_saudade",
        "1200328_jordao_ac",
        "3305158_sao_jose_do_vale_do_rio_preto",
    ],
)
def test_required_municipalities_render_full_labels_without_clipping(
    monkeypatch,
    helpers,
    code_muni: str,
    municipio_label: str,
    point1_lat: float,
    point1_lon: float,
    point2_lat: float,
    point2_lon: float,
):
    del code_muni
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    capital_label = "Capital da UF"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=point1_lat,
        point1_lon=point1_lon,
        point1_label=municipio_label,
        point2_lat=point2_lat,
        point2_lon=point2_lon,
        point2_label=capital_label,
        label_size=26.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        capital_artist = _assert_label_fully_visible(fig, ax, capital_label)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        overlap = _overlap_area(
            municipio_artist.get_window_extent(renderer=renderer),
            capital_artist.get_window_extent(renderer=renderer),
        )
        assert overlap <= 1.0
    finally:
        plt.close(fig)


def test_jordao_ac_critical_case_keeps_full_label_visible(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    municipio_label = "Jordão - AC"
    capital_label = "Rio Branco - AC"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-10.02,
        point1_lon=-49.98,
        point1_label=municipio_label,
        point2_lat=-19.90,
        point2_lon=-40.20,
        point2_label=capital_label,
        label_size=26.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        capital_artist = _assert_label_fully_visible(fig, ax, capital_label)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        overlap = _overlap_area(
            municipio_artist.get_window_extent(renderer=renderer),
            capital_artist.get_window_extent(renderer=renderer),
        )
        assert overlap <= 1.0
    finally:
        plt.close(fig)


def test_non_capital_highlights_municipality_by_reducing_capital_font(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    municipio_label = "Município Referência"
    capital_label = "Capital Referência"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-14.5,
        point1_lon=-48.8,
        point1_label=municipio_label,
        point2_lat=-13.2,
        point2_lon=-42.0,
        point2_label=capital_label,
        label_size=26.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        capital_artist = _assert_label_fully_visible(fig, ax, capital_label)
        size_delta = float(municipio_artist.get_fontsize()) - float(capital_artist.get_fontsize())
        assert size_delta == pytest.approx(6.0, abs=0.05)
    finally:
        plt.close(fig)


def test_non_capital_uses_distinct_colors_for_municipality_and_capital(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    municipio_label = "Municipio Referencia"
    capital_label = "Capital Referencia"
    point1_lat = -14.5
    point1_lon = -48.8
    point2_lat = -13.2
    point2_lon = -42.0
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=point1_lat,
        point1_lon=point1_lon,
        point1_label=municipio_label,
        point2_lat=point2_lat,
        point2_lon=point2_lon,
        point2_label=capital_label,
        label_size=26.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        capital_artist = _assert_label_fully_visible(fig, ax, capital_label)

        expected_municipio_color = _color_to_hex(helpers._MAP_MUNICIPALITY_COLOR)
        expected_capital_point_color = _color_to_hex(helpers._MAP_CAPITAL_POINT_COLOR)
        expected_capital_label_color = _color_to_hex(
            helpers._default_capital_label_color(helpers._MAP_STATE_FILL_COLOR)
        )

        assert _color_to_hex(municipio_artist.get_color()) == expected_municipio_color
        assert _color_to_hex(capital_artist.get_color()) == expected_capital_label_color
        assert _color_to_hex(municipio_artist.get_color()) != _color_to_hex(
            capital_artist.get_color()
        )

        municipio_point_color = _find_point_color_hex(ax, lon=point1_lon, lat=point1_lat)
        capital_point_color = _find_point_color_hex(ax, lon=point2_lon, lat=point2_lat)
        assert municipio_point_color == expected_municipio_color
        assert capital_point_color == expected_capital_point_color
        assert municipio_point_color != capital_point_color

        capital_point_edge_color = _find_point_edge_color_hex(ax, lon=point2_lon, lat=point2_lat)
        capital_point_linewidth = _find_point_linewidth(ax, lon=point2_lon, lat=point2_lat)
        assert capital_point_edge_color == "#ffffff"
        assert capital_point_linewidth == pytest.approx(1.5, abs=0.05)

        assert len(capital_artist.get_path_effects()) > 0
    finally:
        plt.close(fig)


def test_map_uses_configured_background_color(monkeypatch, helpers):
    captured_state_plot: dict[str, object] = {}

    class _RecordingStateGeometry(_FakeStateGeometry):
        def plot(self, ax, color=None, edgecolor=None, linewidth=None):  # noqa: ANN001
            captured_state_plot["color"] = color
            captured_state_plot["edgecolor"] = edgecolor
            captured_state_plot["linewidth"] = linewidth
            return super().plot(ax, color=color, edgecolor=edgecolor, linewidth=linewidth)

    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _RecordingStateGeometry(),
    )

    map_background_color = "#dce8ff"
    state_fill_color = "#ffb300"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-14.5,
        point1_lon=-48.8,
        point1_label="Municipio",
        point2_lat=-13.2,
        point2_lon=-42.0,
        point2_label="Capital",
        label_size=26.0,
        map_background_color=map_background_color,
        state_fill_color=state_fill_color,
        is_capital=False,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        assert _color_to_hex(ax.get_facecolor()) == map_background_color
        assert captured_state_plot.get("color") == state_fill_color
        assert float(fig.get_facecolor()[3]) == pytest.approx(0.0, abs=0.01)

        svg = ChartGenerator()._fig_to_svg(fig).decode("utf-8").lower()
        patch1 = re.search(
            r"<g id=\"patch_1\">.*?<path[^>]*style=\"([^\"]+)\"",
            svg,
            re.DOTALL,
        )
        assert patch1 is not None
        assert "fill: none" in patch1.group(1)

        patch2 = re.search(
            r"<g id=\"patch_2\">.*?<path[^>]*style=\"([^\"]+)\"",
            svg,
            re.DOTALL,
        )
        assert patch2 is not None
        assert map_background_color in patch2.group(1)
    finally:
        plt.close(fig)


def test_fill_color_legacy_alias_still_sets_map_background(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    legacy_background = "#cfe8d8"
    with pytest.warns(DeprecationWarning, match="fill_color"):
        fig = helpers.plot_state_map_with_points(
            state_code="SP",
            point1_lat=-14.0,
            point1_lon=-45.0,
            point1_label="Cidade Capital",
            is_capital=True,
            figsize=(5.0, 5.0),
            fill_color=legacy_background,
        )

    try:
        ax = fig.axes[0]
        assert _color_to_hex(ax.get_facecolor()) == legacy_background
        assert float(fig.get_facecolor()[3]) == pytest.approx(0.0, abs=0.01)
    finally:
        plt.close(fig)


def test_capital_case_keeps_default_label_size(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    municipio_label = "Cidade Capital"
    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-14.0,
        point1_lon=-45.0,
        point1_label=municipio_label,
        label_size=26.0,
        is_capital=True,
        figsize=(5.0, 5.0),
    )

    try:
        ax = fig.axes[0]
        municipio_artist = _assert_label_fully_visible(fig, ax, municipio_label)
        assert float(municipio_artist.get_fontsize()) == pytest.approx(26.0, abs=0.05)
    finally:
        plt.close(fig)


def test_map_svg_export_preserves_exact_designer_dimensions(monkeypatch, helpers):
    monkeypatch.setattr(
        helpers,
        "get_cached_state_geometry",
        lambda *_args, **_kwargs: _FakeStateGeometry(),
    )

    fig = helpers.plot_state_map_with_points(
        state_code="SP",
        point1_lat=-10.02,
        point1_lon=-49.98,
        point1_label="Jordão - AC",
        point2_lat=-19.90,
        point2_lon=-40.20,
        point2_label="Rio Branco - AC",
        label_size=26.0,
        is_capital=False,
        figsize=(5.0, 5.0),
    )
    fig.set_dpi(100)

    try:
        assert bool(getattr(fig, "_schoolreport_preserve_svg_size", False))
        svg = ChartGenerator()._fig_to_svg(fig).decode("utf-8")
        width_pt, height_pt = _extract_svg_dimensions_points(svg)
        assert width_pt == pytest.approx(360.0, abs=0.1)
        assert height_pt == pytest.approx(360.0, abs=0.1)

        ax = fig.axes[0]
        _assert_label_fully_visible(fig, ax, "Jordão - AC")
    finally:
        plt.close(fig)
