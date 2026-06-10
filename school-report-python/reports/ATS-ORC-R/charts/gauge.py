"""Gauge chart generator for ATS-02 report.

Generates semicircular percentage gauge charts as SVG.
"""

import math
import base64
from typing import Optional


def generate_gauge_svg(
    value: float,
    max_value: float = 100.0,
    color: str = "#0095DA",
    background_color: str = "#D9D9D9",
    width: int = 153,
    height: int = 76,
) -> str:
    """Generate a semicircular gauge SVG.

    Args:
        value: Current value (0 to max_value)
        max_value: Maximum value for the gauge
        color: Color for the filled arc
        background_color: Color for the background arc
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG string
    """
    # Calculate percentage (0 to 1)
    percentage = min(max(value / max_value, 0.0), 1.0)

    # Calculate center and radius
    cx = width / 2
    cy = height  # Bottom center
    outer_radius = width / 2
    inner_radius = outer_radius - 20.0938  # Width of the arc

    # Background arc (full semicircle)
    background_path = _create_semicircle_path(cx, cy, outer_radius, inner_radius)

    # Value arc (partial semicircle based on percentage)
    # Angle goes from 180° (left) to 0° (right)
    # percentage = 1.0 means full semicircle (180°)
    # percentage = 0.0 means no arc
    end_angle = math.pi * (1 - percentage)  # radians
    value_path = _create_arc_path(cx, cy, outer_radius, inner_radius, math.pi, end_angle)

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="{background_path}" fill="{background_color}"/>
<path d="{value_path}" fill="{color}"/>
</svg>'''

    return svg


def _create_semicircle_path(cx: float, cy: float, outer_r: float, inner_r: float) -> str:
    """Create a full semicircular arc path (from 180° to 0°)."""
    # Outer arc: start at left, go to right
    outer_left_x = cx - outer_r
    outer_left_y = cy
    outer_right_x = cx + outer_r
    outer_right_y = cy

    # Inner arc: start at right, go to left
    inner_right_x = cx + inner_r
    inner_right_y = cy
    inner_left_x = cx - inner_r
    inner_left_y = cy

    path = (
        f"M {outer_left_x} {outer_left_y} "  # Move to outer left
        f"A {outer_r} {outer_r} 0 0 1 {outer_right_x} {outer_right_y} "  # Outer arc to right
        f"L {inner_right_x} {inner_right_y} "  # Line to inner right
        f"A {inner_r} {inner_r} 0 0 0 {inner_left_x} {inner_left_y} "  # Inner arc to left
        f"Z"  # Close path
    )

    return path


def _create_arc_path(
    cx: float, cy: float, outer_r: float, inner_r: float, start_angle: float, end_angle: float
) -> str:
    """Create a partial arc path from start_angle to end_angle (in radians).

    Args:
        cx, cy: Center coordinates
        outer_r, inner_r: Outer and inner radius
        start_angle: Start angle in radians (180° = π)
        end_angle: End angle in radians (0° = 0)
    """
    # Calculate outer arc endpoints
    outer_start_x = cx + outer_r * math.cos(start_angle)
    outer_start_y = cy - outer_r * math.sin(start_angle)
    outer_end_x = cx + outer_r * math.cos(end_angle)
    outer_end_y = cy - outer_r * math.sin(end_angle)

    # Calculate inner arc endpoints
    inner_end_x = cx + inner_r * math.cos(end_angle)
    inner_end_y = cy - inner_r * math.sin(end_angle)
    inner_start_x = cx + inner_r * math.cos(start_angle)
    inner_start_y = cy - inner_r * math.sin(start_angle)

    # Large arc flag: 1 if angle > 180°
    large_arc_flag = 1 if abs(start_angle - end_angle) > math.pi else 0

    path = (
        f"M {outer_start_x} {outer_start_y} "  # Move to outer start
        f"A {outer_r} {outer_r} 0 {large_arc_flag} 1 {outer_end_x} {outer_end_y} "  # Outer arc
        f"L {inner_end_x} {inner_end_y} "  # Line to inner end
        f"A {inner_r} {inner_r} 0 {large_arc_flag} 0 {inner_start_x} {inner_start_y} "  # Inner arc back
        f"Z"  # Close path
    )

    return path


def generate_gauge(
    value: float,
    max_value: float = 100.0,
    color: str = "#0095DA",
    background_color: str = "#D9D9D9",
    width: int = 153,
    height: int = 76,
    output_format: str = "base64",
) -> str:
    """Generate a gauge chart.

    Args:
        value: Current value
        max_value: Maximum value
        color: Fill color
        background_color: Background color
        width: Width in pixels
        height: Height in pixels
        output_format: 'svg' for raw SVG, 'base64' for base64-encoded SVG

    Returns:
        SVG string or base64-encoded SVG
    """
    svg = generate_gauge_svg(value, max_value, color, background_color, width, height)

    if output_format == "base64":
        return base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    else:
        return svg


# Example usage
if __name__ == "__main__":
    # Test with different percentages
    for pct in [0, 25, 50, 58.1, 75, 100]:
        svg = generate_gauge(pct, 100)
        print(f"{pct}%: Generated base64 SVG ({len(svg)} chars)")

    # Save a sample SVG
    sample_svg = generate_gauge_svg(58.1, 100)
    with open("sample_gauge.svg", "w") as f:
        f.write(sample_svg)
    print("\nSample SVG saved to sample_gauge.svg")
