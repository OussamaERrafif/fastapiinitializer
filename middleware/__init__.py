"""
Middleware package

This package contains custom middleware components for the FastAPI application,
including error handling, request tracking, and validation utilities.

Exported:
    - Custom exception classes (AppException, ProjectGenerationError, ValidationError, etc.)
    - Exception handlers for different error types
    - Request tracking middleware
    - Validation utilities
"""
from .error_handler import (
    AppException,
    ProjectGenerationError,
    ValidationError,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

__all__ = [
    "AppException",
    "ProjectGenerationError",
    "ValidationError",
    "app_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "general_exception_handler"
]
