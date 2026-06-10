"""Health check endpoints for monitoring and Kubernetes probes."""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str
    uptime_seconds: float | None = None


class ServiceCheck(BaseModel):
    """Individual service health check result."""

    status: str  # "healthy" or "unhealthy"
    error: str | None = None


class ReadinessResponse(BaseModel):
    """Readiness check response."""

    status: str  # "ready" or "not_ready"
    checks: Dict[str, ServiceCheck]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Basic health check",
    description="Returns basic health status and system information."
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Always returns 200 OK if the service is running.
    Used for basic liveness checks.

    Returns:
        HealthResponse: Health status and metadata
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",  # TODO: Read from package metadata
        uptime_seconds=None  # TODO: Calculate uptime
    )


@router.get(
    "/ready",
    responses={
        200: {"description": "Service is ready"},
        503: {"description": "Service is not ready"}
    },
    summary="Readiness check",
    description="Checks if service and all dependencies are ready to handle requests."
)
async def readiness_check(request: Request) -> JSONResponse:
    """
    Readiness check endpoint for Kubernetes.

    Verifies that all critical dependencies (Redis, PostgreSQL) are accessible.
    Returns 200 if ready, 503 if not ready.

    This is used by Kubernetes readiness probes to determine if the pod
    should receive traffic.

    Args:
        request: FastAPI request object with app state

    Returns:
        JSONResponse: Readiness status with dependency checks
    """
    checks: Dict[str, ServiceCheck] = {}
    all_healthy = True

    # Check Redis
    try:
        redis = getattr(request.app.state, "redis", None)
        if redis:
            await redis.ping()
            checks["redis"] = ServiceCheck(status="healthy")
        else:
            checks["redis"] = ServiceCheck(
                status="unhealthy",
                error="Redis client not initialized"
            )
            all_healthy = False
    except Exception as e:
        checks["redis"] = ServiceCheck(
            status="unhealthy",
            error=str(e)
        )
        all_healthy = False

    # Check PostgreSQL
    try:
        postgres = getattr(request.app.state, "postgres", None)
        if postgres:
            await postgres.fetchval("SELECT 1")
            checks["postgres"] = ServiceCheck(status="healthy")
        else:
            checks["postgres"] = ServiceCheck(
                status="unhealthy",
                error="PostgreSQL client not initialized"
            )
            all_healthy = False
    except Exception as e:
        checks["postgres"] = ServiceCheck(
            status="unhealthy",
            error=str(e)
        )
        all_healthy = False

    # Determine overall status
    overall_status = "ready" if all_healthy else "not_ready"
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    response_data = ReadinessResponse(
        status=overall_status,
        checks=checks
    )

    return JSONResponse(
        status_code=status_code,
        content=response_data.model_dump()
    )
