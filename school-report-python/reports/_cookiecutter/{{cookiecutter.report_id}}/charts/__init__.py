"""
{{ cookiecutter.report_name }} - Chart Generators

Módulos de geração de gráficos para o relatório {{ cookiecutter.report_id }}.
"""

{% if cookiecutter.has_charts == "yes" %}
from .bar_chart import generate_bar_chart
from .line_chart import generate_line_chart
from .gauge import generate_gauge

__all__ = [
    "generate_bar_chart",
    "generate_line_chart",
    "generate_gauge",
]
{% else %}
# Nenhum gráfico dinâmico configurado
__all__ = []
{% endif %}
