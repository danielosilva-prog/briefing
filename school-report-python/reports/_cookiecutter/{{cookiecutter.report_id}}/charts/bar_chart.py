{% if cookiecutter.has_charts == "yes" %}"""
Gerador de gráficos de barras.
"""

import base64
import io
from typing import Dict, List, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def generate_bar_chart(
    data: Dict[str, List],
    title: str = "Gráfico de Barras",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple = (10, 6),
    color: str = "#0095DA",
) -> str:
    """
    Gera um gráfico de barras e retorna como base64.

    Args:
        data: Dicionário com 'labels' e 'values'
        title: Título do gráfico
        xlabel: Rótulo do eixo X
        ylabel: Rótulo do eixo Y
        figsize: Tamanho da figura (width, height)
        color: Cor das barras

    Returns:
        str: Gráfico em PNG codificado em base64

    Example:
        >>> data = {
        ...     "labels": ["2020", "2021", "2022", "2023"],
        ...     "values": [100, 120, 135, 150]
        ... }
        >>> chart_b64 = generate_bar_chart(data, title="Evolução Anual")
    """
    labels = data.get("labels", [])
    values = data.get("values", [])

    if not labels or not values:
        raise ValueError("Dados vazios: 'labels' e 'values' são obrigatórios")

    # Criar figura
    fig, ax = plt.subplots(figsize=figsize)

    # Plotar barras
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, values, color=color, alpha=0.8)

    # Configurar eixos
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Formatação brasileira nos valores
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'{x:,.0f}'.replace(',', '.'))
    )

    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Converter para base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, transparent=True, bbox_inches='tight')
    plt.close(fig)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')
{% else %}
# Chart generation not enabled for this report
pass
{% endif %}
