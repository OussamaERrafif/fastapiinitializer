"""
Project configuration models

This module defines Pydantic models for project configuration and validation.
These models ensure type safety and data validation for all user inputs during
the project generation process.

Models:
    ProjectConfig: Main configuration model for project generation
    DependencyOption: Represents an available dependency option
    TemplateOption: Represents a project template option
    CICDOption: Represents a CI/CD pipeline option
    AvailableOptions: Container for all available configuration options

All models include field validation to ensure:
- Project names are valid Python package names
- Python versions are supported
- Database and structure choices are valid
- Required fields are present
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re


class ProjectConfig(BaseModel):
    """
    Configuration for generating a FastAPI project
    
    This model represents all user-configurable options for project generation.
    It includes comprehensive validation to ensure all inputs are valid before
    attempting to generate the project.
    
    Attributes:
        project_name (str): Name of the project (alphanumeric, hyphens, underscores)
        python_version (str): Target Python version (3.9, 3.10, 3.11, 3.12)
        database (str): Database choice (none, postgresql, mysql, sqlite, mongodb)
        dependencies (List[str]): List of dependency IDs to include
        structure (str): Project structure (minimal, standard, modular, microservice)
        template (str): Base template to use (blank, crud, microservice, etc.)
        ci_cd (str): CI/CD platform (github-actions, gitlab-ci, none)
        include_docker (bool): Whether to include Docker configuration
        include_tests (bool): Whether to include test suite
        include_middleware (bool): Whether to include custom middleware
        include_logging (bool): Whether to include structured logging
        description (str, optional): Project description for README
        author (str, optional): Project author name
        license (str, optional): Project license type
    
    Validation:
        - Project name is converted to lowercase with hyphens replaced by underscores
        - Python version must be one of the supported versions
        - Database must be a valid choice
        - Structure must be a valid architecture type
    """
    project_name: str = Field(..., min_length=1, max_length=50)
    python_version: str = Field(default="3.11")
    database: str = Field(default="none")
    dependencies: List[str] = Field(default_factory=list)
    structure: str = Field(default="standard")
    template: str = Field(default="blank")
    ci_cd: str = Field(default="none")
    include_docker: bool = Field(default=False)
    include_tests: bool = Field(default=True)
    include_middleware: bool = Field(default=True)
    include_logging: bool = Field(default=True)
    description: Optional[str] = Field(default="A FastAPI project")
    author: Optional[str] = Field(default="")
    license: Optional[str] = Field(default="MIT")
    
    @validator("project_name")
    def validate_project_name(cls, v):
        """
        Ensure project name is a valid Python package name
        
        Validates that the name contains only alphanumeric characters,
        hyphens, and underscores. Converts to lowercase and replaces
        hyphens with underscores for Python compatibility.
        """
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Project name must contain only letters, numbers, hyphens, and underscores")
        return v.lower().replace("-", "_")
    
    @validator("python_version")
    def validate_python_version(cls, v):
        """Ensure Python version is one of the supported versions"""
        valid_versions = ["3.9", "3.10", "3.11", "3.12"]
        if v not in valid_versions:
            raise ValueError(f"Python version must be one of: {', '.join(valid_versions)}")
        return v
    
    @validator("database")
    def validate_database(cls, v):
        """Ensure database choice is a valid option"""
        valid_dbs = ["none", "postgresql", "mysql", "sqlite", "mongodb"]
        if v not in valid_dbs:
            raise ValueError(f"Database must be one of: {', '.join(valid_dbs)}")
        return v
    
    @validator("structure")
    def validate_structure(cls, v):
        """Ensure project structure is a valid architecture type"""
        valid_structures = ["minimal", "standard", "modular", "microservice"]
        if v not in valid_structures:
            raise ValueError(f"Structure must be one of: {', '.join(valid_structures)}")
        return v


class DependencyOption(BaseModel):
    """
    Represents an available dependency option
    
    Attributes:
        id (str): Unique identifier for the dependency
        name (str): Display name of the dependency
        description (str): Brief description of what the dependency provides
        category (str): Category for grouping (database, auth, monitoring, etc.)
    """
    id: str
    name: str
    description: str
    category: str = "general"


class TemplateOption(BaseModel):
    """
    Represents a project template option
    
    Attributes:
        id (str): Unique identifier for the template
        name (str): Display name of the template
        description (str): Brief description of the template
    """
    id: str
    name: str
    description: str


class CICDOption(BaseModel):
    """
    Represents a CI/CD pipeline option
    
    Attributes:
        id (str): Unique identifier for the CI/CD option
        name (str): Display name of the CI/CD platform
        description (str): Brief description of the CI/CD option
    """
    id: str
    name: str
    description: str


class AvailableOptions(BaseModel):
    """
    Container for all available configuration options
    
    This model is returned by the /api/options endpoint to provide
    the frontend with all available choices for project configuration.
    
    Attributes:
        python_versions (List[str]): Supported Python versions
        databases (List[str]): Available database options
        dependencies (List[DependencyOption]): Available dependencies
        structures (List[str]): Available project structures
        templates (List[TemplateOption]): Available project templates
        ci_cd (List[CICDOption]): Available CI/CD platforms
    """
    python_versions: List[str]
    databases: List[str]
    dependencies: List[DependencyOption]
    structures: List[str]
    templates: List[TemplateOption]
    ci_cd: List[CICDOption]
