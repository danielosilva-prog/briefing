"""Executor dos anexos de obras para briefings.

Le um arquivo local com obras da SETEC e da SESU, filtra por UF e secretaria,
e monta o contrato usado pelo Typst.
"""

import logging
from pathlib import Path
import shutil
import tempfile
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class ANEXOSBRIEFINGSExecutor:
    """Executor local para anexos de briefing."""

    REQUIRED_COLUMNS = {
        "secretaria",
        "sigla_uf",
        "instituicao",
        "descricao_empreendimento",
        "municipio",
        "valor_previsto",
    }

    SECRETARIA_TITLES = {
        "SETEC": "Obras da Educação Profissional e Tecnológica",
        "SESU": "Obras da Educação Superior",
    }

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "ANEXOS-BRIEFINGS"
        self.template_path = self.report_dir / "template" / "main.typ"

    async def execute(self, data: dict[str, Any]) -> bytes:
        params = data.get("params", {})
        uf = str(params.get("uf", "")).strip().upper()
        secretaria = str(params.get("secretaria", "")).strip().upper()
        input_file = str(params.get("input_file", "")).strip()

        if not uf:
            raise ValueError("Parametro obrigatorio ausente: uf")
        if not secretaria:
            raise ValueError("Parametro obrigatorio ausente: secretaria")
        if secretaria not in {"SETEC", "SESU"}:
            raise ValueError("Parametro secretaria deve ser SETEC ou SESU")
        if not input_file:
            raise ValueError("Parametro obrigatorio ausente: input_file")

        rows = self._load_rows(input_file=input_file, uf=uf, secretaria=secretaria)
        total = sum(row["valor_num"] for row in rows)

        title = f"{secretaria} - {uf}"
        template_data = {
            "metadata": data.get("metadata", {}),
            "params": params,
            "queries": {
                "contexto": [
                    {
                        "uf": uf,
                        "secretaria": secretaria,
                        "titulo": title,
                        "subtitulo": self.SECRETARIA_TITLES[secretaria],
                        "total_obras": str(len(rows)),
                        "total_valor": self._format_currency(total),
                    }
                ],
                "obras": [
                    {
                        "instituicao": row["instituicao"],
                        "descricao": row["descricao"],
                        "municipio": row["municipio"],
                        "valor_previsto": self._format_currency(row["valor_num"]),
                    }
                    for row in rows
                ],
            },
            "charts": {},
            "template_params": data.get("template_params", {}),
        }

        logger.info("Compilando anexo %s para UF %s", secretaria, uf)
        return await self._compile_typst(template_data, secretaria=secretaria, uf=uf)

    def _load_rows(self, input_file: str, uf: str, secretaria: str) -> list[dict[str, Any]]:
        path = Path(input_file).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {path}")

        suffix = path.suffix.lower()
        if suffix == ".csv":
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig", sep=None, engine="python")
        elif suffix in {".xlsx", ".xls"}:
            frame = pd.read_excel(path, dtype=str)
        else:
            raise ValueError("Formato nao suportado. Use .csv, .xlsx ou .xls.")

        frame.columns = [str(column).strip() for column in frame.columns]
        missing = sorted(self.REQUIRED_COLUMNS - set(frame.columns))
        if missing:
            raise ValueError(f"Colunas obrigatorias ausentes no arquivo de entrada: {', '.join(missing)}")

        filtered = frame[
            (frame["sigla_uf"].astype(str).str.strip().str.upper() == uf)
            & (frame["secretaria"].astype(str).str.strip().str.upper() == secretaria)
        ].copy()

        if filtered.empty:
            available = frame[["sigla_uf", "secretaria"]].dropna().drop_duplicates()
            pairs = ", ".join(
                sorted(
                    f"{str(row.sigla_uf).strip().upper()}-{str(row.secretaria).strip().upper()}"
                    for row in available.itertuples(index=False)
                )
            )
            raise ValueError(f"Nenhuma obra encontrada para {secretaria}/{uf}. Pares disponiveis: {pairs}")

        filtered["_valor_num"] = filtered["valor_previsto"].map(self._parse_number)
        filtered["_instituicao_sort"] = filtered["instituicao"].astype(str).str.upper()
        filtered["_municipio_sort"] = filtered["municipio"].astype(str).str.upper()
        filtered = filtered.sort_values(["_instituicao_sort", "_municipio_sort", "descricao_empreendimento"])

        return [
            {
                "instituicao": self._clean_value(row["instituicao"]),
                "descricao": self._clean_value(row["descricao_empreendimento"]),
                "municipio": self._clean_value(row["municipio"]),
                "valor_num": float(row["_valor_num"]),
            }
            for row in filtered.to_dict(orient="records")
        ]

    def _clean_value(self, value: Any) -> str:
        if value is None or pd.isna(value):
            return ""
        text = str(value).strip()
        if text.lower() in {"nan", "none", "null"}:
            return ""
        return text

    def _parse_number(self, value: Any) -> float:
        text = self._clean_value(value)
        if not text:
            return 0.0
        normalized = text.replace("R$", "").replace(" ", "")
        if "," in normalized and "." in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        elif "," in normalized:
            normalized = normalized.replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return 0.0

    def _format_currency(self, value: float) -> str:
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"

    async def _compile_typst(self, template_data: dict[str, Any], *, secretaria: str, uf: str) -> bytes:
        from schoolreport.core.typst import TypstRenderer

        renderer = TypstRenderer()
        tmp_root = Path.cwd() / ".tmp"
        tmp_root.mkdir(exist_ok=True)
        output_dir = Path(tempfile.mkdtemp(dir=tmp_root))
        output_path = output_dir / f"anexo-{secretaria.lower()}-{uf.lower()}.pdf"

        try:
            await renderer.render(
                template_path=self.template_path,
                output_path=output_path,
                data=template_data,
            )
            return output_path.read_bytes()
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)
