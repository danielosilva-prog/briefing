{% if cookiecutter.has_charts == "yes" %}"""
Gerador de gráficos de linha.
"""

import base64
import io
from typing import Dict, List

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def generate_line_chart(
    data: Dict[str, List],
    title: str = "Gráfico de Linha",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple = (10, 6),
    color: str = "#0095DA",
) -> str:
    """
    Gera um gráfico de linha e retorna como base64.

    Args:
        data: Dicionário com 'x' e 'y'
        title: Título do gráfico
        xlabel: Rótulo do eixo X
        ylabel: Rótulo do eixo Y
        figsize: Tamanho da figura
        color: Cor da linha

    Returns:
        str: Gráfico em PNG codificado em base64
    """
    x_values = data.get("x", [])
    y_values = data.get("y", [])

    if not x_values or not y_values:
        raise ValueError("Dados vazios: 'x' e 'y' são obrigatórios")

    # Criar figura
    fig, ax = plt.subplots(figsize=figsize)

    # Plotar linha
    ax.plot(x_values, y_values, color=color, linewidth=2, marker='o', markersize=6)

    # Configurar eixos
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')

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
