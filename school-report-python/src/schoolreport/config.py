"""Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_gcp_project_id() -> Optional[str]:
    """Try to extract project_id from a GCP credentials JSON file.

    Checks (in order):
    1. GOOGLE_APPLICATION_CREDENTIALS env var path
    2. .gcp-credentials.json in project root
    """
    candidates = []

    env_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path:
        candidates.append(Path(env_path))

    candidates.append(Path(".gcp-credentials.json"))

    for path in candidates:
        if path.is_file():
            try:
                data = json.loads(path.read_text())
                project_id = data.get("project_id")
                if project_id:
                    return project_id
            except (json.JSONDecodeError, OSError):
                continue

    return None


class LocalSettings(BaseSettings):
    """Minimal settings for local CLI execution.

    This settings class only requires what's needed for local report generation,
    without the infrastructure requirements (PostgreSQL, Redis) needed by the
    API and workers.

    Required:
        - gcp_project_id: For BigQuery access (auto-resolved from credentials file if not set)

    Optional:
        - google_application_credentials: Path to service account JSON
        - gcs_bucket_name: Only needed if using --upload flag
    """

    # Google Cloud Platform - auto-resolved from credentials file if not set
    gcp_project_id: Optional[str] = Field(
        None,
        description="GCP project ID for BigQuery access",
    )
    google_application_credentials: Optional[str] = Field(
        None,
        description="Path to GCP service account JSON file",
    )

    # Google Cloud Storage - optional, only needed for --upload
    gcs_bucket_name: Optional[str] = Field(
        None,
        description="GCS bucket name for storing reports (only needed with --upload)",
    )

    # Query execution settings
    query_max_concurrency: int = Field(
        10,
        description="Maximum concurrent BigQuery queries (semaphore limit)",
        ge=1,
        le=50,
    )

    # Query caching settings
    query_cache_enabled: bool = Field(
        True,
        description="Enable local disk caching of BigQuery results",
    )
    query_cache_ttl_seconds: int = Field(
        2592000,
        description="Cache TTL in seconds (default 30 days, content-based invalidation)",
        ge=0,
    )
    query_cache_dir: Optional[str] = Field(
        None,
        description="Custom cache directory (defaults to ~/.cache/schoolreport/queries)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def resolve_gcp_project_id(self) -> "LocalSettings":
        """Auto-resolve gcp_project_id from credentials file if not set."""
        if self.gcp_project_id is None:
            resolved = _resolve_gcp_project_id()
            if resolved:
                self.gcp_project_id = resolved
            else:
                raise ValueError(
                    "gcp_project_id is required but was not found. "
                    "Set GCP_PROJECT_ID in your environment or .env file, "
                    "or ensure .gcp-credentials.json (or the file at "
                    "GOOGLE_APPLICATION_CREDENTIALS) contains a 'project_id' field."
                )
        return self


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Cloud Platform
    gcp_project_id: str = Field(
        ...,
        description="GCP project ID",
    )
    google_application_credentials: Optional[str] = Field(
        None,
        description="Path to GCP service account JSON file",
    )

    # Database
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL",
    )

    # Redis
    redis_url: RedisDsn = Field(
        ...,
        description="Redis connection URL",
    )

    # Google Cloud Storage
    gcs_bucket_name: Optional[str] = Field(
        None,
        description="GCS bucket name for storing reports",
    )

    # API Configuration
    api_host: str = Field(
        "0.0.0.0",
        description="API server host",
    )
    api_port: int = Field(
        8000,
        description="API server port",
        ge=1,
        le=65535,
    )
    api_workers: int = Field(
        4,
        description="Number of API worker processes",
        ge=1,
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )

    # Worker Configuration
    worker_concurrency: int = Field(
        5,
        description="Number of concurrent jobs per worker",
        ge=1,
    )
    worker_max_retries: int = Field(
        3,
        description="Maximum number of job retries",
        ge=0,
    )

    # Cache Configuration
    cache_ttl_days: int = Field(
        30,
        description="Cache TTL in days",
        ge=1,
    )

    # Legacy R Service (during migration)
    legacy_r_service_url: Optional[str] = Field(
        None,
        description="URL of legacy R Plumber service",
    )
    legacy_enabled: bool = Field(
        True,
        description="Whether legacy R service is enabled",
    )

    # Environment
    environment: str = Field(
        "development",
        description="Environment name (development, staging, production)",
    )
    log_level: str = Field(
        "INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        The global Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None


# Singleton instance for local settings
_local_settings: Optional[LocalSettings] = None


def get_local_settings() -> LocalSettings:
    """Get the local settings instance for CLI execution.

    This returns a minimal settings object that only requires:
    - GCP_PROJECT_ID environment variable

    Use this for CLI commands that don't need database or Redis.

    Returns:
        The LocalSettings instance
    """
    global _local_settings
    if _local_settings is None:
        _local_settings = LocalSettings()
    return _local_settings


def reset_local_settings() -> None:
    """Reset the local settings instance (useful for testing)."""
    global _local_settings
    _local_settings = None
