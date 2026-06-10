"""Carrega ATU 2025 de UF e Brasil no sandbox.

Uso:
    uv run python reports/ATM-EQ/scripts/load_atu_brasil_regioes_ufs_2025.py
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import zipfile

from google.cloud import bigquery

from atu_loader_common import (
    ATU_FIELD_MAP,
    EXPECTED_YEAR,
    JOB_PROJECT_ID,
    REGIOES,
    ROOT_DIR,
    build_uf_name_map,
    load_records,
    load_schema_from_metadata,
    load_shared_strings,
    locate_header_row,
    normalize_ascii,
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


XLSX_PATH = ROOT_DIR / "reports" / "ATM-EQ" / "scripts" / "ATU_BRASIL_REGIOES_UFS_2025.xlsx"
TABLE_ID_UF = "educacao_inep_indicadores_educacionais_uf"
TABLE_ID_BRASIL = "educacao_inep_indicadores_educacionais_brasil"
OFFICIAL_TABLE_UF = official_table_fqn("uf")
OFFICIAL_TABLE_BRASIL = official_table_fqn("brasil")
EXPECTED_SHEET_NAME = "BRASIL_REGIOES_UFS"
EXPECTED_TOTAL_ROWS = 588
EXPECTED_TOTAL_UF_ROWS = 480
EXPECTED_TOTAL_BRASIL_ROWS = 18
EXPECTED_TOTAL_REGIAO_ROWS = 90
EXPECTED_LOCALIZACOES = {"total", "urbana", "rural"}
EXPECTED_REDES = {"total", "publica", "municipal", "estadual", "privada", "federal"}


def _classify_unit(unit_name: str, uf_name_map: dict[str, str]) -> tuple[str, str | None]:
    normalized = normalize_ascii(unit_name)
    if normalized == "Brasil":
        return "brasil", None
    if normalized in REGIOES:
        return "regiao", None
    sigla_uf = uf_name_map.get(normalized)
    if sigla_uf is None:
        raise RuntimeError(f"Unidade geografica nao mapeada: {unit_name!r}")
    return "uf", sigla_uf


def _transform_rows(
    rows: list[list[str]],
    uf_schema_names: set[str],
    brasil_schema_names: set[str],
    uf_name_map: dict[str, str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    header_idx = locate_header_row(rows)
    technical_header = rows[header_idx]
    allowed_headers = {"NU_ANO_CENSO", "UNIDGEO", "NO_CATEGORIA", "NO_DEPENDENCIA", *ATU_FIELD_MAP}
    unknown_headers = [header for header in technical_header if header and header not in allowed_headers]
    if unknown_headers:
        raise RuntimeError(f"Cabecalhos nao mapeados encontrados: {unknown_headers}")

    uf_records: list[dict[str, object]] = []
    brasil_records: list[dict[str, object]] = []
    ignored_regiao_rows = 0

    for row in rows[header_idx + 1 :]:
        if len(row) < 4:
            continue
        if row[0] != str(EXPECTED_YEAR):
            continue

        padded = (row + [""] * len(technical_header))[: len(technical_header)]
        unit_type, sigla_uf = _classify_unit(padded[1], uf_name_map)
        if unit_type == "regiao":
            ignored_regiao_rows += 1
            continue

        record: dict[str, object] = {}
        for idx, source_name in enumerate(technical_header):
            raw_value = padded[idx]
            if source_name == "NU_ANO_CENSO":
                record["ano"] = int(raw_value)
            elif source_name == "NO_CATEGORIA":
                record["localizacao"] = normalize_localizacao(raw_value)
            elif source_name == "NO_DEPENDENCIA":
                record["rede"] = normalize_rede(raw_value)
            elif source_name in ATU_FIELD_MAP:
                record[ATU_FIELD_MAP[source_name]] = to_optional_float(raw_value)

        if unit_type == "uf":
            record["sigla_uf"] = sigla_uf
            extra_fields = set(record) - uf_schema_names
            if extra_fields:
                raise RuntimeError(f"Campos fora do schema oficial de UF: {sorted(extra_fields)}")
            uf_records.append(record)
        else:
            extra_fields = set(record) - brasil_schema_names
            if extra_fields:
                raise RuntimeError(f"Campos fora do schema oficial de Brasil: {sorted(extra_fields)}")
            brasil_records.append(record)

    return uf_records, brasil_records, ignored_regiao_rows


def _validate_source_records(
    uf_records: list[dict[str, object]],
    brasil_records: list[dict[str, object]],
    ignored_regiao_rows: int,
) -> None:
    total_rows = len(uf_records) + len(brasil_records) + ignored_regiao_rows
    if total_rows != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(f"Total bruto inesperado: {total_rows}")
    if len(uf_records) != EXPECTED_TOTAL_UF_ROWS:
        raise RuntimeError(f"Total de linhas de UF inesperado: {len(uf_records)}")
    if len(brasil_records) != EXPECTED_TOTAL_BRASIL_ROWS:
        raise RuntimeError(f"Total de linhas de Brasil inesperado: {len(brasil_records)}")
    if ignored_regiao_rows != EXPECTED_TOTAL_REGIAO_ROWS:
        raise RuntimeError(f"Total de linhas de Regiao inesperado: {ignored_regiao_rows}")

    for records in (uf_records, brasil_records):
        localizacoes = {record["localizacao"] for record in records}
        redes = {record["rede"] for record in records}
        if localizacoes != EXPECTED_LOCALIZACOES:
            raise RuntimeError(f"Dominio de localizacao divergente: {sorted(localizacoes)}")
        if redes != EXPECTED_REDES:
            raise RuntimeError(f"Dominio de rede divergente: {sorted(redes)}")


def _validate_aggregates(
    client: bigquery.Client,
    table_id: str,
    records: list[dict[str, object]],
    key_fields: list[str],
) -> None:
    expected_localizacao = Counter(record["localizacao"] for record in records)
    expected_rede = Counter(record["rede"] for record in records)
    expected_duplicates = len(records) - len(
        {tuple(record[field] for field in key_fields) for record in records}
    )

    concat_keys = ", '|', ".join(f"CAST({field} AS STRING)" for field in key_fields)
    summary_query = f"""
    SELECT
      COUNT(*) AS total_rows,
      COUNT(*) - COUNT(DISTINCT CONCAT({concat_keys})) AS duplicate_rows
    FROM `{table_fqn(table_id)}`
    """
    totals = dict(next(iter(client.query(summary_query).result())).items())
    if totals["total_rows"] != len(records):
        raise RuntimeError(f"Total carregado divergente em {table_id}.")
    if totals["duplicate_rows"] != expected_duplicates:
        raise RuntimeError(f"Duplicidades divergentes em {table_id}.")

    for field, expected in [("localizacao", expected_localizacao), ("rede", expected_rede)]:
        query = f"SELECT {field}, COUNT(*) AS total FROM `{table_fqn(table_id)}` GROUP BY 1"
        loaded = {row[field]: row["total"] for row in client.query(query).result()}
        if loaded != dict(expected):
            raise RuntimeError(f"Contagens divergentes em {table_id} para {field}: {loaded}")


def _sample_uf_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = [
        ("SP", "total", "municipal"),
        ("BA", "urbana", "municipal"),
        ("PA", "rural", "municipal"),
        ("MG", "total", "estadual"),
        ("SC", "total", "privada"),
    ]
    samples: list[dict[str, object]] = []
    seen = set()
    for sigla_uf, localizacao, rede in wanted:
        for record in records:
            key = (record["sigla_uf"], record["localizacao"], record["rede"])
            if key in seen:
                continue
            if key == (sigla_uf, localizacao, rede):
                samples.append(record)
                seen.add(key)
                break
    if len(samples) < 3:
        raise RuntimeError("Amostras insuficientes para UF.")
    return samples


def _sample_brasil_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = [("total", "municipal"), ("total", "estadual"), ("total", "privada")]
    samples: list[dict[str, object]] = []
    for localizacao, rede in wanted:
        for record in records:
            if record["localizacao"] == localizacao and record["rede"] == rede:
                samples.append(record)
                break
    if len(samples) < 3:
        raise RuntimeError("Amostras insuficientes para Brasil.")
    return samples


def _validate_samples(
    client: bigquery.Client,
    table_id: str,
    records: list[dict[str, object]],
    fields: list[str],
    key_fields: list[str],
) -> None:
    sample_records = _sample_uf_records(records) if "sigla_uf" in key_fields else _sample_brasil_records(records)
    for sample in sample_records:
        where_clause = " AND ".join(f"{field} = @{field}" for field in key_fields)
        params = []
        for field in key_fields:
            param_type = "INT64" if field == "ano" else "STRING"
            params.append(bigquery.ScalarQueryParameter(field, param_type, sample[field]))
        query = f"SELECT {', '.join(fields)} FROM `{table_fqn(table_id)}` WHERE {where_clause}"
        rows = list(client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params)).result())
        if len(rows) != 1:
            raise RuntimeError(f"Amostra nao encontrada ou duplicada em {table_id}.")
        loaded = dict(rows[0].items())
        for field in fields:
            expected = sample.get(field)
            actual = loaded[field]
            if isinstance(expected, float):
                if actual is None or abs(actual - expected) > 1e-6:
                    raise RuntimeError(f"Divergencia em {table_id} para {field}: {expected} != {actual}")
            elif actual != expected:
                raise RuntimeError(f"Divergencia em {table_id} para {field}: {expected!r} != {actual!r}")


def main() -> None:
    print(f"Lendo planilha: {XLSX_PATH}")
    uf_schema = load_schema_from_metadata("uf")
    brasil_schema = load_schema_from_metadata("brasil")
    if len(uf_schema) != 215:
        raise RuntimeError(f"Schema inesperado para uf: {len(uf_schema)}")
    if len(brasil_schema) != 214:
        raise RuntimeError(f"Schema inesperado para brasil: {len(brasil_schema)}")

    client = bigquery.Client(project=JOB_PROJECT_ID)
    uf_name_map = build_uf_name_map(client)

    with zipfile.ZipFile(XLSX_PATH) as archive:
        shared = load_shared_strings(archive)
        targets = sheet_targets(archive)
        if EXPECTED_SHEET_NAME not in targets:
            raise RuntimeError(f"Aba nao encontrada: {EXPECTED_SHEET_NAME}")
        rows = read_sheet(archive, shared, targets[EXPECTED_SHEET_NAME])

    uf_records, brasil_records, ignored_regiao_rows = _transform_rows(
        rows,
        set(schema_field_names(uf_schema)),
        set(schema_field_names(brasil_schema)),
        uf_name_map,
    )
    print(f"Linhas UF validas: {len(uf_records)}")
    print(f"Linhas Brasil validas: {len(brasil_records)}")
    print(f"Linhas Regiao ignoradas: {ignored_regiao_rows}")
    _validate_source_records(uf_records, brasil_records, ignored_regiao_rows)
    print("Validacao estrutural da planilha concluida.")

    print(f"Recriando tabela {table_fqn(TABLE_ID_UF)}...")
    recreate_table(client, TABLE_ID_UF, uf_schema)
    print(f"Recriando tabela {table_fqn(TABLE_ID_BRASIL)}...")
    recreate_table(client, TABLE_ID_BRASIL, brasil_schema)

    print("Inserindo registros de UF...")
    load_records(client, TABLE_ID_UF, uf_schema, uf_records)
    print("Inserindo registros de Brasil...")
    load_records(client, TABLE_ID_BRASIL, brasil_schema, brasil_records)

    print("Validando schema...")
    validate_schema(client, TABLE_ID_UF, uf_schema, OFFICIAL_TABLE_UF)
    validate_schema(client, TABLE_ID_BRASIL, brasil_schema, OFFICIAL_TABLE_BRASIL)

    print("Validando contagens, dominios e duplicidades...")
    _validate_aggregates(client, TABLE_ID_UF, uf_records, ["ano", "sigla_uf", "localizacao", "rede"])
    _validate_aggregates(client, TABLE_ID_BRASIL, brasil_records, ["ano", "localizacao", "rede"])

    fields_uf = ["ano", "sigla_uf", "localizacao", "rede", *ATU_FIELD_MAP.values()]
    fields_brasil = ["ano", "localizacao", "rede", *ATU_FIELD_MAP.values()]
    print("Validando amostras...")
    _validate_samples(client, TABLE_ID_UF, uf_records, fields_uf, ["ano", "sigla_uf", "localizacao", "rede"])
    _validate_samples(client, TABLE_ID_BRASIL, brasil_records, fields_brasil, ["ano", "localizacao", "rede"])

    if not official_has_expected_year(client, OFFICIAL_TABLE_UF):
        print(
            "Validacao contra a tabela oficial foi ignorada: "
            f"{OFFICIAL_TABLE_UF} nao possui registros para {EXPECTED_YEAR}."
        )
    if not official_has_expected_year(client, OFFICIAL_TABLE_BRASIL):
        print(
            "Validacao contra a tabela oficial foi ignorada: "
            f"{OFFICIAL_TABLE_BRASIL} nao possui registros para {EXPECTED_YEAR}."
        )

    print("Carga concluida com sucesso.")
    print(f"Tabela UF: {table_fqn(TABLE_ID_UF)}")
    print(f"Tabela Brasil: {table_fqn(TABLE_ID_BRASIL)}")
    print(f"Total UF: {len(uf_records)}")
    print(f"Total Brasil: {len(brasil_records)}")


if __name__ == "__main__":
    main()
