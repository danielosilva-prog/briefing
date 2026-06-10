{% if cookiecutter.has_charts == "yes" %}"""
Gerador de gráficos gauge (semicírculo).
"""

import base64
import math
from typing import Optional


def generate_gauge(
    value: float,
    max_value: float = 100.0,
    color: str = "#0095DA",
    background_color: str = "#D9D9D9",
    width: int = 153,
    height: int = 76,
) -> str:
    """
    Gera um gráfico gauge semicircular em SVG e retorna como base64.

    Args:
        value: Valor atual (0 a max_value)
        max_value: Valor máximo do gauge
        color: Cor do arco preenchido
        background_color: Cor do arco de fundo
        width: Largura do SVG
        height: Altura do SVG

    Returns:
        str: SVG codificado em base64

    Example:
        >>> gauge_b64 = generate_gauge(75.5, max_value=100, color="#0095DA")
    """
    # Calcular porcentagem
    percentage = min(max(value / max_value, 0.0), 1.0)

    # Parâmetros do arco
    center_x = width / 2
    center_y = height
    outer_radius = width / 2
    inner_radius = outer_radius * 0.73

    # Ângulos (180° = semicírculo)
    start_angle = 180
    end_angle = 180 - (180 * percentage)

    # Converter para radianos
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)

    # Calcular pontos do arco externo
    outer_start_x = center_x + outer_radius * math.cos(start_rad)
    outer_start_y = center_y + outer_radius * math.sin(start_rad)
    outer_end_x = center_x + outer_radius * math.cos(end_rad)
    outer_end_y = center_y + outer_radius * math.sin(end_rad)

    # Calcular pontos do arco interno
    inner_start_x = center_x + inner_radius * math.cos(start_rad)
    inner_start_y = center_y + inner_radius * math.sin(start_rad)
    inner_end_x = center_x + inner_radius * math.cos(end_rad)
    inner_end_y = center_y + inner_radius * math.sin(end_rad)

    # Determinar large-arc-flag
    large_arc = 1 if percentage > 0.5 else 0

    # Path do arco de fundo (completo)
    background_path = f"""
        M {outer_start_x} {outer_start_y}
        A {outer_radius} {outer_radius} 0 1 0 {center_x - outer_radius} {center_y}
        L {center_x - inner_radius} {center_y}
        A {inner_radius} {inner_radius} 0 1 1 {inner_start_x} {inner_start_y}
        Z
    """

    # Path do arco de valor (preenchido)
    value_path = f"""
        M {outer_start_x} {outer_start_y}
        A {outer_radius} {outer_radius} 0 {large_arc} 0 {outer_end_x} {outer_end_y}
        L {inner_end_x} {inner_end_y}
        A {inner_radius} {inner_radius} 0 {large_arc} 1 {inner_start_x} {inner_start_y}
        Z
    """

    # Gerar SVG
    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Arco de fundo -->
        <path d="{background_path}" fill="{background_color}"/>
        <!-- Arco de valor -->
        <path d="{value_path}" fill="{color}"/>
    </svg>'''

    # Codificar em base64
    return base64.b64encode(svg.encode('utf-8')).decode('utf-8')
{% else %}
# Chart generation not enabled for this report
pass
{% endif %}
