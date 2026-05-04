"""
Project configuration models with Pydantic v2.

Defines all input/output models and the single-source-of-truth constants
used both for validation here and for the /api/options response.
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
import re

# ── Single source of truth ──────────────────────────────────────────────────

VALID_PYTHON_VERSIONS: List[str] = ["3.12", "3.11", "3.10", "3.9"]
VALID_DATABASES: List[str] = ["none", "postgresql", "mysql", "sqlite", "mongodb", "redis"]
VALID_STRUCTURES: List[str] = ["minimal", "standard", "modular", "microservice"]

# ── Models ───────────────────────────────────────────────────────────────────

class ProjectConfig(BaseModel):
    """Configuration for generating a FastAPI project."""

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

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Project name must contain only letters, numbers, hyphens, and underscores"
            )
        return v.lower().replace("-", "_")

    @field_validator("python_version")
    @classmethod
    def validate_python_version(cls, v: str) -> str:
        if v not in VALID_PYTHON_VERSIONS:
            raise ValueError(f"Python version must be one of: {', '.join(VALID_PYTHON_VERSIONS)}")
        return v

    @field_validator("database")
    @classmethod
    def validate_database(cls, v: str) -> str:
        if v not in VALID_DATABASES:
            raise ValueError(f"Database must be one of: {', '.join(VALID_DATABASES)}")
        return v

    @field_validator("structure")
    @classmethod
    def validate_structure(cls, v: str) -> str:
        if v not in VALID_STRUCTURES:
            raise ValueError(f"Structure must be one of: {', '.join(VALID_STRUCTURES)}")
        return v

    @model_validator(mode="after")
    def validate_dependency_compatibility(self) -> "ProjectConfig":
        deps = set(self.dependencies)
        errors = []
        if "alembic" in deps and "sqlalchemy" not in deps:
            errors.append("'alembic' requires 'sqlalchemy' — add sqlalchemy to your dependencies")
        if errors:
            raise ValueError("; ".join(errors))
        return self


class DependencyOption(BaseModel):
    id: str
    name: str
    description: str
    category: str = "general"


class TemplateOption(BaseModel):
    id: str
    name: str
    description: str


class CICDOption(BaseModel):
    id: str
    name: str
    description: str


class AvailableOptions(BaseModel):
    python_versions: List[str]
    databases: List[str]
    dependencies: List[DependencyOption]
    structures: List[str]
    templates: List[TemplateOption]
    ci_cd: List[CICDOption]
