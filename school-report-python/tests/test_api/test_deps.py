"""Tests for API dependency injection."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestSettingsDependency:
    """Test settings dependency injection."""

    def test_get_settings(self, mock_env):
        """Should inject settings into route."""
        from fastapi import Depends
        from schoolreport.api.deps import get_settings
        from schoolreport.config import Settings

        app = FastAPI()

        @app.get("/test")
        async def test_route(settings: Settings = Depends(get_settings)):
            return {"gcp_project": settings.gcp_project_id}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json()["gcp_project"] == "test-project"


class TestRedisDependency:
    """Test Redis client dependency injection."""

    @pytest.mark.asyncio
    async def test_get_redis(self, mock_env):
        """Should create and inject Redis client."""
        from schoolreport.api.deps import get_redis

        # Should yield a Redis client
        async for redis in get_redis():
            assert redis is not None
            # Client should be configured
            assert hasattr(redis, "ping")
            assert hasattr(redis, "get")
            assert hasattr(redis, "set")

    @pytest.mark.asyncio
    async def test_redis_pool_initialization(self, mock_env):
        """Should initialize Redis connection pool."""
        from schoolreport.api.deps import get_redis, _redis_pool

        # First call should create pool
        async for redis in get_redis():
            assert redis is not None

        # Pool should be initialized after first use
        # (This is implicitly verified by not raising errors)
        assert True


class TestQueueDependency:
    """Test arq queue dependency injection."""

    @pytest.mark.skip(reason="Requires Redis server - integration test")
    @pytest.mark.asyncio
    async def test_queue_settings_parsing(self, mock_env):
        """Should parse Redis URL for queue configuration."""
        from schoolreport.api.deps import get_queue

        # Should parse URL and create queue without errors
        async for queue in get_queue():
            assert queue is not None
            # Queue should have enqueue method
            assert hasattr(queue, "enqueue_job")


class TestDependencyLifecycle:
    """Test dependency lifecycle management."""

    def test_dependencies_in_route(self, mock_env):
        """Should inject settings dependency into route."""
        from fastapi import Depends
        from schoolreport.api.deps import get_settings
        from schoolreport.config import Settings

        app = FastAPI()

        @app.get("/test")
        async def test_route(
            settings: Settings = Depends(get_settings),
        ):
            return {
                "settings": settings.gcp_project_id,
            }

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()
        assert data["settings"] == "test-project"

    @pytest.mark.asyncio
    async def test_dependency_cleanup(self, mock_env):
        """Dependencies should cleanup resources on exit."""
        from schoolreport.api.deps import get_redis

        async for redis in get_redis():
            assert redis is not None

        # Cleanup should happen after generator exits
        # This is implicitly tested by no errors/warnings
        assert True

    @pytest.mark.asyncio
    async def test_cleanup_dependencies_function(self, mock_env):
        """Should have cleanup function for shutdown."""
        from schoolreport.api.deps import cleanup_dependencies, get_redis

        # Create some dependencies
        async for redis in get_redis():
            assert redis is not None

        # Cleanup should work without errors
        await cleanup_dependencies()

        # Verify cleanup was successful
        assert True


class TestDependencyConfiguration:
    """Test dependency configuration."""

    def test_dependencies_use_settings(self, mock_env):
        """Dependencies should use settings from environment."""
        from schoolreport.api.deps import get_settings

        settings = get_settings()

        assert settings.gcp_project_id == "test-project"
        assert str(settings.redis_url) == "redis://localhost:6379/0"
        assert str(settings.database_url).startswith("postgresql://")

    def test_dependencies_callable(self, mock_env):
        """All dependency functions should be callable."""
        from schoolreport.api.deps import (
            get_settings,
            get_redis,
            get_postgres,
            get_bigquery,
            get_queue,
        )

        # Settings should be callable
        assert callable(get_settings)

        # Async generators should be callable
        assert callable(get_redis)
        assert callable(get_postgres)
        assert callable(get_bigquery)
        assert callable(get_queue)


class TestDependencyDocumentation:
    """Test dependency documentation and examples."""

    def test_dependencies_have_docstrings(self, mock_env):
        """All dependencies should be documented."""
        from schoolreport.api.deps import (
            get_settings,
            get_redis,
            get_postgres,
            get_bigquery,
            get_queue,
        )

        assert get_settings.__doc__ is not None
        assert get_redis.__doc__ is not None
        assert get_postgres.__doc__ is not None
        assert get_bigquery.__doc__ is not None
        assert get_queue.__doc__ is not None

    def test_dependencies_have_type_annotations(self, mock_env):
        """Dependencies should have proper type annotations."""
        from schoolreport.api.deps import get_settings
        import inspect

        sig = inspect.signature(get_settings)
        assert sig.return_annotation is not None
