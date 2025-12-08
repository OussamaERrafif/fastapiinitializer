"""
Custom error handling middleware and exception handlers

This module provides comprehensive error handling for the FastAPI application including:
- Custom exception classes with enhanced error tracking
- Global exception handlers for different error types
- Request tracking middleware with unique request IDs
- Validation utilities for common input validation scenarios

Exception Hierarchy:
    AppException (base)
    ├── ProjectGenerationError (500)
    ├── ValidationError (422)
    ├── ResourceNotFoundError (404)
    ├── RateLimitExceededError (429)
    ├── ConfigurationError (500)
    └── BusinessLogicError (400)

Features:
- Unique request ID tracking across the request lifecycle
- Detailed error logging with structured data
- Consistent JSON error response format
- Request timing and performance monitoring
- Validation utilities for common patterns

Usage:
    # Raise custom exceptions
    raise ValidationError("Invalid input", details={"field": "name"})
    
    # Use validation utilities
    ValidationUtils.validate_email(email, "email")
    ValidationUtils.validate_choice(status, "status", ["active", "inactive"])
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback
import time
import uuid
from typing import Union, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ==================== Custom Exception Classes ====================

class AppException(Exception):
    """
    Base application exception with enhanced tracking
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling and tracking across the application.
    
    Attributes:
        message (str): Human-readable error message
        status_code (int): HTTP status code for the error response
        details (dict): Additional context about the error
        error_code (str): Machine-readable error code for client handling
        timestamp (str): ISO 8601 timestamp of when the error occurred
    
    Args:
        message: Error description
        status_code: HTTP status code (default: 500)
        details: Additional error context (default: {})
        error_code: Error code identifier (default: class name)
    """
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.error_code = error_code or self.__class__.__name__
        self.timestamp = datetime.now(timezone.utc).isoformat()
        super().__init__(self.message)


class ProjectGenerationError(AppException):
    """Exception raised during project generation"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="PROJECT_GENERATION_FAILED"
        )


class ValidationError(AppException):
    """Exception raised for validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
            error_code="VALIDATION_ERROR"
        )


class ResourceNotFoundError(AppException):
    """Exception raised when a resource is not found"""
    def __init__(self, resource: str, identifier: str = ""):
        super().__init__(
            message=f"{resource} not found" + (f": {identifier}" if identifier else ""),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier},
            error_code="RESOURCE_NOT_FOUND"
        )


class RateLimitExceededError(AppException):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
            error_code="RATE_LIMIT_EXCEEDED"
        )


class ConfigurationError(AppException):
    """Exception raised for configuration errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
            error_code="CONFIGURATION_ERROR"
        )


class BusinessLogicError(AppException):
    """Exception raised for business logic violations"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
            error_code="BUSINESS_LOGIC_ERROR"
        )


# ==================== Exception Handlers ====================

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions with detailed logging"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"[{request_id}] Application error: {exc.message}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": exc.timestamp
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "type": exc.__class__.__name__,
                "details": exc.details,
                "path": request.url.path,
                "timestamp": exc.timestamp,
                "request_id": request_id
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with enhanced logging"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.warning(
        f"[{request_id}] HTTP error {exc.status_code}: {exc.detail}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": f"HTTP_{exc.status_code}",
                "type": "HTTPException",
                "status_code": exc.status_code,
                "path": request.url.path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors with detailed field information"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field_path,
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })
    
    logger.warning(
        f"[{request_id}] Validation error on {request.url.path}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Request validation failed",
                "code": "VALIDATION_ERROR",
                "type": "ValidationError",
                "details": {
                    "errors": errors,
                    "error_count": len(errors)
                },
                "path": request.url.path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other uncaught exceptions with detailed error tracking"""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    error_id = str(uuid.uuid4())
    
    # Log full traceback for debugging
    logger.critical(
        f"[{request_id}] Unhandled exception [{error_id}]: {str(exc)}",
        extra={
            "request_id": request_id,
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    # In production, don't expose internal error details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An internal server error occurred. Please contact support if the problem persists.",
                "code": "INTERNAL_SERVER_ERROR",
                "type": "InternalServerError",
                "error_id": error_id,
                "path": request.url.path,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id
            }
        }
    )


# ==================== Request Tracking Middleware ====================

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests with unique IDs and timing information.
    Adds request_id to request.state for use in error handlers and logging.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Record start time
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # Log response
            logger.info(
                f"[{request_id}] Response {response.status_code} - {process_time:.4f}s",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            return response
            
        except Exception as exc:
            # Log exception in middleware
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Request failed after {process_time:.4f}s",
                extra={
                    "request_id": request_id,
                    "process_time": process_time,
                    "exception": str(exc)
                }
            )
            raise


# ==================== Validation Utilities ====================

class ValidationUtils:
    """Utility class for common validation operations"""
    
    @staticmethod
    def validate_string_length(
        value: str, 
        field_name: str, 
        min_length: int = 1, 
        max_length: int = 255
    ) -> None:
        """Validate string length"""
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters long",
                details={"field": field_name, "value_length": len(value), "min_length": min_length}
            )
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} must not exceed {max_length} characters",
                details={"field": field_name, "value_length": len(value), "max_length": max_length}
            )
    
    @staticmethod
    def validate_alphanumeric(value: str, field_name: str, allow_special: str = "_-") -> None:
        """Validate that string contains only alphanumeric characters and allowed special chars"""
        import re
        pattern = f"^[a-zA-Z0-9{re.escape(allow_special)}]+$"
        if not re.match(pattern, value):
            raise ValidationError(
                f"{field_name} must contain only letters, numbers, and {allow_special}",
                details={"field": field_name, "value": value, "allowed_special": allow_special}
            )
    
    @staticmethod
    def validate_email(value: str, field_name: str = "email") -> None:
        """Validate email format"""
        import re
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            raise ValidationError(
                f"Invalid {field_name} format",
                details={"field": field_name, "value": value}
            )
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: list) -> None:
        """Validate that value is in allowed choices"""
        if value not in choices:
            raise ValidationError(
                f"Invalid {field_name}. Must be one of: {', '.join(str(c) for c in choices)}",
                details={"field": field_name, "value": value, "allowed_choices": choices}
            )
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_size_mb: int = 10) -> None:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        if size_bytes > max_size_bytes:
            raise ValidationError(
                f"File size exceeds maximum allowed size of {max_size_mb}MB",
                details={
                    "file_size_bytes": size_bytes,
                    "file_size_mb": round(size_bytes / 1024 / 1024, 2),
                    "max_size_mb": max_size_mb
                }
            )
    
    @staticmethod
    def validate_non_empty_list(value: list, field_name: str) -> None:
        """Validate that list is not empty"""
        if not value or len(value) == 0:
            raise ValidationError(
                f"{field_name} must contain at least one item",
                details={"field": field_name}
            )
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize and trim string input"""
        return value.strip()[:max_length]

