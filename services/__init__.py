"""
Services package

This package contains business logic and service layer components for the
FastAPI project generator. Services handle the core functionality of generating
projects from templates.

Exported:
    - ProjectGenerator: Main service for generating FastAPI projects from templates
"""
from .generator import ProjectGenerator

__all__ = ["ProjectGenerator"]
