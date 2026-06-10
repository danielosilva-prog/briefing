"""FastAPI application factory."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schoolreport.api.errors import register_error_handlers
from schoolreport.api.middleware import RequestLoggingMiddleware, RequestIDMiddleware
from schoolreport.api.routes import health
from schoolreport.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting School Report API...")

    settings = get_settings()

    # Initialize app state (placeholders for now)
    app.state.redis = None  # Will be initialized by dependency injection
    app.state.postgres = None  # Will be initialized by dependency injection

    logger.info(f"Environment: {settings.environment}")
    logger.info("School Report API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down School Report API...")

    # Cleanup resources
    if hasattr(app.state, "redis") and app.state.redis:
        logger.info("Closing Redis connection...")
        # await app.state.redis.close()

    if hasattr(app.state, "postgres") and app.state.postgres:
        logger.info("Closing PostgreSQL connection...")
        # await app.state.postgres.close()

    logger.info("School Report API shutdown complete")


def create_app(
    title: str = "School Report API",
    version: str = "0.1.0",
    debug: bool | None = None
) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        title: API title for OpenAPI documentation
        version: API version
        debug: Enable debug mode (defaults to environment setting)

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    if debug is None:
        debug = settings.environment == "development"

    # Create FastAPI app
    app = FastAPI(
        title=title,
        version=version,
        description="API for generating educational reports for SEGAPE/MEC",
        debug=debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Register error handlers
    register_error_handlers(app)

    # Include routers
    app.include_router(health.router, tags=["health"])
    # More routers will be added here

    return app
