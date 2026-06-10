"""Generate ATM-EQ P03 review artifacts using real municipalities by motive.

Outputs:
- one representative real municipality per Condicionalidade III motive
- raw representative reference files (JSON and CSV)
- current P03 review files based on the active report query (JSON and CSV)
- one focused JSON payload per representative municipality
- optional ATM-EQ PDFs for the selected representatives
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import re
import unicodedata
from decimal import Decimal
from pathlib import Path
from typing import Any

from google.cloud import bigquery

from schoolreport.cli.executor import LocalExecutor
from schoolreport.services.registry import ReportRegistry


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = PROJECT_ROOT / "output" / "atm-eq-p03-motivos-reais"
PDF_DIR = OUTPUT_DIR / "pdfs"
P03_PAYLOAD_DIR = OUTPUT_DIR / "p03_payloads"
REPORT_ID = "ATM-EQ"
GCP_PROJECT_ID = "br-mec-segape"
P3_QUERY_PATH = REPORTS_DIR / REPORT_ID / "queries" / "p3_condicionalidade_iii_vaar.sql"
P3_QUERY_SQL = P3_QUERY_PATH.read_text(encoding="utf-8")


REPRESENTANTES_SQL = r"""
WITH anos_referencia AS (
  SELECT
    CAST(id_localidade AS STRING) AS cod_ibge,
    MAX(ano) AS ano
  FROM `br-mec-segape.educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar`
  WHERE LENGTH(CAST(id_localidade AS STRING)) = 7
  GROUP BY 1
),
base AS (
  SELECT
    t.ano,
    CAST(t.id_localidade AS STRING) AS cod_ibge,
    m.nome AS municipio,
    m.sigla_uf AS uf,
    t.motivo,
    t.indicador_habilitado,
    t.indice_ppi,
    t.indice_nse,
    t.proporcao_estudante_ppi_desempenho_adequado_saeb_2019 AS ppi_2019,
    t.proporcao_estudante_ppi_desempenho_adequado_saeb_2023 AS ppi_2023,
    t.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2019 AS nse_2019,
    t.proporcao_estudante_nse_baixo_desempenho_adequado_saeb_2023 AS nse_2023,
    COUNT(*) OVER (PARTITION BY t.motivo) AS qtd_municipios_motivo,
    ROW_NUMBER() OVER (
      PARTITION BY t.motivo
      ORDER BY m.sigla_uf, m.nome, CAST(t.id_localidade AS STRING)
    ) AS ordem
  FROM `br-mec-segape.educacao_politica_fundeb.fundeb_resultado_condicionalidade_iii_vaar` t
  JOIN anos_referencia a
    ON CAST(t.id_localidade AS STRING) = a.cod_ibge
   AND t.ano = a.ano
  LEFT JOIN `br-mec-segape.educacao_dados_mestres.municipio` m
    ON CAST(m.id_municipio AS STRING) = CAST(t.id_localidade AS STRING)
)
SELECT
  ano,
  cod_ibge,
  municipio,
  uf,
  motivo,
  indicador_habilitado,
  indice_ppi,
  indice_nse,
  ppi_2019,
  ppi_2023,
  nse_2019,
  nse_2023,
  qtd_municipios_motivo
FROM base
WHERE ordem = 1
ORDER BY motivo
"""

RAW_REFERENCE_FIELDNAMES = [
    "ano",
    "cod_ibge",
    "municipio",
    "uf",
    "motivo",
    "indicador_habilitado",
    "qtd_municipios_motivo",
    "indice_ppi",
    "indice_nse",
    "ppi_2019",
    "ppi_2023",
    "nse_2019",
    "nse_2023",
]

P03_REVIEW_FIELDNAMES = [
    "anoRepresentante",
    "cod_ibge",
    "municipio",
    "uf",
    "motivoTabela",
    "indicadorHabilitadoTabela",
    "qtdMunicipiosMotivo",
    "indicePpiTabela",
    "indiceNseTabela",
    "ppi2019Tabela",
    "ppi2023Tabela",
    "nse2019Tabela",
    "nse2023Tabela",
    "p3AnoReferencia",
    "p3GrupoMargemErro",
    "p3MargemErroPercentual",
    "p3PercentualRacial2019",
    "p3PercentualRacial2023",
    "p3DiferencaPercentualRacial",
    "reduziuDesigualdadeRacial",
    "margemDeErroDesigualdadeRacial",
    "p3PercentualSocioeconomica2019",
    "p3PercentualSocioeconomica2023",
    "p3DiferencaPercentualSocioeconomica",
    "reduziuDesigualdadeSocioeconomica",
    "margemDeErroDesigualdadeSocioeconomica",
    "habilitadoCondicionalidade",
    "habilitadoCondicionalidadeMotivo",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-pdfs",
        action="store_true",
        help="Gera apenas artefatos de revisão da P03, sem PDFs completos.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita a quantidade de representantes processados, útil para smoke tests.",
    )
    parser.add_argument(
        "--keep-chart-files",
        action="store_true",
        help="Preserva os SVGs temporários dos charts ao gerar os PDFs.",
    )
    return parser.parse_args()


def sanitize_path_component(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9_ -]+", " ", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "sem_nome"


def _fmt_decimal(value: Any, digits: int = 4) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return f"{value:.{digits}f}"
    return str(value)


def _sanitize_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_json_value(item) for item in value]
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()
    return value


def _to_serializable(row: dict[str, Any]) -> dict[str, Any]:
    converted = dict(row)
    converted["indicador_habilitado"] = bool(converted.get("indicador_habilitado"))
    return _sanitize_json_value(converted)


def _apply_limit(rows: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None:
        return rows
    if limit <= 0:
        return []
    return rows[:limit]


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_sanitize_json_value(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def _write_reference_files(rows: list[dict[str, Any]]) -> None:
    _write_json(OUTPUT_DIR / "representantes_por_motivo.json", rows)
    _write_csv(
        OUTPUT_DIR / "representantes_por_motivo.csv",
        rows,
        fieldnames=RAW_REFERENCE_FIELDNAMES,
    )


def _write_review_files(rows: list[dict[str, Any]]) -> None:
    _write_json(OUTPUT_DIR / "p03_revisao_por_motivo.json", rows)
    _write_csv(
        OUTPUT_DIR / "p03_revisao_por_motivo.csv",
        rows,
        fieldnames=P03_REVIEW_FIELDNAMES,
    )


def _row_to_dict(row: bigquery.table.Row) -> dict[str, Any]:
    return {key: _sanitize_json_value(row[key]) for key in row.keys()}


def _extract_first_row(
    query_data: dict[str, Any],
    query_name: str,
) -> dict[str, Any]:
    rows = query_data.get(query_name, [])
    if isinstance(rows, list) and rows:
        first = rows[0]
        if isinstance(first, dict):
            return _sanitize_json_value(first)
    return {}


def _build_review_row(
    representative: dict[str, Any],
    p3_row: dict[str, Any],
) -> dict[str, Any]:
    return _sanitize_json_value(
        {
            "anoRepresentante": representative.get("ano"),
            "cod_ibge": representative.get("cod_ibge"),
            "municipio": representative.get("municipio"),
            "uf": representative.get("uf"),
            "motivoTabela": representative.get("motivo", ""),
            "indicadorHabilitadoTabela": representative.get("indicador_habilitado"),
            "qtdMunicipiosMotivo": representative.get("qtd_municipios_motivo"),
            "indicePpiTabela": representative.get("indice_ppi", ""),
            "indiceNseTabela": representative.get("indice_nse", ""),
            "ppi2019Tabela": representative.get("ppi_2019", ""),
            "ppi2023Tabela": representative.get("ppi_2023", ""),
            "nse2019Tabela": representative.get("nse_2019", ""),
            "nse2023Tabela": representative.get("nse_2023", ""),
            "p3AnoReferencia": p3_row.get("p3AnoReferencia", ""),
            "p3GrupoMargemErro": p3_row.get("p3GrupoMargemErro", ""),
            "p3MargemErroPercentual": p3_row.get("p3MargemErroPercentual", ""),
            "p3PercentualRacial2019": p3_row.get("p3PercentualRacial2019", ""),
            "p3PercentualRacial2023": p3_row.get("p3PercentualRacial2023", ""),
            "p3DiferencaPercentualRacial": p3_row.get("p3DiferencaPercentualRacial", ""),
            "reduziuDesigualdadeRacial": p3_row.get("reduziuDesigualdadeRacial", ""),
            "margemDeErroDesigualdadeRacial": p3_row.get(
                "margemDeErroDesigualdadeRacial",
                "",
            ),
            "p3PercentualSocioeconomica2019": p3_row.get(
                "p3PercentualSocioeconomica2019",
                "",
            ),
            "p3PercentualSocioeconomica2023": p3_row.get(
                "p3PercentualSocioeconomica2023",
                "",
            ),
            "p3DiferencaPercentualSocioeconomica": p3_row.get(
                "p3DiferencaPercentualSocioeconomica",
                "",
            ),
            "reduziuDesigualdadeSocioeconomica": p3_row.get(
                "reduziuDesigualdadeSocioeconomica",
                "",
            ),
            "margemDeErroDesigualdadeSocioeconomica": p3_row.get(
                "margemDeErroDesigualdadeSocioeconomica",
                "",
            ),
            "habilitadoCondicionalidade": p3_row.get("habilitadoCondicionalidade", ""),
            "habilitadoCondicionalidadeMotivo": p3_row.get(
                "habilitadoCondicionalidadeMotivo",
                representative.get("motivo", ""),
            ),
        }
    )


def _build_payload_filename(row: dict[str, Any]) -> str:
    municipio_safe = sanitize_path_component(row["municipio"])
    return f"{row['cod_ibge']}_{municipio_safe}_{row['uf']}.json"


def _build_pdf_filename(row: dict[str, Any]) -> str:
    motivo_safe = sanitize_path_component(row["motivo"])[:70]
    municipio_safe = sanitize_path_component(row["municipio"])
    return f"{REPORT_ID}_{row['cod_ibge']}_{municipio_safe}_{row['uf']}_{motivo_safe}.pdf"


async def _load_representatives(client: bigquery.Client) -> list[dict[str, Any]]:
    query_job = client.query(REPRESENTANTES_SQL)
    rows = []
    for row in query_job.result():
        item = {
            "ano": row["ano"],
            "cod_ibge": row["cod_ibge"],
            "municipio": row["municipio"],
            "uf": row["uf"],
            "motivo": row["motivo"],
            "indicador_habilitado": row["indicador_habilitado"],
            "qtd_municipios_motivo": row["qtd_municipios_motivo"],
            "indice_ppi": _fmt_decimal(row["indice_ppi"]),
            "indice_nse": _fmt_decimal(row["indice_nse"]),
            "ppi_2019": _fmt_decimal(row["ppi_2019"]),
            "ppi_2023": _fmt_decimal(row["ppi_2023"]),
            "nse_2019": _fmt_decimal(row["nse_2019"]),
            "nse_2023": _fmt_decimal(row["nse_2023"]),
        }
        rows.append(_to_serializable(item))
    return rows


async def _load_p3_review_row(
    client: bigquery.Client,
    cod_ibge: str,
) -> dict[str, Any]:
    query_job = client.query(
        P3_QUERY_SQL,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("cod_ibge", "STRING", cod_ibge),
            ],
        ),
    )
    for row in query_job.result():
        return _row_to_dict(row)
    return {}


async def _collect_review_rows(
    client: bigquery.Client,
    rows: list[dict[str, Any]],
    *,
    skip_pdfs: bool,
    keep_chart_files: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    review_rows: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []

    report = None
    executor = None
    if not skip_pdfs:
        registry = ReportRegistry(REPORTS_DIR)
        report = registry.get(REPORT_ID)
        executor = LocalExecutor()
        PDF_DIR.mkdir(parents=True, exist_ok=True)

    for idx, row in enumerate(rows, start=1):
        params = {"cod_ibge": row["cod_ibge"]}

        if skip_pdfs:
            p3_row = await _load_p3_review_row(client, row["cod_ibge"])
        else:
            assert report is not None
            assert executor is not None
            query_data = await executor.execute_data_only(report=report, params=params)
            p3_row = _extract_first_row(query_data, "p3_condicionalidade_iii_vaar")

            filename = _build_pdf_filename(row)
            output_path = PDF_DIR / filename
            await executor.execute_with_data(
                report=report,
                data={
                    "metadata": {},
                    "params": params,
                    "queries": query_data,
                    "charts": {},
                    "template_params": {},
                },
                params=params,
                output=output_path,
                keep_chart_files=keep_chart_files,
            )
            manifest.append(
                {
                    "arquivo": filename,
                    "cod_ibge": row["cod_ibge"],
                    "municipio": row["municipio"],
                    "uf": row["uf"],
                    "motivo": row["motivo"],
                }
            )

        review_row = _build_review_row(row, p3_row)
        review_rows.append(review_row)

        payload = {
            "representante": row,
            "p3_condicionalidade_iii_vaar": p3_row,
            "revisao_p03": review_row,
        }
        _write_json(P03_PAYLOAD_DIR / _build_payload_filename(row), payload)

        status = "artefatos P03" if skip_pdfs else "artefatos P03 + PDF"
        print(
            f"[{idx:02d}/{len(rows)}] {row['municipio']}/{row['uf']} "
            f"-> {status}"
        )

    return review_rows, manifest


async def main() -> None:
    args = parse_args()
    client = bigquery.Client(project=GCP_PROJECT_ID)

    rows = await _load_representatives(client)
    rows = _apply_limit(rows, args.limit)

    _write_reference_files(rows)

    review_rows, manifest = await _collect_review_rows(
        client,
        rows,
        skip_pdfs=args.skip_pdfs,
        keep_chart_files=args.keep_chart_files,
    )
    _write_review_files(review_rows)

    if manifest:
        _write_json(OUTPUT_DIR / "manifesto_pdfs.json", manifest)

    print(f"\nRepresentantes salvos em: {OUTPUT_DIR}")
    print(f"Payloads P03 salvos em: {P03_PAYLOAD_DIR}")
    print(f"Linhas de revisão P03 geradas: {len(review_rows)}")
    if manifest:
        print(f"PDFs salvos em: {PDF_DIR}")
        print(f"PDFs gerados: {len(manifest)}")
    else:
        print("PDFs não gerados (--skip-pdfs).")


if __name__ == "__main__":
    asyncio.run(main())
