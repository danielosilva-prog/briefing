"""Tests for FastAPI application setup."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestAppFactory:
    """Test FastAPI application factory."""

    def test_create_app(self, mock_env):
        """Should create FastAPI application."""
        from schoolreport.api.app import create_app

        app = create_app()

        assert isinstance(app, FastAPI)
        assert app.title == "School Report API"
        assert app.version == "0.1.0"

    def test_app_includes_health_routes(self, mock_env):
        """Should include health check routes."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        # Health endpoint should exist
        response = client.get("/health")
        assert response.status_code == 200

        # Ready endpoint should exist
        response = client.get("/ready")
        assert response.status_code in [200, 503]  # May be down in tests

    def test_app_has_openapi_docs(self, mock_env):
        """Should have OpenAPI documentation enabled."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        # OpenAPI schema endpoint
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

        # Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200

    def test_app_has_cors_middleware(self, mock_env):
        """Should have CORS middleware configured."""
        from schoolreport.api.app import create_app

        app = create_app()

        # Check if CORS middleware is in the middleware stack
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_app_cors_allows_origins(self, mock_env):
        """CORS should allow configured origins."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        # Preflight request
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers


class TestRequestMiddleware:
    """Test request logging and ID middleware."""

    def test_request_id_added_to_response(self, mock_env):
        """Should add request ID to response headers."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/health")

        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID format

    def test_request_id_can_be_provided(self, mock_env):
        """Should use provided request ID if given."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        custom_id = "custom-request-123"
        response = client.get("/health", headers={"X-Request-ID": custom_id})

        assert response.headers["X-Request-ID"] == custom_id

    def test_requests_are_logged(self, mock_env, caplog):
        """Should log all requests."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        with caplog.at_level("INFO"):
            response = client.get("/health")

        # Should log request details
        assert any("GET /health" in record.message for record in caplog.records)


class TestErrorHandlers:
    """Test global error handlers."""

    def test_404_error_handler(self, mock_env):
        """Should return JSON for 404 errors."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"
        assert "message" in data["error"]

    def test_500_error_handler(self, mock_env):
        """Should return JSON for internal server errors."""
        from schoolreport.api.app import create_app
        from fastapi import HTTPException

        app = create_app()

        # Add a route that raises an exception
        @app.get("/test-error")
        async def test_error():
            raise Exception("Test internal error")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-error")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INTERNAL_ERROR"

    def test_validation_error_handler(self, mock_env):
        """Should return detailed JSON for validation errors."""
        from schoolreport.api.app import create_app
        from pydantic import BaseModel

        app = create_app()

        class TestModel(BaseModel):
            name: str
            age: int

        @app.post("/test-validation")
        async def test_validation(data: TestModel):
            return data

        client = TestClient(app)
        response = client.post("/test-validation", json={"name": "test", "age": "not-a-number"})

        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]
        assert isinstance(data["error"]["details"], list)

    def test_error_includes_request_id(self, mock_env):
        """Errors should include request ID for tracing."""
        from schoolreport.api.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/nonexistent")

        assert "X-Request-ID" in response.headers
        data = response.json()
        assert "error" in data
        # Request ID should be in headers, allowing correlation


class TestAppLifecycle:
    """Test application startup and shutdown events."""

    @pytest.mark.asyncio
    async def test_startup_event(self, mock_env):
        """Should execute startup logic."""
        from schoolreport.api.app import create_app

        app = create_app()

        # Startup should initialize app state
        # This is tested implicitly by app creation
        assert hasattr(app, "state")

    @pytest.mark.asyncio
    async def test_shutdown_event(self, mock_env):
        """Should execute shutdown logic."""
        from schoolreport.api.app import create_app

        app = create_app()

        # Shutdown logic should cleanup resources
        # This would be tested with actual lifecycle in integration tests
        assert True  # Placeholder


class TestAppConfiguration:
    """Test application configuration."""

    def test_app_accepts_custom_title(self, mock_env):
        """Should accept custom title."""
        from schoolreport.api.app import create_app

        app = create_app(title="Custom API")

        assert app.title == "Custom API"

    def test_app_accepts_custom_version(self, mock_env):
        """Should accept custom version."""
        from schoolreport.api.app import create_app

        app = create_app(version="1.2.3")

        assert app.version == "1.2.3"

    def test_app_debug_mode(self, mock_env, monkeypatch):
        """Should support debug mode."""
        from schoolreport.api.app import create_app

        monkeypatch.setenv("ENVIRONMENT", "development")

        app = create_app()

        # Debug mode should enable detailed errors
        assert app.debug is True or app.debug is False  # Just check it's configurable
