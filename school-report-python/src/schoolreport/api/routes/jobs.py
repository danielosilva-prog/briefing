"""Jobs API routes for managing report generation jobs."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from schoolreport.models.job import JobResponse, JobStatus
from schoolreport.services.job_service import JobService, get_job_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobListResponse:
    """Response model for job list endpoint."""

    def __init__(self, jobs: List[JobResponse], total: int, limit: int, offset: int):
        self.jobs = jobs
        self.total = total
        self.limit = limit
        self.offset = offset


@router.get(
    "",
    response_model=dict,
    summary="List jobs",
    description="List all jobs with optional filtering and pagination"
)
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by job status"),
    report_id: Optional[str] = Query(None, description="Filter by report ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    job_service: JobService = Depends(get_job_service),
):
    """
    List jobs with optional filtering.

    - **status**: Filter by job status (queued, processing, completed, failed, cancelled)
    - **report_id**: Filter by report type
    - **limit**: Maximum number of results (1-100, default 50)
    - **offset**: Number of results to skip (for pagination)

    Returns paginated list of jobs with metadata.
    """
    jobs, total = await job_service.list_jobs(
        status=status,
        report_id=report_id,
        limit=limit,
        offset=offset
    )

    # Convert to response models
    job_responses = [
        JobResponse(
            job_id=str(job.id),
            status=job.status,
            report_id=job.report_id,
            parameters=job.parameters,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            failed_at=job.failed_at,
            result=job.result,
            error=job.error,
            attempts=job.attempts,
            duration_ms=job.duration_ms,
        )
        for job in jobs
    ]

    return {
        "jobs": [job.model_dump() for job in job_responses],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
    description="Get detailed status of a specific job",
    responses={
        200: {"description": "Job found"},
        404: {"description": "Job not found"}
    }
)
async def get_job(
    job_id: str,
    job_service: JobService = Depends(get_job_service),
):
    """
    Get job status by ID.

    Returns detailed job information including:
    - Current status
    - Progress information (if processing)
    - Result (if completed)
    - Error details (if failed)
    - Links to related resources
    """
    job = await job_service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return JobResponse(
        job_id=str(job.id),
        status=job.status,
        report_id=job.report_id,
        parameters=job.parameters,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        failed_at=job.failed_at,
        result=job.result,
        error=job.error,
        attempts=job.attempts,
        duration_ms=job.duration_ms,
    )


@router.get(
    "/{job_id}/download",
    response_class=Response,
    summary="Download report PDF",
    description="Download the generated PDF report for a completed job",
    responses={
        200: {
            "description": "PDF file",
            "content": {"application/pdf": {}}
        },
        400: {"description": "Job not completed yet"},
        404: {"description": "Job not found"}
    }
)
async def download_job(
    job_id: str,
    job_service: JobService = Depends(get_job_service),
):
    """
    Download generated PDF report.

    Only works for completed jobs. Returns the PDF file as a binary stream.

    Raises:
    - 404: Job not found
    - 400: Job not completed (still processing, failed, or cancelled)
    """
    job = await job_service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    # Check if job is completed
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is {job.status.value}, not completed"
        )

    # Download PDF from GCS
    pdf_content = await job_service.download_job(job_id)

    # Generate filename from job metadata
    filename = f"{job.report_id}_{job.parameters.get('cod_ibge', 'national')}_{job_id[:8]}.pdf"

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.delete(
    "/{job_id}",
    response_model=JobResponse,
    summary="Cancel job",
    description="Cancel a pending or processing job",
    responses={
        200: {"description": "Job cancelled"},
        400: {"description": "Job cannot be cancelled"},
        404: {"description": "Job not found"}
    }
)
async def cancel_job(
    job_id: str,
    job_service: JobService = Depends(get_job_service),
):
    """
    Cancel a job.

    Only queued or processing jobs can be cancelled.
    Completed or already cancelled jobs cannot be cancelled.

    Returns the updated job status.
    """
    job = await job_service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    # Check if job can be cancelled
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status {job.status.value}"
        )

    # Cancel the job
    cancelled_job = await job_service.cancel_job(job_id)

    return JobResponse(
        job_id=str(cancelled_job.id),
        status=cancelled_job.status,
        report_id=cancelled_job.report_id,
        parameters=cancelled_job.parameters,
        created_at=cancelled_job.created_at,
        started_at=cancelled_job.started_at,
        completed_at=cancelled_job.completed_at,
        failed_at=cancelled_job.failed_at,
        result=cancelled_job.result,
        error=cancelled_job.error,
        attempts=cancelled_job.attempts,
        duration_ms=cancelled_job.duration_ms,
    )
