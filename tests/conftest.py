"""
Pytest configuration and fixtures
"""
import pytest
from pathlib import Path
from models.project_config import ProjectConfig
from services.generator import ProjectGenerator


@pytest.fixture
def template_dir():
    """Return the templates directory path"""
    return Path("templates")


@pytest.fixture
def generator():
    """Return a ProjectGenerator instance"""
    return ProjectGenerator()


@pytest.fixture
def minimal_config():
    """Return a minimal project configuration"""
    return ProjectConfig(
        project_name="test_project",
        python_version="3.11",
        database="none",
        structure="minimal",
        include_docker=False,
        include_tests=False,
    )


@pytest.fixture
def standard_config():
    """Return a standard project configuration"""
    return ProjectConfig(
        project_name="my_api",
        python_version="3.11",
        database="postgresql",
        dependencies=["sqlalchemy", "alembic", "jwt", "cors"],
        structure="standard",
        include_docker=True,
        include_tests=True,
        description="Test API project",
        author="Test Author",
        license="MIT",
    )


@pytest.fixture
def modular_config():
    """Return a modular project configuration"""
    return ProjectConfig(
        project_name="advanced_api",
        python_version="3.12",
        database="postgresql",
        dependencies=["sqlalchemy", "alembic", "jwt", "oauth2", "celery", "redis", "cors", "logging", "prometheus"],
        structure="modular",
        include_docker=True,
        include_tests=True,
        ci_cd="github-actions",
        include_middleware=True,
        include_logging=True,
    )


@pytest.fixture
def microservice_config():
    """Return a microservice project configuration"""
    return ProjectConfig(
        project_name="user_service",
        python_version="3.11",
        database="postgresql",
        dependencies=["sqlalchemy", "jwt", "cors", "logging", "prometheus", "ratelimit"],
        structure="microservice",
        include_docker=True,
        include_tests=True,
        ci_cd="github-actions",
    )
