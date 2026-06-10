"""Helpers compartilhados para os loaders de ATU 2025."""

from __future__ import annotations

import json
import re
import time
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from google.cloud import bigquery


ROOT_DIR = Path(__file__).resolve().parents[3]
PROJECT_ID = "br-mec-segape-sandbox"
JOB_PROJECT_ID = "br-mec-segape"
DATASET_ID = "projeto_segape_dmape_relat_automatico"
OFFICIAL_PROJECT = "br-mec-segape"
METADATA_ROOT = ROOT_DIR / "output" / "metadata"
EXPECTED_YEAR = 2025
BATCH_SIZE = 500

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

LOCALIZACAO_MAP = {
    "Total": "total",
    "Urbana": "urbana",
    "Rural": "rural",
}

REDE_MAP = {
    "Total": "total",
    "Pública": "publica",
    "Municipal": "municipal",
    "Estadual": "estadual",
    "Privada": "privada",
    "Federal": "federal",
}

ATU_FIELD_MAP = {
    "ED_INF_CAT_0": "atu_ei",
    "CRE_CAT_0": "atu_ei_creche",
    "PRE_CAT_0": "atu_ei_pre_escola",
    "FUN_CAT_0": "atu_ef",
    "FUN_AI_CAT_0": "atu_ef_anos_iniciais",
    "FUN_AF_CAT_0": "atu_ef_anos_finais",
    "FUN_01_CAT_0": "atu_ef_1_ano",
    "FUN_02_CAT_0": "atu_ef_2_ano",
    "FUN_03_CAT_0": "atu_ef_3_ano",
    "FUN_04_CAT_0": "atu_ef_4_ano",
    "FUN_05_CAT_0": "atu_ef_5_ano",
    "FUN_06_CAT_0": "atu_ef_6_ano",
    "FUN_07_CAT_0": "atu_ef_7_ano",
    "FUN_08_CAT_0": "atu_ef_8_ano",
    "FUN_09_CAT_0": "atu_ef_9_ano",
    "MULT_ETA_CAT_0": "atu_ef_turmas_unif_multi_fluxo",
    "MED_CAT_0": "atu_em",
    "MED_01_CAT_0": "atu_em_1_ano",
    "MED_02_CAT_0": "atu_em_2_ano",
    "MED_03_CAT_0": "atu_em_3_ano",
    "MED_04_CAT_0": "atu_em_4_ano",
    "MED_NS_CAT_0": "atu_em_nao_seriado",
}

REGIOES = {"Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"}


def normalize_ascii(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def table_fqn(table_id: str) -> str:
    return f"{PROJECT_ID}.{DATASET_ID}.{table_id}"


def official_table_fqn(table_name: str) -> str:
    return f"{OFFICIAL_PROJECT}.educacao_inep_indicadores_educacionais.{table_name}"


def latest_metadata_snapshot_dir() -> Path:
    snapshots = sorted(METADATA_ROOT.glob("metadata_snapshot_*"))
    if not snapshots:
        raise RuntimeError(f"Nenhum snapshot de metadata encontrado em {METADATA_ROOT}")
    return snapshots[-1]


def load_schema_from_metadata(table_name: str) -> list[bigquery.SchemaField]:
    schema_path = (
        latest_metadata_snapshot_dir()
        / "schemas"
        / "educacao_inep_indicadores_educacionais"
        / f"{table_name}.json"
    )
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    return [
        bigquery.SchemaField(column["column_name"], column["data_type"], mode=column["mode"])
        for column in data["columns"]
    ]


def schema_field_names(schema: list[bigquery.SchemaField]) -> list[str]:
    return [field.name for field in schema]


def col_to_idx(ref: str) -> int:
    match = re.match(r"([A-Z]+)(\d+)", ref)
    if not match:
        raise ValueError(f"Referencia de celula invalida: {ref}")

    col = 0
    for ch in match.group(1):
        col = col * 26 + (ord(ch) - 64)
    return col - 1


def load_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//a:t", NS)) for si in root.findall("a:si", NS)]


def sheet_targets(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relmap = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    return {
        sheet.attrib["name"]: "xl/"
        + relmap[sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]]
        for sheet in workbook.find("a:sheets", NS)
    }


def read_sheet(archive: zipfile.ZipFile, shared: list[str], target: str) -> list[list[str]]:
    root = ET.fromstring(archive.read(target))
    rows: list[list[str]] = []

    for row in root.findall(".//a:sheetData/a:row", NS):
        values: dict[int, str] = {}
        for cell in row.findall("a:c", NS):
            idx = col_to_idx(cell.attrib["r"])
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


def locate_header_row(rows: list[list[str]]) -> int:
    for idx, row in enumerate(rows):
        if row and row[0] == "NU_ANO_CENSO" and row[-1] == "MED_NS_CAT_0":
            return idx
    raise RuntimeError("Cabecalho tecnico da planilha ATU nao encontrado.")


def normalize_localizacao(value: str) -> str:
    normalized = LOCALIZACAO_MAP.get(value)
    if normalized is None:
        raise RuntimeError(f"Localizacao nao suportada: {value!r}")
    return normalized


def normalize_rede(value: str) -> str:
    normalized = REDE_MAP.get(value)
    if normalized is None:
        raise RuntimeError(f"Rede nao suportada: {value!r}")
    return normalized


def to_optional_float(raw_value: str) -> float | None:
    value = raw_value.strip()
    if value in {"", "--"}:
        return None
    return float(value)


def recreate_table(client: bigquery.Client, table_id: str, schema: list[bigquery.SchemaField]) -> None:
    fqn = table_fqn(table_id)
    client.delete_table(fqn, not_found_ok=True)
    client.create_table(bigquery.Table(fqn, schema=schema))

    expected = [(field.name, field.field_type) for field in schema]
    for _ in range(30):
        try:
            table = client.get_table(fqn)
            actual = [(field.name, field.field_type) for field in table.schema]
            if actual == expected:
                time.sleep(5)
                return
        except Exception:
            time.sleep(1)

    raise RuntimeError(f"Tabela nao ficou disponivel a tempo: {fqn}")


def load_records(
    client: bigquery.Client,
    table_id: str,
    schema: list[bigquery.SchemaField],
    records: list[dict[str, object]],
) -> None:
    fqn = table_fqn(table_id)
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    for idx in range(0, len(records), BATCH_SIZE):
        chunk = records[idx : idx + BATCH_SIZE]
        job = client.load_table_from_json(chunk, fqn, job_config=job_config)
        job.result()


def validate_schema(
    client: bigquery.Client,
    table_id: str,
    schema: list[bigquery.SchemaField],
    official_table: str,
) -> None:
    expected = [(field.name, field.field_type) for field in schema]

    loaded = client.get_table(table_fqn(table_id))
    loaded_schema = [(field.name, field.field_type) for field in loaded.schema]
    if loaded_schema != expected:
        raise RuntimeError(f"Schema carregado divergente em {table_id}.")

    official = client.get_table(official_table)
    official_schema = [(field.name, field.field_type) for field in official.schema]
    if official_schema != expected:
        raise RuntimeError(f"Schema oficial divergente para {official_table}.")


def official_has_expected_year(client: bigquery.Client, official_table: str) -> bool:
    query = f"SELECT COUNT(*) AS total FROM `{official_table}` WHERE ano = @ano"
    config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("ano", "INT64", EXPECTED_YEAR)]
    )
    row = next(iter(client.query(query, job_config=config).result()))
    return row["total"] > 0


def build_uf_name_map(client: bigquery.Client) -> dict[str, str]:
    query = """
    SELECT sigla, nome
    FROM `br-mec-segape.educacao_dados_mestres.uf`
    """
    return {
        normalize_ascii(row["nome"]): row["sigla"]
        for row in client.query(query).result()
    }
