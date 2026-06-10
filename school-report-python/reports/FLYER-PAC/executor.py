"""Executor do relatorio FLYER-PAC.

Le um arquivo local com uma linha por UF e monta o contrato usado pelo Typst
para gerar a pagina de apoio ao flyer da ACS.
"""

import logging
from pathlib import Path
import shutil
import tempfile
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class FLYERPACExecutor:
    """Executor para flyer estadual do Novo PAC."""

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "FLYER-PAC"
        self.template_path = self.report_dir / "template" / "main.typ"

    async def execute(self, data: dict[str, Any]) -> bytes:
        params = data.get("params", {})
        uf = str(params.get("uf", "")).strip().upper()
        input_file = str(params.get("input_file", "")).strip()

        if not uf:
            raise ValueError("Parametro obrigatorio ausente: uf")
        if not input_file:
            raise ValueError("Parametro obrigatorio ausente: input_file")

        row = self._load_state_row(input_file=input_file, uf=uf)
        nome = self._clean_value(row.get("nome")) or uf

        template_data = {
            "metadata": data.get("metadata", {}),
            "params": params,
            "queries": {
                "flyer_contexto": [
                    {
                        "uf": uf,
                        "nome": nome,
                        "titulo": f"Novo PAC e Programas do MEC - {nome}",
                    }
                ],
                "resumo_novopac": self._build_novopac_rows(row),
                "programas_mec": self._build_program_rows(row),
                "obras": self._build_obras(row),
            },
            "charts": {},
            "template_params": data.get("template_params", {}),
        }

        logger.info("Compilando flyer PAC para UF %s", uf)
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
            frame = pd.read_excel(path, dtype=str)
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

    def _build_novopac_rows(self, row: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            self._row(
                "Novo PAC Seleções - Creche - Edital 1",
                row,
                "creches_edital_1",
                "qtd_creches",
                quantity_rowspan=2,
            ),
            self._row("Novo PAC Seleções - Creche - Edital 2", row, "creches_edital_2", skip_quantity=True),
            self._row("Novo PAC Seleções - ETI - Edital 1", row, "eti_edital_1", "qtd_eti"),
            self._row(
                "Novo PAC Seleções - Ônibus - Edital 1",
                row,
                "onibus_edital_1",
                "qtd_onibus",
                quantity_rowspan=2,
            ),
            self._row("Novo PAC Seleções - Ônibus - Edital 2", row, "onibus_edital_2", skip_quantity=True),
            self._row("Novo PAC Seleções - Indígena", row, "indigena_valor", "qtd_indigena"),
            self._row("Subtotal Educação Básica", row, "subtotal_edbasica_valor", subtotal=True),
            self._row("Novo PAC Educação Superior - Expansão", row, "sesu_expansao_valor", "sesu_qtd_campus"),
            self._row(
                "Novo PAC Educação Superior - Consolidação",
                row,
                "sesu_consolidacao_valor",
                "sesu_consolidacao_qtd",
            ),
            self._row("Novo PAC Educação Superior - HU Brasil", row, "hu_valor", "hu_qtd_obras"),
            self._row("Subtotal Educação Superior", row, "subtotal_edsuperior_valor", subtotal=True),
            self._row(
                "Novo PAC Educação Profissional e Tecnológica - Expansão",
                row,
                "ept_expansao_valor",
                "ept_qtd_campus",
            ),
            self._row(
                "Novo PAC Educação Profissional e Tecnológica - Consolidação",
                row,
                "ept_consolidacao_valor",
                "sesu_consolidacao_qtd_1",
            ),
            self._row("Subtotal Educação Profissional e Tecnológica", row, "subtotal_ept_valor", subtotal=True),
            self._row("TOTAL NOVO PAC NO ESTADO", row, "total_novopac_valor", total=True),
        ]

    def _build_program_rows(self, row: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "label": "Pé-de-Meia",
                "value": f"{self._value(row, 'pdm_estudantes')} estudantes beneficiados desde o início do programa",
            },
            {
                "label": "Escolas Conectadas",
                "value": f"{self._value(row, 'escolas_conectadas_45')} Escolas Conectadas (Nível 4 e 5)",
            },
            {
                "label": "Escola em Tempo Integral",
                "value": f"{self._value(row, 'eti_matriculas')} Matrículas fomentadas desde o início do programa",
            },
            {
                "label": "Pacto pela Retomada das obras do Novo PAC",
                "value": f"{self._value(row, 'pacto_obras_qtd')} Obras Aprovadas",
            },
            {
                "label": "Compromisso Nacional Criança Alfabetizada (CNCA)",
                "value": f"{self._value(row, 'cnca_cantinhos')} Cantinhos da Leitura desde 2023",
            },
            {
                "label": "Total Articuladores RENALFA",
                "value": f"{self._value(row, 'cnca_articuladores')} Em 2025",
            },
        ]

    def _build_obras(self, row: dict[str, Any]) -> list[dict[str, str]]:
        raw = None
        for column in ("obras_expansao_lista", "obras_lista", "lista_obras", "obras"):
            raw = self._clean_value(row.get(column))
            if raw is not None:
                break
        if raw is None:
            return []

        obras = []
        separator = "-x-" if "-x-" in raw else "|"
        for item in [part.strip() for part in raw.split(separator) if part.strip()]:
            if "§" in item:
                pieces = [piece.strip() for piece in item.split("§")]
            else:
                pieces = [piece.strip() for piece in item.split(";")]

            if "§" not in item and len(pieces) >= 5:
                obras.append(
                    {
                        "acao": pieces[0],
                        "tipo_sigla": pieces[1] or pieces[2],
                        "municipio": pieces[3],
                        "obra": "; ".join(pieces[4:]),
                    }
                )
            elif len(pieces) >= 4:
                obras.append(
                    {
                        "acao": pieces[0],
                        "tipo_sigla": pieces[1],
                        "municipio": pieces[2],
                        "obra": "§".join(pieces[3:]) if "§" in item else "; ".join(pieces[3:]),
                    }
                )
            else:
                obras.append({"acao": "", "tipo_sigla": "", "municipio": "", "obra": item})
        return obras

    def _row(
        self,
        label: str,
        row: dict[str, Any],
        value_column: str,
        quantity_column: str | None = None,
        *,
        subtotal: bool = False,
        total: bool = False,
        quantity_rowspan: int = 1,
        skip_quantity: bool = False,
    ) -> dict[str, Any]:
        return {
            "label": label,
            "value": self._value(row, value_column),
            "quantity": self._value(row, quantity_column) if quantity_column else "",
            "subtotal": subtotal,
            "total": total,
            "quantity_rowspan": quantity_rowspan,
            "skip_quantity": skip_quantity,
        }

    def _value(self, row: dict[str, Any], column: str | None) -> str:
        if column is None:
            return ""
        return self._clean_value(row.get(column)) or "0"

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
        output_path = output_dir / "flyer-pac.pdf"

        try:
            await renderer.render(
                template_path=self.template_path,
                output_path=output_path,
                data=template_data,
            )
            return output_path.read_bytes()
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)
