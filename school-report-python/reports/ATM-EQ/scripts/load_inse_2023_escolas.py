"""Carrega a planilha INSE 2023 por escola no sandbox.

Uso:
    uv run python reports/ATM-EQ/scripts/load_inse_2023_escolas.py

Observacao:
    O campo ``nivel_socioeconomico`` nesta tabela reutiliza diretamente o valor
    de ``MEDIA_INSE`` da planilha INSE 2023. Portanto, sua escala e semantica
    seguem a nota tecnica do INSE 2023 e nao o contrato historico da tabela
    ``inep_nse_escola`` usada hoje pelo ATM em R.
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
XLSX_PATH = ROOT_DIR / "reports" / "ATM-EQ" / "scripts" / "INSE_2023_escolas.xlsx"

PROJECT_ID = "br-mec-segape-sandbox"
JOB_PROJECT_ID = "br-mec-segape"
DATASET_ID = "projeto_segape_dmape_relat_automatico"
TABLE_ID = "inep_inse_escola"

EXPECTED_SHEET_NAME = "INSE_ESC_2023"
EXPECTED_YEAR = 2023
BATCH_SIZE = 1000

EXPECTED_TOTAL_ROWS = 69756
EXPECTED_UNIQUE_ESCOLAS = 69756
EXPECTED_UNIQUE_MUNICIPIOS = 5558
EXPECTED_REDE_COUNTS = {
    1: 514,
    2: 25181,
    3: 44061,
}
EXPECTED_LOCALIZACAO_COUNTS = {
    1: 53617,
    2: 16139,
}
EXPECTED_TP_CAPITAL = {1, 2}

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

HEADER_MAP = {
    "NU_ANO_SAEB": "ano",
    "CO_UF": "id_uf",
    "SG_UF": "sigla_uf",
    "NO_UF": "estado",
    "CO_MUNICIPIO": "id_municipio",
    "NO_MUNICIPIO": "municipio",
    "ID_ESCOLA": "id_escola",
    "NO_ESCOLA": "escola",
    "TP_TIPO_REDE": "id_dependencia_administrativa",
    "TP_LOCALIZACAO": "id_localizacao",
    "TP_CAPITAL": "tp_capital",
    "QTD_ALUNOS_INSE": "numero_matriculas",
    "MEDIA_INSE": "nivel_socioeconomico",
    "INSE_CLASSIFICACAO": "inse_classificacao",
    "PC_NIVEL_1": "pc_nivel_1",
    "PC_NIVEL_2": "pc_nivel_2",
    "PC_NIVEL_3": "pc_nivel_3",
    "PC_NIVEL_4": "pc_nivel_4",
    "PC_NIVEL_5": "pc_nivel_5",
    "PC_NIVEL_6": "pc_nivel_6",
    "PC_NIVEL_7": "pc_nivel_7",
    "PC_NIVEL_8": "pc_nivel_8",
}

STRING_FIELDS = {
    "sigla_uf",
    "estado",
    "municipio",
    "escola",
    "inse_classificacao",
}
INTEGER_FIELDS = {
    "ano",
    "id_uf",
    "id_municipio",
    "id_escola",
    "id_dependencia_administrativa",
    "id_localizacao",
    "tp_capital",
    "numero_matriculas",
}


def _table_fqn() -> str:
    return f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


def _schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField("ano", "INT64"),
        bigquery.SchemaField("id_uf", "INT64"),
        bigquery.SchemaField("sigla_uf", "STRING"),
        bigquery.SchemaField("estado", "STRING"),
        bigquery.SchemaField("id_municipio", "INT64"),
        bigquery.SchemaField("municipio", "STRING"),
        bigquery.SchemaField("id_escola", "INT64"),
        bigquery.SchemaField("escola", "STRING"),
        bigquery.SchemaField("id_dependencia_administrativa", "INT64"),
        bigquery.SchemaField("id_localizacao", "INT64"),
        bigquery.SchemaField("tp_capital", "INT64"),
        bigquery.SchemaField("numero_matriculas", "INT64"),
        bigquery.SchemaField("nivel_socioeconomico", "FLOAT64"),
        bigquery.SchemaField("inse_classificacao", "STRING"),
        bigquery.SchemaField("pc_nivel_1", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_2", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_3", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_4", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_5", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_6", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_7", "FLOAT64"),
        bigquery.SchemaField("pc_nivel_8", "FLOAT64"),
        bigquery.SchemaField("data_ultima_atualizacao", "TIMESTAMP"),
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
        if row and row[0] == "NU_ANO_SAEB" and len(row) > 13 and row[13] == "INSE_CLASSIFICACAO":
            return idx
    raise RuntimeError("Cabecalho tecnico da planilha INSE nao encontrado.")


def _to_optional_float(raw_value: str) -> float | None:
    value = raw_value.strip()
    if value in {"", "--"}:
        return None
    return float(value)


def _to_optional_int(raw_value: str) -> int | None:
    value = raw_value.strip()
    if value in {"", "--"}:
        return None
    return int(value)


def _transform_rows(rows: list[list[str]], data_ultima_atualizacao: str) -> list[dict[str, object]]:
    header_idx = _locate_header_row(rows)
    technical_header = rows[header_idx]

    unknown_headers = [header for header in technical_header if header and header not in HEADER_MAP]
    if unknown_headers:
        raise RuntimeError(f"Cabecalhos nao mapeados encontrados: {unknown_headers}")

    records: list[dict[str, object]] = []
    for row in rows[header_idx + 1 :]:
        if len(row) < 7:
            continue

        padded = (row + [""] * len(technical_header))[: len(technical_header)]
        if padded[0] != str(EXPECTED_YEAR):
            continue
        if not padded[6].isdigit():
            continue

        record: dict[str, object] = {}
        for idx, source_name in enumerate(technical_header):
            target_name = HEADER_MAP[source_name]
            raw_value = padded[idx]

            if target_name in STRING_FIELDS:
                value = raw_value or None
            elif target_name in INTEGER_FIELDS:
                value = _to_optional_int(raw_value)
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

    unique_escolas = len({record["id_escola"] for record in records})
    if unique_escolas != EXPECTED_UNIQUE_ESCOLAS:
        raise RuntimeError(
            f"Quantidade de escolas divergente: esperado={EXPECTED_UNIQUE_ESCOLAS} atual={unique_escolas}"
        )

    unique_municipios = len({record["id_municipio"] for record in records})
    if unique_municipios != EXPECTED_UNIQUE_MUNICIPIOS:
        raise RuntimeError(
            "Quantidade de municipios divergente: "
            f"esperado={EXPECTED_UNIQUE_MUNICIPIOS} atual={unique_municipios}"
        )

    duplicate_rows = len(records) - len({(record["ano"], record["id_escola"]) for record in records})
    if duplicate_rows != 0:
        raise RuntimeError(f"Duplicidades na origem por ano/id_escola: {duplicate_rows}")

    rede_counts = Counter(record["id_dependencia_administrativa"] for record in records)
    if dict(rede_counts) != EXPECTED_REDE_COUNTS:
        raise RuntimeError(
            f"Contagens de rede divergentes: esperado={EXPECTED_REDE_COUNTS} atual={dict(rede_counts)}"
        )

    localizacao_counts = Counter(record["id_localizacao"] for record in records)
    if dict(localizacao_counts) != EXPECTED_LOCALIZACAO_COUNTS:
        raise RuntimeError(
            "Contagens de localizacao divergentes: "
            f"esperado={EXPECTED_LOCALIZACAO_COUNTS} atual={dict(localizacao_counts)}"
        )

    tp_capital = {record["tp_capital"] for record in records}
    if tp_capital != EXPECTED_TP_CAPITAL:
        raise RuntimeError(f"Dominio de tp_capital divergente: {sorted(tp_capital)}")


def _recreate_table(client: bigquery.Client, schema: list[bigquery.SchemaField]) -> None:
    table_id = _table_fqn()
    client.delete_table(table_id, not_found_ok=True)

    table = bigquery.Table(table_id, schema=schema)
    table = client.create_table(table)

    for _ in range(20):
        current = client.get_table(table.reference)
        if len(current.schema) == len(schema):
            return
        time.sleep(1)

    raise RuntimeError(f"Schema da tabela {table_id} nao ficou disponivel a tempo.")


def _load_records(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    table_fqn = _table_fqn()
    for start in range(0, len(records), BATCH_SIZE):
        chunk = records[start : start + BATCH_SIZE]
        job_config = bigquery.LoadJobConfig(
            schema=_schema(),
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )
        job = client.load_table_from_json(chunk, table_fqn, job_config=job_config)
        job.result()


def _validate_schema(client: bigquery.Client) -> None:
    table = client.get_table(_table_fqn())
    canonical_type = {
        "INTEGER": "INT64",
        "INT64": "INT64",
        "FLOAT": "FLOAT64",
        "FLOAT64": "FLOAT64",
        "STRING": "STRING",
        "TIMESTAMP": "TIMESTAMP",
    }
    actual = [
        (field.name, canonical_type.get(field.field_type, field.field_type), field.mode)
        for field in table.schema
    ]
    expected = [
        (field.name, canonical_type.get(field.field_type, field.field_type), field.mode)
        for field in _schema()
    ]
    if actual != expected:
        raise RuntimeError(f"Schema divergente: esperado={expected} atual={actual}")


def _validate_aggregates(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    query = f"""
    SELECT
      COUNT(*) AS total_rows,
      COUNT(DISTINCT id_escola) AS unique_escolas,
      COUNT(DISTINCT id_municipio) AS unique_municipios,
      COUNT(*) - COUNT(DISTINCT CONCAT(CAST(ano AS STRING), '|', CAST(id_escola AS STRING))) AS duplicate_rows,
      COUNTIF(data_ultima_atualizacao IS NULL) AS null_data_ultima_atualizacao
    FROM `{_table_fqn()}`
    """
    totals = dict(next(iter(client.query(query).result())).items())
    expected = {
        "total_rows": EXPECTED_TOTAL_ROWS,
        "unique_escolas": EXPECTED_UNIQUE_ESCOLAS,
        "unique_municipios": EXPECTED_UNIQUE_MUNICIPIOS,
        "duplicate_rows": 0,
        "null_data_ultima_atualizacao": 0,
    }
    for key, value in expected.items():
        if totals[key] != value:
            raise RuntimeError(f"Validacao falhou para {key}: esperado={value} atual={totals[key]}")

    for field_name, expected_counts in [
        ("id_dependencia_administrativa", EXPECTED_REDE_COUNTS),
        ("id_localizacao", EXPECTED_LOCALIZACAO_COUNTS),
    ]:
        query = f"SELECT {field_name}, COUNT(*) AS total FROM `{_table_fqn()}` GROUP BY 1"
        actual_counts = {row[field_name]: row["total"] for row in client.query(query).result()}
        if actual_counts != expected_counts:
            raise RuntimeError(
                f"Contagens divergentes para {field_name}: esperado={expected_counts} atual={actual_counts}"
            )

    domain_query = f"""
    SELECT
      ARRAY_AGG(DISTINCT id_dependencia_administrativa ORDER BY id_dependencia_administrativa) AS redes,
      ARRAY_AGG(DISTINCT id_localizacao ORDER BY id_localizacao) AS localizacoes,
      ARRAY_AGG(DISTINCT tp_capital ORDER BY tp_capital) AS capitais
    FROM `{_table_fqn()}`
    """
    domain_row = next(iter(client.query(domain_query).result()))
    if list(domain_row["redes"]) != sorted(EXPECTED_REDE_COUNTS):
        raise RuntimeError("Dominio carregado de id_dependencia_administrativa divergente.")
    if list(domain_row["localizacoes"]) != sorted(EXPECTED_LOCALIZACAO_COUNTS):
        raise RuntimeError("Dominio carregado de id_localizacao divergente.")
    if list(domain_row["capitais"]) != sorted(EXPECTED_TP_CAPITAL):
        raise RuntimeError("Dominio carregado de tp_capital divergente.")

    nse_query = f"""
    SELECT
      MIN(nivel_socioeconomico) AS min_nse,
      MAX(nivel_socioeconomico) AS max_nse
    FROM `{_table_fqn()}`
    """
    nse_row = next(iter(client.query(nse_query).result()))
    expected_min = min(record["nivel_socioeconomico"] for record in records if record["nivel_socioeconomico"] is not None)
    expected_max = max(record["nivel_socioeconomico"] for record in records if record["nivel_socioeconomico"] is not None)
    if abs(nse_row["min_nse"] - expected_min) > 1e-9 or abs(nse_row["max_nse"] - expected_max) > 1e-9:
        raise RuntimeError(
            "Faixa de nivel_socioeconomico divergente: "
            f"esperado=({expected_min}, {expected_max}) atual=({nse_row['min_nse']}, {nse_row['max_nse']})"
        )


def _sample_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
        (3, 1),
        (3, 2),
    ]

    samples: list[dict[str, object]] = []
    seen_keys: set[tuple[int, int]] = set()
    for rede, localizacao in wanted:
        for record in records:
            key = (record["id_dependencia_administrativa"], record["id_localizacao"])
            if key in seen_keys:
                continue
            if key == (rede, localizacao):
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


def _fetch_record(client: bigquery.Client, sample: dict[str, object]) -> dict[str, object]:
    query = f"""
    SELECT {", ".join(_schema_field_names())}
    FROM `{_table_fqn()}`
    WHERE ano = @ano
      AND id_escola = @id_escola
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ano", "INT64", sample["ano"]),
            bigquery.ScalarQueryParameter("id_escola", "INT64", sample["id_escola"]),
        ]
    )
    rows = list(client.query(query, job_config=config).result())
    if len(rows) != 1:
        raise RuntimeError(
            f"Esperava 1 linha para a chave {sample['ano']}/{sample['id_escola']}, mas encontrei {len(rows)}"
        )
        return {}
    return dict(rows[0].items())


def _validate_samples(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    for idx, sample in enumerate(_sample_records(records), start=1):
        sample_name = f"amostra_{idx}_{sample['id_escola']}"
        loaded = _fetch_record(client, sample)
        _compare_record(loaded, sample, sample_name)


def main() -> None:
    print(f"Lendo planilha: {XLSX_PATH}")

    with zipfile.ZipFile(XLSX_PATH) as archive:
        shared = _load_shared_strings(archive)
        targets = _sheet_targets(archive)

        if EXPECTED_SHEET_NAME not in targets:
            raise RuntimeError(
                f"Aba nao encontrada: {EXPECTED_SHEET_NAME}. Abas disponiveis: {sorted(targets)}"
            )

        rows = _read_sheet(archive, shared, targets[EXPECTED_SHEET_NAME])

    data_ultima_atualizacao = datetime.now(UTC).isoformat()
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
