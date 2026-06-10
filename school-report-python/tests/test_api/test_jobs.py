"""Tests for Jobs API routes."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_job_service():
    """Mock job service for testing."""
    from unittest.mock import AsyncMock
    from schoolreport.models.job import Job, JobStatus, JobResult

    service = AsyncMock()

    # Mock job data
    job_id = str(uuid4())
    mock_job = Job(
        id=job_id,
        report_id="ATM",
        parameters={"cod_ibge": "2304400"},
        status=JobStatus.COMPLETED,
        created_at=datetime.now(timezone.utc),
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        result=JobResult(
            gcs_path="gs://bucket/report.pdf",
            size_bytes=100000,
            cached=False
        )
    )

    service.get_job = AsyncMock(return_value=mock_job)
    service.list_jobs = AsyncMock(return_value=([mock_job], 1))
    service.cancel_job = AsyncMock(return_value=mock_job)
    service.download_job = AsyncMock(return_value=b"PDF content")

    return service


class TestListJobsEndpoint:
    """Test GET /jobs endpoint."""

    def test_list_jobs_success(self, mock_env, mock_job_service):
        """Should list all jobs."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)

        # Override job service dependency
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.get("/jobs")

        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)
        assert len(data["jobs"]) > 0

    def test_list_jobs_with_status_filter(self, mock_env, mock_job_service):
        """Should filter jobs by status."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.get("/jobs?status=completed")

        assert response.status_code == 200
        mock_job_service.list_jobs.assert_called_once()

    def test_list_jobs_with_report_id_filter(self, mock_env, mock_job_service):
        """Should filter jobs by report_id."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.get("/jobs?report_id=ATM")

        assert response.status_code == 200

    def test_list_jobs_pagination(self, mock_env, mock_job_service):
        """Should support pagination."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.get("/jobs?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data


class TestGetJobEndpoint:
    """Test GET /jobs/{job_id} endpoint."""

    def test_get_job_success(self, mock_env, mock_job_service):
        """Should get job by ID."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router

        app = FastAPI()
        app.include_router(router)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert "report_id" in data

    def test_get_job_not_found(self, mock_env, mock_job_service):
        """Should return 404 for non-existent job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router

        app = FastAPI()
        app.include_router(router)

        from schoolreport.services.job_service import get_job_service
        mock_job_service.get_job = AsyncMock(return_value=None)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "error" in data

    def test_get_job_includes_links(self, mock_env, mock_job_service):
        """Should include resource links."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router

        app = FastAPI()
        app.include_router(router)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert "links" in data
        assert "self" in data["links"]
        assert "download" in data["links"]


class TestDownloadJobEndpoint:
    """Test GET /jobs/{job_id}/download endpoint."""

    def test_download_completed_job(self, mock_env, mock_job_service):
        """Should download PDF for completed job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router

        app = FastAPI()
        app.include_router(router)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.get(f"/jobs/{job_id}/download")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "content-disposition" in response.headers
        assert response.content == b"PDF content"

    def test_download_pending_job_fails(self, mock_env, mock_job_service):
        """Should return 400 for pending job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.models.job import Job, JobStatus

        app = FastAPI()
        app.include_router(router)

        pending_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.QUEUED
        )
        mock_job_service.get_job = AsyncMock(return_value=pending_job)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.get(f"/jobs/{job_id}/download")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "error" in data

    def test_download_failed_job_fails(self, mock_env, mock_job_service):
        """Should return 400 for failed job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.models.job import Job, JobStatus

        app = FastAPI()
        app.include_router(router)

        failed_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.FAILED,
            error="Query timeout"
        )
        mock_job_service.get_job = AsyncMock(return_value=failed_job)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.get(f"/jobs/{job_id}/download")

        assert response.status_code == 400


class TestCancelJobEndpoint:
    """Test DELETE /jobs/{job_id} endpoint."""

    def test_cancel_pending_job(self, mock_env, mock_job_service):
        """Should cancel pending job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.models.job import Job, JobStatus

        app = FastAPI()
        app.include_router(router)

        # Mock a queued job
        queued_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.QUEUED
        )
        cancelled_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.CANCELLED
        )
        mock_job_service.get_job = AsyncMock(return_value=queued_job)
        mock_job_service.cancel_job = AsyncMock(return_value=cancelled_job)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.delete(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data

    def test_cancel_processing_job(self, mock_env, mock_job_service):
        """Should cancel processing job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.models.job import Job, JobStatus

        app = FastAPI()
        app.include_router(router)

        # Mock a processing job
        processing_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.PROCESSING
        )
        cancelled_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.CANCELLED
        )
        mock_job_service.get_job = AsyncMock(return_value=processing_job)
        mock_job_service.cancel_job = AsyncMock(return_value=cancelled_job)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.delete(f"/jobs/{job_id}")

        assert response.status_code == 200

    def test_cancel_completed_job_fails(self, mock_env, mock_job_service):
        """Should not cancel completed job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router
        from schoolreport.models.job import Job, JobStatus, JobResult

        app = FastAPI()
        app.include_router(router)

        completed_job = Job(
            report_id="ATM",
            parameters={},
            status=JobStatus.COMPLETED,
            result=JobResult(gcs_path="gs://bucket/report.pdf", size_bytes=100000)
        )
        mock_job_service.get_job = AsyncMock(return_value=completed_job)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.delete(f"/jobs/{job_id}")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data or "error" in data

    def test_cancel_nonexistent_job(self, mock_env, mock_job_service):
        """Should return 404 for non-existent job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router

        app = FastAPI()
        app.include_router(router)

        mock_job_service.get_job = AsyncMock(return_value=None)

        from schoolreport.services.job_service import get_job_service
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        job_id = str(uuid4())
        client = TestClient(app)
        response = client.delete(f"/jobs/{job_id}")

        assert response.status_code == 404


class TestJobsRouteIntegration:
    """Test jobs routes integration."""

    def test_routes_registered(self, mock_env):
        """Should register all job routes."""
        from fastapi import FastAPI
        from schoolreport.api.routes.jobs import router

        app = FastAPI()
        app.include_router(router)

        # Check routes exist in OpenAPI schema
        client = TestClient(app)
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        paths = schema["paths"]

        assert "/jobs" in paths
        assert "/jobs/{job_id}" in paths
        assert "/jobs/{job_id}/download" in paths

    def test_routes_have_tags(self, mock_env):
        """Routes should be tagged for documentation."""
        from schoolreport.api.routes.jobs import router

        assert router.tags == ["jobs"]
