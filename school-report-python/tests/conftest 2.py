"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def mock_gcp_credentials(monkeypatch, tmp_path):
    """Mock GCP credentials for testing."""
    credentials_file = tmp_path / "test-credentials.json"
    credentials_file.write_text('{"type": "service_account", "project_id": "test-project"}')
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(credentials_file))
    return credentials_file


@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings singleton before and after each test."""
    from schoolreport.config import reset_settings
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("GCS_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    return redis_mock


@pytest.fixture
def mock_redis_down():
    """Mock Redis client that's down."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(side_effect=ConnectionError("Connection refused"))
    return redis_mock


@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL client."""
    postgres_mock = AsyncMock()
    postgres_mock.fetchval = AsyncMock(return_value=1)  # SELECT 1
    return postgres_mock


@pytest.fixture
def mock_postgres_down():
    """Mock PostgreSQL client that's down."""
    postgres_mock = AsyncMock()
    postgres_mock.fetchval = AsyncMock(side_effect=ConnectionError("Connection refused"))
    return postgres_mock


@pytest.fixture
def test_app(mock_env, mock_redis, mock_postgres):
    """Create FastAPI test application with mocked dependencies."""
    from fastapi import FastAPI
    from schoolreport.api.routes.health import router as health_router

    app = FastAPI(title="Test App")
    app.include_router(health_router)

    # Store mocks on app state for dependency overrides
    app.state.redis = mock_redis
    app.state.postgres = mock_postgres

    return app


@pytest.fixture
def client_with_redis_down(mock_env, mock_redis_down, mock_postgres):
    """Create test client with Redis down."""
    from fastapi import FastAPI
    from schoolreport.api.routes.health import router as health_router

    app = FastAPI(title="Test App")
    app.include_router(health_router)

    app.state.redis = mock_redis_down
    app.state.postgres = mock_postgres

    from fastapi.testclient import TestClient
    return TestClient(app)
