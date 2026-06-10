"""Carrega ATU 2025 de municipio no sandbox.

Uso:
    uv run python reports/ATM-EQ/scripts/load_atu_municipios_2025.py
"""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import zipfile

from google.cloud import bigquery

from atu_loader_common import (
    ATU_FIELD_MAP,
    EXPECTED_YEAR,
    JOB_PROJECT_ID,
    ROOT_DIR,
    build_uf_name_map,
    load_records,
    load_schema_from_metadata,
    load_shared_strings,
    locate_header_row,
    normalize_localizacao,
    normalize_rede,
    official_has_expected_year,
    official_table_fqn,
    read_sheet,
    recreate_table,
    schema_field_names,
    sheet_targets,
    table_fqn,
    to_optional_float,
    validate_schema,
)


XLSX_PATH = ROOT_DIR / "reports" / "ATM-EQ" / "scripts" / "ATU_MUNICIPIOS_2025.xlsx"
TABLE_ID = "educacao_inep_indicadores_educacionais_municipio"
OFFICIAL_TABLE = official_table_fqn("municipio")
EXPECTED_SHEET_NAME = "MUNICIPIO"
EXPECTED_TOTAL_ROWS = 66298
EXPECTED_UNIQUE_MUNICIPIOS = 5571
EXPECTED_LOCALIZACOES = {"total", "urbana", "rural"}
EXPECTED_REDES = {"total", "publica", "municipal", "estadual", "privada", "federal"}
ALLOWED_UNUSED_HEADERS = {"NO_REGIAO", "SG_UF", "NO_MUNICIPIO"}


def _transform_rows(rows: list[list[str]], schema_names: set[str]) -> list[dict[str, object]]:
    header_idx = locate_header_row(rows)
    technical_header = rows[header_idx]

    allowed_headers = {"NU_ANO_CENSO", "CO_MUNICIPIO", "NO_CATEGORIA", "NO_DEPENDENCIA", *ATU_FIELD_MAP}
    unknown_headers = [
        header
        for header in technical_header
        if header and header not in allowed_headers and header not in ALLOWED_UNUSED_HEADERS
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
            raw_value = padded[idx]
            if source_name == "NU_ANO_CENSO":
                record["ano"] = int(raw_value)
            elif source_name == "CO_MUNICIPIO":
                record["id_municipio"] = raw_value
            elif source_name == "NO_CATEGORIA":
                record["localizacao"] = normalize_localizacao(raw_value)
            elif source_name == "NO_DEPENDENCIA":
                record["rede"] = normalize_rede(raw_value)
            elif source_name in ATU_FIELD_MAP:
                record[ATU_FIELD_MAP[source_name]] = to_optional_float(raw_value)

        extra_fields = set(record) - schema_names
        if extra_fields:
            raise RuntimeError(f"Campos fora do schema oficial: {sorted(extra_fields)}")

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
            f"Quantidade de municipios divergente: esperado={EXPECTED_UNIQUE_MUNICIPIOS} atual={unique_municipios}"
        )

    localizacoes = {record["localizacao"] for record in records}
    redes = {record["rede"] for record in records}
    if localizacoes != EXPECTED_LOCALIZACOES:
        raise RuntimeError(f"Dominio de localizacao divergente: {sorted(localizacoes)}")
    if redes != EXPECTED_REDES:
        raise RuntimeError(f"Dominio de rede divergente: {sorted(redes)}")


def _validate_aggregates(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    expected_localizacao = Counter(record["localizacao"] for record in records)
    expected_rede = Counter(record["rede"] for record in records)
    expected_duplicates = len(records) - len(
        {
            (record["ano"], record["id_municipio"], record["localizacao"], record["rede"])
            for record in records
        }
    )

    summary_query = f"""
    SELECT
      COUNT(*) AS total_rows,
      COUNT(DISTINCT id_municipio) AS unique_municipios,
      COUNT(*) - COUNT(DISTINCT CONCAT(CAST(ano AS STRING), '|', id_municipio, '|', localizacao, '|', rede)) AS duplicate_rows
    FROM `{table_fqn(TABLE_ID)}`
    """
    totals = dict(next(iter(client.query(summary_query).result())).items())
    if totals["total_rows"] != EXPECTED_TOTAL_ROWS:
        raise RuntimeError("Total de linhas carregadas divergente.")
    if totals["unique_municipios"] != EXPECTED_UNIQUE_MUNICIPIOS:
        raise RuntimeError("Total de municipios carregados divergente.")
    if totals["duplicate_rows"] != expected_duplicates:
        raise RuntimeError("Duplicidades carregadas divergentes.")

    for field, expected in [("localizacao", expected_localizacao), ("rede", expected_rede)]:
        query = f"SELECT {field}, COUNT(*) AS total FROM `{table_fqn(TABLE_ID)}` GROUP BY 1"
        loaded = {row[field]: row["total"] for row in client.query(query).result()}
        if loaded != dict(expected):
            raise RuntimeError(f"Contagens divergentes para {field}: {loaded}")


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
    seen = set()
    for localizacao, rede in wanted:
        for record in records:
            key = (record["id_municipio"], record["localizacao"], record["rede"])
            if key in seen:
                continue
            if record["localizacao"] == localizacao and record["rede"] == rede:
                samples.append(record)
                seen.add(key)
                break
    if len(samples) < 5:
        raise RuntimeError(f"Amostras insuficientes: {len(samples)}")
    return samples


def _validate_samples(client: bigquery.Client, records: list[dict[str, object]]) -> None:
    fields = ["ano", "id_municipio", "localizacao", "rede", *ATU_FIELD_MAP.values()]

    for sample in _sample_records(records):
        query = f"""
        SELECT {", ".join(fields)}
        FROM `{table_fqn(TABLE_ID)}`
        WHERE ano = @ano
          AND id_municipio = @id_municipio
          AND localizacao = @localizacao
          AND rede = @rede
        """
        config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("ano", "INT64", sample["ano"]),
                bigquery.ScalarQueryParameter("id_municipio", "STRING", sample["id_municipio"]),
                bigquery.ScalarQueryParameter("localizacao", "STRING", sample["localizacao"]),
                bigquery.ScalarQueryParameter("rede", "STRING", sample["rede"]),
            ]
        )
        rows = list(client.query(query, job_config=config).result())
        if len(rows) != 1:
            raise RuntimeError("Amostra nao encontrada ou duplicada na tabela carregada.")
        loaded = dict(rows[0].items())
        for field in fields:
            expected = sample.get(field)
            actual = loaded[field]
            if isinstance(expected, float):
                if actual is None or abs(actual - expected) > 1e-6:
                    raise RuntimeError(f"Divergencia na amostra para {field}: {expected} != {actual}")
            elif actual != expected:
                raise RuntimeError(f"Divergencia na amostra para {field}: {expected!r} != {actual!r}")


def main() -> None:
    print(f"Lendo planilha: {XLSX_PATH}")
    schema = load_schema_from_metadata("municipio")
    schema_names = set(schema_field_names(schema))
    if len(schema) != 215:
        raise RuntimeError(f"Schema inesperado para municipio: {len(schema)} colunas")

    with zipfile.ZipFile(XLSX_PATH) as archive:
        shared = load_shared_strings(archive)
        targets = sheet_targets(archive)
        if EXPECTED_SHEET_NAME not in targets:
            raise RuntimeError(f"Aba nao encontrada: {EXPECTED_SHEET_NAME}")
        rows = read_sheet(archive, shared, targets[EXPECTED_SHEET_NAME])

    records = _transform_rows(rows, schema_names)
    print(f"Linhas validas lidas: {len(records)}")
    _validate_source_records(records)
    print("Validacao estrutural da planilha concluida.")

    client = bigquery.Client(project=JOB_PROJECT_ID)
    print(f"Recriando tabela {table_fqn(TABLE_ID)}...")
    recreate_table(client, TABLE_ID, schema)

    print("Inserindo registros...")
    load_records(client, TABLE_ID, schema, records)

    print("Validando schema...")
    validate_schema(client, TABLE_ID, schema, OFFICIAL_TABLE)

    print("Validando contagens, dominios e duplicidades...")
    _validate_aggregates(client, records)

    print("Validando amostras...")
    _validate_samples(client, records)

    if not official_has_expected_year(client, OFFICIAL_TABLE):
        print(
            "Validacao contra a tabela oficial foi ignorada: "
            f"{OFFICIAL_TABLE} nao possui registros para {EXPECTED_YEAR}."
        )

    print("Carga concluida com sucesso.")
    print(f"Tabela: {table_fqn(TABLE_ID)}")
    print(f"Total de linhas carregadas: {len(records)}")


if __name__ == "__main__":
    main()
