"""
{{ cookiecutter.report_name }} - Executor

Este módulo implementa a lógica de geração do relatório {{ cookiecutter.report_id }}.
"""

import logging
from pathlib import Path
from typing import Any, Dict

from schoolreport.core.chart_assets import (
    ensure_placeholder_charts,
    write_charts_to_assets,
)
from schoolreport.core.typst import TypstClient
{% if cookiecutter.has_charts == "yes" %}
from schoolreport.rendering.chart_framework import ChartLoader
from schoolreport.rendering.charts import ChartGenerator
{% endif %}

logger = logging.getLogger(__name__)


class {{ cookiecutter.report_id.replace('-', '').replace('_', '') }}Executor:
    """Executor para o relatório {{ cookiecutter.report_id }}."""

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "{{ cookiecutter.report_id }}"
        self.template_path = self.report_dir / "template" / "main.typ"
        self.assets_dir = self.report_dir / "template" / "assets"

        if not self.report_dir.exists():
            raise ValueError(f"Report directory not found: {self.report_dir}")
        if not self.template_path.exists():
            raise ValueError(f"Template not found: {self.template_path}")

        self._typst = TypstClient()
{% if cookiecutter.has_charts == "yes" %}
        self.chart_loader = ChartLoader()
        self.chart_generator = ChartGenerator()
{% endif %}

    async def execute(self, data: Dict[str, Any]) -> bytes:
        """Gera o PDF do relatório {{ cookiecutter.report_id }}.

        Args:
            data: Dados de entrada (metadata, params, queries)

        Returns:
            Conteúdo do PDF gerado
        """
        logger.info("Iniciando geração do relatório {{ cookiecutter.report_id }}")
        self._validate_input(data)

{% if cookiecutter.has_charts == "yes" %}
        # Gerar gráficos
        charts = await self._generate_charts(data)
        generated = write_charts_to_assets(charts, self.assets_dir)
        ensure_placeholder_charts(
            self.report_dir / "template" / "pages", self.assets_dir, generated
        )
{% else %}
        charts = {}
{% endif %}

        # Preparar dados para o template
        template_data = {
            "metadata": data.get("metadata", {}),
            "params": data.get("params", {}),
            "queries": data.get("queries", {}),
            "charts": charts,
        }
        if data.get("template_params"):
            template_data["template_params"] = data["template_params"]

        # Compilar PDF
        logger.info("Compilando template Typst...")
        pdf_bytes = await self._typst.render_to_bytes(self.template_path, template_data)
        logger.info(f"Relatório {{ cookiecutter.report_id }} gerado: {len(pdf_bytes)} bytes")
        return pdf_bytes

    def _validate_input(self, data: Dict[str, Any]) -> None:
        if "metadata" not in data:
            raise ValueError("Campo obrigatório ausente: metadata")
        if "params" not in data:
            raise ValueError("Campo obrigatório ausente: params")

{% if cookiecutter.has_charts == "yes" %}
    async def _generate_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Gera gráficos usando @chart decorators de charts.py."""
        registry = self.chart_loader.load(self.report_dir, "{{ cookiecutter.report_id }}")
        if len(registry) == 0:
            logger.warning("Nenhum chart registrado em charts.py")
            return {}

        # TODO: Montar data_map a partir dos dados de entrada
        data_map = {}

        return await self.chart_generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=registry,
            report_id="{{ cookiecutter.report_id }}",
            params=data.get("params", {}),
            assets_dir=self.assets_dir,
        )
{% endif %}
