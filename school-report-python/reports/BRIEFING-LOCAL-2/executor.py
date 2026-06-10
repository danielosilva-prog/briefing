"""Executor do relatorio BRIEFING-LOCAL-2.

Le um CSV/XLSX local, seleciona a UF informada e monta um contrato de
renderizacao .
"""

import json
import logging
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class BRIEFINGLOCAL2Executor:
    """Executor para briefing local por UF no modelo 2."""

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "BRIEFING-LOCAL-2"
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
        title = self._clean_value(row.get("titulo")) or f"BRIEFING - Visita Ministerial - {uf}"

        template_data = {
            "metadata": data.get("metadata", {}),
            "params": params,
            "queries": {
                "briefing_contexto": [
                    {
                        "uf": uf,
                        "territorio": self._clean_value(row.get("territorio")) or uf,
                        "titulo": title,
                        
                    }
                ],
                "briefing_sections": sections,
            },
            "charts": {},
            "template_params": data.get("template_params", {}),
        }

        logger.info("Compilando briefing local 2 para UF %s", uf)
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
            lines = []
            for item in section.get("lines", []):
                line = self._build_line(item, row)
                if line is not None:
                    lines.append(line)

            if lines:
                sections.append(
                    {
                        "ordem": section.get("ordem", len(sections) + 1),
                        "numero": section.get("numero", ""),
                        "titulo": section.get("titulo", ""),
                        "lines": lines,
                        "keep_together": section.get("keep_together", False),

                    }
                )

        return sections

    def _build_line(self, item: dict[str, Any], row: dict[str, Any]) -> dict[str, Any] | None:
        kind = item.get("type", "field")

        if kind == "spacer":
            return {"type": "spacer", "size": item.get("size", "small")}

        if kind == "text":
            text = item.get("text", "")
            if not text:
                return None
            return {
                "type": "text",
                "text": text,
                "bold": bool(item.get("bold", False)),
                "color": item.get("color", "black"),
            }

        if kind == "template_text":
            text = self._render_template_text(item, row)
            if text is None:
                return None
            return {
                "type": "text",
                "text": text,
                "bold": bool(item.get("bold", False)),
                "color": item.get("color", "black"),
            }

        if kind == "campi_table":
            overview_rows = item.get("overview_rows")
            if overview_rows is None:
                overview_rows = self._parse_campi_rows(row.get(item.get("overview_column", "")))
            expansion_rows = item.get("expansion_rows")
            if expansion_rows is None:
                expansion_rows = self._parse_campi_rows(
                    row.get(item.get("expansion_column", "")),
                    add_total=True,
                )
            if not overview_rows and not expansion_rows:
                return None
            return {
                "type": "campi_table",
                "overview_title": item.get("overview_title", "Visão Geral (inclusive Expansão Novo PAC)"),
                "expansion_title": item.get("expansion_title", "Somente Expansão Novo PAC"),
                "overview_rows": overview_rows,
                "expansion_rows": expansion_rows,
            }

        if kind == "if_table":
            return {
                "type": "if_table",
                "tables": item.get("tables", []),
            }

        if kind == "field":
            value = self._clean_value(row.get(item.get("column", "")))
            if value is None:
                value = str(item.get("default", "0"))
            brasil = item.get("brasil")
            value, parsed_brasil = self._split_value_brasil(value)
            if parsed_brasil is not None:
                brasil = parsed_brasil
            if item.get("hide_brasil", False):
                brasil = None
            value, value_note = self._extract_note(value, item)
            brasil, brasil_note = self._extract_note(brasil, item)
            value_lines = self._split_series(value, item) if item.get("split_items", False) else None
            brasil_lines = (
                self._split_series(brasil, item, strip_brasil=True)
                if item.get("split_items", False)
                else None
            )
            value_parts = self._format_bold_prefix(value, item)
            brasil_parts = self._format_bold_prefix(brasil, item, key="brasil_bold_prefixes")
            value_lines = self._format_bold_prefixes(value_lines, item)
            brasil_lines = self._format_bold_prefixes(brasil_lines, item)
            note = brasil_note or value_note
            return {
                "type": "field",
                "label": item.get("label", ""),
                "value": value,
                "brasil": brasil,
                "value_parts": value_parts,
                "brasil_parts": brasil_parts,
                "value_lines": value_lines,
                "brasil_lines": brasil_lines,
                "note": note,
                "label_bold": item.get("label_bold", True),
                "value_bold": item.get("value_bold", False),
                "value_newline": item.get("value_newline", False),
                "brasil_newline": item.get("brasil_newline", False),
                "brasil_separator": item.get("brasil_separator", " - "),
                "indent": item.get("indent", False),
            }

        if kind == "list":
            raw = self._clean_value(row.get(item.get("column", "")))
            if raw is None:
                return None
            entries = [self._format_list_entry(part) for part in raw.split("|")]
            entries = [entry for entry in entries if entry]
            if not entries:
                return None
            return {"type": "list", "items": entries}

        return None

    def _format_list_entry(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        return text.replace(" - R$", " = R$")

    def _parse_campi_rows(self, value: Any, *, add_total: bool = False) -> list[dict[str, Any]]:
        text = self._clean_value(value)
        if text is None:
            return []

        rows: list[dict[str, Any]] = []
        for part in [part.strip() for part in text.split("|") if part.strip()]:
            if ":" not in part:
                continue
            label, rest = [piece.strip() for piece in part.split(":", 1)]
            label = f"{label}:"
            row_value = rest
            detail = ""
            if "(" in rest and rest.endswith(")"):
                row_value, detail = rest.split("(", 1)
                row_value = row_value.strip()
                detail = detail[:-1].strip()

            is_total = label.lower().startswith("total geral")
            rows.append(
                {
                    "label": label,
                    "value": row_value.strip(),
                    "bold": True,
                    "total": is_total,
                    "indent": False,
                }
            )

            if detail:
                for detail_part in [item.strip() for item in detail.split(",") if item.strip()]:
                    if ":" not in detail_part:
                        continue
                    detail_label, detail_value = [
                        piece.strip() for piece in detail_part.split(":", 1)
                    ]
                    rows.append(
                        {
                            "label": detail_label,
                            "value": detail_value,
                            "bold": False,
                            "total": False,
                            "indent": True,
                        }
                    )

        if add_total and rows and not any(row.get("total") for row in rows):
            total_value = next((row["value"] for row in rows if not row.get("indent")), "")
            rows.append(
                {
                    "label": "Total Geral:",
                    "value": total_value,
                    "bold": True,
                    "total": True,
                    "indent": False,
                }
            )
        return rows

    def _normalize_brasil(self, text: str) -> str:
        text = text.strip()
        if text.lower().startswith("brasil:"):
            return "BRASIL:" + text.split(":", 1)[1]
        return text

    def _split_value_brasil(self, text: str) -> tuple[str, str | None]:
        marker = re.search(r"\|\|\s*brasil\s*:", text, flags=re.IGNORECASE)
        if marker is not None:
            value = text[: marker.start()].strip()
            brasil = text[marker.start() + 2 :].strip()
            return value, self._normalize_brasil(brasil)

        marker = re.search(r"\|\s*brasil\s*:", text, flags=re.IGNORECASE)
        if marker is not None:
            value = text[: marker.start()].strip()
            brasil = text[marker.start() + 1 :].strip()
            return value, self._normalize_brasil(brasil)

        return text, None

    def _split_series(
        self,
        text: str | None,
        item: dict[str, Any],
        *,
        strip_brasil: bool = False,
    ) -> list[str] | None:
        text = self._clean_value(text)
        if text is None:
            return None
        if strip_brasil and text.lower().startswith("brasil:"):
            text = text.split(":", 1)[1].strip()

        parts = [part.strip() for part in text.split("|")]
        parts = [part for part in parts if part]
        min_year = item.get("min_year")
        if min_year is not None:
            min_year = int(min_year)
            parts = [part for part in parts if self._first_year(part) is None or self._first_year(part) >= min_year]
        return parts or None

    def _extract_note(self, text: str | None, item: dict[str, Any]) -> tuple[str | None, str | None]:
        text = self._clean_value(text)
        if text is None:
            return None, None

        for prefix in item.get("note_prefixes", []):
            index = text.lower().find(str(prefix).lower())
            if index != -1:
                return text[:index].strip(), text[index:].strip()
        return text, None

    def _format_bold_prefix(
        self,
        text: str | None,
        item: dict[str, Any],
        *,
        key: str = "bold_prefixes",
    ) -> dict[str, str] | None:
        text = self._clean_value(text)
        if text is None:
            return None

        for prefix in item.get(key, []):
            prefix = str(prefix)
            if text.lower().startswith(prefix.lower()):
                rest = text[len(prefix) :].lstrip()
                inline_prefixes = item.get("inline_bold_prefixes", [])
                if inline_prefixes:
                    return {
                        "segments": [
                            {"text": text[: len(prefix)], "bold": True},
                            *self._format_inline_bold_segments(rest, inline_prefixes),
                        ]
                    }
                return {
                    "prefix": text[: len(prefix)],
                    "rest": rest,
                }
        return None

    def _format_inline_bold_segments(
        self,
        text: str,
        prefixes: list[str],
    ) -> list[dict[str, Any]]:
        if not text:
            return []

        pattern = re.compile(
            "(" + "|".join(re.escape(str(prefix)) for prefix in prefixes) + ")",
            flags=re.IGNORECASE,
        )
        segments: list[dict[str, Any]] = []
        position = 0
        for match in pattern.finditer(text):
            if match.start() > position:
                segments.append({"text": text[position : match.start()], "bold": False})
            segments.append({"text": text[match.start() : match.end()], "bold": True})
            position = match.end()
        if position < len(text):
            segments.append({"text": text[position:], "bold": False})
        return segments

    def _format_bold_prefixes(
        self,
        lines: list[str] | None,
        item: dict[str, Any],
    ) -> list[str | dict[str, str]] | None:
        if lines is None:
            return None
        return [self._format_bold_prefix(line, item) or line for line in lines]

    def _first_year(self, text: str) -> int | None:
        match = re.search(r"\b(19|20)\d{2}\b", text)
        if match is None:
            return None
        return int(match.group(0))

    def _render_template_text(self, item: dict[str, Any], row: dict[str, Any]) -> str | None:
        template = item.get("template", "")
        if not template:
            return None

        text = template
        for column in item.get("columns", []):
            value = self._clean_value(row.get(column))
            if value is None:
                value = str(item.get("default", "0"))
            text = text.replace("{" + column + "}", value)
        return text

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
        output_path = output_dir / "briefing-local-2.pdf"

        try:
            await renderer.render(
                template_path=self.template_path,
                output_path=output_path,
                data=template_data,
            )
            return output_path.read_bytes()
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)
