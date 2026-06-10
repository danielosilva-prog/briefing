"""Horizontal bar chart generator for ATS-02 report.

Generates horizontal bar charts comparing two series (e.g., LOA vs Dotação Atualizada).
"""

import io
import base64
from typing import List, Tuple, Optional

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    raise ImportError(
        "matplotlib is required for chart generation. "
        "Install it with: pip install matplotlib"
    )


def generate_horizontal_bar(
    labels: List[str],
    values1: List[float],
    values2: List[float],
    label1: str = "LOA",
    label2: str = "Dotação Atualizada",
    colors: Tuple[str, str] = ("#2E4172", "#0095DA"),
    figsize: Tuple[float, float] = (10, 6),
    title: Optional[str] = None,
    image_format: str = "svg",
    output_format: str = "base64",
) -> str:
    """Generate a horizontal bar chart comparing two series.

    Args:
        labels: Y-axis labels (e.g., years)
        values1: First series values
        values2: Second series values
        label1: Legend label for first series
        label2: Legend label for second series
        colors: Tuple of (color1, color2)
        figsize: Figure size (width, height) in inches
        title: Optional chart title
        image_format: Image format ('svg' or 'png')
        output_format: 'raw' for raw content string, 'base64' for base64

    Returns:
        Base64-encoded image or raw image content as string
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Calculate positions for grouped bars
    y_pos = range(len(labels))
    bar_height = 0.35

    # Create horizontal bars
    bars1 = ax.barh(
        [i - bar_height / 2 for i in y_pos],
        values1,
        bar_height,
        label=label1,
        color=colors[0],
    )
    bars2 = ax.barh(
        [i + bar_height / 2 for i in y_pos],
        values2,
        bar_height,
        label=label2,
        color=colors[1],
    )

    # Configure axes
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Valor (R$ milhões)", fontsize=10)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold")

    # Format x-axis with Brazilian number formatting
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, p: f"R$ {x:,.0f}".replace(",", "."))
    )

    # Add legend
    ax.legend(loc="best", frameon=False)

    # Add grid for readability
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Adjust layout
    plt.tight_layout()

    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format=image_format, dpi=100, transparent=False, bbox_inches="tight")
    plt.close(fig)

    buffer.seek(0)
    image_data = buffer.read()

    if output_format == "base64":
        return base64.b64encode(image_data).decode("utf-8")
    return image_data.decode("utf-8" if image_format == "svg" else "latin-1")


# Example usage
if __name__ == "__main__":
    # Test data
    years = ["2020", "2021", "2022", "2023", "2024"]
    loa_values = [100, 110, 120, 115, 125]
    dotacao_values = [95, 105, 118, 112, 122]

    chart_b64 = generate_horizontal_bar(
        labels=years,
        values1=loa_values,
        values2=dotacao_values,
        title="LOA vs Dotação Atualizada (2020-2024)",
    )

    print(f"Generated horizontal bar chart: {len(chart_b64)} chars (base64)")

    # Save sample PNG
    with open("sample_horizontal_bar.png", "wb") as f:
        png_bytes = generate_horizontal_bar(
            labels=years,
            values1=loa_values,
            values2=dotacao_values,
            output_format="png",
        )
        f.write(png_bytes.encode("latin-1"))

    print("Sample PNG saved to sample_horizontal_bar.png")
