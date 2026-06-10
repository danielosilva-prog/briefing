"""Materializa tabelas derivadas do INEP censo para o ATM-EQ.

Uso:
    uv run python reports/ATM-EQ/scripts/materialize_inep_censo_derived_tables.py
"""

from __future__ import annotations

from pathlib import Path

from google.cloud import bigquery


ROOT_DIR = Path(__file__).resolve().parents[3]
SQL_DIR = ROOT_DIR / "reports" / "ATM-EQ" / "scripts"
JOB_PROJECT = "br-mec-segape-sandbox"

SQL_FILES = [
    "atm_eq_grafico_distribuicao_matriculas.sql",
    "atm_eq_grafico_atendimento_creche_pre_escola.sql",
    "atm_eq_tabela_infraestrutura_basica.sql",
]


def run_query_file(client: bigquery.Client, sql_path: Path) -> None:
    print(f"Materializando {sql_path.name}...")
    query = sql_path.read_text(encoding="utf-8")
    job = client.query(query)
    job.result()
    print(f"Concluido: {sql_path.name}")


def main() -> None:
    client = bigquery.Client(project=JOB_PROJECT)
    for filename in SQL_FILES:
        run_query_file(client, SQL_DIR / filename)


if __name__ == "__main__":
    main()
