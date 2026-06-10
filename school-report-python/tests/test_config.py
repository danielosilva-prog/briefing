"""Tests for configuration module."""

import pytest
from pydantic import ValidationError
from schoolreport.config import Settings


class TestSettings:
    """Test Settings class."""

    def test_settings_from_env(self, mock_env):
        """Test loading settings from environment variables."""
        settings = Settings()

        assert settings.gcp_project_id == "test-project"
        assert settings.database_url.unicode_string() == "postgresql://test:test@localhost:5432/test"
        assert settings.redis_url.unicode_string() == "redis://localhost:6379/0"
        assert settings.gcs_bucket_name == "test-bucket"
        assert settings.environment == "test"
        assert settings.log_level == "DEBUG"

    def test_settings_defaults(self, monkeypatch):
        """Test settings with default values."""
        # Clear all environment variables
        for key in ["GCP_PROJECT_ID", "DATABASE_URL", "REDIS_URL", "GCS_BUCKET_NAME"]:
            monkeypatch.delenv(key, raising=False)

        # Set only required ones
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")
        monkeypatch.setenv("REDIS_URL", "redis://localhost/0")

        settings = Settings()

        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.api_workers == 4
        assert settings.worker_concurrency == 5
        assert settings.worker_max_retries == 3
        assert settings.cache_ttl_days == 30
        assert settings.environment == "development"
        assert settings.log_level == "INFO"

    def test_settings_missing_required(self, monkeypatch):
        """Test validation error when required settings missing."""
        monkeypatch.delenv("GCP_PROJECT_ID", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_invalid_port(self, mock_env, monkeypatch):
        """Test validation error for invalid port."""
        monkeypatch.setenv("API_PORT", "invalid")

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_api_configuration(self, mock_env, monkeypatch):
        """Test API-specific configuration."""
        monkeypatch.setenv("API_HOST", "127.0.0.1")
        monkeypatch.setenv("API_PORT", "9000")
        monkeypatch.setenv("API_WORKERS", "8")

        settings = Settings()

        assert settings.api_host == "127.0.0.1"
        assert settings.api_port == 9000
        assert settings.api_workers == 8

    def test_settings_worker_configuration(self, mock_env, monkeypatch):
        """Test worker-specific configuration."""
        monkeypatch.setenv("WORKER_CONCURRENCY", "10")
        monkeypatch.setenv("WORKER_MAX_RETRIES", "5")

        settings = Settings()

        assert settings.worker_concurrency == 10
        assert settings.worker_max_retries == 5

    def test_settings_cache_configuration(self, mock_env, monkeypatch):
        """Test cache configuration."""
        monkeypatch.setenv("CACHE_TTL_DAYS", "7")

        settings = Settings()

        assert settings.cache_ttl_days == 7

    def test_settings_legacy_r_service(self, mock_env, monkeypatch):
        """Test legacy R service configuration."""
        monkeypatch.setenv("LEGACY_R_SERVICE_URL", "http://legacy-r:8080")
        monkeypatch.setenv("LEGACY_ENABLED", "false")

        settings = Settings()

        assert settings.legacy_r_service_url == "http://legacy-r:8080"
        assert settings.legacy_enabled is False

    def test_settings_gcs_bucket(self, mock_env, monkeypatch):
        """Test GCS bucket configuration."""
        monkeypatch.setenv("GCS_BUCKET_NAME", "my-reports-bucket")

        settings = Settings()

        assert settings.gcs_bucket_name == "my-reports-bucket"

    def test_settings_environment_prod(self, mock_env, monkeypatch):
        """Test production environment configuration."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")

        settings = Settings()

        assert settings.environment == "production"
        assert settings.log_level == "WARNING"

    def test_settings_google_application_credentials(self, mock_env, monkeypatch):
        """Test GOOGLE_APPLICATION_CREDENTIALS configuration."""
        monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/path/to/creds.json")

        settings = Settings()

        assert settings.google_application_credentials == "/path/to/creds.json"

    def test_settings_no_google_application_credentials(self, mock_env, monkeypatch):
        """Test when GOOGLE_APPLICATION_CREDENTIALS is not set."""
        monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

        settings = Settings()

        assert settings.google_application_credentials is None

    def test_settings_model_config(self, mock_env):
        """Test that Settings uses correct model config."""
        settings = Settings()

        # Should be case-insensitive
        assert settings.model_config["case_sensitive"] is False
        # Should read from .env file
        assert settings.model_config["env_file"] == ".env"
