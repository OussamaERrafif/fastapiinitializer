"""
Models package

This package contains Pydantic models for data validation and serialization.
These models define the structure of project configurations and available options
for the FastAPI project generator.

Exported:
    - ProjectConfig: Main configuration model for project generation
    - AvailableOptions: Container for all available configuration options
    - DependencyOption: Model for dependency options
    - TemplateOption: Model for template options
    - CICDOption: Model for CI/CD options
"""
from .project_config import ProjectConfig, AvailableOptions, DependencyOption, TemplateOption, CICDOption

__all__ = ["ProjectConfig", "AvailableOptions", "DependencyOption", "TemplateOption", "CICDOption"]
