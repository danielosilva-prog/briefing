"""Job service for managing report generation jobs."""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, timezone

from schoolreport.models.job import Job, JobStatus

logger = logging.getLogger(__name__)


class JobService:
    """
    Service for managing report generation jobs.

    Handles job lifecycle including:
    - Creating jobs
    - Querying job status
    - Updating job progress
    - Cancelling jobs
    - Downloading results
    """

    def __init__(self, postgres_pool=None, storage_client=None):
        """
        Initialize job service.

        Args:
            postgres_pool: PostgreSQL connection pool
            storage_client: Google Cloud Storage client
        """
        self.postgres_pool = postgres_pool
        self.storage_client = storage_client

    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        report_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Job], int]:
        """
        List jobs with optional filtering.

        Args:
            status: Filter by job status
            report_id: Filter by report ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Tuple of (jobs list, total count)
        """
        # TODO: Implement actual database query
        # For now, return mock data
        logger.info(
            f"Listing jobs: status={status}, report_id={report_id}, "
            f"limit={limit}, offset={offset}"
        )

        # Mock implementation
        jobs = []
        total = 0

        return jobs, total

    async def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job if found, None otherwise
        """
        # TODO: Implement actual database query
        logger.info(f"Getting job: {job_id}")

        # Mock implementation
        return None

    async def create_job(
        self,
        report_id: str,
        parameters: dict,
        requester: Optional[str] = None
    ) -> Job:
        """
        Create a new job.

        Args:
            report_id: Report type identifier
            parameters: Report generation parameters
            requester: Who requested the report

        Returns:
            Created job
        """
        # TODO: Implement actual database insert
        logger.info(f"Creating job: report_id={report_id}, parameters={parameters}")

        # Create job model
        job = Job(
            report_id=report_id,
            parameters=parameters,
            status=JobStatus.QUEUED,
            requester=requester,
        )

        return job

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        **kwargs
    ) -> Optional[Job]:
        """
        Update job status.

        Args:
            job_id: Job identifier
            status: New status
            **kwargs: Additional fields to update (error, result, etc.)

        Returns:
            Updated job if found, None otherwise
        """
        # TODO: Implement actual database update
        logger.info(f"Updating job {job_id}: status={status}, kwargs={kwargs}")

        return None

    async def cancel_job(self, job_id: str) -> Optional[Job]:
        """
        Cancel a job.

        Args:
            job_id: Job identifier

        Returns:
            Cancelled job if found, None otherwise
        """
        # TODO: Implement actual job cancellation
        logger.info(f"Cancelling job: {job_id}")

        # Mock implementation
        return None

    async def download_job(self, job_id: str) -> bytes:
        """
        Download job result PDF from GCS.

        Args:
            job_id: Job identifier

        Returns:
            PDF file content as bytes

        Raises:
            FileNotFoundError: If PDF doesn't exist
        """
        # TODO: Implement actual GCS download
        logger.info(f"Downloading job result: {job_id}")

        # Mock implementation
        return b"PDF content"

    async def delete_old_jobs(self, cutoff_date) -> int:
        """
        Delete jobs older than the cutoff date.

        Args:
            cutoff_date: Delete jobs created before this date

        Returns:
            Number of jobs deleted
        """
        logger.info(f"Deleting jobs older than {cutoff_date}")

        if not self.postgres_pool:
            return 0

        try:
            async with self.postgres_pool.acquire() as conn:
                result = await conn.execute(
                    """
                    DELETE FROM jobs
                    WHERE status IN ('completed', 'failed')
                    AND created_at < $1
                    """,
                    cutoff_date
                )
                count = int(result.split()[-1]) if result else 0
                logger.info(f"Deleted {count} old jobs")
                return count

        except Exception as e:
            logger.error(f"Failed to delete old jobs: {e}")
            return 0


# Global service instance (will be initialized with dependencies)
_job_service: Optional[JobService] = None


def get_job_service() -> JobService:
    """
    Get global job service instance.

    Returns:
        JobService instance
    """
    global _job_service

    if _job_service is None:
        # Initialize with dependencies
        # In production, these would come from dependency injection
        _job_service = JobService()

    return _job_service


def set_job_service(service: JobService):
    """
    Set global job service instance (for testing).

    Args:
        service: JobService instance to use
    """
    global _job_service
    _job_service = service
