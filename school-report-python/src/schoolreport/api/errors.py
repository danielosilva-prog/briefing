"""Global error handlers for FastAPI application."""

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorResponse:
    """
    Standardized error response format.

    All errors return JSON in this format:
    {
        "error": {
            "code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {...}  // Optional additional context
        }
    }
    """

    @staticmethod
    def format(
        code: str,
        message: str,
        details: Any = None,
        status_code: int = 500
    ) -> JSONResponse:
        """
        Create standardized error response.

        Args:
            code: Error code (e.g., "VALIDATION_ERROR")
            message: Human-readable error message
            details: Optional additional error details
            status_code: HTTP status code

        Returns:
            JSONResponse: Formatted error response
        """
        error_data: Dict[str, Any] = {
            "code": code,
            "message": message,
        }

        if details is not None:
            error_data["details"] = details

        return JSONResponse(
            status_code=status_code,
            content={"error": error_data}
        )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: Request that caused the exception
        exc: HTTP exception

    Returns:
        JSONResponse: Formatted error response
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
        }
    )

    # Map status code to error code
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }

    code = error_codes.get(exc.status_code, "HTTP_ERROR")

    return ErrorResponse.format(
        code=code,
        message=str(exc.detail),
        status_code=exc.status_code
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.

    Args:
        request: Request that failed validation
        exc: Validation exception

    Returns:
        JSONResponse: Formatted validation error response
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        f"Validation error: {len(exc.errors())} errors",
        extra={
            "request_id": request_id,
            "errors": exc.errors(),
        }
    )

    # Format validation errors
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    return ErrorResponse.format(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=details,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: Request that caused the validation error
        exc: Pydantic validation exception

    Returns:
        JSONResponse: Formatted validation error response
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        f"Pydantic validation error: {len(exc.errors())} errors",
        extra={
            "request_id": request_id,
            "errors": exc.errors(),
        }
    )

    # Format validation errors
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    return ErrorResponse.format(
        code="VALIDATION_ERROR",
        message="Data validation failed",
        details=details,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: Request that caused the exception
        exc: Unexpected exception

    Returns:
        JSONResponse: Formatted error response
    """
    request_id = getattr(request.state, "request_id", None)

    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        },
        exc_info=True
    )

    return ErrorResponse.format(
        code="INTERNAL_ERROR",
        message="An internal server error occurred",
        # Don't expose internal error details in production
        details={"type": type(exc).__name__} if logger.level == logging.DEBUG else None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all error handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Error handlers registered")
