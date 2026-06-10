"""Custom middleware for FastAPI application."""

import logging
import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add request ID to all requests.

    Generates a unique ID for each request or uses provided X-Request-ID header.
    Adds the ID to response headers for tracing.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and add request ID.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response: Response with X-Request-ID header
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid4())

        # Store request ID in request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests.

    Logs request method, path, status code, and duration.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process and log request.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response: Response from handler
        """
        # Start timer
        start_time = time.time()

        # Get request ID if available
        request_id = getattr(request.state, "request_id", None) or "unknown"

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- {response.status_code} - {duration_ms:.2f}ms",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )

            return response

        except Exception as e:
            # Calculate duration even on error
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- {duration_ms:.2f}ms - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "error": str(e),
                },
                exc_info=True
            )

            # Re-raise to let error handlers deal with it
            raise
