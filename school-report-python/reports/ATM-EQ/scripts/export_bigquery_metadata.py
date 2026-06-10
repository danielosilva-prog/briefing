"""Exporta metadados de datasets/tabelas/campos do BigQuery em estrutura enxuta.

Uso:
    uv run python reports/ATM-EQ/scripts/export_bigquery_metadata.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from google.cloud import bigquery

# Permite importar o pacote local sem instalar em modo editable.
# script: school-report-python/reports/ATM-EQ/scripts/export_bigquery_metadata.py
# root:   school-report-python/
ROOT_DIR = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schoolreport.config import get_local_settings  # noqa: E402


@dataclass
class ColumnMetadata:
    project_id: str
    dataset_id: str
    dataset_description: str | None
    table_id: str
    table_type: str
    table_description: str | None
    column_name: str
    column_path: str
    parent_field: str | None
    depth: int
    data_type: str
    mode: str
    is_nullable: bool
    is_repeated: bool
    description: str | None
    policy_tags: str | None


def _flatten_schema(
    project_id: str,
    dataset_id: str,
    dataset_description: str | None,
    table_id: str,
    table_type: str,
    table_description: str | None,
    fields: Iterable[bigquery.SchemaField],
    parent_path: str = "",
    parent_field: str | None = None,
    depth: int = 0,
) -> list[ColumnMetadata]:
    rows: list[ColumnMetadata] = []

    for field in fields:
        column_path = f"{parent_path}.{field.name}" if parent_path else field.name
        mode = (field.mode or "NULLABLE").upper()
        policy_tags = None
        if field.policy_tags and field.policy_tags.names:
            policy_tags = ",".join(field.policy_tags.names)

        rows.append(
            ColumnMetadata(
                project_id=project_id,
                dataset_id=dataset_id,
                dataset_description=dataset_description,
                table_id=table_id,
                table_type=table_type,
                table_description=table_description,
                column_name=field.name,
                column_path=column_path,
                parent_field=parent_field,
                depth=depth,
                data_type=field.field_type,
                mode=mode,
                is_nullable=mode == "NULLABLE",
                is_repeated=mode == "REPEATED",
                description=field.description,
                policy_tags=policy_tags,
            )
        )

        if field.field_type == "RECORD" and field.fields:
            rows.extend(
                _flatten_schema(
                    project_id=project_id,
                    dataset_id=dataset_id,
                    dataset_description=dataset_description,
                    table_id=table_id,
                    table_type=table_type,
                    table_description=table_description,
                    fields=field.fields,
                    parent_path=column_path,
                    parent_field=field.name,
                    depth=depth + 1,
                )
            )

    return rows


def _get_selected_datasets(
    client: bigquery.Client,
    project_id: str,
    datasets_arg: str | None,
    dataset_regex: str | None,
) -> list[str]:
    available = sorted(dataset.dataset_id for dataset in client.list_datasets(project=project_id))

    if not available:
        return []

    selected = available

    if datasets_arg:
        requested = {d.strip() for d in datasets_arg.split(",") if d.strip()}
        selected = [d for d in selected if d in requested]

    if dataset_regex:
        pattern = re.compile(dataset_regex)
        selected = [d for d in selected if pattern.search(d)]

    return selected


def collect_metadata(
    client: bigquery.Client,
    project_id: str,
    selected_datasets: list[str],
    include_views: bool,
) -> tuple[list[dict], list[dict]]:
    nested_datasets: list[dict] = []
    flat_rows: list[dict] = []

    for dataset_id in selected_datasets:
        dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
        dataset = client.get_dataset(dataset_ref)
        tables_summary = []

        for table_item in client.list_tables(dataset_ref):
            table_type = (table_item.table_type or "").upper()
            if not include_views and table_type in {"VIEW", "MATERIALIZED_VIEW"}:
                continue

            table = client.get_table(table_item.reference)
            columns = _flatten_schema(
                project_id=project_id,
                dataset_id=dataset_id,
                dataset_description=dataset.description,
                table_id=table.table_id,
                table_type=table_type or "TABLE",
                table_description=table.description,
                fields=table.schema,
            )

            flat_rows.extend(asdict(column) for column in columns)

            tables_summary.append(
                {
                    "table_id": table.table_id,
                    "table_type": table_type or "TABLE",
                    "description": table.description,
                    "num_rows": table.num_rows,
                    "num_bytes": table.num_bytes,
                    "created": table.created.isoformat() if table.created else None,
                    "modified": table.modified.isoformat() if table.modified else None,
                    "columns": [asdict(column) for column in columns],
                }
            )

        nested_datasets.append(
            {
                "project_id": project_id,
                "dataset_id": dataset_id,
                "description": dataset.description,
                "location": dataset.location,
                "created": dataset.created.isoformat() if dataset.created else None,
                "modified": dataset.modified.isoformat() if dataset.modified else None,
                "tables": tables_summary,
            }
        )

    return nested_datasets, flat_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_catalog_rows(nested_datasets: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for dataset in nested_datasets:
        for table in dataset["tables"]:
            rows.append(
                {
                    "project_id": dataset["project_id"],
                    "dataset_id": dataset["dataset_id"],
                    "dataset_description": dataset.get("description"),
                    "table_id": table["table_id"],
                    "table_type": table["table_type"],
                    "table_description": table.get("description"),
                    "column_count": len(table["columns"]),
                    "num_rows": table.get("num_rows"),
                    "num_bytes": table.get("num_bytes"),
                    "created": table.get("created"),
                    "modified": table.get("modified"),
                }
            )
    return rows


def write_structured_outputs(
    base_dir: Path,
    generated_at: str,
    project_id: str,
    nested_datasets: list[dict],
    flat_rows: list[dict],
) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    schemas_dir = base_dir / "schemas"
    query_examples_dir = base_dir / "query_examples"
    query_examples_dir.mkdir(parents=True, exist_ok=True)

    catalog_rows = build_catalog_rows(nested_datasets)
    catalog_index_path = base_dir / "catalog_index.csv"
    column_search_path = base_dir / "column_search.csv"
    write_csv(catalog_index_path, catalog_rows)
    write_csv(column_search_path, flat_rows)

    for dataset in nested_datasets:
        dataset_id = dataset["dataset_id"]
        dataset_dir = schemas_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)

        for table in dataset["tables"]:
            table_path = dataset_dir / f"{table['table_id']}.json"
            table_payload = {
                "generated_at": generated_at,
                "project_id": dataset["project_id"],
                "dataset_id": dataset_id,
                "dataset_description": dataset.get("description"),
                "table_id": table["table_id"],
                "table_type": table["table_type"],
                "table_description": table.get("description"),
                "num_rows": table.get("num_rows"),
                "num_bytes": table.get("num_bytes"),
                "created": table.get("created"),
                "modified": table.get("modified"),
                "columns": table["columns"],
            }
            write_json(table_path, table_payload)

    manifest = {
        "generated_at": generated_at,
        "project_id": project_id,
        "dataset_count": len(nested_datasets),
        "table_count": sum(len(ds["tables"]) for ds in nested_datasets),
        "column_count": len(flat_rows),
        "files": {
            "catalog_index": str(catalog_index_path.relative_to(base_dir)),
            "column_search": str(column_search_path.relative_to(base_dir)),
            "schemas_dir": str(schemas_dir.relative_to(base_dir)),
            "query_examples_dir": str(query_examples_dir.relative_to(base_dir)),
        },
    }
    write_json(base_dir / "manifest.json", manifest)
    write_json(base_dir / "full_catalog.json", {"datasets": nested_datasets, **manifest})

    readme = [
        "# Query Examples",
        "",
        "Coloque aqui consultas SQL exemplo organizadas por dominio.",
        "Sugestao de estrutura:",
        "- query_examples/docentes/",
        "- query_examples/matriculas/",
        "- query_examples/escolas/",
        "",
        "Use `catalog_index.csv` para achar tabelas e `column_search.csv` para achar colunas.",
    ]
    (query_examples_dir / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exporta metadados do BigQuery em estrutura pronta para busca."
    )
    parser.add_argument(
        "--project-id",
        help="Projeto GCP. Se omitido, usa GCP_PROJECT_ID do .env.",
        default=None,
    )
    parser.add_argument(
        "--datasets",
        help="Lista de datasets separados por virgula (ex: ds1,ds2).",
        default=None,
    )
    parser.add_argument(
        "--dataset-regex",
        help="Regex para filtrar datasets pelo nome.",
        default=None,
    )
    parser.add_argument(
        "--include-views",
        action="store_true",
        help="Inclui views e materialized views no resultado.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT_DIR / "output" / "metadata"),
        help="Diretorio base de saida dos snapshots.",
    )
    parser.add_argument(
        "--filename-prefix",
        default="metadata_snapshot",
        help="Prefixo do diretorio de snapshot.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    settings = get_local_settings()
    project_id = args.project_id or settings.gcp_project_id
    if not project_id:
        print("Projeto nao definido. Configure GCP_PROJECT_ID no .env.")
        return 2

    client = bigquery.Client(project=project_id)
    selected_datasets = _get_selected_datasets(
        client=client,
        project_id=project_id,
        datasets_arg=args.datasets,
        dataset_regex=args.dataset_regex,
    )

    if not selected_datasets:
        print(f"Nenhum dataset encontrado para o projeto '{project_id}'.")
        return 1

    nested_datasets, flat_rows = collect_metadata(
        client=client,
        project_id=project_id,
        selected_datasets=selected_datasets,
        include_views=args.include_views,
    )

    generated_at = datetime.now(timezone.utc).isoformat()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = output_dir / f"{args.filename_prefix}_{timestamp}"
    write_structured_outputs(
        base_dir=snapshot_dir,
        generated_at=generated_at,
        project_id=project_id,
        nested_datasets=nested_datasets,
        flat_rows=flat_rows,
    )

    print(
        f"Snapshot gerado em: {snapshot_dir}\n"
        f"Concluido: {len(nested_datasets)} dataset(s), "
        f"{sum(len(ds['tables']) for ds in nested_datasets)} tabela(s), "
        f"{len(flat_rows)} campo(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
