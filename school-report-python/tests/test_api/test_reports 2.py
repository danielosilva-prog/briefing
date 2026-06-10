"""Tests for Reports API routes."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from uuid import uuid4


@pytest.fixture
def mock_job_service():
    """Mock job service for testing."""
    from schoolreport.models.job import Job, JobStatus

    service = AsyncMock()

    # Mock job creation
    mock_job = Job(
        id=str(uuid4()),
        report_id="ATM",
        parameters={"cod_ibge": "2304400", "ano": 2024},
        status=JobStatus.QUEUED
    )
    service.create_job = AsyncMock(return_value=mock_job)

    return service


class TestListReportsEndpoint:
    """Test GET /reports endpoint."""

    def test_list_reports(self, mock_env):
        """Should list all available reports."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/reports")

        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)
        assert len(data["reports"]) > 0

    def test_list_reports_includes_metadata(self, mock_env):
        """Should include report metadata."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/reports")

        assert response.status_code == 200
        reports = response.json()["reports"]

        # Check first report has required fields
        report = reports[0]
        assert "id" in report
        assert "name" in report
        assert "description" in report
        assert "parameters" in report

    def test_list_reports_includes_atm(self, mock_env):
        """Should include ATM report."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/reports")

        reports = response.json()["reports"]
        atm_report = next((r for r in reports if r["id"] == "ATM"), None)

        assert atm_report is not None
        assert atm_report["name"] == "Aqui Tem MEC 2"


class TestGetReportEndpoint:
    """Test GET /reports/{report_id} endpoint."""

    def test_get_report_success(self, mock_env):
        """Should get report metadata."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/reports/ATM")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "ATM"
        assert data["name"] == "Aqui Tem MEC 2"
        assert "parameters" in data

    def test_get_report_not_found(self, mock_env):
        """Should return 404 for unknown report."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/reports/UNKNOWN")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data or "error" in data


class TestGenerateReportEndpoint:
    """Test POST /reports/{report_id}/generate endpoint."""

    def test_generate_report_success(self, mock_env, mock_job_service):
        """Should create job for report generation."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.post(
            "/reports/ATM/generate",
            json={
                "parameters": {"cod_ibge": "2304400", "ano": 2024}
            }
        )

        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert data["report_id"] == "ATM"

    def test_generate_report_with_requester(self, mock_env, mock_job_service):
        """Should include requester in job."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.post(
            "/reports/ATM/generate",
            json={
                "parameters": {"cod_ibge": "2304400"},
                "requester": "admin@segape.gov.br"
            }
        )

        assert response.status_code == 202
        mock_job_service.create_job.assert_called_once()
        call_args = mock_job_service.create_job.call_args
        assert call_args.kwargs["requester"] == "admin@segape.gov.br"

    def test_generate_report_invalid_report_id(self, mock_env, mock_job_service):
        """Should return 404 for unknown report type."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.post(
            "/reports/UNKNOWN/generate",
            json={"parameters": {}}
        )

        assert response.status_code == 404

    def test_generate_report_returns_job_links(self, mock_env, mock_job_service):
        """Should include links in response."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router
        from schoolreport.services.job_service import get_job_service

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_job_service] = lambda: mock_job_service

        client = TestClient(app)
        response = client.post(
            "/reports/ATM/generate",
            json={"parameters": {"cod_ibge": "2304400"}}
        )

        assert response.status_code == 202
        data = response.json()
        assert "links" in data
        assert "self" in data["links"]


class TestReportsRouteIntegration:
    """Test reports routes integration."""

    def test_routes_registered(self, mock_env):
        """Should register all report routes."""
        from fastapi import FastAPI
        from schoolreport.api.routes.reports import router

        app = FastAPI()
        app.include_router(router)

        client = TestClient(app)
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()
        paths = schema["paths"]

        assert "/reports" in paths
        assert "/reports/{report_id}" in paths
        assert "/reports/{report_id}/generate" in paths

    def test_routes_have_tags(self, mock_env):
        """Routes should be tagged for documentation."""
        from schoolreport.api.routes.reports import router

        assert router.tags == ["reports"]
