"""Executor pipeline for orchestrating report generation."""

import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional
from uuid import UUID

import pandas as pd

from schoolreport.core.storage import StorageClient
from schoolreport.models.report import ReportDefinition
from schoolreport.rendering.charts import ChartGenerator
from schoolreport.rendering.pdf import PDFRenderer
from schoolreport.services.audit import AuditService
from schoolreport.services.cache import CacheService
from schoolreport.services.data_layer import DataLayer
from schoolreport.services.registry import ReportRegistry

logger = logging.getLogger(__name__)


class ExecutorError(Exception):
    """Raised when executor pipeline fails."""

    pass


class ReportExecutor:
    """
    Orchestrate end-to-end report generation pipeline.

    9-stage pipeline:
    1. Load report definition
    2. Validate parameters
    3. Check cache
    4. Execute queries (parallel)
    5. Generate charts (parallel)
    6. Render PDF
    7. Upload to GCS
    8. Update cache
    9. Write audit log
    """

    def __init__(
        self,
        registry: ReportRegistry,
        data_layer: DataLayer,
        chart_generator: ChartGenerator,
        pdf_renderer: PDFRenderer,
        storage_client: StorageClient,
        cache_service: CacheService,
        audit_service: AuditService,
    ):
        """Initialize executor with all required services."""
        self.registry = registry
        self.data_layer = data_layer
        self.chart_generator = chart_generator
        self.pdf_renderer = pdf_renderer
        self.storage = storage_client
        self.cache = cache_service
        self.audit = audit_service

    async def execute(
        self,
        job_id: UUID,
        report_id: str,
        parameters: dict,
        requester: str = "system",
    ) -> Dict[str, str]:
        """
        Execute complete report generation pipeline.

        Args:
            job_id: Job identifier
            report_id: Report type to generate
            parameters: Report parameters
            requester: Who requested the report

        Returns:
            Dictionary with gcs_path, duration_ms, etc.

        Raises:
            ExecutorError: If any stage fails
        """
        start_time = time.time()
        audit_id = None

        try:
            # Stage 1: Load report definition
            logger.info(f"[Job {job_id}] Stage 1: Loading report definition '{report_id}'")
            report_def = self.registry.get(report_id)

            # Stage 2: Validate parameters
            logger.info(f"[Job {job_id}] Stage 2: Validating parameters")
            self._validate_parameters(report_def, parameters)

            # Create audit log
            audit_id = await self.audit.log_start(
                job_id=job_id,
                report_id=report_id,
                parameters=parameters,
                requester=requester,
                metadata={"version": report_def.version}
            )

            # Stage 3: Check cache
            logger.info(f"[Job {job_id}] Stage 3: Checking cache")
            cached_path = await self.cache.get(report_id, parameters)
            if cached_path:
                duration_ms = int((time.time() - start_time) * 1000)
                await self.audit.log_complete(audit_id, cached_path, duration_ms)
                return {
                    "gcs_path": cached_path,
                    "duration_ms": duration_ms,
                    "cached": True
                }

            # Stage 4: Execute queries (parallel)
            logger.info(f"[Job {job_id}] Stage 4: Executing {len(report_def.queries)} queries")
            query_data = await self._execute_queries(report_def, parameters)

            # Stage 5: Generate charts (parallel)
            chart_registry = self.registry.get_chart_registry(report_id)
            chart_count = len(report_def.charts) + (len(chart_registry) if chart_registry else 0)
            logger.info(f"[Job {job_id}] Stage 5: Generating {chart_count} charts")
            chart_data = await self._generate_charts(report_def, query_data, parameters)

            # Stage 6: Render PDF
            logger.info(f"[Job {job_id}] Stage 6: Rendering PDF")
            pdf_path = await self._render_pdf(report_def, query_data, chart_data)

            # Stage 7: Upload to GCS
            logger.info(f"[Job {job_id}] Stage 7: Uploading to GCS")
            gcs_path = await self._upload_to_gcs(report_id, parameters, pdf_path)

            # Stage 8: Update cache
            logger.info(f"[Job {job_id}] Stage 8: Updating cache")
            await self.cache.set(
                report_id=report_id,
                params=parameters,
                gcs_path=gcs_path,
                ttl_days=report_def.cache.ttl_days
            )

            # Stage 9: Write audit log
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"[Job {job_id}] Stage 9: Writing audit log ({duration_ms}ms)")
            await self.audit.log_complete(audit_id, gcs_path, duration_ms)

            logger.info(f"[Job {job_id}] Pipeline completed successfully")
            return {
                "gcs_path": gcs_path,
                "duration_ms": duration_ms,
                "cached": False
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[Job {job_id}] Pipeline failed: {e}")

            if audit_id:
                await self.audit.log_failure(audit_id, str(e), duration_ms)

            raise ExecutorError(f"Report generation failed: {e}") from e

    def _validate_parameters(self, report_def: ReportDefinition, params: dict) -> None:
        """Validate parameters against report definition."""
        for param_def in report_def.parameters:
            if param_def.required and param_def.name not in params:
                raise ExecutorError(f"Required parameter missing: {param_def.name}")

            # Basic type validation
            if param_def.name in params:
                value = params[param_def.name]
                # TODO: Add type checking

    async def _execute_queries(
        self,
        report_def: ReportDefinition,
        params: dict
    ) -> Dict[str, pd.DataFrame]:
        """Execute all queries in parallel."""
        # Load SQL files
        sql_map = {}
        for query in report_def.queries:
            sql_path = report_def.get_query_path(query)
            sql_map[query.name] = sql_path.read_text(encoding="utf-8")

        # Execute in parallel
        return await self.data_layer.execute_many(
            queries=report_def.queries,
            sql_map=sql_map,
            params=params
        )

    async def _generate_charts(
        self,
        report_def: ReportDefinition,
        query_data: Dict[str, pd.DataFrame],
        params: dict,
    ) -> Dict[str, str]:
        """Generate all charts in parallel (custom + YAML-defined)."""
        chart_registry = self.registry.get_chart_registry(report_def.id)

        # Skip if no charts defined (neither YAML nor custom)
        if not report_def.charts and (chart_registry is None or len(chart_registry) == 0):
            return {}

        return await self.chart_generator.generate_many(
            charts=report_def.charts,
            data_map=query_data,
            chart_registry=chart_registry,
            report_id=report_def.id,
            params=params,
            assets_dir=report_def.get_assets_path(),
        )

    async def _render_pdf(
        self,
        report_def: ReportDefinition,
        query_data: Dict[str, pd.DataFrame],
        chart_data: Dict[str, str]
    ) -> Path:
        """Render PDF from template and data."""
        # Combine data
        combined_data = {
            **{name: df.to_dict(orient="records") for name, df in query_data.items()},
            "charts": chart_data
        }

        # Get template path
        template_path = report_def.get_template_path()
        assets_dir = report_def.get_assets_path()

        # Render
        temp_dir = Path(tempfile.mkdtemp())
        output_path = temp_dir / "report.pdf"

        await self.pdf_renderer.render(
            template_path=template_path,
            output_path=output_path,
            data=combined_data,
            assets_dir=assets_dir
        )

        return output_path

    async def _upload_to_gcs(
        self,
        report_id: str,
        params: dict,
        pdf_path: Path
    ) -> str:
        """Upload PDF to Google Cloud Storage."""
        # Generate GCS path
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        gcs_filename = f"{report_id}/{param_str}.pdf"

        # Upload
        gcs_path = await self.storage.upload_file(
            local_path=pdf_path,
            gcs_path=gcs_filename
        )

        return gcs_path
