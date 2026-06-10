"""Grouped bar chart generator for ATS-02 report.

Generates grouped (side-by-side) bar charts for comparative analysis
(e.g., Empenhado vs Liquidado).
"""

import io
import base64
from typing import List, Dict, Tuple, Optional

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np
except ImportError:
    raise ImportError(
        "matplotlib and numpy are required for chart generation. "
        "Install them with: pip install matplotlib numpy"
    )


def generate_grouped_bar(
    labels: List[str],
    series: Dict[str, List[float]],
    colors: Optional[Dict[str, str]] = None,
    figsize: Tuple[float, float] = (10, 6),
    title: Optional[str] = None,
    horizontal: bool = False,
    image_format: str = "svg",
    output_format: str = "base64",
) -> str:
    """Generate a grouped bar chart.

    Args:
        labels: X-axis labels (e.g., categories)
        series: Dictionary mapping series names to values
                e.g., {"Empenhado": [50, 30, 80], "Liquidado": [45, 25, 78]}
        colors: Optional dictionary mapping series names to colors
        figsize: Figure size (width, height) in inches
        title: Optional chart title
        horizontal: If True, creates horizontal grouped bars
        image_format: Image format ('svg' or 'png')
        output_format: 'raw' for raw content string, 'base64' for base64

    Returns:
        Base64-encoded image or raw image content as string
    """
    # Default color palette
    if colors is None:
        default_colors = ["#2E4172", "#0095DA", "#00C7B1", "#FFB81C", "#E63946"]
        colors = {name: default_colors[i % len(default_colors)] for i, name in enumerate(series.keys())}

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    series_names = list(series.keys())
    n_series = len(series_names)
    n_labels = len(labels)
    x = np.arange(n_labels)

    # Calculate bar width and positions
    total_width = 0.8
    bar_width = total_width / n_series
    offsets = np.linspace(
        -(total_width - bar_width) / 2, (total_width - bar_width) / 2, n_series
    )

    # Create grouped bars
    for i, series_name in enumerate(series_names):
        values = np.array(series[series_name])
        positions = x + offsets[i]

        if horizontal:
            bars = ax.barh(
                positions,
                values,
                bar_width * 0.9,  # Slight gap between bars
                label=series_name,
                color=colors.get(series_name, "#999999"),
            )
        else:
            bars = ax.bar(
                positions,
                values,
                bar_width * 0.9,  # Slight gap between bars
                label=series_name,
                color=colors.get(series_name, "#999999"),
            )

    # Configure axes
    if horizontal:
        ax.set_yticks(x)
        ax.set_yticklabels(labels)
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    else:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.spines["left"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", which="both", left=False, length=0, labelleft=False)
        ax.set_yticks([])

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold")

    # Add legend
    ax.legend(loc="best", frameon=False)

    # Add grid for readability
    if horizontal:
        ax.grid(axis="x", alpha=0.3, linestyle="--")
    else:
        ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Adjust layout
    plt.tight_layout()

    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format=image_format, dpi=200, transparent=False, bbox_inches="tight")
    plt.close(fig)

    buffer.seek(0)
    image_data = buffer.read()

    if output_format == "base64":
        return base64.b64encode(image_data).decode("utf-8")
    return image_data.decode("utf-8" if image_format == "svg" else "latin-1")


# Example usage
if __name__ == "__main__":
    # Test data
    categories = ["Custeio", "Capital", "Pessoal"]
    execution_series = {
        "Empenhado": [50, 30, 80],
        "Liquidado": [45, 25, 78],
    }

    custom_colors = {
        "Empenhado": "#2E4172",
        "Liquidado": "#0095DA",
    }

    chart_b64 = generate_grouped_bar(
        labels=categories,
        series=execution_series,
        colors=custom_colors,
        title="Execução Orçamentária: Empenhado vs Liquidado",
    )

    print(f"Generated grouped bar chart: {len(chart_b64)} chars (base64)")

    # Save sample PNG
    with open("sample_grouped_bar.png", "wb") as f:
        png_bytes = generate_grouped_bar(
            labels=categories,
            series=execution_series,
            colors=custom_colors,
            output_format="png",
        )
        f.write(png_bytes.encode("latin-1"))

    print("Sample PNG saved to sample_grouped_bar.png")
