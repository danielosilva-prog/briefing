#!/usr/bin/env python
"""ATM-EQ batch runner (planning or execution).

Mirrors the R batch runner structure:
- Uses `schoolreport generate ATM-EQ ...` for faithful execution
- Keeps dry-run by default (EXECUTE = False)
- Supports filters, folder grouping, skip-existing, and structured logs
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORT_ROOT = Path(__file__).resolve().parents[2]

# ==============================
# CONFIGURACAO (edite aqui)
# ==============================

EXECUTE = True
PARALLEL = True
WORKERS = 5
CONTINUE_ON_ERROR = True
SKIP_EXISTING = False

FOLDER_GROUPING = "regiao"  # "brasil" | "regiao" | "uf"
OUTPUT_ROOT = Path(r"C:\Users\Anderson\OneDrive - MEC-Ministério da Educação\ATM_EQ_arquivos")
LOG_DIR = OUTPUT_ROOT / "_logs"

# Divisao operacional do lote entre 3 pessoas.
# Para cada pessoa, ajuste EXPORT_SPLIT_PROFILE e rode o script na propria maquina.
# A pessoa 1 fica com 3 regioes; as pessoas 2 e 3 ficam com 1 regiao cada.
EXPORT_SPLIT_PROFILE = "pessoa_3"
EXPORT_SPLITS: dict[str, list[str]] = {
    "pessoa_1": ["Norte", "Sul", "Centro-Oeste"],
    "pessoa_2": ["Sudeste"],
    "pessoa_3": ["Nordeste"],
}
if EXPORT_SPLIT_PROFILE not in EXPORT_SPLITS:
    raise ValueError(
        "EXPORT_SPLIT_PROFILE deve ser um de "
        f"{', '.join(sorted(EXPORT_SPLITS))}."
    )

# Filtros (use None para nao filtrar)
FILTER_UFS: list[str] | None = None
FILTER_REGIOES: list[str] | None = EXPORT_SPLITS[EXPORT_SPLIT_PROFILE]
FILTER_COD_IBGE: list[str] | None = None
MAX_MUNICIPIOS: int | None = None

INCLUDE_TIMESTAMP = False
REPORT_ID = "ATM-EQ"
DATA_PROJECT = "br-mec-segape"


UF_REGION_MAP = {
    "AC": "Norte",
    "AL": "Nordeste",
    "AP": "Norte",
    "AM": "Norte",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "DF": "Centro-Oeste",
    "ES": "Sudeste",
    "GO": "Centro-Oeste",
    "MA": "Nordeste",
    "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "MG": "Sudeste",
    "PA": "Norte",
    "PB": "Nordeste",
    "PR": "Sul",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RJ": "Sudeste",
    "RN": "Nordeste",
    "RS": "Sul",
    "RO": "Norte",
    "RR": "Norte",
    "SC": "Sul",
    "SP": "Sudeste",
    "SE": "Nordeste",
    "TO": "Norte",
}


def sanitize_path_component(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9_ -]+", " ", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "sem_nome"


def validate_grouping(grouping: str) -> str:
    valid = {"brasil", "regiao", "uf"}
    if grouping not in valid:
        raise ValueError(f"folder_grouping deve ser um de {sorted(valid)}")
    return grouping


def normalize_upper_list(values: list[str] | None) -> list[str] | None:
    if values is None:
        return None
    return sorted({str(value).strip().upper() for value in values if str(value).strip()})


def normalize_region_list(values: list[str] | None) -> list[str] | None:
    if values is None:
        return None

    normalized = set()
    for value in values:
        item = str(value).strip().lower()
        item = item.replace("centro oeste", "centro-oeste").replace("centro_oeste", "centro-oeste")
        normalized.add(item.title())
    return sorted(normalized)


def output_dir_for_row(row: pd.Series, output_root: Path, grouping: str) -> Path:
    grouping = validate_grouping(grouping)
    if grouping == "brasil":
        return output_root / "brasil"
    if grouping == "regiao":
        return output_root / sanitize_path_component(row["regiao"])
    return output_root / str(row["uf"])


def filename_for_row(row: pd.Series, report_prefix: str = REPORT_ID, timestamp: bool = True) -> str:
    municipio_safe = sanitize_path_component(row["municipio"])
    suffix = ""
    if timestamp:
        suffix = "_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{report_prefix}_{row['cod_ibge']}_{municipio_safe}_{row['uf']}{suffix}.pdf"


def _timestamp_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_batch_artifacts(result_df: pd.DataFrame, log_dir: Path | None, run_mode: str) -> dict[str, str] | None:
    if log_dir is None:
        return None

    log_dir.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest_path = log_dir / f"atm_eq_batch_{run_mode}_{run_id}.csv"
    summary_path = log_dir / f"atm_eq_batch_{run_mode}_{run_id}_summary.json"

    result_df.to_csv(manifest_path, index=False, encoding="utf-8-sig")

    duration_series = pd.to_numeric(result_df.get("duration_seconds"), errors="coerce")
    summary = {
        "run_id": run_id,
        "run_mode": run_mode,
        "generated_at": _timestamp_now(),
        "total": int(len(result_df)),
        "total_duration_sec": float(duration_series.fillna(0).sum()) if not duration_series.empty else None,
        "planned": int((result_df.get("status") == "planned").sum()) if "status" in result_df else 0,
        "success": int((result_df.get("status") == "success").sum()) if "status" in result_df else 0,
        "skipped_existing": int((result_df.get("status") == "skipped_existing").sum()) if "status" in result_df else 0,
        "error": int((result_df.get("status") == "error").sum()) if "status" in result_df else 0,
        "log_csv": str(manifest_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "manifest_path": str(manifest_path),
        "summary_path": str(summary_path),
    }


def get_atm_eq_municipality_catalog(project: str = DATA_PROJECT) -> pd.DataFrame:
    from schoolreport.config import get_local_settings
    from schoolreport.core.bigquery import BigQueryClient

    sql = f"""
    SELECT DISTINCT
      CAST(id_municipio AS STRING) AS cod_ibge,
      nome AS municipio,
      UPPER(sigla_uf) AS uf,
      nome_uf AS estado
    FROM `{project}.educacao_dados_mestres.municipio`
    WHERE id_municipio IS NOT NULL
      AND sigla_uf IS NOT NULL
      AND nome IS NOT NULL
    """

    settings = get_local_settings()
    client = BigQueryClient(project_id=settings.gcp_project_id)
    catalog = asyncio.run(client.execute_query(sql))

    if catalog.empty:
        raise RuntimeError("Catalogo de municipios retornou vazio.")

    catalog = catalog.copy()
    catalog["cod_ibge"] = catalog["cod_ibge"].astype(str).str.zfill(7)
    catalog["municipio"] = catalog["municipio"].astype(str)
    catalog["uf"] = catalog["uf"].astype(str).str.upper()
    catalog["estado"] = catalog["estado"].astype(str)
    catalog["regiao"] = catalog["uf"].map(UF_REGION_MAP)
    catalog = catalog.dropna(subset=["regiao"]).drop_duplicates(subset=["cod_ibge"])
    return catalog.sort_values(["regiao", "uf", "municipio"]).reset_index(drop=True)


def build_atm_eq_batch_plan(
    municipios: pd.DataFrame | None = None,
    cod_ibge: list[str] | None = None,
    ufs: list[str] | None = None,
    regioes: list[str] | None = None,
    output_root: Path = OUTPUT_ROOT,
    folder_grouping: str = FOLDER_GROUPING,
    report_id: str = REPORT_ID,
    max_municipios: int | None = None,
    include_timestamp: bool = False,
) -> pd.DataFrame:
    folder_grouping = validate_grouping(folder_grouping)
    cod_ibge_filter = None if cod_ibge is None else sorted({str(value).strip() for value in cod_ibge if str(value).strip()})
    uf_filter = normalize_upper_list(ufs)
    region_filter = normalize_region_list(regioes)

    if municipios is None:
        municipios = get_atm_eq_municipality_catalog()

    required_columns = {"cod_ibge", "municipio", "uf", "estado", "regiao"}
    missing = sorted(required_columns - set(municipios.columns))
    if missing:
        raise ValueError(f"Tabela municipios sem colunas obrigatorias: {', '.join(missing)}")

    plan = municipios.copy()
    plan["cod_ibge"] = plan["cod_ibge"].astype(str)
    plan["municipio"] = plan["municipio"].astype(str)
    plan["uf"] = plan["uf"].astype(str).str.upper()
    plan["estado"] = plan["estado"].astype(str)
    plan["regiao"] = plan["regiao"].astype(str)

    if cod_ibge_filter is not None:
        plan = plan[plan["cod_ibge"].isin(cod_ibge_filter)]
    if uf_filter is not None:
        plan = plan[plan["uf"].isin(uf_filter)]
    if region_filter is not None:
        plan = plan[plan["regiao"].isin(region_filter)]

    if plan.empty:
        raise RuntimeError("Nenhum municipio encontrado apos aplicar os filtros do lote.")

    if max_municipios is not None:
        if max_municipios < 1:
            raise ValueError("max_municipios deve ser um inteiro positivo.")
        plan = plan.head(int(max_municipios))

    plan = plan.sort_values(["regiao", "uf", "municipio"]).reset_index(drop=True)
    plan["report_id"] = report_id
    plan["output_dir"] = [
        str(output_dir_for_row(row, output_root=output_root, grouping=folder_grouping))
        for _, row in plan.iterrows()
    ]
    plan["output_filename"] = [
        filename_for_row(row, report_prefix=report_id, timestamp=include_timestamp)
        for _, row in plan.iterrows()
    ]
    plan["output_file"] = [
        str(Path(output_dir) / filename)
        for output_dir, filename in zip(plan["output_dir"], plan["output_filename"], strict=False)
    ]
    plan["folder_grouping"] = folder_grouping
    plan["output_exists"] = [Path(path).exists() for path in plan["output_file"]]
    return plan


@dataclass
class ExecutionResult:
    status: str
    error_message: str | None
    error_detail: str | None
    started_at: str
    rendered_at: str
    duration_seconds: float
    command: str


def _extract_process_error(stdout: str, stderr: str) -> tuple[str, str]:
    stdout = stdout.strip()
    stderr = stderr.strip()
    message = stderr.splitlines()[-1] if stderr else (stdout.splitlines()[-1] if stdout else "Falha ao gerar relatorio.")
    detail_parts = []
    if stderr:
        detail_parts.append(f"stderr: {stderr}")
    if stdout:
        detail_parts.append(f"stdout: {stdout}")
    return message, " | ".join(detail_parts) if detail_parts else message


def _run_one_generation(row: pd.Series, skip_existing: bool) -> ExecutionResult:
    output_file = Path(row["output_file"])
    started_at = _timestamp_now()
    command = [
        "uv",
        "run",
        "schoolreport",
        "generate",
        row["report_id"],
        f"cod_ibge={row['cod_ibge']}",
        "--output",
        str(output_file),
    ]

    if skip_existing and output_file.exists():
        return ExecutionResult(
            status="skipped_existing",
            error_message=None,
            error_detail=None,
            started_at=started_at,
            rendered_at=_timestamp_now(),
            duration_seconds=0.0,
            command=" ".join(command),
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    start_perf = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
    )
    elapsed = time.perf_counter() - start_perf
    rendered_at = _timestamp_now()

    if completed.returncode == 0:
        return ExecutionResult(
            status="success",
            error_message=None,
            error_detail=None,
            started_at=started_at,
            rendered_at=rendered_at,
            duration_seconds=elapsed,
            command=" ".join(command),
        )

    error_message, error_detail = _extract_process_error(completed.stdout, completed.stderr)
    return ExecutionResult(
        status="error",
        error_message=error_message,
        error_detail=error_detail,
        started_at=started_at,
        rendered_at=rendered_at,
        duration_seconds=elapsed,
        command=" ".join(command),
    )


def render_atm_eq_batch(
    plan: pd.DataFrame | None = None,
    execute: bool = False,
    parallel: bool = False,
    workers: int | None = None,
    continue_on_error: bool = True,
    skip_existing: bool = True,
    log_dir: Path | None = None,
    **build_kwargs: Any,
) -> pd.DataFrame:
    if plan is None:
        plan = build_atm_eq_batch_plan(**build_kwargs)

    if not execute:
        planned = plan.copy()
        planned["status"] = "planned"
        planned["error_message"] = pd.NA
        planned["error_detail"] = pd.NA
        planned["started_at"] = pd.NA
        planned["rendered_at"] = pd.NA
        planned["duration_seconds"] = pd.NA
        planned["command"] = pd.NA
        write_batch_artifacts(planned, log_dir=log_dir, run_mode="planned")
        return planned

    if plan.empty:
        return plan

    rows = [row for _, row in plan.iterrows()]
    results: list[dict[str, Any] | None] = [None] * len(rows)

    def execute_index(index: int) -> dict[str, Any]:
        row = rows[index]
        result = _run_one_generation(row, skip_existing=skip_existing)
        payload = row.to_dict()
        payload.update(
            {
                "status": result.status,
                "error_message": result.error_message,
                "error_detail": result.error_detail,
                "started_at": result.started_at,
                "rendered_at": result.rendered_at,
                "duration_seconds": result.duration_seconds,
                "command": result.command,
            }
        )
        return payload

    if parallel:
        worker_count = workers or min(len(rows), max(1, (os.cpu_count() or 1) - 1))
        print(f"[{datetime.now():%H:%M:%S}] Execucao paralela ATM-EQ iniciada: {len(rows)} municipios, {worker_count} workers.")
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_index = {executor.submit(execute_index, idx): idx for idx in range(len(rows))}
            completed_count = 0

            while future_to_index:
                done, _ = wait(future_to_index, timeout=5, return_when=FIRST_COMPLETED)
                if not done:
                    print(f"[{datetime.now():%H:%M:%S}] Progresso ATM-EQ batch: {completed_count}/{len(rows)} concluidos.")
                    continue

                for future in done:
                    idx = future_to_index.pop(future)
                    result = future.result()
                    results[idx] = result
                    completed_count += 1
                    duration_txt = f"{result['duration_seconds']:.2f}s" if pd.notna(result["duration_seconds"]) else "NA"
                    print(
                        f"[{datetime.now():%H:%M:%S}] Concluido cod_ibge={result['cod_ibge']} "
                        f"(status={result['status']}, duracao={duration_txt})."
                    )
                    if result["status"] == "error" and not continue_on_error:
                        for pending in future_to_index:
                            pending.cancel()
                        future_to_index.clear()
                        raise RuntimeError(f"Falha no lote para cod_ibge={result['cod_ibge']}: {result['error_message']}")
    else:
        print(f"[{datetime.now():%H:%M:%S}] Execucao sequencial ATM-EQ iniciada: {len(rows)} municipios.")
        for idx in range(len(rows)):
            print(f"[{datetime.now():%H:%M:%S}] Iniciando {idx + 1}/{len(rows)} (cod_ibge={rows[idx]['cod_ibge']}).")
            result = execute_index(idx)
            results[idx] = result
            print(
                f"[{datetime.now():%H:%M:%S}] Finalizado {idx + 1}/{len(rows)} "
                f"(cod_ibge={result['cod_ibge']}, status={result['status']})."
            )
            if result["status"] == "error" and not continue_on_error:
                raise RuntimeError(f"Falha no lote para cod_ibge={result['cod_ibge']}: {result['error_message']}")

    final_result = pd.DataFrame([result for result in results if result is not None])
    write_batch_artifacts(final_result, log_dir=log_dir, run_mode="executed")
    return final_result


def print_summary(result: pd.DataFrame, elapsed_sec: float, parallel: bool, workers: int | None) -> None:
    status_counts = result["status"].value_counts(dropna=False)
    print("Resumo por status:")
    print(status_counts.to_string())
    print(f"\nTempo total da execucao do lote: {elapsed_sec:.2f} s")

    duration = pd.to_numeric(result.get("duration_seconds"), errors="coerce").dropna()
    if not duration.empty:
        total_individual = float(duration.sum())
        total_rows = len(result)
        wall_avg = elapsed_sec / total_rows if total_rows else float("nan")
        throughput = (total_rows / elapsed_sec) * 3600 if elapsed_sec > 0 else float("nan")

        print(f"Soma das duracoes individuais: {total_individual:.2f} s")
        print(f"Tempo medio individual por municipio: {duration.mean():.2f} s")
        print(f"Tempo medio real por municipio no lote (wall-clock): {wall_avg:.2f} s")
        print(f"Throughput aproximado: {throughput:.2f} municipios/hora")

        if parallel:
            effective_workers = total_individual / elapsed_sec if elapsed_sec > 0 else float("nan")
            print(
                "Paralelismo efetivo medio: "
                f"{effective_workers:.2f} workers-equivalentes (duracoes individuais / tempo total)"
            )
            if workers:
                efficiency = (effective_workers / workers) * 100
                print(f"Eficiencia aproximada vs WORKERS={workers}: {efficiency:.1f}%")

    print("\nAmostra:")
    sample_cols = ["cod_ibge", "municipio", "uf", "regiao", "output_file", "status"]
    print(result[sample_cols].head(10).to_string(index=False))

    if (result["status"] == "error").any():
        print("\nErros (amostra):")
        error_cols = ["cod_ibge", "municipio", "error_message", "error_detail"]
        print(result.loc[result["status"] == "error", error_cols].head(10).to_string(index=False))


def main() -> None:
    print("\nATM-EQ BATCH RUNNER")
    print("=" * 19)
    print(f"EXECUTE: {EXECUTE}")
    print(f"PARALLEL: {PARALLEL}")
    print(f"FOLDER_GROUPING: {FOLDER_GROUPING}")
    print(f"OUTPUT_ROOT: {OUTPUT_ROOT}")
    print(f"LOG_DIR: {LOG_DIR}")
    print(f"EXPORT_SPLIT_PROFILE: {EXPORT_SPLIT_PROFILE}")
    print(f"FILTER_REGIOES: {FILTER_REGIOES}")
    print(f"SKIP_EXISTING: {SKIP_EXISTING}")
    print(f"MAX_MUNICIPIOS: {MAX_MUNICIPIOS if MAX_MUNICIPIOS is not None else 'None'}\n")

    plan = build_atm_eq_batch_plan(
        cod_ibge=FILTER_COD_IBGE,
        ufs=FILTER_UFS,
        regioes=FILTER_REGIOES,
        output_root=OUTPUT_ROOT,
        folder_grouping=FOLDER_GROUPING,
        report_id=REPORT_ID,
        max_municipios=MAX_MUNICIPIOS,
        include_timestamp=INCLUDE_TIMESTAMP,
    )

    print(f"Municipios selecionados: {len(plan)}")
    print("Pastas destino (amostra):")
    print("\n".join(plan["output_dir"].drop_duplicates().head(10).tolist()))
    print()

    started = time.perf_counter()
    result = render_atm_eq_batch(
        plan=plan,
        execute=EXECUTE,
        parallel=PARALLEL,
        workers=WORKERS,
        continue_on_error=CONTINUE_ON_ERROR,
        skip_existing=SKIP_EXISTING,
        log_dir=LOG_DIR,
    )
    elapsed = time.perf_counter() - started
    print_summary(result, elapsed_sec=elapsed, parallel=PARALLEL, workers=WORKERS)
    print("\nConcluido.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecucao interrompida pelo usuario.", file=sys.stderr)
        raise SystemExit(130)
