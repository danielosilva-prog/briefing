"""ATS-ORC-R Report Executor.

Custom executor for the ATS-ORC-R budget execution report (resumo com P01 e P02)
that generates dynamic charts and renders the Typst template.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from schoolreport.config import get_local_settings
from schoolreport.core.bigquery import BigQueryClient
from schoolreport.core.chart_assets import (
    ensure_placeholder_charts,
    write_charts_to_assets,
)
from schoolreport.core.formatting import fmt_brl, fmt_pct
from schoolreport.core.query_cache import get_query_cache
from schoolreport.core.typst import TypstClient
from schoolreport.rendering.chart_framework import ChartLoader, ChartRegistry
from schoolreport.rendering.charts import ChartGenerator

logger = logging.getLogger(__name__)

# UO filters per page
_UO_BY_PAGE = {
    "p2": ["26101", "26290", "26291", "26298", "26443"],  # Geral
}

# IPCA acumulado fixo por período
_IPCA_PERIODO1 = 26.94   # 2019-2022
_IPCA_PERIODO2 = 19.49   # 2023-2026

# P01: Créditos Totais = UO + Destaque (7 queries)
_CT_QUERIES = [
    ("g1", "creditos_totais_chart_p1.sql"),
    ("g2", "creditos_totais_chart_p2.sql"),
    ("g3", "creditos_totais_resultado_lei_p1.sql"),
    ("g4", "creditos_totais_resultado_lei_p2.sql"),
    ("g5", "creditos_totais_grupo_despesa_p1.sql"),
    ("g6", "creditos_totais_grupo_despesa_p2.sql"),
    ("metricas", "metricas_creditos_totais.sql"),
]

# P02: Orçamento Geral (UO/LOA apenas)
_UO_QUERIES = [
    ("g1", "visao_geral_periodo1.sql"),
    ("g2", "visao_geral_periodo2.sql"),
    ("metricas", "metricas_orcamento.sql"),
]

# P02 CE: Créditos Extraorçamentários (destaque apenas)
_CE_QUERIES = [
    ("g3", "credito_recebido_geral_p1.sql"),
    ("g4", "credito_recebido_geral_p2.sql"),
    ("metricas", "metricas_credito_recebido.sql"),
]


class ATSOrcRExecutor:
    """Executor for the ATS-ORC-R budget execution report (P01 + P02 only)."""

    def __init__(self, reports_dir: Path):
        """Initialize executor.

        Args:
            reports_dir: Path to the reports directory
        """
        self.report_dir = reports_dir / "ATS-ORC-R"
        self.template_path = self.report_dir / "template" / "main.typ"
        self.assets_dir = self.report_dir / "template" / "assets"
        self.queries_dir = self.report_dir / "queries"

        # Validate paths
        if not self.report_dir.exists():
            raise ValueError(f"ATS-ORC-R report directory not found: {self.report_dir}")
        if not self.template_path.exists():
            raise ValueError(f"Template not found: {self.template_path}")

        settings = get_local_settings()
        self._bq = BigQueryClient(project_id=settings.gcp_project_id)
        self._typst = TypstClient()
        self._cache = get_query_cache(ttl_seconds=3600)  # 1h
        self._semaphore = asyncio.Semaphore(8)
        self.chart_loader = ChartLoader()
        self.chart_generator = ChartGenerator()

    async def execute(self, data: Dict[str, Any]) -> bytes:
        """Generate the ATS-ORC-R PDF report.

        Args:
            data: Input data containing metadata, params, and budget_data

        Returns:
            PDF bytes

        Raises:
            ValueError: If required data is missing
            RuntimeError: If chart generation or PDF rendering fails
        """
        logger.info("Starting ATS-ORC-R report generation")
        self._validate_input(data)

        # 1. BigQuery enrichment
        if data.get("params", {}).get("use_bigquery", False):
            logger.info("BigQuery mode: fetching real data...")
            data = await self._enrich_with_bigquery(data)

        # 2. Charts
        logger.info("Generating charts...")
        charts = await self._generate_charts(data)
        logger.info(f"Generated {len(charts)} charts")
        generated = write_charts_to_assets(charts, self.assets_dir)
        ensure_placeholder_charts(
            self.report_dir / "template" / "pages", self.assets_dir, generated
        )

        # 3. Template data
        template_data = {
            "metadata": data.get("metadata", {}),
            "params": data.get("params", {}),
            "queries": data.get("queries", {}),
            "charts": charts,
        }
        if data.get("template_params"):
            template_data["template_params"] = data["template_params"]

        # 4. Render
        logger.info("Rendering PDF with Typst...")
        pdf_bytes = await self._typst.render_to_bytes(self.template_path, template_data)
        logger.info(f"PDF generated: {len(pdf_bytes)} bytes")

        return pdf_bytes

    def _validate_input(self, data: Dict[str, Any]) -> None:
        """Validate input data structure."""
        if "metadata" not in data:
            raise ValueError("Missing required field: metadata")
        if "params" not in data:
            raise ValueError("Missing required field: params")

    # ─── BigQuery Integration ──────────────────────────────────────────────────

    async def _enrich_with_bigquery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch all chart data and metrics from BigQuery in parallel."""
        chart_data: Dict[str, List[Dict]] = {}
        template_params: Dict[str, str] = dict(data.get("template_params", {}))

        # Resolve institution filter
        institution_filter = await self._resolve_institution_filter(data)

        # Caso Brasil: sem filtro de instituição → forçar sigla no template
        if institution_filter is None and not data.get("params", {}).get("sigla"):
            template_params["sigla"] = "Brasil"

        # Build query tasks: (key, sql_file, params)
        tasks: List[tuple] = []

        # P01: Créditos Totais = UO + Destaque (7 queries)
        _MEC_UOS = _UO_BY_PAGE["p2"]
        ct_params = {
            "id_uo_list": institution_filter if institution_filter else [],
            "id_uo_list_source": _MEC_UOS,
        }
        for suffix, sql_file in _CT_QUERIES:
            tasks.append((f"p1_{suffix}", sql_file, ct_params))

        # P02: Orçamento Geral (UO/LOA apenas) — G1/G2 + metricas
        uo_params = {"id_uo_list": institution_filter if institution_filter else []}
        for suffix, sql_file in _UO_QUERIES:
            tasks.append((f"p2_{suffix}", sql_file, uo_params))

        # P02 CE: Créditos Extraorçamentários (destaque apenas)
        cr_params = {
            "id_uo_list": _MEC_UOS,
            "id_orgao_uge_list": institution_filter if institution_filter else [],
        }
        tasks.append(("p2_ce_metricas", "metricas_credito_recebido.sql", cr_params))

        # P02 CE: Gráficos G3/G4
        for suffix, sql_file in [("g3", "credito_recebido_geral_p1.sql"), ("g4", "credito_recebido_geral_p2.sql")]:
            tasks.append((f"p2_{suffix}", sql_file, cr_params))

        # Execute all queries in parallel
        logger.info(f"Executing {len(tasks)} BigQuery queries in parallel (semaphore=8)...")
        coroutines = [
            self._run_query(sql_file, params) for _, sql_file, params in tasks
        ]
        all_results = await asyncio.gather(*coroutines)

        cache_stats = self._cache.stats()
        logger.info(
            f"Queries complete: {len(tasks)} total, "
            f"cache hits={cache_stats['hits']}, misses={cache_stats['misses']}"
        )

        for (key, _, _), result in zip(tasks, all_results):
            chart_data[key] = result
            logger.info(f"chart_data['{key}'] = {len(result) if isinstance(result, list) else 'not-a-list'} rows")
            if result and isinstance(result, list) and len(result) > 0:
                logger.debug(f"  First row: {result[0]}")

        # ── Compute metrics from results ─────────────────────────────────────────
        # P01 — Créditos Totais (UO + Destaque)
        df_metrics_p1 = pd.DataFrame(chart_data.pop("p1_metricas", []))
        template_params.update(self._compute_metrics(
            df_metrics_p1, "creditos_totais",
            noun_prefix="p1Orcamento", page_prefix="p1"
        ))

        # P02 — Orçamento Geral (UO/LOA apenas)
        df_metrics_p2 = pd.DataFrame(chart_data.pop("p2_metricas", []))
        template_params.update(self._compute_metrics(
            df_metrics_p2, "valor",
            noun_prefix="p2CreditoRecebido", page_prefix="p2"
        ))

        # P02 CE — Créditos Extraorçamentários (destaque apenas)
        df_metrics_ce = pd.DataFrame(chart_data.pop("p2_ce_metricas", []))
        template_params.update(self._compute_metrics(
            df_metrics_ce, "valor",
            noun_prefix="p2CECreditoRecebido", page_prefix="p2CE"
        ))

        # Shared Y-axis limits
        shared_ylims = self._compute_shared_ylims(chart_data, page_range=range(1, 3))
        logger.info(f"Computed {len(shared_ylims)} shared Y-axis limits")

        data = dict(data)
        data["budget_data"] = {"chart_data": chart_data}
        data["template_params"] = template_params
        data["shared_ylims"] = shared_ylims
        return data

    async def _resolve_institution_filter(
        self, data: Dict[str, Any]
    ) -> Optional[List[str]]:
        """Resolve sigla/id_uo params into an institution filter list."""
        id_uo = data.get("params", {}).get("id_uo", "")
        sigla = data.get("params", {}).get("sigla", "")

        if sigla and not id_uo:
            logger.info(f"Resolving sigla '{sigla}' to id_uo...")
            rows = await self._run_query("id_uo_by_sigla.sql", {"sigla": sigla})
            if rows:
                id_uo = str(rows[0].get("id_unidade_orcamentaria", ""))
                universidade = rows[0].get("nome_universidade", id_uo)
                logger.info(f"Resolved sigla '{sigla}' → id_uo '{id_uo}' ({universidade})")
                data = dict(data)
                data["metadata"] = {**data.get("metadata", {}), "universidade": universidade}
            else:
                logger.warning(f"Could not resolve sigla '{sigla}' to id_uo")

        if id_uo:
            logger.info(f"Filtering all queries to institution: [{id_uo}]")
            universidade = data.get("metadata", {}).get("universidade", "")
            if not universidade or universidade == id_uo:
                rows = await self._run_query(
                    "universidade_by_sigla.sql",
                    {"id_unidade_orcamentaria": int(id_uo)},
                )
                if rows:
                    data = dict(data)
                    data["metadata"] = {
                        **data.get("metadata", {}),
                        "universidade": rows[0].get("nome_universidade", id_uo),
                    }
            return [str(id_uo)]

        return None

    def _load_query(self, filename: str) -> str:
        """Load SQL query from queries directory."""
        query_path = self.queries_dir / filename
        if not query_path.exists():
            raise FileNotFoundError(f"Query file not found: {query_path}")
        return query_path.read_text(encoding="utf-8")

    async def _run_query(
        self, sql_file: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """Execute a BigQuery query with caching and concurrency control."""
        sql = self._load_query(sql_file)

        cached = self._cache.get(sql, params)
        if cached is not None:
            return cached

        async with self._semaphore:
            try:
                rows = await self._bq.execute_query_as_dicts(sql, params)
                logger.info(f"BigQuery returned {len(rows)} rows for {sql_file}")
                self._cache.set(sql, params, rows)
                return rows
            except Exception as exc:
                logger.error(f"BigQuery query failed ({sql_file}): {exc}")
                return []

    # ─── Metrics ───────────────────────────────────────────────────────────────

    def _compute_metrics(
        self,
        df: pd.DataFrame,
        value_col: str,
        noun_prefix: str,
        page_prefix: str,
    ) -> Dict[str, str]:
        """Compute KPI metrics from a time-series DataFrame.

        Args:
            df: DataFrame with columns [ano, <value_col>]
            value_col: Name of the numeric value column
            noun_prefix: Prefix for Acumulado keys (e.g. 'p1Orcamento', 'p2CreditoRecebido')
            page_prefix: Prefix for Percent/Incremento keys (e.g. 'p1', 'p2')

        Returns:
            Dict mapping template param names → formatted string values, matching
            exactly the parameter names expected by typst-template.typ Article().
        """
        if df.empty or value_col not in df.columns or "ano" not in df.columns:
            logger.warning(
                f"_compute_metrics({noun_prefix}) received empty/invalid DataFrame: "
                f"empty={df.empty}, columns={df.columns.tolist() if not df.empty else []}"
            )
            return {}

        logger.info(f"_compute_metrics({noun_prefix}) processing DataFrame with {len(df)} rows")

        df = df.copy()
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)

        def _get_year(year: int) -> float:
            row = df[df["ano"] == year]
            return float(row[value_col].iloc[0]) if not row.empty else 0.0

        # Acumulados (4-year periods)
        acc1 = sum(_get_year(y) for y in [2019, 2020, 2021, 2022])
        acc2 = sum(_get_year(y) for y in [2023, 2024, 2025, 2026])

        # Variações dentro de cada período
        v2019, v2022 = _get_year(2019), _get_year(2022)
        v2023, v2026 = _get_year(2023), _get_year(2026)
        pct_var1 = ((v2022 - v2019) / v2019 * 100) if v2019 > 0 else 0.0
        pct_var2 = ((v2026 - v2023) / v2023 * 100) if v2023 > 0 else 0.0

        # Incremento entre períodos
        incremento = acc2 - acc1
        pct_incremento = (incremento / acc1 * 100) if acc1 > 0 else 0.0

        return {
            f"{noun_prefix}MedioPeriodo1": fmt_brl(acc1 / 4),
            f"{noun_prefix}AcumuladoPeriodo1": fmt_brl(acc1),
            f"{page_prefix}PercentVariacaoOrcamentoPeriodo1": fmt_pct(pct_var1),
            f"{page_prefix}PercentIPCAPeriodo1": fmt_pct(_IPCA_PERIODO1),
            f"{noun_prefix}MedioPeriodo2": fmt_brl(acc2 / 4),
            f"{noun_prefix}AcumuladoPeriodo2": fmt_brl(acc2),
            f"{page_prefix}IncrementoOrcamentario": fmt_brl(incremento),
            f"{page_prefix}PercentVariacaoOrcamentoPeriodo2": fmt_pct(pct_var2),
            f"{page_prefix}PercentIPCAPeriodo2": fmt_pct(_IPCA_PERIODO2),
            f"{page_prefix}PercentIncrementoOrcamentario": fmt_pct(pct_incremento),
        }

    def _compute_shared_ylims(
        self,
        chart_data: Dict[str, List[Dict]],
        page_range: range = range(1, 3),
    ) -> Dict[str, float]:
        """Calculates shared Y-axis limits for pairs of charts.

        For each pair (G1/G2, G3/G4, G5/G6) in each page, finds the
        maximum value between the two periods to ensure consistent visual scale.
        """
        shared_ylims = {}

        GRAPH_PAIRS = [
            ("g1", "g2"),
            ("g3", "g4"),
            ("g5", "g6"),
        ]

        for page_num in page_range:
            page_prefix = f"p{page_num}"
            for g_pair in GRAPH_PAIRS:
                g1_key = f"{page_prefix}_{g_pair[0]}"
                g2_key = f"{page_prefix}_{g_pair[1]}"
                pair_key = f"{page_prefix}_{g_pair[0]}_{g_pair[1]}"

                df1 = pd.DataFrame(chart_data.get(g1_key, []))
                df2 = pd.DataFrame(chart_data.get(g2_key, []))

                max1 = self._get_max_numeric_value(df1)
                max2 = self._get_max_numeric_value(df2)

                max_value = max(max1, max2)
                if max_value > 0:
                    shared_ylims[pair_key] = max_value * 1.12

        return shared_ylims

    def _get_max_numeric_value(self, df: pd.DataFrame) -> float:
        """Extract the maximum row sum from a chart DataFrame.

        For stacked bar charts, the relevant scale is the total bar height
        (sum of all series per row), not the max individual column value.
        """
        if df.empty:
            return 0.0
        if df.shape[1] <= 1:
            return 0.0
        numeric_df = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').fillna(0)
        return float(numeric_df.sum(axis=1).max())

    # ─── Chart Generation ─────────────────────────────────────────────────────

    async def _generate_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate charts using the framework engine + @chart decorators."""
        budget_data = data.get("budget_data", {})
        data_map = self._build_chart_data_map(budget_data)
        registry = self.chart_loader.load(self.report_dir, "ATS-ORC-R")

        if len(registry) == 0:
            logger.warning("No charts registered in reports/ATS-ORC-R/charts.py")
            return {}

        # Generate only charts with provided datasets
        filtered_registry = ChartRegistry("ATS-ORC-R")
        for chart_name in data_map.keys():
            chart_fn = registry.get(chart_name)
            if chart_fn is None:
                continue
            filtered_registry.register(chart_name, chart_fn.func, chart_fn.metadata)

        if len(filtered_registry) == 0:
            logger.info("No matching chart datasets found; using static/mock chart assets")
            return {}

        # Add shared_ylims to params
        params = dict(data.get("params", {}))
        params["shared_ylims"] = data.get("shared_ylims", {})

        return await self.chart_generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=filtered_registry,
            report_id="ATS-ORC-R",
            params=params,
            assets_dir=self.assets_dir,
        )

    def _build_chart_data_map(self, budget_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Convert budget_data.chart_data payload into data_map for chart engine."""
        chart_data = budget_data.get("chart_data", {})
        if not isinstance(chart_data, dict):
            return {}

        data_map: Dict[str, pd.DataFrame] = {}
        for dataset_name, payload in chart_data.items():
            try:
                if isinstance(payload, list):
                    data_map[dataset_name] = pd.DataFrame(payload)
                elif isinstance(payload, dict):
                    if payload and all(isinstance(v, list) for v in payload.values()):
                        data_map[dataset_name] = pd.DataFrame(payload)
                    else:
                        data_map[dataset_name] = pd.DataFrame([payload])
                else:
                    data_map[dataset_name] = pd.DataFrame()
            except Exception as exc:
                logger.warning(f"Failed to parse chart dataset '{dataset_name}': {exc}")
                data_map[dataset_name] = pd.DataFrame()
        return data_map


# Convenience function for standalone usage
async def generate_ats_orc_r_report(
    data: Dict[str, Any],
    reports_dir: Optional[Path] = None,
) -> bytes:
    """Generate an ATS-ORC-R report.

    Args:
        data: Input data
        reports_dir: Path to reports directory (defaults to ../reports)

    Returns:
        PDF bytes
    """
    if reports_dir is None:
        reports_dir = Path(__file__).parent.parent

    executor = ATSOrcRExecutor(reports_dir)
    return await executor.execute(data)
