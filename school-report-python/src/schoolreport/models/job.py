"""Job models for report generation tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, computed_field


class JobStatus(str, Enum):
    """Job processing states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResult(BaseModel):
    """Result of a completed job."""

    gcs_path: str = Field(
        ...,
        description="Google Cloud Storage path to generated PDF",
        examples=["gs://segape-reports/ATM/2304400-2024.pdf"]
    )
    size_bytes: int = Field(..., gt=0, description="PDF file size in bytes")
    cached: bool = Field(
        default=False,
        description="Whether result was from cache"
    )

    @field_validator("size_bytes")
    @classmethod
    def validate_size(cls, v: int) -> int:
        """Validate size_bytes is positive."""
        if v <= 0:
            raise ValueError("size_bytes must be positive")
        return v


class JobCreate(BaseModel):
    """Request to create a new job."""

    report_id: str = Field(..., min_length=1, description="Report identifier")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Report parameters"
    )
    requester: Optional[str] = Field(
        default=None,
        description="Identity of requester (email, service account, etc.)"
    )

    @field_validator("report_id")
    @classmethod
    def validate_report_id(cls, v: str) -> str:
        """Validate report_id is non-empty."""
        if not v or not v.strip():
            raise ValueError("report_id cannot be empty")
        return v.strip()


class JobUpdate(BaseModel):
    """Update to an existing job."""

    status: Optional[JobStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[JobResult] = None
    attempts: Optional[int] = None


class Job(BaseModel):
    """Domain model for a report generation job."""

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique job identifier")

    # Metadata
    report_id: str = Field(..., description="Report type identifier")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Report generation parameters"
    )
    requester: Optional[str] = Field(
        default=None,
        description="Who requested this report"
    )

    # Status tracking
    status: JobStatus = Field(..., description="Current job status")
    attempts: int = Field(default=0, ge=0, description="Number of processing attempts")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When job was created"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="When processing started"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="When processing completed successfully"
    )
    failed_at: Optional[datetime] = Field(
        default=None,
        description="When processing failed"
    )

    # Results
    result: Optional[JobResult] = Field(
        default=None,
        description="Result if completed"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )

    @computed_field  # type: ignore[misc]
    @property
    def duration_ms(self) -> Optional[int]:
        """Calculate duration in milliseconds if completed or failed."""
        if self.started_at is None:
            return None

        end_time = self.completed_at or self.failed_at
        if end_time is None:
            return None

        delta = end_time - self.started_at
        return int(delta.total_seconds() * 1000)

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "report_id": "ATM",
                "parameters": {"cod_ibge": "2304400", "ano": 2024},
                "status": "completed",
                "created_at": "2024-01-24T10:00:00Z",
                "started_at": "2024-01-24T10:00:02Z",
                "completed_at": "2024-01-24T10:00:15Z",
                "result": {
                    "gcs_path": "gs://segape-reports/ATM/2304400-2024.pdf",
                    "size_bytes": 524288,
                    "cached": False
                }
            }
        }


class JobResponse(BaseModel):
    """API response model for job status."""

    job_id: str = Field(..., description="Job identifier")
    status: JobStatus
    report_id: str
    parameters: Dict[str, Any]

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    # Results
    result: Optional[JobResult] = None
    error: Optional[str] = None
    attempts: Optional[int] = None
    duration_ms: Optional[int] = None

    # Progress info (optional, for processing jobs)
    progress: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Current progress information",
        examples=[{"stage": "queries", "message": "Executing 3 of 10 queries..."}]
    )

    @computed_field  # type: ignore[misc]
    @property
    def links(self) -> Dict[str, str]:
        """Generate resource links."""
        return {
            "self": f"/jobs/{self.job_id}",
            "download": f"/jobs/{self.job_id}/download"
        }

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "report_id": "ATM",
                "parameters": {"cod_ibge": "2304400", "ano": 2024},
                "created_at": "2024-01-24T10:00:00Z",
                "started_at": "2024-01-24T10:00:02Z",
                "completed_at": "2024-01-24T10:00:15Z",
                "duration_ms": 13000,
                "result": {
                    "gcs_path": "gs://segape-reports/ATM/2304400-2024.pdf",
                    "size_bytes": 524288,
                    "cached": False
                },
                "links": {
                    "self": "/jobs/550e8400-e29b-41d4-a716-446655440000",
                    "download": "/jobs/550e8400-e29b-41d4-a716-446655440000/download"
                }
            }
        }
