"""Background tasks for report generation."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from uuid import UUID

from arq import Retry

from schoolreport.models.job import JobStatus
from schoolreport.services.executor import ExecutorError

logger = logging.getLogger(__name__)


async def generate_report(
    ctx: Dict[str, Any],
    job_id: str,
    report_id: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to generate a report.

    This is the main worker task that:
    1. Updates job status to PROCESSING
    2. Delegates to ReportExecutor for full pipeline
    3. Updates job with result

    Args:
        ctx: Worker context with services
        job_id: Job identifier
        report_id: Report type
        parameters: Report parameters

    Returns:
        Dict with job result information

    Raises:
        Retry: On transient failures (network, BigQuery timeout, etc.)
    """
    logger.info(
        f"Starting report generation: job_id={job_id}, report_id={report_id}",
        extra={
            "job_id": job_id,
            "report_id": report_id,
            "parameters": parameters,
        }
    )

    executor = ctx["executor"]
    job_service = ctx["job_service"]

    try:
        # Update job status to PROCESSING
        await job_service.update_job_status(
            job_id,
            JobStatus.PROCESSING,
            started_at=datetime.now(timezone.utc)
        )

        # Execute the full report generation pipeline
        result = await executor.execute(
            job_id=UUID(job_id) if isinstance(job_id, str) else job_id,
            report_id=report_id,
            parameters=parameters,
        )

        # Update job with success
        await job_service.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            gcs_path=result["gcs_path"],
            duration_ms=result["duration_ms"],
            cached=result["cached"],
            completed_at=datetime.now(timezone.utc)
        )

        logger.info(
            f"Report generation completed: job_id={job_id}",
            extra={
                "job_id": job_id,
                "gcs_path": result["gcs_path"],
                "duration_ms": result["duration_ms"],
                "cached": result["cached"],
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Report generation failed: job_id={job_id}, error={str(e)}",
            extra={
                "job_id": job_id,
                "report_id": report_id,
                "error": str(e),
            },
            exc_info=True
        )

        # Update job with failure
        await job_service.update_job_status(
            job_id,
            JobStatus.FAILED,
            error=str(e),
            completed_at=datetime.now(timezone.utc)
        )

        # Retry on transient errors
        if is_retriable_error(e):
            logger.info(f"[{job_id}] Retrying due to transient error...")
            raise Retry(defer=60)  # Retry after 60 seconds

        # Don't retry on permanent errors
        raise


async def cleanup_old_jobs(ctx: Dict[str, Any]) -> int:
    """
    Periodic task to cleanup old completed/failed jobs.

    Removes job records older than 90 days to prevent
    database bloat.

    Args:
        ctx: Worker context

    Returns:
        Number of jobs cleaned up
    """
    logger.info("Starting old job cleanup...")

    job_service = ctx["job_service"]
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)

    cleanup_count = await job_service.delete_old_jobs(cutoff_date)

    logger.info(f"Cleaned up {cleanup_count} old jobs")

    return cleanup_count


async def cleanup_expired_cache(ctx: Dict[str, Any]) -> int:
    """
    Periodic task to cleanup expired cache entries.

    Args:
        ctx: Worker context

    Returns:
        Number of cache entries cleaned up
    """
    logger.info("Starting cache cleanup...")

    cache_service = ctx["cache_service"]
    cleanup_count = await cache_service.cleanup_expired()

    logger.info(f"Cleaned up {cleanup_count} expired cache entries")

    return cleanup_count


def is_retriable_error(error: Exception) -> bool:
    """
    Determine if an error is retriable.

    Transient errors that should trigger retry:
    - Network errors
    - BigQuery timeouts
    - Rate limiting
    - Temporary GCS errors

    Permanent errors that should not retry:
    - Invalid parameters
    - Missing data
    - Template errors
    - ExecutorError (validation failures)
    """
    # ExecutorError means validation or permanent failure
    if isinstance(error, ExecutorError):
        return False

    # Value/Key errors are validation failures
    if isinstance(error, (ValueError, KeyError)):
        return False

    error_type = type(error).__name__
    error_msg = str(error).lower()

    # Network errors
    if error_type in ["ConnectionError", "TimeoutError", "OSError"]:
        return True

    # BigQuery errors
    if "timeout" in error_msg or "deadline" in error_msg:
        return True

    # Rate limiting
    if "rate limit" in error_msg or "quota exceeded" in error_msg:
        return True

    # GCS errors
    if "503" in error_msg or "service unavailable" in error_msg:
        return True

    # Default: don't retry
    return False
