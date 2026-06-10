"""Local executor for CLI - no queue, no database."""

import asyncio
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import pandas as pd
from rich.progress import Progress

from schoolreport.config import get_local_settings
from schoolreport.core.bigquery import BigQueryClient
from schoolreport.core.query_cache import QueryCache
from schoolreport.core.storage import GCSClient
from schoolreport.core.typst import TypstRenderer
from schoolreport.models.report import Query, ReportDefinition, SourceType
from schoolreport.rendering.chart_framework import ChartLoader, ChartRegistry
from schoolreport.rendering.charts import ChartGenerator

logger = logging.getLogger(__name__)


def discover_custom_executor(report_dir: Path) -> Optional[Type]:
    """Discover a custom executor class in a report's executor.py file.

    Looks for a file named ``executor.py`` inside *report_dir* and returns the
    first class whose name ends with ``Executor`` (excluding any base classes
    from schoolreport itself).

    Args:
        report_dir: Path to the report directory (e.g. ``reports/ATS-02``).

    Returns:
        The executor class, or ``None`` if no custom executor is found.
    """
    executor_path = report_dir / "executor.py"
    if not executor_path.exists():
        return None

    spec = importlib.util.spec_from_file_location(
        f"_executor_{report_dir.name}", executor_path
    )
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for name, obj in inspect.getmembers(module, inspect.isclass):
        if name.endswith("Executor") and obj.__module__ == module.__name__:
            return obj

    return None


class LocalExecutorError(Exception):
    """Raised when local execution fails."""
    pass


class LocalExecutor:
    """
    Simplified executor for CLI - no queue, no database.

    This executor runs report generation directly without:
    - Redis/arq queue
    - PostgreSQL for audit logs
    - PostgreSQL for caching

    It's designed for local development and testing.
    Only requires GCP_PROJECT_ID environment variable for BigQuery access.
    """

    def __init__(
        self,
        gcp_project_id: Optional[str] = None,
        max_concurrency: Optional[int] = None,
        cache_enabled: Optional[bool] = None,
        cache_ttl_seconds: Optional[int] = None,
    ):
        """Initialize the local executor.

        Args:
            gcp_project_id: Optional GCP project ID override. If not provided,
                           will be read from GCP_PROJECT_ID environment variable.
            max_concurrency: Maximum concurrent BigQuery queries. Defaults to 10.
            cache_enabled: Enable query result caching. Defaults to True.
            cache_ttl_seconds: Cache TTL in seconds. Defaults to 3600 (1 hour).
        """
        self._gcp_project_id = gcp_project_id
        self._bigquery_client: Optional[BigQueryClient] = None
        self._chart_generator: Optional[ChartGenerator] = None
        self._typst_renderer: Optional[TypstRenderer] = None
        self._gcs_client: Optional[GCSClient] = None
        self._chart_loader = ChartLoader()
        self._chart_registries: Dict[str, ChartRegistry] = {}

        # Load settings for defaults
        settings = get_local_settings()

        # Query concurrency control
        concurrency = max_concurrency or settings.query_max_concurrency
        self._query_semaphore = asyncio.Semaphore(concurrency)
        self._max_concurrency = concurrency

        # Query result cache
        cache_dir = Path(settings.query_cache_dir) if settings.query_cache_dir else None
        self._query_cache = QueryCache(
            cache_dir=cache_dir,
            ttl_seconds=cache_ttl_seconds or settings.query_cache_ttl_seconds,
            enabled=cache_enabled if cache_enabled is not None else settings.query_cache_enabled,
        )

    @property
    def bigquery_client(self) -> BigQueryClient:
        """Lazy-load BigQuery client."""
        if self._bigquery_client is None:
            project_id = self._gcp_project_id or get_local_settings().gcp_project_id
            self._bigquery_client = BigQueryClient(project_id=project_id)
        return self._bigquery_client

    @property
    def chart_generator(self) -> ChartGenerator:
        """Lazy-load chart generator."""
        if self._chart_generator is None:
            self._chart_generator = ChartGenerator()
        return self._chart_generator

    @property
    def typst_renderer(self) -> TypstRenderer:
        """Lazy-load Typst renderer."""
        if self._typst_renderer is None:
            self._typst_renderer = TypstRenderer()
        return self._typst_renderer

    @property
    def gcs_client(self) -> GCSClient:
        """Lazy-load GCS client.

        Raises:
            LocalExecutorError: If GCS_BUCKET_NAME is not configured.
        """
        if self._gcs_client is None:
            settings = get_local_settings()
            if not settings.gcs_bucket_name:
                raise LocalExecutorError(
                    "GCS upload requires GCS_BUCKET_NAME environment variable. "
                    "Set it or omit the --upload flag to save locally only."
                )
            self._gcs_client = GCSClient(bucket_name=settings.gcs_bucket_name)
        return self._gcs_client

    def get_chart_registry(self, report: ReportDefinition) -> Optional[ChartRegistry]:
        """Get or load chart registry for a report.

        Args:
            report: Report definition

        Returns:
            ChartRegistry if charts.py exists, None otherwise
        """
        report_dir = getattr(report, "_report_dir", None)
        if report_dir is None:
            return None

        # Check cache
        if report.id in self._chart_registries:
            return self._chart_registries[report.id]

        # Load chart module
        registry = self._chart_loader.load(report_dir, report.id)
        self._chart_registries[report.id] = registry
        return registry

    async def _execute_pipeline(
        self,
        report: ReportDefinition,
        params: Dict[str, Any],
        progress: Optional[Progress] = None,
    ) -> tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        Execute queries and charts in a parallel pipeline.

        Each chart starts generating as soon as its dependency query finishes,
        rather than waiting for all queries to complete first.

        Args:
            report: Report definition
            params: Report parameters
            progress: Optional Rich progress instance

        Returns:
            Tuple of (query_results, chart_results)
        """
        report_dir = getattr(report, "_report_dir", None)
        chart_registry = self.get_chart_registry(report)

        # --- Build chart list (custom + YAML) ---
        charts_to_generate: List[tuple[str, bool]] = []  # (name, is_custom)
        if chart_registry:
            for name in chart_registry.list():
                charts_to_generate.append((name, True))
        custom_names = {name for name, _ in charts_to_generate}
        for chart in report.charts:
            if chart.name not in custom_names:
                charts_to_generate.append((chart.name, False))

        yaml_charts = {chart.name: chart for chart in report.charts}

        # --- Build dependency map: chart_name -> list of query names ---
        def _get_data_spec(chart_name: str, is_custom: bool) -> Union[str, List[str], None]:
            if is_custom and chart_registry:
                chart_fn = chart_registry.get(chart_name)
                return chart_fn.metadata.data if chart_fn else None
            else:
                chart_def = yaml_charts.get(chart_name)
                return chart_def.data if chart_def else None

        # --- Asyncio events: one per query ---
        query_events: Dict[str, asyncio.Event] = {
            q.name: asyncio.Event() for q in report.queries
        }
        query_results: Dict[str, pd.DataFrame] = {}
        chart_results: Dict[str, str] = {}

        # --- Progress tracking ---
        n_queries = len(report.queries)
        n_charts = len(charts_to_generate)
        queries_done = 0
        charts_done = 0

        query_progress_task = None
        chart_progress_task = None
        if progress:
            if n_queries > 0:
                query_progress_task = progress.add_task(
                    f"Queries: 0/{n_queries}",
                    total=n_queries,
                )
            if n_charts > 0:
                chart_progress_task = progress.add_task(
                    f"Charts: 0/{n_charts}",
                    total=n_charts,
                )

        def _advance_query():
            nonlocal queries_done
            queries_done += 1
            if progress and query_progress_task is not None:
                progress.update(
                    query_progress_task,
                    advance=1,
                    description=f"Queries: {queries_done}/{n_queries}",
                )

        def _advance_chart():
            nonlocal charts_done
            charts_done += 1
            if progress and chart_progress_task is not None:
                progress.update(
                    chart_progress_task,
                    advance=1,
                    description=f"Charts: {charts_done}/{n_charts}",
                )

        # --- Query tasks ---
        async def _run_query_task(query: Query):
            try:
                name, df = await self._run_single_query(query, params, report_dir)
                query_results[name] = df
            finally:
                # Always set the event so chart tasks don't hang forever
                query_events[query.name].set()
            _advance_query()

        # --- Chart tasks ---
        async def _run_chart_task(chart_name: str, is_custom: bool):
            data_spec = _get_data_spec(chart_name, is_custom)

            # Wait for required queries
            if isinstance(data_spec, str):
                if data_spec in query_events:
                    await query_events[data_spec].wait()
            elif isinstance(data_spec, list):
                await asyncio.gather(
                    *[query_events[q].wait() for q in data_spec if q in query_events]
                )

            # Generate chart
            name, svg = await self.chart_generator.generate_one(
                chart_name=chart_name,
                is_custom=is_custom,
                data_map=query_results,
                chart_registry=chart_registry,
                yaml_charts=yaml_charts,
                report_id=report.id,
                params=params,
                assets_dir=(
                    report_dir / report.template.assets
                    if report_dir and report.template.assets
                    else None
                ),
            )
            if svg:
                chart_results[name] = svg
            _advance_chart()

        # --- Launch all tasks together ---
        all_tasks = [
            *[_run_query_task(q) for q in report.queries],
            *[_run_chart_task(name, is_custom) for name, is_custom in charts_to_generate],
        ]
        results = await asyncio.gather(*all_tasks, return_exceptions=True)

        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                if i < n_queries:
                    label = f"Query '{report.queries[i].name}'"
                else:
                    chart_idx = i - n_queries
                    label = f"Chart '{charts_to_generate[chart_idx][0]}'"
                raise LocalExecutorError(f"{label} failed: {result}") from result

        # Log cache stats
        stats = self._query_cache.stats()
        if stats["total_requests"] > 0:
            logger.info(
                f"Query cache: {stats['hits']}/{stats['total_requests']} hits "
                f"({stats['hit_rate_percent']}%)"
            )

        return query_results, chart_results

    async def execute(
        self,
        report: ReportDefinition,
        params: Dict[str, Any],
        output: Path,
        progress: Optional[Progress] = None,
        keep_chart_files: bool = False,
    ) -> Path:
        """
        Execute full report generation pipeline.

        Args:
            report: Report definition
            params: Report parameters
            output: Output file path
            progress: Optional Rich progress instance

        Returns:
            Path to generated PDF

        Raises:
            LocalExecutorError: If generation fails
        """
        try:
            # Pipeline: queries and charts interleaved in parallel
            data, charts = await self._execute_pipeline(report, params, progress)

            # Render PDF (sequential, needs all data + charts ready)
            if progress:
                render_task = progress.add_task("Rendering PDF...", total=None)

            output_path = await self._render_pdf(
                report,
                data,
                charts,
                output,
                keep_chart_files=keep_chart_files,
            )

            if progress:
                progress.update(render_task, description="PDF rendered!")

            return output_path

        except LocalExecutorError:
            raise
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise LocalExecutorError(f"Report generation failed: {e}") from e

    async def execute_data_only(
        self,
        report: ReportDefinition,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute queries only, return data as dict.

        Args:
            report: Report definition
            params: Report parameters

        Returns:
            Dict mapping query names to results (as lists of dicts)
        """
        try:
            data = await self._run_queries(report, params)

            # Convert DataFrames to lists of dicts
            result = {}
            for name, df in data.items():
                if isinstance(df, pd.DataFrame):
                    result[name] = df.to_dict(orient="records")
                else:
                    result[name] = df

            return result

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise LocalExecutorError(f"Query execution failed: {e}") from e

    async def execute_with_data(
        self,
        report: ReportDefinition,
        data: Dict[str, Any],
        params: Dict[str, Any],
        output: Path,
        progress: Optional[Progress] = None,
        keep_chart_files: bool = False,
    ) -> Path:
        """Execute report generation using pre-loaded JSON data instead of BigQuery.

        The *data* dict is expected to have a ``queries`` key mapping query
        names to lists of row dicts (the same shape produced by
        ``--data-only``).  Any other top-level keys are passed through to the
        template as-is.

        Args:
            report: Report definition
            data: Pre-loaded JSON data (must contain ``queries`` key)
            params: Report parameters
            output: Output file path
            progress: Optional Rich progress instance

        Returns:
            Path to generated PDF
        """
        try:
            # Convert JSON query results into DataFrames
            raw_queries = data.get("queries", {})
            query_results: Dict[str, pd.DataFrame] = {}
            for name, rows in raw_queries.items():
                if isinstance(rows, list):
                    query_results[name] = pd.DataFrame(rows)
                elif isinstance(rows, dict):
                    query_results[name] = pd.DataFrame(rows)
                else:
                    query_results[name] = pd.DataFrame()

            # Generate charts using the standard pipeline
            if progress:
                chart_task = progress.add_task("Generating charts...", total=None)

            charts = await self._generate_charts(report, query_results, params)

            if progress:
                progress.update(chart_task, description="Charts done!")

            # Render PDF
            if progress:
                render_task = progress.add_task("Rendering PDF...", total=None)

            output_path = await self._render_pdf(
                report,
                query_results,
                charts,
                output,
                keep_chart_files=keep_chart_files,
            )

            if progress:
                progress.update(render_task, description="PDF rendered!")

            return output_path

        except LocalExecutorError:
            raise
        except Exception as e:
            logger.error(f"Report generation with data failed: {e}")
            raise LocalExecutorError(f"Report generation with data failed: {e}") from e

    async def upload(
        self,
        local_path: Path,
        report_id: str,
        params: Dict[str, Any],
    ) -> str:
        """
        Upload generated PDF to GCS.

        Args:
            local_path: Path to local PDF file
            report_id: Report ID
            params: Report parameters

        Returns:
            GCS URI
        """
        # Build GCS path
        param_parts = [f"{v}" for k, v in sorted(params.items())]
        param_str = "-".join(param_parts) if param_parts else "report"
        gcs_path = f"{report_id}/{param_str}.pdf"

        # Upload
        content = local_path.read_bytes()
        return await self.gcs_client.upload(gcs_path, content, content_type="application/pdf")

    async def _run_single_query(
        self,
        query: Query,
        params: Dict[str, Any],
        report_dir: Optional[Path] = None,
    ) -> tuple[str, pd.DataFrame]:
        """
        Run a single query with caching and semaphore.

        Args:
            query: Query definition
            params: Query parameters
            report_dir: Optional report directory for resolving SQL file paths

        Returns:
            Tuple of (query_name, DataFrame)
        """
        # Load SQL from file
        if report_dir:
            sql_path = report_dir / query.file
        else:
            sql_path = Path(query.file)

        if not sql_path.exists():
            raise LocalExecutorError(f"SQL file not found: {sql_path}")

        sql = sql_path.read_text(encoding="utf-8")

        # Check cache first
        cached_result = self._query_cache.get(sql, params)
        if cached_result is not None:
            logger.info(f"Cache hit for query '{query.name}'")
            return query.name, cached_result

        # Execute query with semaphore to limit concurrency
        if query.source == SourceType.BIGQUERY:
            async with self._query_semaphore:
                logger.info(f"Executing query '{query.name}' via BigQuery")
                df = await self.bigquery_client.execute_query(sql, params)
        else:
            raise LocalExecutorError(f"Unsupported source: {query.source}")

        # Cache the result
        self._query_cache.set(sql, params, df)

        return query.name, df

    async def _run_queries(
        self,
        report: ReportDefinition,
        params: Dict[str, Any],
        progress: Optional[Progress] = None,
        task_id: Optional[int] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Run all queries for a report with caching and concurrency control.

        Queries are executed in parallel with a semaphore limiting concurrent
        BigQuery requests. Results are cached locally to avoid redundant queries.

        Args:
            report: Report definition
            params: Query parameters
            progress: Optional progress bar
            task_id: Optional task ID for progress updates

        Returns:
            Dict mapping query names to DataFrames
        """
        results = {}
        report_dir = getattr(report, "_report_dir", None)

        # Run queries in parallel (semaphore limits actual concurrency)
        tasks = [self._run_single_query(q, params, report_dir) for q in report.queries]
        query_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(query_results):
            if isinstance(result, Exception):
                raise LocalExecutorError(f"Query '{report.queries[i].name}' failed: {result}")
            name, df = result
            results[name] = df

            if progress and task_id:
                progress.advance(task_id)

        # Log cache stats
        stats = self._query_cache.stats()
        if stats["total_requests"] > 0:
            logger.info(
                f"Query cache: {stats['hits']}/{stats['total_requests']} hits "
                f"({stats['hit_rate_percent']}%)"
            )

        return results

    async def _generate_charts(
        self,
        report: ReportDefinition,
        data: Dict[str, pd.DataFrame],
        params: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Generate all charts for a report (custom + YAML-defined).

        Args:
            report: Report definition
            data: Query results
            params: Report parameters

        Returns:
            Dict mapping chart names to base64-encoded SVGs
        """
        chart_registry = self.get_chart_registry(report)

        # Skip if no charts
        if not report.charts and (chart_registry is None or len(chart_registry) == 0):
            return {}

        report_dir = getattr(report, "_report_dir", None)
        assets_dir = None
        if report_dir and report.template.assets:
            assets_dir = report_dir / report.template.assets

        return await self.chart_generator.generate_many(
            charts=report.charts,
            data_map=data,
            chart_registry=chart_registry,
            report_id=report.id,
            params=params,
            assets_dir=assets_dir,
        )

    async def _render_pdf(
        self,
        report: ReportDefinition,
        data: Dict[str, pd.DataFrame],
        charts: Dict[str, str],
        output: Path,
        keep_chart_files: bool = False,
    ) -> Path:
        """
        Render the PDF using Typst.

        Args:
            report: Report definition
            data: Query results
            charts: Generated charts
            output: Output file path

        Returns:
            Path to generated PDF
        """
        report_dir = getattr(report, "_report_dir", None)

        if report_dir:
            template_path = report_dir / report.template.entry
            assets_dir = report_dir / report.template.assets if report.template.assets else None
        else:
            template_path = Path(report.template.entry)
            assets_dir = Path(report.template.assets) if report.template.assets else None

        if not template_path.exists():
            raise LocalExecutorError(f"Template not found: {template_path}")

        logger.info(f"Rendering PDF with Typst ({template_path.name})")

        # Prepare data for template
        template_data = {
            "queries": {
                name: df.to_dict(orient="records") if isinstance(df, pd.DataFrame) else df
                for name, df in data.items()
            },
            "charts": charts,
            "params": {},
        }

        # Render
        await self.typst_renderer.render(
            template_path=template_path,
            output_path=output,
            data=template_data,
            assets_dir=assets_dir,
            keep_chart_files=keep_chart_files,
        )

        return output
