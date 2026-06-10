"""Tests for Job models."""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from schoolreport.models.job import (
    JobStatus,
    Job,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobResult,
)


class TestJobStatus:
    """Test JobStatus enum."""

    def test_job_status_values(self):
        """JobStatus should have all required states."""
        assert JobStatus.QUEUED == "queued"
        assert JobStatus.PROCESSING == "processing"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"

    def test_job_status_members(self):
        """JobStatus should have exactly 5 states."""
        assert len(JobStatus) == 5


class TestJobCreate:
    """Test JobCreate Pydantic model."""

    def test_create_job_minimal(self):
        """Should create job with minimal required fields."""
        job_create = JobCreate(
            report_id="ATM",
            parameters={"cod_ibge": "2304400", "ano": 2024}
        )
        assert job_create.report_id == "ATM"
        assert job_create.parameters == {"cod_ibge": "2304400", "ano": 2024}
        assert job_create.requester is None

    def test_create_job_with_requester(self):
        """Should create job with requester."""
        job_create = JobCreate(
            report_id="ATSBR",
            parameters={},
            requester="user@example.com"
        )
        assert job_create.requester == "user@example.com"

    def test_create_job_empty_parameters(self):
        """Should allow empty parameters."""
        job_create = JobCreate(report_id="ATSBR", parameters={})
        assert job_create.parameters == {}

    def test_create_job_invalid_report_id(self):
        """Should validate report_id is non-empty string."""
        with pytest.raises(ValueError):
            JobCreate(report_id="", parameters={})


class TestJobUpdate:
    """Test JobUpdate Pydantic model."""

    def test_update_status(self):
        """Should update job status."""
        update = JobUpdate(status=JobStatus.PROCESSING)
        assert update.status == JobStatus.PROCESSING
        assert update.started_at is None
        assert update.completed_at is None
        assert update.error is None
        assert update.result is None

    def test_update_with_timestamps(self):
        """Should update with timestamps."""
        now = datetime.now(timezone.utc)
        update = JobUpdate(
            status=JobStatus.COMPLETED,
            started_at=now,
            completed_at=now
        )
        assert update.started_at == now
        assert update.completed_at == now

    def test_update_with_error(self):
        """Should update with error message."""
        update = JobUpdate(
            status=JobStatus.FAILED,
            error="BigQuery timeout"
        )
        assert update.status == JobStatus.FAILED
        assert update.error == "BigQuery timeout"

    def test_update_with_result(self):
        """Should update with result."""
        result = JobResult(
            gcs_path="gs://bucket/report.pdf",
            size_bytes=524288,
            cached=False
        )
        update = JobUpdate(status=JobStatus.COMPLETED, result=result)
        assert update.result == result


class TestJobResult:
    """Test JobResult Pydantic model."""

    def test_create_result_minimal(self):
        """Should create result with minimal fields."""
        result = JobResult(
            gcs_path="gs://bucket/ATM/report.pdf",
            size_bytes=100000
        )
        assert result.gcs_path == "gs://bucket/ATM/report.pdf"
        assert result.size_bytes == 100000
        assert result.cached is False  # default

    def test_create_result_cached(self):
        """Should create result for cached report."""
        result = JobResult(
            gcs_path="gs://bucket/ATM/report.pdf",
            size_bytes=100000,
            cached=True
        )
        assert result.cached is True

    def test_result_size_validation(self):
        """Should validate size_bytes is positive."""
        with pytest.raises(ValueError):
            JobResult(gcs_path="gs://bucket/report.pdf", size_bytes=-1)


class TestJob:
    """Test Job Pydantic model (domain model)."""

    def test_create_job(self):
        """Should create job with auto-generated ID and timestamps."""
        job = Job(
            report_id="ATM",
            parameters={"cod_ibge": "2304400"},
            status=JobStatus.QUEUED
        )

        # Auto-generated fields
        assert isinstance(job.id, UUID)
        assert isinstance(job.created_at, datetime)

        # Provided fields
        assert job.report_id == "ATM"
        assert job.parameters == {"cod_ibge": "2304400"}
        assert job.status == JobStatus.QUEUED

        # Optional fields should be None
        assert job.requester is None
        assert job.started_at is None
        assert job.completed_at is None
        assert job.failed_at is None
        assert job.error is None
        assert job.result is None
        assert job.attempts == 0

    def test_job_with_requester(self):
        """Should create job with requester."""
        job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.QUEUED,
            requester="admin@segape.gov.br"
        )
        assert job.requester == "admin@segape.gov.br"

    def test_job_processing(self):
        """Should track processing timestamps."""
        now = datetime.now(timezone.utc)
        job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.PROCESSING,
            started_at=now,
            attempts=1
        )
        assert job.status == JobStatus.PROCESSING
        assert job.started_at == now
        assert job.attempts == 1

    def test_job_completed(self):
        """Should track completion with result."""
        now = datetime.now(timezone.utc)
        result = JobResult(
            gcs_path="gs://bucket/report.pdf",
            size_bytes=100000
        )
        job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.COMPLETED,
            started_at=now,
            completed_at=now,
            result=result
        )
        assert job.status == JobStatus.COMPLETED
        assert job.completed_at == now
        assert job.result == result

    def test_job_failed(self):
        """Should track failure with error."""
        now = datetime.now(timezone.utc)
        job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.FAILED,
            started_at=now,
            failed_at=now,
            error="Query timeout",
            attempts=3
        )
        assert job.status == JobStatus.FAILED
        assert job.failed_at == now
        assert job.error == "Query timeout"
        assert job.attempts == 3

    def test_job_duration_ms(self):
        """Should calculate duration in milliseconds."""
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 13, 500000, tzinfo=timezone.utc)  # 13.5 seconds

        job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.COMPLETED,
            started_at=start,
            completed_at=end
        )

        assert job.duration_ms == 13500

    def test_job_duration_ms_not_completed(self):
        """Should return None for duration if not completed."""
        job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.PROCESSING
        )
        assert job.duration_ms is None


class TestJobResponse:
    """Test JobResponse API response model."""

    def test_response_minimal(self):
        """Should create response with minimal fields."""
        response = JobResponse(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            status=JobStatus.QUEUED,
            report_id="ATM",
            parameters={"cod_ibge": "2304400"},
            created_at=datetime.now(timezone.utc)
        )

        assert response.job_id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.status == JobStatus.QUEUED
        assert response.report_id == "ATM"

    def test_response_with_links(self):
        """Should include links to job resources."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        response = JobResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            report_id="ATM",
            parameters={},
            created_at=datetime.now(timezone.utc)
        )

        # Links should be generated
        assert response.links is not None
        assert response.links["self"] == f"/jobs/{job_id}"
        assert response.links["download"] == f"/jobs/{job_id}/download"

    def test_response_completed_with_result(self):
        """Should include result when completed."""
        result = JobResult(
            gcs_path="gs://bucket/report.pdf",
            size_bytes=100000,
            cached=False
        )
        response = JobResponse(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            status=JobStatus.COMPLETED,
            report_id="ATM",
            parameters={},
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            result=result
        )

        assert response.result == result
        assert response.status == JobStatus.COMPLETED

    def test_response_failed_with_error(self):
        """Should include error when failed."""
        response = JobResponse(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            status=JobStatus.FAILED,
            report_id="ATM",
            parameters={},
            created_at=datetime.now(timezone.utc),
            failed_at=datetime.now(timezone.utc),
            error="Query failed: Table not found"
        )

        assert response.status == JobStatus.FAILED
        assert response.error == "Query failed: Table not found"

    def test_response_with_duration(self):
        """Should include duration_ms when completed."""
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 10, tzinfo=timezone.utc)

        response = JobResponse(
            job_id="550e8400-e29b-41d4-a716-446655440000",
            status=JobStatus.COMPLETED,
            report_id="ATM",
            parameters={},
            created_at=start,
            started_at=start,
            completed_at=end,
            duration_ms=10000
        )

        assert response.duration_ms == 10000
