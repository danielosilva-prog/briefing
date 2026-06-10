"""Tests for health check endpoints."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient


@pytest.fixture
def client(test_app):
    """Create test client."""
    from fastapi.testclient import TestClient
    return TestClient(test_app)


class TestHealthEndpoint:
    """Test GET /health endpoint."""

    def test_health_check_success(self, client):
        """Should return 200 OK with status and timestamp."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

        # Timestamp should be valid ISO format
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        assert isinstance(timestamp, datetime)

    def test_health_check_includes_version(self, client):
        """Should include application version."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


class TestReadinessEndpoint:
    """Test GET /ready endpoint (Kubernetes readiness probe)."""

    def test_readiness_check_success(self, client):
        """Should return 200 OK when all dependencies are ready."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    def test_readiness_includes_dependency_checks(self, client):
        """Should include status of all dependencies."""
        response = client.get("/ready")

        assert response.status_code == 200
        data = response.json()

        checks = data["checks"]

        # Should check key dependencies
        assert "redis" in checks
        assert "postgres" in checks

        # Each check should have status
        for service, check_result in checks.items():
            assert "status" in check_result
            assert check_result["status"] in ["healthy", "unhealthy"]

    def test_readiness_fails_when_dependency_down(self, client_with_redis_down):
        """Should return 503 when critical dependency is down."""
        response = client_with_redis_down.get("/ready")

        assert response.status_code == 503
        data = response.json()

        assert data["status"] == "not_ready"
        assert data["checks"]["redis"]["status"] == "unhealthy"

    def test_readiness_includes_error_details(self, client_with_redis_down):
        """Should include error details for failed checks."""
        response = client_with_redis_down.get("/ready")

        assert response.status_code == 503
        data = response.json()

        redis_check = data["checks"]["redis"]
        assert "error" in redis_check
        assert isinstance(redis_check["error"], str)


class TestHealthMetadata:
    """Test health endpoint metadata."""

    def test_health_response_schema(self, client):
        """Health response should match expected schema."""
        response = client.get("/health")
        data = response.json()

        # Required fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

        # Optional fields
        assert "uptime_seconds" in data or True  # optional

    def test_readiness_response_schema(self, client):
        """Readiness response should match expected schema."""
        response = client.get("/ready")
        data = response.json()

        # Required fields
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)

        # Each check should have consistent structure
        for service, check in data["checks"].items():
            assert "status" in check
            if check["status"] == "unhealthy":
                assert "error" in check
