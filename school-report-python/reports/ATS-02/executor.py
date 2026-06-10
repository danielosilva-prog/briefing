"""ATS-02 Report Executor.

Custom executor for the ATS-02 budget execution report that generates
dynamic charts and renders the Typst template.
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
    "p3": ["26101"],  # MEC
    "p4": ["26290"],  # INEP
    "p5": ["26291"],  # CAPES
    "p6": ["26298"],  # FNDE
    "p7": ["26443"],  # EBSERH
}

# IPCA acumulado fixo por período
_IPCA_PERIODO1 = 19.99  # 2019-2021
_IPCA_PERIODO2 = 14.35  # 2023-2025

# SQL files for Orçamento Originário (P01)
_P1_QUERIES = [
    ("g1", "visao_geral_periodo1.sql"),
    ("g2", "visao_geral_periodo2.sql"),
    ("g3", "resultado_lei_periodo1.sql"),
    ("g4", "resultado_lei_periodo2.sql"),
    ("g5", "grupo_despesa_periodo1.sql"),
    ("g6", "grupo_despesa_periodo2.sql"),
    ("metricas", "metricas_orcamento.sql"),
]

# SQL files for Crédito Recebido por Destaque (P02+)
_CR_QUERIES = [
    ("g1", "credito_recebido_geral_p1.sql"),
    ("g2", "credito_recebido_geral_p2.sql"),
    ("g3", "credito_resultado_lei_p1.sql"),
    ("g4", "credito_resultado_lei_p2.sql"),
    ("g5", "credito_grupo_despesa_p1.sql"),
    ("g6", "credito_grupo_despesa_p2.sql"),
    ("metricas", "metricas_credito_recebido.sql"),
]

# Graph pairs that should share Y-axis
_GRAPH_PAIRS = [("g1", "g2"), ("g3", "g4"), ("g5", "g6")]


class ATS02Executor:
    """Executor for the ATS-02 budget execution report."""

    def __init__(self, reports_dir: Path):
        self.report_dir = reports_dir / "ATS-02"
        self.template_path = self.report_dir / "template" / "main.typ"
        self.assets_dir = self.report_dir / "template" / "assets"
        self.queries_dir = self.report_dir / "queries"

        if not self.report_dir.exists():
            raise ValueError(f"ATS-02 report directory not found: {self.report_dir}")
        if not self.template_path.exists():
            raise ValueError(f"Template not found: {self.template_path}")

        settings = get_local_settings()
        self._bq = BigQueryClient(project_id=settings.gcp_project_id)
        self._typst = TypstClient()
        self._cache = get_query_cache(ttl_seconds=3600)
        self._semaphore = asyncio.Semaphore(8)
        self.chart_loader = ChartLoader()
        self.chart_generator = ChartGenerator()

    async def execute(self, data: Dict[str, Any]) -> bytes:
        """Generate the ATS-02 PDF report.

        Args:
            data: Input data containing metadata, params, and budget_data

        Returns:
            PDF bytes
        """
        logger.info("Starting ATS-02 report generation")
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
        if "metadata" not in data:
            raise ValueError("Missing required field: metadata")
        if "params" not in data:
            raise ValueError("Missing required field: params")

    # ─── BigQuery Integration ──────────────────────────────────────────────────

    async def _enrich_with_bigquery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch chart data and metrics from BigQuery in parallel."""
        chart_data: Dict[str, List[Dict]] = {}
        template_params: Dict[str, str] = dict(data.get("template_params", {}))

        # Resolve institution filter
        institution_filter = await self._resolve_institution_filter(data)

        # Build query tasks: (key, sql_file, params)
        tasks: List[tuple] = []

        # P01: Orçamento Originário
        p1_params = {"id_uo_list": institution_filter or []}
        for suffix, sql_file in _P1_QUERIES:
            tasks.append((f"p1_{suffix}", sql_file, p1_params))

        # P02-P07: Crédito Recebido por Destaque
        for page_prefix, uo_list in _UO_BY_PAGE.items():
            params = {
                "id_uo_list": uo_list,
                "id_orgao_uge_list": institution_filter or [],
            }
            for suffix, sql_file in _CR_QUERIES:
                tasks.append((f"{page_prefix}_{suffix}", sql_file, params))

        # CAPES extra: Auxílios Financeiros (same filters as P05)
        capes_params = {
            "id_uo_list": ["26291"],
            "id_orgao_uge_list": institution_filter or [],
        }
        tasks.append(("p5_g_aux", "capes_auxilios_financeiros.sql", capes_params))

        # Execute all queries in parallel
        logger.info(f"Executing {len(tasks)} BigQuery queries in parallel (semaphore=8)...")
        coroutines = [
            self._run_query(sql_file, params) for _, sql_file, params in tasks
        ]
        all_results = await asyncio.gather(*coroutines)

        for (key, _, _), result in zip(tasks, all_results):
            chart_data[key] = result
            logger.info(f"chart_data['{key}'] = {len(result)} rows")

        # Compute metrics from P01 time-series data
        df_metrics_p1 = pd.DataFrame(chart_data.pop("p1_metricas", []))
        p1_metrics = self._compute_metrics(
            df_metrics_p1, "despesa_empenhada", "p1Orcamento", "p1"
        )
        template_params.update(p1_metrics)

        # Compute metrics for P02-P07
        for page_prefix in _UO_BY_PAGE:
            df_metrics = pd.DataFrame(chart_data.pop(f"{page_prefix}_metricas", []))
            cr_metrics = self._compute_metrics(
                df_metrics,
                "despesa_empenhada",
                f"{page_prefix}CreditoRecebido",
                page_prefix,
            )
            template_params.update(cr_metrics)

        # Shared Y-axis limits
        shared_ylims = self._compute_shared_ylims(chart_data, page_range=range(1, 8))
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
            noun_prefix: Prefix for Acumulado keys (e.g. 'p1Orcamento')
            page_prefix: Prefix for Percent/Incremento keys (e.g. 'p1')

        Returns:
            Dict mapping template param names → formatted string values.
        """
        if df.empty or value_col not in df.columns or "ano" not in df.columns:
            logger.warning(
                f"_compute_metrics({noun_prefix}) received empty/invalid DataFrame"
            )
            return {}

        df = df.copy()
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce").fillna(0)

        def _get_year(year: int) -> float:
            row = df[df["ano"] == year]
            return float(row[value_col].iloc[0]) if not row.empty else 0.0

        # Acumulados
        acc1 = sum(_get_year(y) for y in [2019, 2020, 2021])
        acc2 = sum(_get_year(y) for y in [2023, 2024, 2025])

        # Variações dentro de cada período
        v2019, v2021 = _get_year(2019), _get_year(2021)
        v2023, v2025 = _get_year(2023), _get_year(2025)
        pct_var1 = ((v2021 - v2019) / v2019 * 100) if v2019 > 0 else 0.0
        pct_var2 = ((v2025 - v2023) / v2023 * 100) if v2023 > 0 else 0.0

        # Incremento entre períodos
        incremento = acc2 - acc1
        pct_incremento = (incremento / acc1 * 100) if acc1 > 0 else 0.0

        return {
            f"{noun_prefix}MedioPeriodo1": fmt_brl(acc1 / 3),
            f"{noun_prefix}AcumuladoPeriodo1": fmt_brl(acc1),
            f"{page_prefix}PercentVariacaoOrcamentoPeriodo1": fmt_pct(pct_var1),
            f"{page_prefix}PercentIPCAPeriodo1": fmt_pct(_IPCA_PERIODO1),
            f"{noun_prefix}MedioPeriodo2": fmt_brl(acc2 / 3),
            f"{noun_prefix}AcumuladoPeriodo2": fmt_brl(acc2),
            f"{page_prefix}IncrementoOrcamentario": fmt_brl(incremento),
            f"{page_prefix}PercentVariacaoOrcamentoPeriodo2": fmt_pct(pct_var2),
            f"{page_prefix}PercentIPCAPeriodo2": fmt_pct(_IPCA_PERIODO2),
            f"{page_prefix}PercentIncrementoOrcamentario": fmt_pct(pct_incremento),
        }

    # ─── Shared Y-axis ────────────────────────────────────────────────────────

    def _compute_shared_ylims(
        self,
        chart_data: Dict[str, List[Dict]],
        page_range: range,
    ) -> Dict[str, float]:
        """Compute shared Y-axis limits for chart pairs across pages."""
        shared_ylims: Dict[str, float] = {}

        for page_num in page_range:
            pp = f"p{page_num}"
            for ga, gb in _GRAPH_PAIRS:
                df1 = pd.DataFrame(chart_data.get(f"{pp}_{ga}", []))
                df2 = pd.DataFrame(chart_data.get(f"{pp}_{gb}", []))
                max_val = max(
                    self._get_max_numeric_value(df1),
                    self._get_max_numeric_value(df2),
                )
                if max_val > 0:
                    shared_ylims[f"{pp}_{ga}_{gb}"] = max_val * 1.12

        return shared_ylims

    @staticmethod
    def _get_max_numeric_value(df: pd.DataFrame) -> float:
        """Extract the maximum numeric value from a chart DataFrame."""
        if df.empty or df.shape[1] <= 1:
            return 0.0
        numeric_df = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0)
        return float(numeric_df.max().max())

    # ─── Chart Generation ─────────────────────────────────────────────────────

    async def _generate_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Generate charts using the framework engine + @chart decorators."""
        budget_data = data.get("budget_data", {})
        data_map = self._build_chart_data_map(budget_data)
        registry = self.chart_loader.load(self.report_dir, "ATS-02")

        if len(registry) == 0:
            logger.warning("No charts registered in reports/ATS-02/charts.py")
            return {}

        # Only generate charts for which we have data
        filtered_registry = ChartRegistry("ATS-02")
        for chart_name in data_map.keys():
            chart_fn = registry.get(chart_name)
            if chart_fn is not None:
                filtered_registry.register(chart_name, chart_fn.func, chart_fn.metadata)

        if len(filtered_registry) == 0:
            logger.info("No matching chart datasets found; using static/mock chart assets")
            return {}

        params = dict(data.get("params", {}))
        params["shared_ylims"] = data.get("shared_ylims", {})

        return await self.chart_generator.generate_many(
            charts=[],
            data_map=data_map,
            chart_registry=filtered_registry,
            report_id="ATS-02",
            params=params,
            assets_dir=self.assets_dir,
        )

    @staticmethod
    def _build_chart_data_map(budget_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Convert budget_data.chart_data payload into data_map for chart engine."""
        chart_data = budget_data.get("chart_data", {})
        if not isinstance(chart_data, dict):
            return {}

        data_map: Dict[str, pd.DataFrame] = {}
        for name, payload in chart_data.items():
            try:
                if isinstance(payload, list):
                    data_map[name] = pd.DataFrame(payload)
                elif isinstance(payload, dict):
                    if payload and all(isinstance(v, list) for v in payload.values()):
                        data_map[name] = pd.DataFrame(payload)
                    else:
                        data_map[name] = pd.DataFrame([payload])
                else:
                    data_map[name] = pd.DataFrame()
            except Exception as exc:
                logger.warning(f"Failed to parse chart dataset '{name}': {exc}")
                data_map[name] = pd.DataFrame()
        return data_map


# Convenience function for standalone usage
async def generate_ats02_report(
    data: Dict[str, Any],
    reports_dir: Optional[Path] = None,
) -> bytes:
    """Generate an ATS-02 report."""
    if reports_dir is None:
        reports_dir = Path(__file__).parent.parent
    executor = ATS02Executor(reports_dir)
    return await executor.execute(data)
