"""arq worker for background report generation."""

import logging
from arq import cron
from arq.connections import RedisSettings

from schoolreport.config import get_settings
from schoolreport.core.postgres import PostgresClient
from schoolreport.core.storage import StorageClient
from schoolreport.rendering.charts import ChartGenerator
from schoolreport.rendering.pdf import PDFRenderer
from schoolreport.services.audit import AuditService
from schoolreport.services.cache import CacheService
from schoolreport.services.data_layer import DataLayer
from schoolreport.services.executor import ReportExecutor
from schoolreport.services.job_service import JobService
from schoolreport.services.registry import ReportRegistry
from schoolreport.worker.tasks import (
    generate_report,
    cleanup_old_jobs,
    cleanup_expired_cache,
)

logger = logging.getLogger(__name__)


class WorkerSettings:
    """
    arq worker configuration.

    Defines job functions, retry behavior, and connection settings.
    """

    # Job functions available to the worker
    functions = [generate_report]

    # Cron jobs (periodic tasks)
    cron_jobs = [
        cron(cleanup_old_jobs, hour=2, minute=0),  # Run at 2 AM daily
        cron(cleanup_expired_cache, hour=3, minute=0),  # Run at 3 AM daily
    ]

    # Redis connection settings
    @staticmethod
    def redis_settings() -> RedisSettings:
        """Get Redis connection settings from app config."""
        settings = get_settings()

        # Parse Redis URL
        redis_url = str(settings.redis_url)
        parts = redis_url.replace("redis://", "").split("/")
        host_port = parts[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 6379
        database = int(parts[1]) if len(parts) > 1 else 0

        return RedisSettings(
            host=host,
            port=port,
            database=database,
        )

    # Worker configuration
    max_jobs = 10  # Maximum concurrent jobs
    job_timeout = 3600  # 1 hour timeout per job
    keep_result = 86400  # Keep results for 24 hours

    # Retry configuration
    max_tries = 3  # Maximum retry attempts
    retry_jobs = True  # Enable automatic retries

    # Logging
    log_results = True
    verbose = True


async def startup(ctx):
    """
    Worker startup handler.

    Initializes connections and resources needed by worker tasks.

    Args:
        ctx: Worker context dictionary
    """
    logger.info("Worker starting up...")

    settings = get_settings()

    # Initialize PostgreSQL client
    logger.info("Creating PostgreSQL connection pool...")
    postgres_client = PostgresClient(
        dsn=str(settings.database_url),
        min_size=2,
        max_size=10,
    )
    await postgres_client.connect()
    ctx["postgres_pool"] = postgres_client

    # Initialize services
    logger.info("Initializing services...")

    # Report registry
    registry = ReportRegistry()
    ctx["registry"] = registry

    # Data layer (BigQuery)
    data_layer = DataLayer(project_id=settings.gcp_project_id)
    ctx["data_layer"] = data_layer

    # Chart generator
    chart_generator = ChartGenerator()
    ctx["chart_generator"] = chart_generator

    # PDF renderer
    pdf_renderer = PDFRenderer()
    ctx["pdf_renderer"] = pdf_renderer

    # Storage client (GCS)
    storage_client = StorageClient(
        project_id=settings.gcp_project_id,
        bucket_name=settings.gcs_bucket,
    )
    ctx["storage_client"] = storage_client

    # Cache service
    cache_service = CacheService(postgres_client=postgres_client)
    ctx["cache_service"] = cache_service

    # Audit service
    audit_service = AuditService(postgres_client=postgres_client)
    ctx["audit_service"] = audit_service

    # Job service
    job_service = JobService(
        postgres_pool=postgres_client._pool,
        storage_client=storage_client,
    )
    ctx["job_service"] = job_service

    # Create the report executor with all services
    executor = ReportExecutor(
        registry=registry,
        data_layer=data_layer,
        chart_generator=chart_generator,
        pdf_renderer=pdf_renderer,
        storage_client=storage_client,
        cache_service=cache_service,
        audit_service=audit_service,
    )
    ctx["executor"] = executor

    logger.info(
        f"Worker initialized for environment: {settings.environment}",
        extra={
            "environment": settings.environment,
            "max_jobs": WorkerSettings.max_jobs,
            "job_timeout": WorkerSettings.job_timeout,
        }
    )


async def shutdown(ctx):
    """
    Worker shutdown handler.

    Cleanup resources before worker terminates.

    Args:
        ctx: Worker context dictionary
    """
    logger.info("Worker shutting down...")

    # Close database connections
    if ctx.get("postgres_pool"):
        await ctx["postgres_pool"].close()
        logger.info("PostgreSQL pool closed")

    # Close GCS client
    if ctx.get("storage_client"):
        ctx["storage_client"].close()
        logger.info("GCS client closed")

    logger.info("Worker shutdown complete")


# Export for arq
WorkerSettings.on_startup = startup
WorkerSettings.on_shutdown = shutdown
