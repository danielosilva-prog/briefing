"""Executor do relatorio BRIEFING-LOCAL.

Este executor nao depende de BigQuery. Ele le um CSV/XLSX local, seleciona a
linha da UF informada e transforma as colunas no contrato consumido pelo Typst.
"""

import json
import logging
from pathlib import Path
import shutil
import tempfile
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class BRIEFINGLOCALExecutor:
    """Executor para briefing local por UF."""

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "BRIEFING-LOCAL"
        self.template_path = self.report_dir / "template" / "main.typ"
        self.sections_path = self.report_dir / "template" / "assets" / "data" / "sections.json"

    async def execute(self, data: dict[str, Any]) -> bytes:
        params = data.get("params", {})
        uf = str(params.get("uf", "")).strip().upper()
        input_file = str(params.get("input_file", "")).strip()

        if not uf:
            raise ValueError("Parametro obrigatorio ausente: uf")
        if not input_file:
            raise ValueError("Parametro obrigatorio ausente: input_file")

        row = self._load_state_row(input_file=input_file, uf=uf)
        sections = self._build_sections(row)

        template_data = {
            "metadata": data.get("metadata", {}),
            "params": params,
            "queries": {
                "briefing_contexto": [
                    {
                        "uf": uf,
                        "territorio": self._clean_value(row.get("territorio")) or uf,
                        "titulo": self._clean_value(row.get("titulo"))
                        or f"BRIEFING - Visita Ministerial a {uf}",
                    }
                ],
                "briefing_sections": sections,
            },
            "charts": {},
            "template_params": data.get("template_params", {}),
        }

        logger.info("Compilando briefing local para UF %s", uf)
        return await self._compile_typst(template_data)

    def _load_state_row(self, input_file: str, uf: str) -> dict[str, Any]:
        path = Path(input_file).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {path}")

        suffix = path.suffix.lower()
        if suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig", sep=None, engine="python")
        elif suffix in {".xlsx", ".xls"}:
            try:
                frame = pd.read_excel(path, dtype=str)
            except ImportError as exc:
                raise RuntimeError(
                    "Para ler planilhas Excel, instale as dependencias com "
                    'uv pip install -e ".[dev]" para incluir openpyxl.'
                ) from exc
        else:
            raise ValueError("Formato nao suportado. Use .csv, .xlsx ou .xls.")

        frame.columns = [str(column).strip() for column in frame.columns]
        if "uf" not in frame.columns:
            raise ValueError("O arquivo de entrada precisa ter uma coluna chamada 'uf'.")

        matches = frame[frame["uf"].astype(str).str.strip().str.upper() == uf]
        if matches.empty:
            available = ", ".join(sorted(frame["uf"].dropna().astype(str).str.upper().unique()))
            raise ValueError(f"UF '{uf}' nao encontrada no arquivo. UFs disponiveis: {available}")
        if len(matches) > 1:
            raise ValueError(f"UF '{uf}' aparece mais de uma vez no arquivo de entrada.")

        return matches.iloc[0].to_dict()

    def _build_sections(self, row: dict[str, Any]) -> list[dict[str, Any]]:
        sections_config = json.loads(self.sections_path.read_text(encoding="utf-8"))
        sections: list[dict[str, Any]] = []

        for section in sections_config:
            indicadores = []
            for item in section.get("indicadores", []):
                value = self._clean_value(row.get(item["coluna"]))
                if value is None:
                    continue
                indicadores.append(
                    {
                        "rotulo": item["rotulo"],
                        "valor": value,
                        "complemento": item.get("complemento"),
                    }
                )

            if indicadores:
                sections.append(
                    {
                        "ordem": section.get("ordem", len(sections) + 1),
                        "numero": section.get("numero", ""),
                        "titulo": section.get("titulo", ""),
                        "indicadores": indicadores,
                    }
                )

        return sections

    def _clean_value(self, value: Any) -> str | None:
        if value is None or pd.isna(value):
            return None
        text = str(value).strip()
        if text == "" or text.lower() in {"nan", "none", "null"}:
            return None
        return text

    async def _compile_typst(self, template_data: dict[str, Any]) -> bytes:
        from schoolreport.core.typst import TypstRenderer

        renderer = TypstRenderer()
        tmp_root = Path.cwd() / ".tmp"
        tmp_root.mkdir(exist_ok=True)
        output_dir = Path(tempfile.mkdtemp(dir=tmp_root))
        output_path = output_dir / "briefing-local.pdf"

        try:
            await renderer.render(
                template_path=self.template_path,
                output_path=output_path,
                data=template_data,
            )
            return output_path.read_bytes()
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)
