"""
Relatorio - Aqui Tem MEC Equidade - Executor.

Este modulo implementa a logica de geracao do relatorio ATM-EQ.
"""

import json
import logging
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict

import pandas as pd

from schoolreport.rendering.chart_framework import ChartLoader
from schoolreport.rendering.charts import ChartGenerator

logger = logging.getLogger(__name__)


class ATMEQExecutor:
    """
    Executor para o relatorio ATM-EQ.

    Orquestra a compilacao do relatorio em PDF usando o contrato de dados
    produzido pelo pipeline local do projeto.
    """

    def __init__(self, reports_dir: Path):
        """
        Inicializa o executor.

        Args:
            reports_dir: Diretorio raiz dos relatorios.
        """
        self.report_dir = reports_dir / "ATM-EQ"
        self.template_path = self.report_dir / "template" / "main.typ"
        self.assets_dir = self.report_dir / "template" / "assets"
        self.chart_loader = ChartLoader()
        self.chart_generator = ChartGenerator()

    async def execute(self, data: Dict[str, Any]) -> bytes:
        """
        Gera o PDF do relatorio ATM-EQ.

        Args:
            data: Dados de entrada, principalmente queries e charts.

        Returns:
            bytes: Conteudo do PDF gerado.
        """
        logger.info("Iniciando geracao do relatorio ATM-EQ")

        self._validate_input(data)

        # Build data_map from query payload and generate dynamic charts.
        # This keeps charts in sync with query/cache results used in this run.
        query_data_map = self._build_chart_data_map(data.get("queries", {}))
        generated_charts = await self._generate_charts(
            query_data_map=query_data_map,
            params=data.get("params", {}),
        )

        # Preserve explicitly provided charts, but let generated charts win.
        merged_charts = dict(data.get("charts", {}))
        merged_charts.update(generated_charts)
        keep_chart_files = bool(data.get("keep_chart_files", False))

        template_data = {
            "metadata": data.get("metadata", {}),
            "params": data.get("params", {}),
            "queries": data.get("queries", {}),
            "charts": merged_charts,
            "template_params": data.get("template_params", {}),
        }

        logger.info("Compilando template Typst...")
        pdf_bytes = await self._compile_typst(
            template_data,
            keep_chart_files=keep_chart_files,
        )
        logger.info("Relatorio ATM-EQ gerado com sucesso")
        return pdf_bytes

    def _build_chart_data_map(self, queries: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Convert query payload into the chart engine data_map format."""
        if not isinstance(queries, dict):
            return {}

        data_map: Dict[str, pd.DataFrame] = {}
        for query_name, payload in queries.items():
            try:
                if isinstance(payload, list):
                    data_map[query_name] = pd.DataFrame(payload)
                elif isinstance(payload, dict):
                    # Dict-of-lists becomes DataFrame directly; scalar dict is one row.
                    if payload and all(isinstance(v, list) for v in payload.values()):
                        data_map[query_name] = pd.DataFrame(payload)
                    else:
                        data_map[query_name] = pd.DataFrame([payload])
                else:
                    data_map[query_name] = pd.DataFrame()
            except Exception as exc:
                logger.warning(f"Falha ao converter query '{query_name}' para DataFrame: {exc}")
                data_map[query_name] = pd.DataFrame()
        return data_map

    async def _generate_charts(
        self,
        query_data_map: Dict[str, pd.DataFrame],
        params: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate custom ATM-EQ charts from query payload."""
        registry = self.chart_loader.load(self.report_dir, "ATM-EQ")
        if len(registry) == 0:
            logger.warning("Nenhum grafico registrado em reports/ATM-EQ/charts.py")
            return {}

        charts = await self.chart_generator.generate_many(
            charts=[],
            data_map=query_data_map,
            chart_registry=registry,
            report_id="ATM-EQ",
            params=params or {},
            assets_dir=self.assets_dir,
        )
        logger.info(f"Graficos dinamicos gerados: {len(charts)}")
        return charts

    def _validate_input(self, data: Dict[str, Any]) -> None:
        """Valida a estrutura minima esperada pelo template."""
        if not isinstance(data, dict):
            raise ValueError("Dados de entrada invalidos")

        if "queries" not in data:
            raise ValueError("Campo obrigatorio ausente: queries")

    async def _compile_typst(
        self,
        template_data: Dict[str, Any],
        keep_chart_files: bool = False,
    ) -> bytes:
        """
        Compila template Typst em PDF.

        Args:
            template_data: Dados para o template.

        Returns:
            bytes: PDF gerado.
        """
        from schoolreport.core.typst import TypstRenderer

        renderer = TypstRenderer()
        
        # Utiliza o diretorio atual (cwd) como base para o temporario, evitando erros
        # de isolamento do /tmp em instalacoes do Typst via Snap, Flatpak ou Docker.
        tmp_root = Path.cwd() / ".tmp"
        tmp_root.mkdir(exist_ok=True)
        output_dir = Path(tempfile.mkdtemp(dir=tmp_root))
        output_path = output_dir / "atm-eq.pdf"

        try:
            await renderer.render(
                template_path=self.template_path,
                output_path=output_path,
                data=template_data,
                keep_chart_files=keep_chart_files,
            )
            return output_path.read_bytes()
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)
