"""Area + line chart generator for ATS-02 report.

Generates time-series charts with filled area for budget totals and
line/markers for executed values.
"""

import base64
import io
from typing import List, Optional, Tuple

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    raise ImportError(
        "matplotlib is required for chart generation. "
        "Install it with: pip install matplotlib"
    )


def generate_area_line(
    labels: List[str],
    area_values: List[float],
    line_values: List[float],
    area_label: str = "Orçamento Total",
    line_label: str = "Despesa Empenhada",
    area_color: str = "#4B61B3",
    line_color: str = "#00B7FF",
    figsize: Tuple[float, float] = (10, 3.2),
    title: Optional[str] = None,
    image_format: str = "svg",
    output_format: str = "base64",
) -> str:
    """Generate area + line time-series chart.

    Args:
        labels: X-axis labels (e.g., years)
        area_values: Values for filled area series
        line_values: Values for line series
        area_label: Legend label for area series
        line_label: Legend label for line series
        area_color: Hex color for area
        line_color: Hex color for line
        figsize: Figure size in inches
        title: Optional chart title
        image_format: Image format ('svg' or 'png')
        output_format: 'raw' for raw content string, 'base64' for base64

    Returns:
        Base64-encoded image or raw image content as string.
    """
    if not labels or len(area_values) != len(labels) or len(line_values) != len(labels):
        raise ValueError("labels, area_values and line_values must have the same non-zero length")

    x = list(range(len(labels)))
    fig, ax = plt.subplots(figsize=figsize)

    # Area for total budget.
    ax.fill_between(
        x,
        area_values,
        color=area_color,
        alpha=0.85,
        label=area_label,
    )

    # Line for executed amount.
    ax.plot(
        x,
        line_values,
        color=line_color,
        linewidth=2.5,
        marker="o",
        markersize=4.5,
        markerfacecolor=line_color,
        markeredgecolor="white",
        markeredgewidth=0.8,
        label=line_label,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    if title:
        ax.set_title(title, fontsize=11, fontweight="bold")

    # Axis and grid styling.
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", which="both", left=False, length=0, labelleft=False)
    ax.set_yticks([])

    # Labels at the last point to match the static style.
    last_idx = len(labels) - 1
    ax.annotate(
        f"R$ {area_values[last_idx]:,.0f}".replace(",", "."),
        (x[last_idx], area_values[last_idx]),
        textcoords="offset points",
        xytext=(6, 6),
        fontsize=8,
        color=area_color,
        weight="bold",
    )
    ax.annotate(
        f"R$ {line_values[last_idx]:,.0f}".replace(",", "."),
        (x[last_idx], line_values[last_idx]),
        textcoords="offset points",
        xytext=(6, -12),
        fontsize=8,
        color=line_color,
        weight="bold",
    )

    ax.legend(loc="upper left", frameon=False, fontsize=8)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format=image_format, dpi=100, transparent=False, bbox_inches="tight")
    plt.close(fig)

    buffer.seek(0)
    image_data = buffer.read()

    if output_format == "base64":
        return base64.b64encode(image_data).decode("utf-8")
    return image_data.decode("utf-8" if image_format == "svg" else "latin-1")
