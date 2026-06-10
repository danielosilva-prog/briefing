"""Reports API routes for managing report types and generation."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from schoolreport.models.job import JobCreate, JobResponse, JobStatus
from schoolreport.services.job_service import JobService, get_job_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportDefinition(BaseModel):
    """Report type definition."""

    id: str
    name: str
    description: str
    parameters: List[str]  # List of required parameter names

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ATM",
                "name": "Aqui Tem MEC 2",
                "description": "Comprehensive school report for PNLD, PNAE, PDDE, and other programs",
                "parameters": ["cod_ibge", "ano"]
            }
        }


class ReportListResponse(BaseModel):
    """Response for list reports endpoint."""

    reports: List[ReportDefinition]


class GenerateReportRequest(BaseModel):
    """Request to generate a report."""

    parameters: dict
    requester: str | None = None


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List available reports",
    description="Get list of all available report types"
)
async def list_reports():
    """
    List all available report types.

    Returns metadata for each report including:
    - Report ID
    - Display name
    - Description
    - Required parameters
    """
    # TODO: Load from registry system (similar to R implementation)
    reports = [
        ReportDefinition(
            id="ATM",
            name="Aqui Tem MEC 2",
            description="Comprehensive school report with PNLD, PNAE, PDDE, SAEB, and more",
            parameters=["cod_ibge", "ano"]
        ),
        ReportDefinition(
            id="ATS",
            name="Aqui Tem Superior",
            description="Higher education institution report",
            parameters=["cod_ies", "ano"]
        ),
        ReportDefinition(
            id="ATSBR",
            name="Aqui Tem Superior - Brasil",
            description="National higher education overview",
            parameters=["ano"]
        ),
    ]

    return ReportListResponse(reports=reports)


@router.get(
    "/{report_id}",
    response_model=ReportDefinition,
    summary="Get report metadata",
    description="Get detailed information about a specific report type",
    responses={
        200: {"description": "Report found"},
        404: {"description": "Report not found"}
    }
)
async def get_report(report_id: str):
    """
    Get report metadata by ID.

    Returns detailed information including:
    - Report name and description
    - Required parameters
    - Optional parameters (if any)
    - Example usage
    """
    # TODO: Load from registry
    reports_map = {
        "ATM": ReportDefinition(
            id="ATM",
            name="Aqui Tem MEC 2",
            description="Comprehensive school report with PNLD, PNAE, PDDE, SAEB, and more",
            parameters=["cod_ibge", "ano"]
        ),
        "ATS": ReportDefinition(
            id="ATS",
            name="Aqui Tem Superior",
            description="Higher education institution report",
            parameters=["cod_ies", "ano"]
        ),
        "ATSBR": ReportDefinition(
            id="ATSBR",
            name="Aqui Tem Superior - Brasil",
            description="National higher education overview",
            parameters=["ano"]
        ),
    }

    report = reports_map.get(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )

    return report


@router.post(
    "/{report_id}/generate",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate report",
    description="Queue a report generation job",
    responses={
        202: {"description": "Job created and queued"},
        404: {"description": "Report type not found"},
        400: {"description": "Invalid parameters"}
    }
)
async def generate_report(
    report_id: str,
    request: GenerateReportRequest,
    job_service: JobService = Depends(get_job_service),
):
    """
    Generate a report asynchronously.

    Creates a job and queues it for background processing.
    Returns immediately with job information.

    The report generation is handled by background workers.
    Use the job endpoints to check status and download results.

    Args:
        report_id: Report type identifier
        request: Generation parameters and metadata
        job_service: Job service (injected)

    Returns:
        JobResponse: Created job with status "queued"
    """
    # TODO: Validate report exists
    # TODO: Validate parameters match report definition

    # Validate report_id
    valid_reports = ["ATM", "ATS", "ATSBR"]
    if report_id not in valid_reports:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )

    # Create job
    job = await job_service.create_job(
        report_id=report_id,
        parameters=request.parameters,
        requester=request.requester
    )

    # TODO: Enqueue to arq for background processing
    # For now, just create the job

    logger.info(
        f"Created job {job.id} for report {report_id}",
        extra={
            "job_id": str(job.id),
            "report_id": report_id,
            "parameters": request.parameters,
        }
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
