"""Carrega a planilha IRD 2025 no sandbox.

Uso:
    uv run python reports/ATM-EQ/scripts/load_ird_municipios_2025.py
"""

from __future__ import annotations

import re
import time
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from google.cloud import bigquery


ROOT_DIR = Path(__file__).resolve().parents[3]
XLSX_PATH = ROOT_DIR / "reports" / "ATM-EQ" / "scripts" / "IRD_MUNICIPIOS_2025.xlsx"

PROJECT_ID = "br-mec-segape-sandbox"
JOB_PROJECT_ID = "br-mec-segape"
DATASET_ID = "projeto_segape_dmape_relat_automatico"
TABLE_ID = "indicadores_educacionais_municipio_ird"
OFFICIAL_TABLE_ID = "br-mec-segape.educacao_inep_dados_abertos.indicadores_educacionais_municipio"

EXPECTED_SHEET_NAMES = {"MUNICIPIOS", "MUNICÍPIOS"}
EXPECTED_YEAR = 2025
BATCH_SIZE = 500

EXPECTED_TOTAL_ROWS = 66588
EXPECTED_UNIQUE_MUNICIPIOS = 5571
EXPECTED_LOCALIZACOES = {"total", "urbana", "rural"}
EXPECTED_REDES = {"total", "publica", "municipal", "estadual", "privada", "federal"}

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

HEADER_MAP = {
    "NU_ANO_CENSO": "ano",
    "CO_MUNICIPIO": "id_municipio",
    "NO_CATEGORIA": "localizacao",
    "NO_DEPENDENCIA": "rede",
    "EDU_BAS_CAT_1": "ird_baixa_regularidade",
    "EDU_BAS_CAT_2": "ird_media_baixa",
    "EDU_BAS_CAT_3": "ird_media_alta",
    "EDU_BAS_CAT_4": "ird_alta",
}

INTEGER_FIELDS = {"ano", "id_municipio"}
ALLOWED_UNUSED_HEADERS = {"NO_REGIAO", "SG_UF", "NO_MUNICIPIO"}

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


def _table_fqn() -> str:
    return f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


def _schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("ano", "INT64"),
        bigquery.SchemaField("id_municipio", "INT64"),
        bigquery.SchemaField("localizacao", "STRING"),
        bigquery.SchemaField("rede", "STRING"),
        bigquery.SchemaField("ird_baixa_regularidade", "FLOAT64"),
        bigquery.SchemaField("ird_media_baixa", "FLOAT64"),
        bigquery.SchemaField("ird_media_alta", "FLOAT64"),
        bigquery.SchemaField("ird_alta", "FLOAT64"),
        bigquery.SchemaField("data_ultima_atualizacao", "DATE"),
    ]


def _schema_field_names() -> list[str]:
    return [field.name for field in _schema()]


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


def _pick_sheet_target(targets: dict[str, str]) -> str:
    for sheet_name in EXPECTED_SHEET_NAMES:
        if sheet_name in targets:
            return targets[sheet_name]
    raise RuntimeError(f"Aba esperada nao encontrada. Abas disponiveis: {sorted(targets)}")


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


def _locate_header_row(rows: list[list[str]]) -> int:
    for idx, row in enumerate(rows):
        if row and row[0] == "NU_ANO_CENSO" and row[-1] == "EDU_BAS_CAT_4":
            return idx
    raise RuntimeError("Cabecalho tecnico da planilha IRD nao encontrado.")


def _normalize_localizacao(value: str) -> str:
    normalized = LOCALIZACAO_MAP.get(value)
    if normalized is None:
        raise RuntimeError(f"Localizacao nao suportada: {value!r}")
    return normalized


def _normalize_rede(value: str) -> str:
    normalized = REDE_MAP.get(value)
    if normalized is None:
        raise RuntimeError(f"Rede nao suportada: {value!r}")
    return normalized


def _to_optional_float(raw_value: str) -> float | None:
    value = raw_value.strip()
    if value in {"", "--"}:
        return None
    return float(value)


def _transform_rows(rows: list[list[str]], data_ultima_atualizacao: str) -> list[dict[str, object]]:
    header_idx = _locate_header_row(rows)
    technical_header = rows[header_idx]

    unknown_headers = [
        header
        for header in technical_header
        if header and header not in HEADER_MAP and header not in ALLOWED_UNUSED_HEADERS
    ]
    if unknown_headers:
        raise RuntimeError(f"Cabecalhos nao mapeados encontrados: {unknown_headers}")

    records: list[dict[str, object]] = []

    for row in rows[header_idx + 1 :]:
        if len(row) < 4:
            continue
        if row[0] != str(EXPECTED_YEAR):
            continue
        if not row[3].isdigit():
            continue

        padded = (row + [""] * len(technical_header))[: len(technical_header)]
        record: dict[str, object] = {}

        for idx, source_name in enumerate(technical_header):
            if source_name not in HEADER_MAP:
                continue
            target_name = HEADER_MAP[source_name]
            raw_value = padded[idx]

            if target_name == "localizacao":
                value = _normalize_localizacao(raw_value)
            elif target_name == "rede":
                value = _normalize_rede(raw_value)
            elif target_name in INTEGER_FIELDS:
                value = int(raw_value)
            else:
                value = _to_optional_float(raw_value)

            record[target_name] = value

        record["data_ultima_atualizacao"] = data_ultima_atualizacao
        records.append(record)

    return records


def _validate_source_records(records: list[dict[str, object]]) -> None:
    if len(records) != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(
            f"Quantidade inesperada de linhas: esperado={EXPECTED_TOTAL_ROWS} atual={len(records)}"
        )

    unique_municipios = len({record["id_municipio"] for record in records})
    if unique_municipios != EXPECTED_UNIQUE_MUNICIPIOS:
        raise RuntimeError(
            f"Quantidade de municipios divergente: esperado={EXPECTED_UNIQUE_MUNICIPIOS} "
            f"atual={unique_municipios}"
        )

    localizacoes = {record["localizacao"] for record in records}
    redes = {record["rede"] for record in records}
    if localizacoes != EXPECTED_LOCALIZACOES:
        raise RuntimeError(
            f"Dominio de localizacao divergente: esperado={sorted(EXPECTED_LOCALIZACOES)} "
            f"atual={sorted(localizacoes)}"
        )
    if redes != EXPECTED_REDES:
        raise RuntimeError(
            f"Dominio de rede divergente: esperado={sorted(EXPECTED_REDES)} "
            f"atual={sorted(redes)}"
        )


def _chunks(records: list[dict[str, object]], size: int) -> list[list[dict[str, object]]]:
    return [records[idx : idx + size] for idx in range(0, len(records), size)]


def _canonical_field_type(field_type: str) -> str:
    mapping = {
        "INT64": "INTEGER",
        "FLOAT64": "FLOAT",
        "BOOL": "BOOLEAN",
    }
    return mapping.get(field_type, field_type)


def _recreate_table(client: bigquery.Client, schema: list[bigquery.SchemaField]) -> None:
    table_fqn = _table_fqn()
    client.delete_table(table_fqn, not_found_ok=True)
    client.create_table(bigquery.Table(table_fqn, schema=schema))

    expected_schema = [(field.name, _canonical_field_type(field.field_type)) for field in schema]
    for _ in range(30):
        try:
            table = client.get_table(table_fqn)
            actual_schema = [(field.name, field.field_type) for field in table.schema]
            if actual_schema == expected_schema:
                time.sleep(5)
                return
        except Exception:
            time.sleep(1)

    raise RuntimeError(f"Tabela nao ficou disponivel a tempo: {table_fqn}")


def _load_records(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    table_fqn = _table_fqn()
    job_config = bigquery.LoadJobConfig(
        schema=_schema(),
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    for chunk in _chunks(records, BATCH_SIZE):
        job = client.load_table_from_json(chunk, table_fqn, job_config=job_config)
        job.result()


def _validate_schema(client: bigquery.Client) -> None:
    expected = [(field.name, _canonical_field_type(field.field_type)) for field in _schema()]
    loaded_table = client.get_table(_table_fqn())
    loaded = [(field.name, field.field_type) for field in loaded_table.schema]
    if loaded != expected:
        raise RuntimeError(f"Schema carregado divergente. Esperado={expected!r} Atual={loaded!r}")


def _expected_counters(
    records: list[dict[str, object]]
) -> tuple[Counter[str], Counter[str], int]:
    localizacao_counts = Counter(record["localizacao"] for record in records)
    rede_counts = Counter(record["rede"] for record in records)
    duplicate_rows = len(records) - len(
        {
            (
                record["ano"],
                record["id_municipio"],
                record["localizacao"],
                record["rede"],
            )
            for record in records
        }
    )
    return localizacao_counts, rede_counts, duplicate_rows


def _validate_aggregates(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    localizacao_counts, rede_counts, expected_duplicates = _expected_counters(records)

    query = f"""
    WITH base AS (
      SELECT *
      FROM `{_table_fqn()}`
    )
    SELECT
      COUNT(*) AS total_rows,
      COUNT(DISTINCT id_municipio) AS unique_municipios,
      COUNT(*) - COUNT(DISTINCT CONCAT(
        CAST(ano AS STRING), '|',
        CAST(id_municipio AS STRING), '|',
        COALESCE(localizacao, ''), '|',
        COALESCE(rede, '')
      )) AS duplicate_rows,
      COUNTIF(data_ultima_atualizacao IS NULL) AS null_data_ultima_atualizacao
    FROM base
    """
    row = next(iter(client.query(query).result()))
    totals = dict(row.items())

    expected = {
        "total_rows": EXPECTED_TOTAL_ROWS,
        "unique_municipios": EXPECTED_UNIQUE_MUNICIPIOS,
        "duplicate_rows": expected_duplicates,
        "null_data_ultima_atualizacao": 0,
    }
    for key, value in expected.items():
        if totals[key] != value:
            raise RuntimeError(f"Validacao falhou para {key}: esperado={value} atual={totals[key]}")

    localizacao_query = f"""
    SELECT localizacao, COUNT(*) AS total
    FROM `{_table_fqn()}`
    GROUP BY 1
    """
    loaded_localizacoes = {
        row["localizacao"]: row["total"] for row in client.query(localizacao_query).result()
    }
    if loaded_localizacoes != dict(localizacao_counts):
        raise RuntimeError(
            f"Contagens de localizacao divergentes: esperado={dict(localizacao_counts)} "
            f"atual={loaded_localizacoes}"
        )

    rede_query = f"""
    SELECT rede, COUNT(*) AS total
    FROM `{_table_fqn()}`
    GROUP BY 1
    """
    loaded_redes = {row["rede"]: row["total"] for row in client.query(rede_query).result()}
    if loaded_redes != dict(rede_counts):
        raise RuntimeError(
            f"Contagens de rede divergentes: esperado={dict(rede_counts)} atual={loaded_redes}"
        )

    domain_query = f"""
    SELECT
      ARRAY_AGG(DISTINCT localizacao ORDER BY localizacao) AS localizacoes,
      ARRAY_AGG(DISTINCT rede ORDER BY rede) AS redes
    FROM `{_table_fqn()}`
    """
    domain_row = next(iter(client.query(domain_query).result()))
    if list(domain_row["localizacoes"]) != sorted(EXPECTED_LOCALIZACOES):
        raise RuntimeError("Dominio carregado de localizacao divergente.")
    if list(domain_row["redes"]) != sorted(EXPECTED_REDES):
        raise RuntimeError("Dominio carregado de rede divergente.")


def _sample_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = [
        ("total", "municipal"),
        ("urbana", "municipal"),
        ("rural", "municipal"),
        ("total", "publica"),
        ("total", "estadual"),
        ("rural", "federal"),
        ("total", "privada"),
    ]

    samples: list[dict[str, object]] = []
    seen_keys: set[tuple[int, str, str]] = set()
    for localizacao, rede in wanted:
        for record in records:
            key = (record["id_municipio"], record["localizacao"], record["rede"])
            if key in seen_keys:
                continue
            if record["localizacao"] == localizacao and record["rede"] == rede:
                samples.append(record)
                seen_keys.add(key)
                break

    if len(samples) < 5:
        raise RuntimeError(f"Quantidade insuficiente de amostras selecionadas: {len(samples)}")

    return samples


def _compare_record(actual: dict[str, object], expected: dict[str, object], sample_name: str) -> None:
    for field_name in _schema_field_names():
        if field_name == "data_ultima_atualizacao":
            if actual[field_name] is None:
                raise RuntimeError(f"{sample_name}: campo data_ultima_atualizacao veio nulo")
            continue

        expected_value = expected[field_name]
        actual_value = actual[field_name]
        if isinstance(expected_value, float):
            if actual_value is None or abs(actual_value - expected_value) > 1e-6:
                raise RuntimeError(
                    f"{sample_name}: divergencia em {field_name}: "
                    f"esperado={expected_value} atual={actual_value}"
                )
        elif actual_value != expected_value:
            raise RuntimeError(
                f"{sample_name}: divergencia em {field_name}: "
                f"esperado={expected_value!r} atual={actual_value!r}"
            )


def _fetch_record(client: bigquery.Client, table_id: str, sample: dict[str, object]) -> dict[str, object]:
    query = f"""
    SELECT {", ".join(_schema_field_names())}
    FROM `{table_id}`
    WHERE ano = @ano
      AND id_municipio = @id_municipio
      AND localizacao = @localizacao
      AND rede = @rede
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ano", "INT64", sample["ano"]),
            bigquery.ScalarQueryParameter("id_municipio", "INT64", sample["id_municipio"]),
            bigquery.ScalarQueryParameter("localizacao", "STRING", sample["localizacao"]),
            bigquery.ScalarQueryParameter("rede", "STRING", sample["rede"]),
        ]
    )

    rows = list(client.query(query, job_config=config).result())
    if len(rows) != 1:
        raise RuntimeError(
            f"Esperava 1 linha em {table_id} para a chave "
            f"{sample['ano']}/{sample['id_municipio']}/{sample['localizacao']}/{sample['rede']}, "
            f"mas encontrei {len(rows)}"
        )
    return dict(rows[0].items())


def _official_has_expected_year(client: bigquery.Client) -> bool:
    query = f"""
    SELECT COUNT(*) AS total
    FROM `{OFFICIAL_TABLE_ID}`
    WHERE ano = @ano
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("ano", "INT64", EXPECTED_YEAR)]
    )
    row = next(iter(client.query(query, job_config=config).result()))
    return row["total"] > 0


def _validate_samples(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    validate_official_samples = _official_has_expected_year(client)

    for idx, sample in enumerate(_sample_records(records), start=1):
        sample_name = (
            f"amostra_{idx}_{sample['id_municipio']}_{sample['localizacao']}_{sample['rede']}"
        )
        loaded = _fetch_record(client, _table_fqn(), sample)
        _compare_record(loaded, sample, sample_name)

    if not validate_official_samples:
        print(
            "Validacao contra a tabela oficial foi ignorada: "
            f"{OFFICIAL_TABLE_ID} nao possui registros para {EXPECTED_YEAR}."
        )


def main() -> None:
    print(f"Lendo planilha: {XLSX_PATH}")

    with zipfile.ZipFile(XLSX_PATH) as archive:
        shared = _load_shared_strings(archive)
        targets = _sheet_targets(archive)
        rows = _read_sheet(archive, shared, _pick_sheet_target(targets))

    data_ultima_atualizacao = datetime.now(UTC).date().isoformat()
    records = _transform_rows(rows, data_ultima_atualizacao)

    print(f"Linhas validas lidas: {len(records)}")
    _validate_source_records(records)
    print("Validacao estrutural da planilha concluida.")

    client = bigquery.Client(project=JOB_PROJECT_ID)

    print(f"Recriando tabela {_table_fqn()}...")
    _recreate_table(client, _schema())

    print("Inserindo registros...")
    _load_records(client, records)

    print("Validando schema...")
    _validate_schema(client)

    print("Validando contagens, dominios e duplicidades...")
    _validate_aggregates(client, records)

    print("Validando amostras...")
    _validate_samples(client, records)

    print("Carga concluida com sucesso.")
    print(f"Tabela: {_table_fqn()}")
    print(f"Total de linhas carregadas: {len(records)}")


if __name__ == "__main__":
    main()
