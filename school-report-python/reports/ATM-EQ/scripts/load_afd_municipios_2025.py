"""Carrega a planilha AFD 2025 no sandbox com schema compatível ao datalake.

Uso:
    uv run python reports/ATM-EQ/scripts/load_afd_municipios_2025.py
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
XLSX_PATH = ROOT_DIR / "reports" / "ATM-EQ" / "scripts" / "AFD_MUNICIPIOS_2025.xlsx"

PROJECT_ID = "br-mec-segape-sandbox"
JOB_PROJECT_ID = "br-mec-segape"
DATASET_ID = "projeto_segape_dmape_relat_automatico"
TABLE_ID = "inep_adequacao_formacao_docente_municipio"
OFFICIAL_TABLE_ID = "br-mec-segape.educacao_inep_dados_abertos.inep_adequacao_formacao_docente_municipio"

EXPECTED_SHEET_NAME = "Ind. adeq. form. doc."
EXPECTED_YEAR = 2025
BATCH_SIZE = 500

EXPECTED_TOTAL_ROWS = 67178
EXPECTED_UNIQUE_MUNICIPIOS = 5571
EXPECTED_LOCALIZACAO_COUNTS = {
    "Total": 26029,
    "Urbana": 25843,
    "Rural": 15306,
}
EXPECTED_DEPENDENCIA_COUNTS = {
    "Total": 15471,
    "Pública": 15454,
    "Municipal": 15259,
    "Estadual": 13160,
    "Privada": 6722,
    "Federal": 1112,
}

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

HEADER_MAP = {
    "NU_ANO_CENSO": "ano_censo",
    "NO_REGIAO": "regiao",
    "SG_UF": "sigla_uf",
    "CO_MUNICIPIO": "id_municipio",
    "NO_MUNICIPIO": "municipio",
    "NO_CATEGORIA": "localizacao",
    "NO_DEPENDENCIA": "dependencia_administrativa",
    "ED_INF_CAT_1": "educacao_infantil_grupo_1",
    "ED_INF_CAT_2": "educacao_infantil_grupo_2",
    "ED_INF_CAT_3": "educacao_infantil_grupo_3",
    "ED_INF_CAT_4": "educacao_infantil_grupo_4",
    "ED_INF_CAT_5": "educacao_infantil_grupo_5",
    "FUN_CAT_1": "ensino_fundamental_grupo_1",
    "FUN_CAT_2": "ensino_fundamental_grupo_2",
    "FUN_CAT_3": "ensino_fundamental_grupo_3",
    "FUN_CAT_4": "ensino_fundamental_grupo_4",
    "FUN_CAT_5": "ensino_fundamental_grupo_5",
    "FUN_AI_CAT_1": "ensino_fundamental_anos_iniciais_grupo_1",
    "FUN_AI_CAT_2": "ensino_fundamental_anos_iniciais_grupo_2",
    "FUN_AI_CAT_3": "ensino_fundamental_anos_iniciais_grupo_3",
    "FUN_AI_CAT_4": "ensino_fundamental_anos_iniciais_grupo_4",
    "FUN_AI_CAT_5": "ensino_fundamental_anos_iniciais_grupo_5",
    "FUN_AF_CAT_1": "ensino_fundamental_anos_finais_grupo_1",
    "FUN_AF_CAT_2": "ensino_fundamental_anos_finais_grupo_2",
    "FUN_AF_CAT_3": "ensino_fundamental_anos_finais_grupo_3",
    "FUN_AF_CAT_4": "ensino_fundamental_anos_finais_grupo_4",
    "FUN_AF_CAT_5": "ensino_fundamental_anos_finais_grupo_5",
    "MED_CAT_1": "ensino_medio_grupo_1",
    "MED_CAT_2": "ensino_medio_grupo_2",
    "MED_CAT_3": "ensino_medio_grupo_3",
    "MED_CAT_4": "ensino_medio_grupo_4",
    "MED_CAT_5": "ensino_medio_grupo_5",
    "EJA_FUN_CAT_1": "eja_ensino_fundamental_grupo_1",
    "EJA_FUN_CAT_2": "eja_ensino_fundamental_grupo_2",
    "EJA_FUN_CAT_3": "eja_ensino_fundamental_grupo_3",
    "EJA_FUN_CAT_4": "eja_ensino_fundamental_grupo_4",
    "EJA_FUN_CAT_5": "eja_ensino_fundamental_grupo_5",
    "EJA_MED_CAT_1": "eja_ensino_medio_grupo_1",
    "EJA_MED_CAT_2": "eja_ensino_medio_grupo_2",
    "EJA_MED_CAT_3": "eja_ensino_medio_grupo_3",
    "EJA_MED_CAT_4": "eja_ensino_medio_grupo_4",
    "EJA_MED_CAT_5": "eja_ensino_medio_grupo_5",
}

STRING_FIELDS = {
    "regiao",
    "sigla_uf",
    "municipio",
    "localizacao",
    "dependencia_administrativa",
}
INTEGER_FIELDS = {"ano_censo", "id_municipio"}


def _table_fqn() -> str:
    return f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


def _schema() -> list[bigquery.SchemaField]:
    fields = [
        bigquery.SchemaField("ano_censo", "INT64"),
        bigquery.SchemaField("regiao", "STRING"),
        bigquery.SchemaField("sigla_uf", "STRING"),
        bigquery.SchemaField("id_municipio", "INT64"),
        bigquery.SchemaField("municipio", "STRING"),
        bigquery.SchemaField("localizacao", "STRING"),
        bigquery.SchemaField("dependencia_administrativa", "STRING"),
    ]

    for technical_name in HEADER_MAP:
        target_name = HEADER_MAP[technical_name]
        if target_name in STRING_FIELDS or target_name in INTEGER_FIELDS:
            continue
        fields.append(bigquery.SchemaField(target_name, "FLOAT64"))

    fields.append(bigquery.SchemaField("data_ultima_atualizacao", "DATE"))
    return fields


def _schema_field_names() -> list[str]:
    return [field.name for field in _schema()]


def _col_to_idx(ref: str) -> int:
    match = re.match(r"([A-Z]+)(\d+)", ref)
    if not match:
        raise ValueError(f"Referência de célula inválida: {ref}")

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
        if row and row[0] == "NU_ANO_CENSO" and len(row) > 6 and row[6] == "NO_DEPENDENCIA":
            return idx
    raise RuntimeError("Cabeçalho técnico da planilha AFD não encontrado.")


def _to_optional_float(raw_value: str) -> float | None:
    value = raw_value.strip()
    if value in {"", "--"}:
        return None
    return float(value)


def _transform_rows(rows: list[list[str]], data_ultima_atualizacao: str) -> list[dict[str, object]]:
    header_idx = _locate_header_row(rows)
    technical_header = rows[header_idx]

    unknown_headers = [header for header in technical_header if header and header not in HEADER_MAP]
    if unknown_headers:
        raise RuntimeError(f"Cabeçalhos não mapeados encontrados: {unknown_headers}")

    records: list[dict[str, object]] = []

    for row in rows[header_idx + 1 :]:
        if len(row) < 7:
            continue
        if row[0] != str(EXPECTED_YEAR):
            continue
        if not row[3].isdigit():
            continue

        padded = (row + [""] * len(technical_header))[: len(technical_header)]
        record: dict[str, object] = {}

        for idx, source_name in enumerate(technical_header):
            target_name = HEADER_MAP[source_name]
            raw_value = padded[idx]

            if target_name in STRING_FIELDS:
                value = raw_value or None
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

    localizacao_counts = Counter(record["localizacao"] for record in records)
    dependencia_counts = Counter(record["dependencia_administrativa"] for record in records)
    unique_municipios = len({record["id_municipio"] for record in records})

    if dict(localizacao_counts) != EXPECTED_LOCALIZACAO_COUNTS:
        raise RuntimeError(
            f"Contagens de localizacao divergentes: esperado={EXPECTED_LOCALIZACAO_COUNTS} "
            f"atual={dict(localizacao_counts)}"
        )

    if dict(dependencia_counts) != EXPECTED_DEPENDENCIA_COUNTS:
        raise RuntimeError(
            f"Contagens de dependencia divergentes: esperado={EXPECTED_DEPENDENCIA_COUNTS} "
            f"atual={dict(dependencia_counts)}"
        )

    if unique_municipios != EXPECTED_UNIQUE_MUNICIPIOS:
        raise RuntimeError(
            f"Quantidade de municipios divergente: esperado={EXPECTED_UNIQUE_MUNICIPIOS} "
            f"atual={unique_municipios}"
        )


def _chunks(records: list[dict[str, object]], size: int) -> list[list[dict[str, object]]]:
    return [records[idx : idx + size] for idx in range(0, len(records), size)]


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
                # O endpoint de streaming pode levar alguns segundos para enxergar o novo schema.
                time.sleep(15)
                return
        except Exception:
            time.sleep(1)

    raise RuntimeError(f"Tabela não ficou disponível a tempo: {table_fqn}")


def _load_records(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    table_fqn = _table_fqn()
    for chunk in _chunks(records, BATCH_SIZE):
        job = client.load_table_from_json(
            chunk,
            table_fqn,
            job_config=bigquery.LoadJobConfig(
                schema=_schema(),
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            ),
        )
        job.result()


def _canonical_field_type(field_type: str) -> str:
    mapping = {
        "INT64": "INTEGER",
        "FLOAT64": "FLOAT",
        "BOOL": "BOOLEAN",
    }
    return mapping.get(field_type, field_type)


def _validate_schema(client: bigquery.Client) -> None:
    expected = [(field.name, _canonical_field_type(field.field_type)) for field in _schema()]

    loaded_table = client.get_table(_table_fqn())
    loaded = [(field.name, field.field_type) for field in loaded_table.schema]
    if loaded != expected:
        raise RuntimeError(f"Schema carregado divergente. Esperado={expected!r} Atual={loaded!r}")

    official_table = client.get_table(OFFICIAL_TABLE_ID)
    official = [(field.name, field.field_type) for field in official_table.schema]
    if official != expected:
        raise RuntimeError(f"Schema oficial divergente do alvo. Esperado={expected!r} Atual={official!r}")


def _validate_aggregates(client: bigquery.Client) -> None:
    query = f"""
    WITH base AS (
      SELECT *
      FROM `{_table_fqn()}`
    )
    SELECT
      COUNT(*) AS total_rows,
      COUNT(DISTINCT id_municipio) AS unique_municipios,
      COUNTIF(localizacao = 'Total') AS loc_total,
      COUNTIF(localizacao = 'Urbana') AS loc_urbana,
      COUNTIF(localizacao = 'Rural') AS loc_rural,
      COUNTIF(dependencia_administrativa = 'Total') AS dep_total,
      COUNTIF(dependencia_administrativa = 'Pública') AS dep_publica,
      COUNTIF(dependencia_administrativa = 'Municipal') AS dep_municipal,
      COUNTIF(dependencia_administrativa = 'Estadual') AS dep_estadual,
      COUNTIF(dependencia_administrativa = 'Privada') AS dep_privada,
      COUNTIF(dependencia_administrativa = 'Federal') AS dep_federal,
      COUNT(*) - COUNT(DISTINCT CONCAT(
        CAST(ano_censo AS STRING), '|',
        CAST(id_municipio AS STRING), '|',
        COALESCE(localizacao, ''), '|',
        COALESCE(dependencia_administrativa, '')
      )) AS duplicate_rows,
      COUNTIF(data_ultima_atualizacao IS NULL) AS null_data_ultima_atualizacao
    FROM base
    """
    row = next(iter(client.query(query).result()))
    totals = dict(row.items())

    expected = {
        "total_rows": EXPECTED_TOTAL_ROWS,
        "unique_municipios": EXPECTED_UNIQUE_MUNICIPIOS,
        "loc_total": EXPECTED_LOCALIZACAO_COUNTS["Total"],
        "loc_urbana": EXPECTED_LOCALIZACAO_COUNTS["Urbana"],
        "loc_rural": EXPECTED_LOCALIZACAO_COUNTS["Rural"],
        "dep_total": EXPECTED_DEPENDENCIA_COUNTS["Total"],
        "dep_publica": EXPECTED_DEPENDENCIA_COUNTS["Pública"],
        "dep_municipal": EXPECTED_DEPENDENCIA_COUNTS["Municipal"],
        "dep_estadual": EXPECTED_DEPENDENCIA_COUNTS["Estadual"],
        "dep_privada": EXPECTED_DEPENDENCIA_COUNTS["Privada"],
        "dep_federal": EXPECTED_DEPENDENCIA_COUNTS["Federal"],
        "duplicate_rows": 0,
        "null_data_ultima_atualizacao": 0,
    }
    for key, value in expected.items():
        if totals[key] != value:
            raise RuntimeError(f"Validação falhou para {key}: esperado={value} atual={totals[key]}")

    domain_query = f"""
    SELECT
      ARRAY_AGG(DISTINCT localizacao ORDER BY localizacao) AS localizacoes,
      ARRAY_AGG(DISTINCT dependencia_administrativa ORDER BY dependencia_administrativa) AS dependencias
    FROM `{_table_fqn()}`
    """
    domain_row = next(iter(client.query(domain_query).result()))
    localizacoes = list(domain_row["localizacoes"])
    dependencias = list(domain_row["dependencias"])
    if localizacoes != sorted(EXPECTED_LOCALIZACAO_COUNTS):
        raise RuntimeError(
            f"Domínio de localizacao divergente: esperado={sorted(EXPECTED_LOCALIZACAO_COUNTS)} "
            f"atual={localizacoes}"
        )
    if dependencias != sorted(EXPECTED_DEPENDENCIA_COUNTS):
        raise RuntimeError(
            f"Domínio de dependencia divergente: esperado={sorted(EXPECTED_DEPENDENCIA_COUNTS)} "
            f"atual={dependencias}"
        )


def _sample_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = [
        ("Total", "Municipal"),
        ("Urbana", "Municipal"),
        ("Rural", "Municipal"),
        ("Total", "Pública"),
        ("Rural", "Pública"),
        ("Total", "Estadual"),
        ("Rural", "Federal"),
        ("Total", "Privada"),
    ]

    samples: list[dict[str, object]] = []
    seen_keys: set[tuple[int, str, str]] = set()
    for localizacao, dependencia in wanted:
        for record in records:
            key = (
                record["id_municipio"],
                record["localizacao"],
                record["dependencia_administrativa"],
            )
            if key in seen_keys:
                continue
            if record["localizacao"] == localizacao and record["dependencia_administrativa"] == dependencia:
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
                    f"{sample_name}: divergência em {field_name}: "
                    f"esperado={expected_value} atual={actual_value}"
                )
        elif actual_value != expected_value:
            raise RuntimeError(
                f"{sample_name}: divergência em {field_name}: "
                f"esperado={expected_value!r} atual={actual_value!r}"
            )


def _fetch_record(
    client: bigquery.Client,
    table_id: str,
    sample: dict[str, object],
    include_timestamp: bool,
) -> dict[str, object]:
    select_fields = list(_schema_field_names())
    if not include_timestamp:
        select_fields = [field for field in select_fields if field != "data_ultima_atualizacao"]

    query = f"""
    SELECT {", ".join(select_fields)}
    FROM `{table_id}`
    WHERE ano_censo = @ano_censo
      AND id_municipio = @id_municipio
      AND localizacao = @localizacao
      AND dependencia_administrativa = @dependencia_administrativa
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ano_censo", "INT64", sample["ano_censo"]),
            bigquery.ScalarQueryParameter("id_municipio", "INT64", sample["id_municipio"]),
            bigquery.ScalarQueryParameter("localizacao", "STRING", sample["localizacao"]),
            bigquery.ScalarQueryParameter(
                "dependencia_administrativa",
                "STRING",
                sample["dependencia_administrativa"],
            ),
        ]
    )

    rows = list(client.query(query, job_config=config).result())
    if len(rows) != 1:
        raise RuntimeError(
            f"Esperava 1 linha em {table_id} para a chave "
            f"{sample['ano_censo']}/{sample['id_municipio']}/"
            f"{sample['localizacao']}/{sample['dependencia_administrativa']}, "
            f"mas encontrei {len(rows)}"
        )
    return dict(rows[0].items())


def _official_has_expected_year(client: bigquery.Client) -> bool:
    query = f"""
    SELECT COUNT(*) AS total
    FROM `{OFFICIAL_TABLE_ID}`
    WHERE ano_censo = @ano_censo
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("ano_censo", "INT64", EXPECTED_YEAR),
        ]
    )
    row = next(iter(client.query(query, job_config=config).result()))
    return row["total"] > 0


def _validate_samples(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    validate_official_samples = _official_has_expected_year(client)

    for idx, sample in enumerate(_sample_records(records), start=1):
        sample_name = (
            f"amostra_{idx}_"
            f"{sample['id_municipio']}_{sample['localizacao']}_{sample['dependencia_administrativa']}"
        )

        loaded = _fetch_record(client, _table_fqn(), sample, include_timestamp=True)
        _compare_record(loaded, sample, sample_name)

        if not validate_official_samples:
            continue

        official = _fetch_record(client, OFFICIAL_TABLE_ID, sample, include_timestamp=False)
        official_expected = {key: value for key, value in sample.items() if key != "data_ultima_atualizacao"}
        for field_name, expected_value in official_expected.items():
            actual_value = official[field_name]
            if isinstance(expected_value, float):
                if actual_value is None or abs(actual_value - expected_value) > 1e-6:
                    raise RuntimeError(
                        f"{sample_name} oficial: divergência em {field_name}: "
                        f"esperado={expected_value} atual={actual_value}"
                    )
            elif actual_value != expected_value:
                raise RuntimeError(
                    f"{sample_name} oficial: divergência em {field_name}: "
                    f"esperado={expected_value!r} atual={actual_value!r}"
                )

    if not validate_official_samples:
        print(
            "Validação contra a tabela oficial foi ignorada: "
            f"{OFFICIAL_TABLE_ID} não possui registros para {EXPECTED_YEAR}."
        )


def main() -> None:
    print(f"Lendo planilha: {XLSX_PATH}")

    with zipfile.ZipFile(XLSX_PATH) as archive:
        shared = _load_shared_strings(archive)
        targets = _sheet_targets(archive)

        if EXPECTED_SHEET_NAME not in targets:
            raise RuntimeError(
                f"Aba não encontrada: {EXPECTED_SHEET_NAME}. Abas disponíveis: {sorted(targets)}"
            )

        rows = _read_sheet(archive, shared, targets[EXPECTED_SHEET_NAME])

    data_ultima_atualizacao = datetime.now(UTC).date().isoformat()
    records = _transform_rows(rows, data_ultima_atualizacao)

    print(f"Linhas válidas lidas: {len(records)}")
    _validate_source_records(records)
    print("Validação estrutural da planilha concluída.")

    client = bigquery.Client(project=JOB_PROJECT_ID)

    print(f"Recriando tabela {_table_fqn()}...")
    _recreate_table(client, _schema())

    print("Inserindo registros...")
    _load_records(client, records)

    print("Validando schema carregado e compatibilidade com o datalake...")
    _validate_schema(client)

    print("Validando contagens, domínios e duplicidades...")
    _validate_aggregates(client)

    print("Validando amostras contra a planilha e a tabela oficial...")
    _validate_samples(client, records)

    print("Carga concluída com sucesso.")
    print(f"Tabela: {_table_fqn()}")
    print(f"Total de linhas carregadas: {len(records)}")


if __name__ == "__main__":
    main()
