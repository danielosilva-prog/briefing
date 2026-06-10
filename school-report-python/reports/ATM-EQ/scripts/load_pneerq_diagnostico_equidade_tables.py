"""Cria e carrega tabelas do Diagnóstico de Equidade (PNEERQ) no sandbox.

Uso:
    uv run python reports/ATM-EQ/scripts/load_pneerq_diagnostico_equidade_tables.py
"""

from __future__ import annotations

import re
import time
import unicodedata
import zipfile
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

from google.api_core.exceptions import NotFound
from google.cloud import bigquery


ROOT_DIR = Path(__file__).resolve().parents[3]
XLSX_PATH = ROOT_DIR / "reports" / "ATM-EQ" / "docs" / "Diagnostico_Equidade_ATM.xlsx"
PROJECT_ID = "br-mec-segape-sandbox"
DATASET_ID = "projeto_segape_dmape_relat_automatico"
TABLE_MUNICIPIO = "atm_eq_pneerq_diagnostico_equidade_municipio"
TABLE_UF = "atm_eq_pneerq_diagnostico_equidade_uf"
TABLE_DICIONARIO = "atm_eq_pneerq_dicionario_variavel"
ANO_REFERENCIA = 2024
BATCH_SIZE = 500

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

BASE_FIELD_MAP = {
    "CO_REGIAO": "co_regiao",
    "NO_REGIAO": "no_regiao",
    "CO_UF": "co_uf",
    "NO_UF": "no_uf",
    "SIGLA_UF": "sg_uf",
    "CO_MUNICIPIO": "co_municipio",
    "NO_MUNICIPIO": "no_municipio",
    "POP_QUILOMBOLA": "in_pop_quilombola",
    "ESCOLAS_QUILOMBOLAS": "in_escolas_quilombolas",
    "ESCOLAS_INDIGENAS": "in_escolas_indigenas",
}

STRING_BASE_FIELDS = {
    "co_regiao",
    "no_regiao",
    "co_uf",
    "no_uf",
    "sg_uf",
    "co_municipio",
    "no_municipio",
}
BOOL_FIELDS = {
    "in_pop_quilombola",
    "in_escolas_quilombolas",
    "in_escolas_indigenas",
}


def _normalize_ascii(value: str) -> str:
    return (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
    )


def _slugify(value: str) -> str:
    normalized = _normalize_ascii(value).lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_")


def _col_to_idx(ref: str) -> int:
    match = re.match(r"([A-Z]+)(\d+)", ref)
    if not match:
        raise ValueError(f"Referencia de celula invalida: {ref}")

    col = 0
    for ch in match.group(1):
        col = col * 26 + (ord(ch) - 64)
    return col - 1


def _load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    shared: list[str] = []
    for si in root.findall("a:si", NS):
        shared.append("".join(t.text or "" for t in si.findall(".//a:t", NS)))
    return shared


def _sheet_targets(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relmap = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

    targets: dict[str, str] = {}
    for sheet in workbook.find("a:sheets", NS):
        name = sheet.attrib["name"]
        rel_id = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        targets[name] = "xl/" + relmap[rel_id]
    return targets


def _read_sheet(archive: zipfile.ZipFile, shared: list[str], target: str) -> list[list[str]]:
    root = ET.fromstring(archive.read(target))
    rows: list[list[str]] = []

    for row in root.findall(".//a:sheetData/a:row", NS):
        values: dict[int, str] = {}
        for cell in row.findall("a:c", NS):
            idx = _col_to_idx(cell.attrib["r"])
            cell_type = cell.attrib.get("t")
            value_node = cell.find("a:v", NS)
            inline_node = cell.find("a:is", NS)
            value = ""

            if cell_type == "s" and value_node is not None:
                value = shared[int(value_node.text)]
            elif cell_type == "inlineStr" and inline_node is not None:
                value = "".join(t.text or "" for t in inline_node.findall(".//a:t", NS))
            elif value_node is not None:
                value = value_node.text or ""

            values[idx] = value.strip()

        if values:
            arr = [""] * (max(values) + 1)
            for idx, value in values.items():
                arr[idx] = value
            rows.append(arr)

    return rows


def _map_sheet_header(raw_header: str) -> str:
    if raw_header in BASE_FIELD_MAP:
        return BASE_FIELD_MAP[raw_header]

    p_match = re.fullmatch(r"P(\d+)([A-Z])", raw_header)
    if p_match:
        return f"p{int(p_match.group(1))}_{p_match.group(2).lower()}"

    if raw_header.startswith("I_"):
        return _slugify(raw_header)

    raise ValueError(f"Cabecalho nao mapeado: {raw_header}")


def _to_bool(value: str) -> bool | None:
    if value in {"", "999"}:
        return None
    if value == "1":
        return True
    if value == "0":
        return False
    raise ValueError(f"Valor booleano inesperado: {value}")


def _to_numeric_string(value: str) -> str | None:
    if value in {"", "999"}:
        return None
    normalized = _normalize_ascii(value).lower()
    if normalized in {"nao respondeu ao questionario", "nao se aplica"}:
        return None
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
        return None
    try:
        decimal_value = Decimal(value).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return None
    return format(decimal_value, "f")


def _to_question_value(value: str) -> str | None:
    if value in {"", "999"}:
        return None
    return value


def _table_id(table_name: str) -> str:
    return f"{PROJECT_ID}.{DATASET_ID}.{table_name}"


def _build_sheet_schema(raw_headers: list[str]) -> tuple[list[str], list[bigquery.SchemaField]]:
    field_names = [_map_sheet_header(header) for header in raw_headers]
    schema: list[bigquery.SchemaField] = []

    for field_name in field_names:
        if field_name in STRING_BASE_FIELDS:
            field_type = "STRING"
        elif field_name in BOOL_FIELDS:
            field_type = "BOOL"
        elif field_name.startswith("p"):
            field_type = "STRING"
        elif field_name.startswith("i_"):
            field_type = "BIGNUMERIC"
        else:
            raise ValueError(f"Tipo nao suportado para campo {field_name}")
        schema.append(bigquery.SchemaField(field_name, field_type))

    schema.extend(
        [
            bigquery.SchemaField("ano_referencia", "INT64"),
            bigquery.SchemaField("dt_carga", "TIMESTAMP"),
        ]
    )
    return field_names, schema


def _transform_sheet_rows(
    rows: list[list[str]], field_names: list[str], dt_carga: str
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    for row in rows[1:]:
        record: dict[str, object] = {}
        for idx, field_name in enumerate(field_names):
            raw_value = row[idx] if idx < len(row) else ""
            if field_name in STRING_BASE_FIELDS:
                value = raw_value or None
            elif field_name in BOOL_FIELDS:
                value = _to_bool(raw_value)
            elif field_name.startswith("p"):
                value = _to_question_value(raw_value)
            elif field_name.startswith("i_"):
                value = _to_numeric_string(raw_value)
            else:
                raise ValueError(f"Campo inesperado: {field_name}")
            record[field_name] = value

        record["ano_referencia"] = ANO_REFERENCIA
        record["dt_carga"] = dt_carga
        records.append(record)

    return records


def _dictionary_schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("co_pergunta", "STRING"),
        bigquery.SchemaField("ds_pergunta", "STRING"),
        bigquery.SchemaField("co_item_pergunta", "STRING"),
        bigquery.SchemaField("tp_variavel", "STRING"),
        bigquery.SchemaField("co_resposta", "STRING"),
        bigquery.SchemaField("ds_resposta", "STRING"),
        bigquery.SchemaField("no_indice", "STRING"),
        bigquery.SchemaField("ano_referencia", "INT64"),
        bigquery.SchemaField("dt_carga", "TIMESTAMP"),
    ]


def _transform_dictionary_rows(rows: list[list[str]], dt_carga: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    carry = {
        "co_pergunta": None,
        "ds_pergunta": None,
        "co_item_pergunta": None,
        "tp_variavel": None,
        "no_indice": None,
    }

    for row in rows[2:]:
        cols = (row + [""] * 8)[:8]
        current = {
            "co_pergunta": cols[1] or None,
            "ds_pergunta": cols[2] or None,
            "co_item_pergunta": cols[3] or None,
            "tp_variavel": cols[4] or None,
            "co_resposta": cols[5] or None,
            "ds_resposta": cols[6] or None,
            "no_indice": cols[7] or None,
        }

        raw_has_data = any(current.values())
        if not raw_has_data:
            continue

        for key in carry:
            if current[key] is not None:
                carry[key] = current[key]
            else:
                current[key] = carry[key]

        if not current["co_pergunta"]:
            continue

        record = {
            "co_pergunta": current["co_pergunta"],
            "ds_pergunta": current["ds_pergunta"],
            "co_item_pergunta": current["co_item_pergunta"],
            "tp_variavel": current["tp_variavel"],
            "co_resposta": current["co_resposta"],
            "ds_resposta": current["ds_resposta"],
            "no_indice": current["no_indice"],
            "ano_referencia": ANO_REFERENCIA,
            "dt_carga": dt_carga,
        }
        records.append(record)

    return records


def _chunks(records: list[dict[str, object]], size: int) -> Iterable[list[dict[str, object]]]:
    for idx in range(0, len(records), size):
        yield records[idx : idx + size]


def _recreate_and_load_table(
    client: bigquery.Client,
    table_name: str,
    schema: list[bigquery.SchemaField],
    records: list[dict[str, object]],
) -> None:
    table_id = _table_id(table_name)
    try:
        table = client.get_table(table_id)
        if table.num_rows and table.num_rows > 0:
            raise RuntimeError(
                f"A tabela {table_name} ja contem dados ({table.num_rows} linhas). "
                "Esvazie ou troque o nome antes de recarregar."
            )
    except NotFound:
        client.create_table(bigquery.Table(table_id, schema=schema), exists_ok=True)
        for _ in range(120):
            try:
                client.get_table(table_id)
                break
            except Exception:
                time.sleep(1)

    for chunk in _chunks(records, BATCH_SIZE):
        errors = None
        for _ in range(120):
            try:
                errors = client.insert_rows_json(table_id, chunk)
                break
            except Exception as exc:
                if "not found" not in str(exc).lower():
                    raise
                time.sleep(1)
        if errors is None:
            raise RuntimeError(f"Falha ao inserir em {table_name}: tabela nao ficou disponivel a tempo")
        if errors:
            raise RuntimeError(f"Falha ao inserir em {table_name}: {errors}")

    table = client.get_table(table_id)
    print(f"{table_name}: {table.num_rows} linhas")


def main() -> None:
    dt_carga = datetime.now(UTC).isoformat()
    client = bigquery.Client(project=PROJECT_ID)

    with zipfile.ZipFile(XLSX_PATH) as archive:
        shared = _load_shared_strings(archive)
        targets = _sheet_targets(archive)

        municipio_rows = _read_sheet(archive, shared, targets["Respostas - Redes Municipais"])
        uf_rows = _read_sheet(archive, shared, targets["Respostas - Redes Estaduais"])
        dicionario_rows = _read_sheet(archive, shared, targets["Dicionario de Variáveis"])

    municipio_fields, municipio_schema = _build_sheet_schema(municipio_rows[0])
    uf_fields, uf_schema = _build_sheet_schema(uf_rows[0])

    municipio_records = _transform_sheet_rows(municipio_rows, municipio_fields, dt_carga)
    uf_records = _transform_sheet_rows(uf_rows, uf_fields, dt_carga)
    dicionario_records = _transform_dictionary_rows(dicionario_rows, dt_carga)

    _recreate_and_load_table(client, TABLE_MUNICIPIO, municipio_schema, municipio_records)
    _recreate_and_load_table(client, TABLE_UF, uf_schema, uf_records)
    _recreate_and_load_table(client, TABLE_DICIONARIO, _dictionary_schema(), dicionario_records)


if __name__ == "__main__":
    main()
