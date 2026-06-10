"""Tests for worker background tasks."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from uuid import UUID

from arq import Retry


class TestGenerateReportTask:
    """Test generate_report background task."""

    @pytest.mark.asyncio
    async def test_generate_report_success(self):
        """Should generate report using executor and update job status."""
        from schoolreport.worker.tasks import generate_report
        from schoolreport.models.job import JobStatus

        # Create mock executor
        mock_executor = AsyncMock()
        mock_executor.execute.return_value = {
            "gcs_path": "gs://bucket/report.pdf",
            "duration_ms": 1500,
            "cached": False
        }

        # Create mock job service
        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        # Execute task
        result = await generate_report(
            ctx,
            job_id="550e8400-e29b-41d4-a716-446655440000",
            report_id="ATM",
            parameters={"cod_ibge": "2304400"}
        )

        # Verify result
        assert result["gcs_path"] == "gs://bucket/report.pdf"
        assert result["duration_ms"] == 1500
        assert result["cached"] is False

        # Verify job status was updated to PROCESSING first
        mock_job_service.update_job_status.assert_any_call(
            "550e8400-e29b-41d4-a716-446655440000",
            JobStatus.PROCESSING,
            started_at=pytest.approx(datetime.now(timezone.utc), abs=5)
        )

        # Verify executor was called
        mock_executor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_report_cache_hit(self):
        """Should handle cache hits correctly."""
        from schoolreport.worker.tasks import generate_report

        mock_executor = AsyncMock()
        mock_executor.execute.return_value = {
            "gcs_path": "gs://bucket/cached.pdf",
            "duration_ms": 50,
            "cached": True
        }

        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        result = await generate_report(
            ctx,
            job_id="job-cache-hit",
            report_id="ATM",
            parameters={"cod_ibge": "2304400"}
        )

        assert result["cached"] is True
        assert result["duration_ms"] < 100

    @pytest.mark.asyncio
    async def test_generate_report_failure_updates_job(self):
        """Should update job status on failure."""
        from schoolreport.worker.tasks import generate_report
        from schoolreport.models.job import JobStatus

        mock_executor = AsyncMock()
        mock_executor.execute.side_effect = ValueError("Invalid parameter: cod_ibge")

        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        with pytest.raises(ValueError):
            await generate_report(
                ctx,
                job_id="job-fail",
                report_id="ATM",
                parameters={}
            )

        # Verify failure was recorded
        mock_job_service.update_job_status.assert_called_with(
            "job-fail",
            JobStatus.FAILED,
            error="Invalid parameter: cod_ibge",
            completed_at=pytest.approx(datetime.now(timezone.utc), abs=5)
        )

    @pytest.mark.asyncio
    async def test_generate_report_retry_on_network_error(self):
        """Should retry on network errors."""
        from schoolreport.worker.tasks import generate_report

        mock_executor = AsyncMock()
        mock_executor.execute.side_effect = ConnectionError("Network unreachable")

        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        with pytest.raises(Retry):
            await generate_report(
                ctx,
                job_id="job-network-fail",
                report_id="ATM",
                parameters={"cod_ibge": "2304400"}
            )

    @pytest.mark.asyncio
    async def test_generate_report_retry_on_timeout(self):
        """Should retry on BigQuery timeout."""
        from schoolreport.worker.tasks import generate_report

        mock_executor = AsyncMock()
        mock_executor.execute.side_effect = TimeoutError("Query timeout")

        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        with pytest.raises(Retry):
            await generate_report(
                ctx,
                job_id="job-timeout",
                report_id="ATM",
                parameters={"cod_ibge": "2304400"}
            )

    @pytest.mark.asyncio
    async def test_generate_report_no_retry_on_validation_error(self):
        """Should not retry on validation errors."""
        from schoolreport.worker.tasks import generate_report
        from schoolreport.services.executor import ExecutorError

        mock_executor = AsyncMock()
        mock_executor.execute.side_effect = ExecutorError("Required parameter missing: cod_ibge")

        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        with pytest.raises(ExecutorError):
            await generate_report(
                ctx,
                job_id="job-validation",
                report_id="ATM",
                parameters={}
            )

    @pytest.mark.asyncio
    async def test_generate_report_completes_job_on_success(self):
        """Should mark job as completed with result."""
        from schoolreport.worker.tasks import generate_report
        from schoolreport.models.job import JobStatus

        mock_executor = AsyncMock()
        mock_executor.execute.return_value = {
            "gcs_path": "gs://bucket/final.pdf",
            "duration_ms": 2000,
            "cached": False
        }

        mock_job_service = AsyncMock()

        ctx = {
            "executor": mock_executor,
            "job_service": mock_job_service,
        }

        await generate_report(
            ctx,
            job_id="job-complete",
            report_id="ATM",
            parameters={"cod_ibge": "2304400"}
        )

        # Verify job was marked completed
        calls = mock_job_service.update_job_status.call_args_list
        completed_call = next(
            (c for c in calls if c[0][1] == JobStatus.COMPLETED),
            None
        )
        assert completed_call is not None
        # Verify gcs_path is in the call
        assert "gcs_path" in completed_call[1]


class TestCleanupOldJobsTask:
    """Test cleanup_old_jobs periodic task."""

    @pytest.mark.asyncio
    async def test_cleanup_old_jobs_removes_expired(self):
        """Should cleanup old completed and failed jobs."""
        from schoolreport.worker.tasks import cleanup_old_jobs

        mock_job_service = AsyncMock()
        mock_job_service.delete_old_jobs.return_value = 42

        ctx = {"job_service": mock_job_service}

        result = await cleanup_old_jobs(ctx)

        assert result == 42
        mock_job_service.delete_old_jobs.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_old_jobs_handles_empty(self):
        """Should handle case where no jobs to cleanup."""
        from schoolreport.worker.tasks import cleanup_old_jobs

        mock_job_service = AsyncMock()
        mock_job_service.delete_old_jobs.return_value = 0

        ctx = {"job_service": mock_job_service}

        result = await cleanup_old_jobs(ctx)

        assert result == 0


class TestCacheCleanupTask:
    """Test cache cleanup periodic task."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_cache(self):
        """Should cleanup expired cache entries."""
        from schoolreport.worker.tasks import cleanup_expired_cache

        mock_cache = AsyncMock()
        mock_cache.cleanup_expired.return_value = 15

        ctx = {"cache_service": mock_cache}

        result = await cleanup_expired_cache(ctx)

        assert result == 15
        mock_cache.cleanup_expired.assert_called_once()


class TestRetriableErrors:
    """Test error retry logic."""

    def test_network_errors_are_retriable(self):
        """Network errors should be retried."""
        from schoolreport.worker.tasks import is_retriable_error

        assert is_retriable_error(ConnectionError("Connection refused"))
        assert is_retriable_error(TimeoutError("Timeout"))
        assert is_retriable_error(OSError("Network unreachable"))

    def test_bigquery_timeouts_are_retriable(self):
        """BigQuery timeouts should be retried."""
        from schoolreport.worker.tasks import is_retriable_error

        assert is_retriable_error(Exception("Query timeout"))
        assert is_retriable_error(Exception("Deadline exceeded"))

    def test_rate_limits_are_retriable(self):
        """Rate limit errors should be retried."""
        from schoolreport.worker.tasks import is_retriable_error

        assert is_retriable_error(Exception("Rate limit exceeded"))
        assert is_retriable_error(Exception("Quota exceeded"))

    def test_gcs_errors_are_retriable(self):
        """GCS service errors should be retried."""
        from schoolreport.worker.tasks import is_retriable_error

        assert is_retriable_error(Exception("503 Service Unavailable"))
        assert is_retriable_error(Exception("Service temporarily unavailable"))

    def test_value_errors_not_retriable(self):
        """Validation errors should not be retried."""
        from schoolreport.worker.tasks import is_retriable_error

        assert not is_retriable_error(ValueError("Invalid parameter"))
        assert not is_retriable_error(KeyError("Missing field"))

    def test_executor_errors_not_retriable(self):
        """Executor validation errors should not be retried."""
        from schoolreport.worker.tasks import is_retriable_error
        from schoolreport.services.executor import ExecutorError

        assert not is_retriable_error(ExecutorError("Required parameter missing"))


class TestWorkerConfiguration:
    """Test worker configuration."""

    def test_worker_settings_defined(self):
        """Worker settings should be properly configured."""
        from schoolreport.worker.main import WorkerSettings

        assert WorkerSettings.max_jobs > 0
        assert WorkerSettings.job_timeout > 0
        assert WorkerSettings.max_tries > 0

    def test_worker_has_functions(self):
        """Worker should have task functions registered."""
        from schoolreport.worker.main import WorkerSettings

        assert len(WorkerSettings.functions) > 0
        function_names = [f.__name__ for f in WorkerSettings.functions]
        assert "generate_report" in function_names

    def test_worker_has_cron_jobs(self):
        """Worker should have cron jobs configured."""
        from schoolreport.worker.main import WorkerSettings

        assert len(WorkerSettings.cron_jobs) > 0

    def test_redis_settings_from_config(self, mock_env):
        """Should create Redis settings from config."""
        from schoolreport.worker.main import WorkerSettings

        redis_settings = WorkerSettings.redis_settings()

        assert redis_settings.host == "localhost"
        assert redis_settings.port == 6379
        assert redis_settings.database == 0


class TestWorkerStartup:
    """Test worker startup initialization."""

    @pytest.mark.asyncio
    async def test_startup_initializes_executor(self, mock_env):
        """Startup should initialize executor with all services."""
        from schoolreport.worker.main import startup

        ctx = {}

        with patch("schoolreport.worker.main.ReportExecutor") as mock_exec_cls, \
             patch("schoolreport.worker.main.ReportRegistry") as mock_registry_cls, \
             patch("schoolreport.worker.main.DataLayer") as mock_data_layer_cls, \
             patch("schoolreport.worker.main.ChartGenerator") as mock_chart_cls, \
             patch("schoolreport.worker.main.PDFRenderer") as mock_pdf_cls, \
             patch("schoolreport.worker.main.StorageClient") as mock_storage_cls, \
             patch("schoolreport.worker.main.CacheService") as mock_cache_cls, \
             patch("schoolreport.worker.main.AuditService") as mock_audit_cls, \
             patch("schoolreport.worker.main.JobService") as mock_job_cls, \
             patch("schoolreport.worker.main.create_pool") as mock_pool:

            mock_pool.return_value = AsyncMock()

            await startup(ctx)

            assert "executor" in ctx
            assert "job_service" in ctx
            assert "cache_service" in ctx
            assert "postgres_pool" in ctx

    @pytest.mark.asyncio
    async def test_startup_creates_postgres_pool(self, mock_env):
        """Startup should create PostgreSQL connection pool."""
        from schoolreport.worker.main import startup

        ctx = {}

        with patch("schoolreport.worker.main.ReportExecutor"), \
             patch("schoolreport.worker.main.ReportRegistry"), \
             patch("schoolreport.worker.main.DataLayer"), \
             patch("schoolreport.worker.main.ChartGenerator"), \
             patch("schoolreport.worker.main.PDFRenderer"), \
             patch("schoolreport.worker.main.StorageClient"), \
             patch("schoolreport.worker.main.CacheService"), \
             patch("schoolreport.worker.main.AuditService"), \
             patch("schoolreport.worker.main.JobService"), \
             patch("schoolreport.worker.main.create_pool") as mock_pool:

            mock_pool.return_value = AsyncMock()

            await startup(ctx)

            mock_pool.assert_called_once()


class TestWorkerShutdown:
    """Test worker shutdown cleanup."""

    @pytest.mark.asyncio
    async def test_shutdown_closes_postgres_pool(self):
        """Shutdown should close PostgreSQL connection pool."""
        from schoolreport.worker.main import shutdown

        mock_pool = AsyncMock()
        ctx = {"postgres_pool": mock_pool}

        await shutdown(ctx)

        mock_pool.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_handles_missing_pool(self):
        """Shutdown should handle missing pool gracefully."""
        from schoolreport.worker.main import shutdown

        ctx = {}

        # Should not raise
        await shutdown(ctx)

    @pytest.mark.asyncio
    async def test_shutdown_closes_storage_client(self):
        """Shutdown should close GCS storage client."""
        from schoolreport.worker.main import shutdown

        mock_storage = MagicMock()
        mock_pool = AsyncMock()
        ctx = {
            "postgres_pool": mock_pool,
            "storage_client": mock_storage
        }

        await shutdown(ctx)

        mock_storage.close.assert_called_once()
