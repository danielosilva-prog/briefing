"""Executor do relatorio BRIEFING."""

import json
import logging
from pathlib import Path
import shutil
import tempfile
from typing import Any

logger = logging.getLogger(__name__)


class BRIEFINGExecutor:
    """Executor enxuto para briefings em Typst."""

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "BRIEFING"
        self.template_path = self.report_dir / "template" / "main.typ"

    async def execute(self, data: dict[str, Any]) -> bytes:
        if not isinstance(data, dict):
            raise ValueError("Dados de entrada invalidos")

        template_data = {
            "metadata": data.get("metadata", {}),
            "params": data.get("params", {}),
            "queries": data.get("queries", {}),
            "charts": data.get("charts", {}),
            "template_params": data.get("template_params", {}),
        }

        logger.info("Compilando briefing em Typst")
        return await self._compile_typst(
            template_data,
            keep_chart_files=bool(data.get("keep_chart_files", False)),
        )

    async def _compile_typst(
        self,
        template_data: dict[str, Any],
        keep_chart_files: bool = False,
    ) -> bytes:
        from schoolreport.core.typst import TypstRenderer

        renderer = TypstRenderer()
        tmp_root = Path.cwd() / ".tmp"
        tmp_root.mkdir(exist_ok=True)
        output_dir = Path(tempfile.mkdtemp(dir=tmp_root))
        output_path = output_dir / "briefing.pdf"

        try:
            await renderer.render(
                template_path=self.template_path,
                output_path=output_path,
                data=template_data,
                keep_chart_files=keep_chart_files,
            )
            return output_path.read_bytes()
        finally:
            if keep_chart_files:
                debug_json = output_dir / "briefing-data.json"
                debug_json.write_text(
                    json.dumps(template_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            else:
                shutil.rmtree(output_dir, ignore_errors=True)
