"""Publica no sandbox apenas os ajustes locais de fundeb_base_repasse_estimativa.

Uso:
    uv run python reports/ATM-EQ/scripts/load_fundeb_base_repasse_estimativa.py

Regras:
    - publica apenas as linhas ajustadas de VAAR Previsto de 2023 e 2024;
    - lê CSVs locais normalizados em UTF-8;
    - preserva o nome textual da portaria na coluna `portaria`.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from google.cloud import bigquery


ROOT_DIR = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_INPUT_DIR = SCRIPT_DIR / "local"
METADATA_ROOT = ROOT_DIR / "output" / "metadata"

OFFICIAL_PROJECT_ID = "br-mec-segape"
OFFICIAL_DATASET_ID = "indicador_politica_fundeb_base"
SANDBOX_PROJECT_ID = "br-mec-segape-sandbox"
SANDBOX_DATASET_ID = "projeto_segape_dmape_relat_automatico"
TABLE_ID = "fundeb_base_repasse_estimativa"
STAGE_TABLE_ID = f"{TABLE_ID}__ajustes_vaar_stage"
TARGET_YEARS = (2023, 2024)
TIPO_TRANSFERENCIA_VAAR = "Complementação VAAR"
STATUS_PREVISTO = "Previsto"
ID_STATUS_PREVISTO = 2
ID_TIPO_TRANSFERENCIA_VAAR = 2
BATCH_SIZE = 500

SCHEMA_COLUMNS = [
    "ano",
    "id_ibge",
    "nome_entidade",
    "sigla_uf",
    "tipo_transferencia",
    "rede",
    "status",
    "portaria",
    "tabela_origem",
    "id_status",
    "id_tipo_transferencia",
    "valor",
]

EXPECTED_PORTARIAS = {
    2023: "5ª publicação - Portaria MEC/MF nº 3, de 25 de abril de 2024",
    2024: "9ª publicação – Portaria nº 3, de 28 de Abril de 2025",
}


@dataclass(frozen=True)
class CsvInput:
    ano: int
    path: Path
    expected_portaria: str


def _official_table_fqn() -> str:
    return f"{OFFICIAL_PROJECT_ID}.{OFFICIAL_DATASET_ID}.{TABLE_ID}"


def _sandbox_table_fqn() -> str:
    return f"{SANDBOX_PROJECT_ID}.{SANDBOX_DATASET_ID}.{TABLE_ID}"


def _stage_table_fqn() -> str:
    return f"{SANDBOX_PROJECT_ID}.{SANDBOX_DATASET_ID}.{STAGE_TABLE_ID}"


def _default_csv_inputs() -> list[CsvInput]:
    return [
        CsvInput(
            ano=2023,
            path=LOCAL_INPUT_DIR / "ajuste_vaar_2023.csv",
            expected_portaria=EXPECTED_PORTARIAS[2023],
        ),
        CsvInput(
            ano=2024,
            path=LOCAL_INPUT_DIR / "ajuste_vaar_2024.csv",
            expected_portaria=EXPECTED_PORTARIAS[2024],
        ),
    ]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publica no sandbox apenas os ajustes locais de fundeb_base_repasse_estimativa."
    )
    parser.add_argument(
        "--csv-2023",
        default=str(_default_csv_inputs()[0].path),
        help="CSV local normalizado para o ajuste VAAR do exercício de 2023.",
    )
    parser.add_argument(
        "--csv-2024",
        default=str(_default_csv_inputs()[1].path),
        help="CSV local normalizado para o ajuste VAAR do exercício de 2024.",
    )
    return parser.parse_args()


def _normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _normalize_portaria(value: str) -> str:
    normalized = _normalize_whitespace(value)
    normalized = re.sub(r"\bn\s*[\?º°o\.]\s*(\d+)", r"nº \1", normalized, flags=re.IGNORECASE)
    return normalized.casefold()


def _schema_signature(schema: list[bigquery.SchemaField]) -> list[tuple[str, str, str]]:
    return [(field.name, field.field_type, (field.mode or "NULLABLE").upper()) for field in schema]


def _load_metadata_schema_signature() -> list[tuple[str, str, str]] | None:
    snapshots = sorted(METADATA_ROOT.glob("metadata_snapshot_*"))
    if not snapshots:
        return None

    schema_path = (
        snapshots[-1]
        / "schemas"
        / OFFICIAL_DATASET_ID
        / f"{TABLE_ID}.json"
    )
    if not schema_path.exists():
        return None

    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    return [
        (
            column["column_name"],
            column["data_type"],
            (column.get("mode") or "NULLABLE").upper(),
        )
        for column in payload["columns"]
        if "." not in column["column_path"]
    ]


def _parse_int(raw_value: str, *, field_name: str) -> int:
    value = _normalize_whitespace(raw_value)
    if not value:
        raise ValueError(f"Campo obrigatório vazio: {field_name}")
    return int(value)


def _parse_float(raw_value: str, *, field_name: str) -> float:
    value = _normalize_whitespace(raw_value)
    if not value:
        raise ValueError(f"Campo obrigatório vazio: {field_name}")
    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")
    return float(value)


def _parse_optional_text(raw_value: str) -> str | None:
    value = _normalize_whitespace(raw_value)
    return value or None


def _is_expected_tipo_transferencia(value: str) -> bool:
    normalized = _normalize_whitespace(value).casefold()
    return normalized.startswith("complement") and "vaar" in normalized


def _validate_header(fieldnames: list[str] | None, csv_path: Path) -> None:
    actual = fieldnames or []
    if actual != SCHEMA_COLUMNS:
        raise ValueError(
            f"Cabeçalho inesperado em {csv_path.name}. "
            f"Esperado={SCHEMA_COLUMNS!r} Atual={actual!r}"
        )


def _read_csv_records(spec: CsvInput) -> list[dict[str, Any]]:
    if not spec.path.exists():
        raise FileNotFoundError(
            f"CSV local não encontrado: {spec.path}. "
            "Gere o CSV local antes de rodar a carga."
        )

    records: list[dict[str, Any]] = []
    duplicate_keys: set[tuple[int, int, str, str, str]] = set()

    with spec.path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_header(reader.fieldnames, spec.path)

        for row_number, raw_row in enumerate(reader, start=2):
            try:
                ano = _parse_int(raw_row["ano"], field_name="ano")
                if ano != spec.ano:
                    raise ValueError(
                        f"Ano divergente em {spec.path.name}:{row_number}. "
                        f"Esperado={spec.ano} Atual={ano}"
                    )

                portaria = _normalize_whitespace(raw_row["portaria"])
                if not portaria:
                    raise ValueError("Portaria vazia")
                if _normalize_portaria(portaria) != _normalize_portaria(spec.expected_portaria):
                    raise ValueError(
                        "Portaria divergente. "
                        f"Esperado={spec.expected_portaria!r} Atual={portaria!r}"
                    )

                tipo_transferencia_raw = _normalize_whitespace(raw_row["tipo_transferencia"])
                if not _is_expected_tipo_transferencia(tipo_transferencia_raw):
                    raise ValueError(
                        f"tipo_transferencia divergente: {tipo_transferencia_raw!r}"
                    )
                tipo_transferencia = TIPO_TRANSFERENCIA_VAAR

                status_raw = _normalize_whitespace(raw_row["status"])
                if status_raw.casefold() != STATUS_PREVISTO.casefold():
                    raise ValueError(f"status divergente: {status_raw!r}")
                status = STATUS_PREVISTO

                id_status = _parse_int(raw_row["id_status"], field_name="id_status")
                if id_status != ID_STATUS_PREVISTO:
                    raise ValueError(f"id_status divergente: {id_status!r}")

                id_tipo_transferencia = _parse_int(
                    raw_row["id_tipo_transferencia"],
                    field_name="id_tipo_transferencia",
                )
                if id_tipo_transferencia != ID_TIPO_TRANSFERENCIA_VAAR:
                    raise ValueError(
                        f"id_tipo_transferencia divergente: {id_tipo_transferencia!r}"
                    )

                id_ibge = _parse_int(raw_row["id_ibge"], field_name="id_ibge")
                valor = _parse_float(raw_row["valor"], field_name="valor")
                rede = _normalize_whitespace(raw_row["rede"])
                if rede not in {"Estadual", "Municipal"}:
                    raise ValueError(f"rede divergente: {rede!r}")

                sigla_uf = _normalize_whitespace(raw_row["sigla_uf"])
                if len(sigla_uf) != 2:
                    raise ValueError(f"sigla_uf divergente: {sigla_uf!r}")

                nome_entidade = _parse_optional_text(raw_row["nome_entidade"])
                if not nome_entidade:
                    raise ValueError("nome_entidade vazio")

                duplicate_key = (ano, id_ibge, tipo_transferencia, status, portaria)
                if duplicate_key in duplicate_keys:
                    raise ValueError(
                        "Duplicidade incompatível encontrada para "
                        f"(ano, id_ibge, tipo_transferencia, status, portaria)={duplicate_key!r}"
                    )
                duplicate_keys.add(duplicate_key)

                records.append(
                    {
                        "ano": ano,
                        "id_ibge": id_ibge,
                        "nome_entidade": nome_entidade,
                        "sigla_uf": sigla_uf,
                        "tipo_transferencia": tipo_transferencia,
                        "rede": rede,
                        "status": status,
                        "portaria": spec.expected_portaria,
                        "tabela_origem": spec.path.name,
                        "id_status": id_status,
                        "id_tipo_transferencia": id_tipo_transferencia,
                        "valor": valor,
                    }
                )
            except Exception as exc:
                raise ValueError(f"Falha ao validar {spec.path.name}:{row_number}: {exc}") from exc

    if not records:
        raise ValueError(f"CSV sem dados válidos: {spec.path}")

    return records


def _chunks(records: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [records[idx : idx + size] for idx in range(0, len(records), size)]


def _load_stage_records(
    client: bigquery.Client,
    schema: list[bigquery.SchemaField],
    records: list[dict[str, Any]],
) -> None:
    for index, chunk in enumerate(_chunks(records, BATCH_SIZE)):
        write_disposition = (
            bigquery.WriteDisposition.WRITE_TRUNCATE
            if index == 0
            else bigquery.WriteDisposition.WRITE_APPEND
        )
        job_config = bigquery.LoadJobConfig(
            schema=schema,
            write_disposition=write_disposition,
        )
        job = client.load_table_from_json(chunk, _stage_table_fqn(), job_config=job_config)
        job.result()


def _publish_final_table(
    client: bigquery.Client,
    schema: list[bigquery.SchemaField],
) -> None:
    columns_sql = ", ".join(f"`{field.name}`" for field in schema)
    query = f"""
    CREATE OR REPLACE TABLE `{_sandbox_table_fqn()}` AS
    SELECT {columns_sql}
    FROM `{_stage_table_fqn()}`
    """
    client.query(query).result()


def _validate_schema(
    client: bigquery.Client,
    schema: list[bigquery.SchemaField],
) -> None:
    expected = _schema_signature(schema)
    official = _schema_signature(client.get_table(_official_table_fqn()).schema)
    sandbox = _schema_signature(client.get_table(_sandbox_table_fqn()).schema)
    if official != expected:
        raise RuntimeError("Schema oficial divergente do schema esperado.")
    if sandbox != expected:
        raise RuntimeError("Schema sandbox divergente do schema esperado.")

    metadata_signature = _load_metadata_schema_signature()
    if metadata_signature is not None and metadata_signature != expected:
        raise RuntimeError("Schema do snapshot de metadata divergente do schema esperado.")


def _validate_counts(
    client: bigquery.Client,
    stage_records: list[dict[str, Any]],
) -> None:
    query = f"""
    SELECT
      COUNT(*) AS sandbox_total,
      COUNTIF(
        status = @status_previsto
        AND tipo_transferencia = @tipo_transferencia_vaar
        AND CAST(ano AS INT64) IN UNNEST(@target_years)
      ) AS sandbox_targeted
    FROM `{_sandbox_table_fqn()}`
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("status_previsto", "STRING", STATUS_PREVISTO),
            bigquery.ScalarQueryParameter(
                "tipo_transferencia_vaar",
                "STRING",
                TIPO_TRANSFERENCIA_VAAR,
            ),
            bigquery.ArrayQueryParameter("target_years", "INT64", list(TARGET_YEARS)),
        ]
    )
    row = next(iter(client.query(query, job_config=job_config).result()))
    stage_total = len(stage_records)
    if row["sandbox_total"] != stage_total:
        raise RuntimeError(
            "Contagem total divergente após publicação. "
            f"Esperado={stage_total} Atual={row['sandbox_total']}"
        )
    if row["sandbox_targeted"] != stage_total:
        raise RuntimeError(
            "Contagem das linhas ajustadas divergente após publicação. "
            f"Esperado={stage_total} Atual={row['sandbox_targeted']}"
        )


def _validate_adjusted_rows(
    client: bigquery.Client,
    stage_records: list[dict[str, Any]],
) -> None:
    expected: dict[tuple[int, str], dict[str, Any]] = {}
    for record in stage_records:
        key = (int(record["ano"]), str(record["portaria"]))
        group = expected.setdefault(key, {"total": 0, "valor_total": 0.0})
        group["total"] += 1
        group["valor_total"] += float(record["valor"])

    query = f"""
    SELECT
      CAST(ano AS INT64) AS ano,
      CAST(portaria AS STRING) AS portaria,
      COUNT(*) AS total,
      SUM(valor) AS valor_total
    FROM `{_sandbox_table_fqn()}`
    WHERE
      status = @status_previsto
      AND tipo_transferencia = @tipo_transferencia_vaar
      AND CAST(ano AS INT64) IN UNNEST(@target_years)
    GROUP BY ano, portaria
    ORDER BY ano, portaria
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("status_previsto", "STRING", STATUS_PREVISTO),
            bigquery.ScalarQueryParameter(
                "tipo_transferencia_vaar",
                "STRING",
                TIPO_TRANSFERENCIA_VAAR,
            ),
            bigquery.ArrayQueryParameter("target_years", "INT64", list(TARGET_YEARS)),
        ]
    )
    actual = {
        (int(row["ano"]), str(row["portaria"])): {
            "total": int(row["total"]),
            "valor_total": float(row["valor_total"] or 0.0),
        }
        for row in client.query(query, job_config=job_config).result()
    }

    if set(actual) != set(expected):
        raise RuntimeError(
            f"Portarias ajustadas divergentes. Esperado={sorted(expected)} Atual={sorted(actual)}"
        )

    for key, expected_group in expected.items():
        actual_group = actual[key]
        if actual_group["total"] != expected_group["total"]:
            raise RuntimeError(
                f"Total de linhas divergente para {key!r}. "
                f"Esperado={expected_group['total']} Atual={actual_group['total']}"
            )
        if abs(actual_group["valor_total"] - expected_group["valor_total"]) > 0.01:
            raise RuntimeError(
                f"Valor total divergente para {key!r}. "
                f"Esperado={expected_group['valor_total']} Atual={actual_group['valor_total']}"
            )


def _cleanup_stage_table(client: bigquery.Client) -> None:
    client.delete_table(_stage_table_fqn(), not_found_ok=True)


def main() -> None:
    args = _parse_args()
    csv_inputs = [
        CsvInput(
            ano=2023,
            path=Path(args.csv_2023).resolve(),
            expected_portaria=EXPECTED_PORTARIAS[2023],
        ),
        CsvInput(
            ano=2024,
            path=Path(args.csv_2024).resolve(),
            expected_portaria=EXPECTED_PORTARIAS[2024],
        ),
    ]

    print(f"Tabela oficial: {_official_table_fqn()}")
    print(f"Tabela sandbox: {_sandbox_table_fqn()}")

    stage_records: list[dict[str, Any]] = []
    for spec in csv_inputs:
        print(f"Lendo CSV local: {spec.path}")
        records = _read_csv_records(spec)
        stage_records.extend(records)
        print(
            f"Arquivo validado: {spec.path.name} | "
            f"ano={spec.ano} | linhas={len(records)} | portaria={spec.expected_portaria}"
        )

    client = bigquery.Client(project=SANDBOX_PROJECT_ID)
    schema = client.get_table(_official_table_fqn()).schema

    try:
        print(f"Carregando stage: {_stage_table_fqn()}...")
        _load_stage_records(client, schema, stage_records)

        print(f"Publicando ajustes locais: {_sandbox_table_fqn()}...")
        _publish_final_table(client, schema)

        print("Validando schema...")
        _validate_schema(client, schema)

        print("Validando contagens...")
        _validate_counts(client, stage_records)

        print("Validando anos e portarias ajustados...")
        _validate_adjusted_rows(client, stage_records)
    finally:
        print(f"Limpando stage temporário: {_stage_table_fqn()}...")
        _cleanup_stage_table(client)

    print("Carga concluída com sucesso.")
    print(f"Ajustes publicados em: {_sandbox_table_fqn()}")
    for spec in csv_inputs:
        print(f"- ajuste {spec.ano}: {spec.path.name} -> {spec.expected_portaria}")


if __name__ == "__main__":
    main()
