r"""Run the ATM SQL batch publish script in BigQuery with local logs.

Usage examples:
    .\school-report-python\.venv\Scripts\python.exe \
        .\school-report-python\reports\ATM\scripts\run_atm_sql_batch_publish.py \
        --mode dry-run

    .\school-report-python\.venv\Scripts\python.exe \
        .\school-report-python\reports\ATM\scripts\run_atm_sql_batch_publish.py \
        --mode execute
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from google.cloud import bigquery
from google.cloud.exceptions import NotFound


SCRIPT_PATH = Path(__file__).resolve()
PYTHON_ROOT = SCRIPT_PATH.parents[3]
MONOREPO_ROOT = SCRIPT_PATH.parents[4]
R_ROOT = MONOREPO_ROOT / "school-report-r"

DEFAULT_SQL_PATH = (
    R_ROOT
    / "scripts"
    / "atm_batch"
    / "sql_batch"
    / "sql_publish"
    / "atm_publish_all_municipios.sql"
)
DEFAULT_SUMMARY_PATH = (
    R_ROOT
    / "scripts"
    / "atm_batch"
    / "sql_batch"
    / "sql_set_based"
    / "atm_set_based_pipeline_summary.json"
)
DEFAULT_SET_BASED_DIR = (
    R_ROOT / "scripts" / "atm_batch" / "sql_batch" / "sql_set_based"
)
DEFAULT_LOG_DIR = PYTHON_ROOT / ".tmp" / "atm_sql_batch"

DEFAULT_JOB_PROJECT = "br-mec-segape-sandbox"
DEFAULT_LOCATION = "southamerica-east1"
EXPECTED_TOTAL_QUERIES = 31


@dataclass
class PublishDeclares:
    source_project: str
    source_municipios_table: str
    target_project: str
    target_dataset: str
    final_table: str


class LocalLogger:
    """Very small UTF-8 logger for terminal + file output."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("", encoding="utf-8")

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the ATM SQL batch publish script in BigQuery."
    )
    parser.add_argument(
        "--mode",
        choices=("dry-run", "execute"),
        default="dry-run",
        help="Run mode. Default: dry-run.",
    )
    parser.add_argument(
        "--sql-path",
        type=Path,
        default=DEFAULT_SQL_PATH,
        help=f"Path to the generated publish SQL. Default: {DEFAULT_SQL_PATH}",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=DEFAULT_SUMMARY_PATH,
        help=f"Path to the set-based summary JSON. Default: {DEFAULT_SUMMARY_PATH}",
    )
    parser.add_argument(
        "--job-project",
        default=DEFAULT_JOB_PROJECT,
        help=f"BigQuery job project. Default: {DEFAULT_JOB_PROJECT}",
    )
    parser.add_argument(
        "--location",
        default=DEFAULT_LOCATION,
        help=f"BigQuery job location. Default: {DEFAULT_LOCATION}",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help=f"Directory for local logs. Default: {DEFAULT_LOG_DIR}",
    )
    parser.add_argument(
        "--skip-summary-check",
        action="store_true",
        help="Skip the summary preflight check before submitting the job.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def read_summary(path: Path) -> dict[str, Any]:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid summary JSON structure: {path}")
    return payload


def check_summary(summary: dict[str, Any], summary_path: Path) -> None:
    required = {
        "total_queries": EXPECTED_TOTAL_QUERIES,
        "validation_not_ok": 0,
        "potentially_stale": 0,
    }
    failures = []
    for key, expected in required.items():
        actual = summary.get(key)
        if actual != expected:
            failures.append(f"{key}={actual!r} (esperado {expected!r})")
    if failures:
        raise RuntimeError(
            "Summary preflight failed for "
            f"{summary_path}: " + ", ".join(failures)
        )


def extract_declare(sql_text: str, name: str) -> str:
    import re

    pattern = rf"(?mi)^DECLARE\s+{name}\s+STRING\s+DEFAULT\s+'([^']*)';"
    match = re.search(pattern, sql_text)
    if match is None:
        raise ValueError(f"Could not extract DECLARE {name!r} from publish SQL.")
    return match.group(1)


def extract_declares(sql_text: str) -> PublishDeclares:
    return PublishDeclares(
        source_project=extract_declare(sql_text, "source_project"),
        source_municipios_table=extract_declare(sql_text, "source_municipios_table"),
        target_project=extract_declare(sql_text, "target_project"),
        target_dataset=extract_declare(sql_text, "target_dataset"),
        final_table=extract_declare(sql_text, "final_table"),
    )


def expected_atm_tables(set_based_dir: Path) -> list[str]:
    names = []
    for path in sorted(set_based_dir.glob("atm_*.sql")):
        if "__all_municipios__stub" in path.name:
            continue
        names.append(path.stem)
    if not names:
        raise RuntimeError(f"No atm_*.sql files found in {set_based_dir}")
    return names


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def collect_job_metadata(
    job: bigquery.QueryJob | None,
    requested_job_id: str | None = None,
) -> dict[str, Any]:
    if job is None:
        return {
            "job_id": requested_job_id,
            "requested_job_id": requested_job_id,
            "state": None,
            "location": None,
            "error_result": None,
            "errors": None,
        }
    return {
        "job_id": job.job_id or requested_job_id,
        "requested_job_id": requested_job_id,
        "state": job.state,
        "location": job.location,
        "error_result": job.error_result,
        "errors": job.errors,
    }


def query_one_row(
    client: bigquery.Client,
    query: str,
    *,
    location: str,
    job_config: bigquery.QueryJobConfig | None = None,
) -> dict[str, Any]:
    job = client.query(query, location=location, job_config=job_config)
    row = next(iter(job.result()))
    return dict(row.items())


def validate_execute_results(
    client: bigquery.Client,
    declares: PublishDeclares,
    *,
    location: str,
) -> dict[str, Any]:
    final_table_fqn = (
        f"{declares.target_project}.{declares.target_dataset}.{declares.final_table}"
    )
    client.get_table(final_table_fqn)

    final_counts_query = f"""
    SELECT
      COUNT(*) AS total_rows,
      COUNT(DISTINCT codIbge) AS distinct_codibge
    FROM `{final_table_fqn}`
    """
    final_counts = query_one_row(client, final_counts_query, location=location)

    municipios_table_fqn = (
        f"{declares.source_project}.{declares.source_municipios_table}"
    )
    municipios_count_query = f"""
    SELECT COUNT(DISTINCT CAST(id_municipio AS STRING)) AS total_municipios
    FROM `{municipios_table_fqn}`
    WHERE id_municipio IS NOT NULL
    """
    municipios_counts = query_one_row(
        client, municipios_count_query, location=location
    )

    expected_tables = expected_atm_tables(DEFAULT_SET_BASED_DIR)
    info_schema_query = f"""
    SELECT table_name
    FROM `{declares.target_project}.{declares.target_dataset}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name IN UNNEST(@table_names)
    """
    info_schema_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("table_names", "STRING", expected_tables)
        ],
        use_legacy_sql=False,
    )
    info_schema_job = client.query(
        info_schema_query,
        location=location,
        job_config=info_schema_config,
    )
    existing_tables = sorted(row["table_name"] for row in info_schema_job.result())
    missing_tables = sorted(set(expected_tables) - set(existing_tables))

    validation = {
        "final_table_fqn": final_table_fqn,
        "final_table_exists": True,
        "final_total_rows": int(final_counts["total_rows"]),
        "final_distinct_codibge": int(final_counts["distinct_codibge"]),
        "source_total_municipios": int(municipios_counts["total_municipios"]),
        "expected_atm_table_count": len(expected_tables),
        "existing_atm_table_count": len(existing_tables),
        "missing_tables": missing_tables,
    }

    if validation["final_total_rows"] != validation["final_distinct_codibge"]:
        raise RuntimeError(
            "Final table count mismatch: "
            f"COUNT(*)={validation['final_total_rows']} "
            f"COUNT(DISTINCT codIbge)={validation['final_distinct_codibge']}"
        )

    if validation["final_total_rows"] != validation["source_total_municipios"]:
        raise RuntimeError(
            "Final table municipality count mismatch: "
            f"final={validation['final_total_rows']} "
            f"source={validation['source_total_municipios']}"
        )

    if missing_tables:
        raise RuntimeError(
            "Missing atm_* tables after execute: " + ", ".join(missing_tables)
        )

    return validation


def build_payload(
    args: argparse.Namespace,
    *,
    timestamp: str,
    log_path: Path,
    json_path: Path,
) -> dict[str, Any]:
    return {
        "timestamp": timestamp,
        "mode": args.mode,
        "sql_path": str(args.sql_path.resolve()),
        "summary_path": str(args.summary_path.resolve()),
        "log_path": str(log_path.resolve()),
        "json_path": str(json_path.resolve()),
        "job_project": args.job_project,
        "location": args.location,
        "skip_summary_check": args.skip_summary_check,
        "status": "initialized",
        "job": collect_job_metadata(None),
        "sql_declares": None,
        "summary": None,
        "post_validation": None,
        "exception_type": None,
        "exception_message": None,
        "duration_seconds": None,
    }


def run(args: argparse.Namespace) -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = args.log_dir / f"{timestamp}_{args.mode}.log"
    json_path = args.log_dir / f"{timestamp}_{args.mode}.json"
    logger = LocalLogger(log_path)
    requested_job_id = f"atm_sql_batch_{args.mode.replace('-', '_')}_{timestamp}"
    payload = build_payload(
        args,
        timestamp=timestamp,
        log_path=log_path,
        json_path=json_path,
    )
    started = time.perf_counter()
    job: bigquery.QueryJob | None = None

    try:
        logger.log(f"Mode: {args.mode}")
        logger.log(f"SQL path: {args.sql_path}")
        logger.log(f"Summary path: {args.summary_path}")
        logger.log(f"Job project: {args.job_project}")
        logger.log(f"Location: {args.location}")
        logger.log("Note: dry-run is a technical preflight only for this script.")

        if not args.skip_summary_check:
            summary = read_summary(args.summary_path)
            check_summary(summary, args.summary_path)
            payload["summary"] = summary
            logger.log("Summary preflight check passed.")
        else:
            logger.log("Skipping summary preflight check by request.")

        sql_text = read_text(args.sql_path)
        declares = extract_declares(sql_text)
        payload["sql_declares"] = asdict(declares)
        logger.log(
            "Extracted SQL declares: "
            f"target={declares.target_project}.{declares.target_dataset}.{declares.final_table}"
        )

        client = bigquery.Client(project=args.job_project)
        if args.mode == "dry-run":
            job_config = bigquery.QueryJobConfig(
                dry_run=True,
                use_query_cache=False,
                use_legacy_sql=False,
            )
        else:
            job_config = bigquery.QueryJobConfig(use_legacy_sql=False)

        logger.log(f"Submitting BigQuery job with requested id: {requested_job_id}")
        job = client.query(
            sql_text,
            location=args.location,
            job_config=job_config,
            job_id=requested_job_id,
            job_retry=None,
        )
        payload["job"] = collect_job_metadata(job, requested_job_id=requested_job_id)
        payload["status"] = "submitted"
        write_json(json_path, payload)
        logger.log(f"Job submitted: {payload['job']['job_id']}")

        if args.mode == "dry-run":
            job.result()
            payload["job"] = collect_job_metadata(job, requested_job_id=requested_job_id)
            payload["status"] = "dry_run_ok"
            payload["dry_run_total_bytes_processed"] = int(
                job.total_bytes_processed or 0
            )
            logger.log(
                "Dry-run completed successfully. "
                f"Total bytes processed: {payload['dry_run_total_bytes_processed']}"
            )
        else:
            job.result()
            payload["job"] = collect_job_metadata(job, requested_job_id=requested_job_id)
            logger.log("Execute completed successfully. Running post-validation...")
            validation = validate_execute_results(
                client,
                declares,
                location=args.location,
            )
            payload["post_validation"] = validation
            payload["status"] = "execute_ok"
            logger.log(
                "Post-validation passed. "
                f"Final rows: {validation['final_total_rows']}"
            )

        return_code = 0
    except NotFound as exc:
        payload["status"] = "error"
        payload["exception_type"] = type(exc).__name__
        payload["exception_message"] = str(exc)
        payload["job"] = collect_job_metadata(job, requested_job_id=requested_job_id)
        logger.log(f"BigQuery object not found: {exc}")
        return_code = 1
    except Exception as exc:  # noqa: BLE001 - we want raw BigQuery failure details
        payload["status"] = "error"
        payload["exception_type"] = type(exc).__name__
        payload["exception_message"] = str(exc)
        payload["job"] = collect_job_metadata(job, requested_job_id=requested_job_id)
        logger.log(f"Execution failed: {type(exc).__name__}: {exc}")
        return_code = 1
    finally:
        payload["duration_seconds"] = round(time.perf_counter() - started, 3)
        write_json(json_path, payload)
        logger.log(f"Log file: {log_path}")
        logger.log(f"JSON file: {json_path}")
        logger.log(f"Final status: {payload['status']}")

    return return_code


def main() -> None:
    args = parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
