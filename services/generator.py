"""
Project generator service

This module handles the core project generation functionality:
- Renders Jinja2 templates with project configuration
- Creates ZIP archives with all generated files
- Manages different project structures (minimal, standard, modular, microservice)
- Adds optional components (Docker, tests, CI/CD)

The generator creates a complete, ready-to-run FastAPI project based on
user selections for:
- Python version
- Database type
- Dependencies (ORMs, auth, caching, etc.)
- Project structure
- Optional features (Docker, tests, CI/CD pipelines)

Usage:
    generator = ProjectGenerator()
    config = ProjectConfig(project_name="myapi", python_version="3.11", ...)
    zip_buffer = generator.generate_project(config)
"""
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import os
import io
import zipfile
from pathlib import Path

from models.project_config import ProjectConfig


class ProjectGenerator:
    """
    Generates FastAPI projects from Jinja2 templates
    
    This class orchestrates the entire project generation process by:
    1. Building a template context from user configuration
    2. Rendering core files (main.py, requirements.txt, README.md, etc.)
    3. Adding selected modules (database, auth, celery, etc.)
    4. Generating structure-specific files based on chosen architecture
    5. Including optional components (Docker, tests, CI/CD)
    
    Attributes:
        template_dir (Path): Directory containing Jinja2 templates
        env (Environment): Jinja2 environment for template rendering
    """
    
    def __init__(self):
        """Initialize the project generator with template environment"""
        self.template_dir = Path("templates")
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate_project(self, config: ProjectConfig) -> io.BytesIO:
        """
        Generate a complete FastAPI project and return as ZIP buffer
        
        This is the main entry point for project generation. It orchestrates
        the creation of all project files and packages them into a ZIP archive.
        
        Args:
            config (ProjectConfig): Complete project configuration including
                name, Python version, database, dependencies, structure, and
                optional features
        
        Returns:
            io.BytesIO: In-memory ZIP file buffer containing the complete project
        
        Raises:
            ProjectGenerationError: If template rendering or ZIP creation fails
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get template context
            context = self._build_context(config)
            
            # Generate core files
            self._add_core_files(zip_file, config, context)
            
            # Add selected modules
            self._add_modules(zip_file, config, context)
            
            # Add structure-specific files
            self._add_structure_files(zip_file, config, context)
            
            # Add optional files (Docker, tests, etc.)
            self._add_optional_files(zip_file, config, context)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def _build_context(self, config: ProjectConfig) -> Dict[str, Any]:
        """
        Build Jinja2 template context from project configuration
        
        Creates a dictionary containing all configuration values and helper
        flags for template rendering. Helper flags (has_*) make templates
        simpler by pre-computing boolean checks for dependencies.
        
        Args:
            config (ProjectConfig): Project configuration
        
        Returns:
            Dict[str, Any]: Template context with all config values and helper flags
        """
        return {
            "project_name": config.project_name,
            "python_version": config.python_version,
            "database": config.database,
            "dependencies": config.dependencies,
            "structure": config.structure,
            "include_docker": config.include_docker,
            "include_tests": config.include_tests,
            "description": config.description,
            "author": config.author,
            "license": config.license,
            "template": config.template,
            "ci_cd": config.ci_cd,
            "include_middleware": config.include_middleware,
            "include_logging": config.include_logging,
            # Helper flags
            "has_sqlalchemy": "sqlalchemy" in config.dependencies,
            "has_alembic": "alembic" in config.dependencies,
            "has_tortoise": "tortoise" in config.dependencies,
            "has_jwt": "jwt" in config.dependencies,
            "has_oauth2": "oauth2" in config.dependencies,
            "has_passlib": "passlib" in config.dependencies,
            "has_celery": "celery" in config.dependencies,
            "has_arq": "arq" in config.dependencies,
            "has_redis": "redis" in config.dependencies,
            "has_graphql": "graphql" in config.dependencies,
            "has_websockets": "websockets" in config.dependencies,
            "has_cors": "cors" in config.dependencies,
            "has_logging": "logging" in config.dependencies or config.include_logging,
            "has_prometheus": "prometheus" in config.dependencies,
            "has_sentry": "sentry" in config.dependencies,
            "has_pytest": "pytest" in config.dependencies,
            "has_docker": "docker" in config.dependencies or config.include_docker,
            "has_pre_commit": "pre-commit" in config.dependencies,
            "has_caching": "caching" in config.dependencies,
            "has_ratelimit": "ratelimit" in config.dependencies,
            "has_database": config.database != "none",
        }
    
    def _add_core_files(self, zip_file: zipfile.ZipFile, config: ProjectConfig, context: Dict[str, Any]):
        """
        Add core project files to ZIP archive
        
        Generates and adds essential files that every project needs:
        - main.py: FastAPI application entry point
        - requirements.txt: Python dependencies
        - README.md: Project documentation
        - .gitignore: Git exclusions
        - .env.example: Environment variable template
        
        Args:
            zip_file: ZIP archive to add files to
            config: Project configuration
            context: Template rendering context
        """
        project_name = config.project_name
        
        # main.py
        template = self.env.get_template("main.py.jinja2")
        zip_file.writestr(f"{project_name}/main.py", template.render(context))
        
        # requirements.txt
        template = self.env.get_template("requirements.txt.jinja2")
        zip_file.writestr(f"{project_name}/requirements.txt", template.render(context))
        
        # README.md
        template = self.env.get_template("README.md.jinja2")
        zip_file.writestr(f"{project_name}/README.md", template.render(context))
        
        # .gitignore
        template = self.env.get_template("gitignore.jinja2")
        zip_file.writestr(f"{project_name}/.gitignore", template.render(context))
        
        # .env.example
        template = self.env.get_template("env.example.jinja2")
        zip_file.writestr(f"{project_name}/.env.example", template.render(context))
    
    def _add_modules(self, zip_file: zipfile.ZipFile, config: ProjectConfig, context: Dict[str, Any]):
        """
        Add selected module files to ZIP archive
        
        Generates module files based on selected dependencies:
        - Database connection and session management
        - SQLAlchemy ORM models
        - JWT authentication
        - Celery task queue
        - Custom middleware
        - Structured logging
        - Rate limiting
        
        Args:
            zip_file: ZIP archive to add files to
            config: Project configuration
            context: Template rendering context with dependency flags
        """
        project_name = config.project_name
        
        # Database module
        if context["has_database"]:
            template = self.env.get_template("modules/database.py.jinja2")
            zip_file.writestr(f"{project_name}/app/database.py", template.render(context))
        
        # SQLAlchemy models
        if context["has_sqlalchemy"]:
            template = self.env.get_template("modules/models.py.jinja2")
            zip_file.writestr(f"{project_name}/app/models.py", template.render(context))
        
        # JWT Auth
        if context["has_jwt"]:
            template = self.env.get_template("modules/auth.py.jinja2")
            zip_file.writestr(f"{project_name}/app/auth.py", template.render(context))
        
        # Celery
        if context["has_celery"]:
            template = self.env.get_template("modules/celery_app.py.jinja2")
            zip_file.writestr(f"{project_name}/app/celery_app.py", template.render(context))
        
        # Middleware
        if config.include_middleware:
            template = self.env.get_template("modules/middleware.py.jinja2")
            zip_file.writestr(f"{project_name}/app/middleware.py", template.render(context))
        
        # Logging
        if context["has_logging"]:
            template = self.env.get_template("modules/logging_config.py.jinja2")
            zip_file.writestr(f"{project_name}/app/logging_config.py", template.render(context))
            # Create logs directory
            zip_file.writestr(f"{project_name}/logs/.gitkeep", "")
        
        # Rate limiting
        if context["has_ratelimit"]:
            template = self.env.get_template("modules/rate_limiter.py.jinja2")
            zip_file.writestr(f"{project_name}/app/rate_limiter.py", template.render(context))
    
    def _add_structure_files(self, zip_file: zipfile.ZipFile, config: ProjectConfig, context: Dict[str, Any]):
        """
        Add structure-specific files to ZIP archive
        
        Creates directory structure and files based on chosen architecture:
        
        - minimal: Simple app/__init__.py (single file app)
        - standard: app/api.py, app/schemas.py (organized modules)
        - modular: app/api/v1/, app/schemas/, app/core/ (versioned API)
        - microservice: Full microservice structure with health checks and config
        
        Args:
            zip_file: ZIP archive to add files to
            config: Project configuration
            context: Template rendering context
        """
        project_name = config.project_name
        
        if config.structure == "minimal":
            # Just app/__init__.py
            zip_file.writestr(f"{project_name}/app/__init__.py", "")
        
        elif config.structure == "standard":
            # app/__init__.py, app/api.py, app/schemas.py
            zip_file.writestr(f"{project_name}/app/__init__.py", "")
            template = self.env.get_template("structures/standard/api.py.jinja2")
            zip_file.writestr(f"{project_name}/app/api.py", template.render(context))
            template = self.env.get_template("structures/standard/schemas.py.jinja2")
            zip_file.writestr(f"{project_name}/app/schemas.py", template.render(context))
        
        elif config.structure == "modular":
            # Full modular structure
            zip_file.writestr(f"{project_name}/app/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/api/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/api/v1/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/schemas/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/core/__init__.py", "")
            
            template = self.env.get_template("structures/modular/api_v1.py.jinja2")
            zip_file.writestr(f"{project_name}/app/api/v1/endpoints.py", template.render(context))
            template = self.env.get_template("structures/modular/config.py.jinja2")
            zip_file.writestr(f"{project_name}/app/core/config.py", template.render(context))
        
        elif config.structure == "microservice":
            # Microservice structure (cloud-native)
            zip_file.writestr(f"{project_name}/app/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/api/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/api/v1/__init__.py", "")
            zip_file.writestr(f"{project_name}/app/core/__init__.py", "")
            
            template = self.env.get_template("structures/microservice/api_v1.py.jinja2")
            zip_file.writestr(f"{project_name}/app/api/v1/endpoints.py", template.render(context))
            template = self.env.get_template("structures/modular/config.py.jinja2")
            zip_file.writestr(f"{project_name}/app/core/config.py", template.render(context))
    
    def _add_optional_files(self, zip_file: zipfile.ZipFile, config: ProjectConfig, context: Dict[str, Any]):
        """
        Add optional files to ZIP archive
        
        Includes additional components based on user selection:
        - Docker: Dockerfile, docker-compose.yml, .dockerignore
        - Tests: pytest configuration and test files
        - CI/CD: GitHub Actions or GitLab CI pipeline configuration
        - Pre-commit: Git hooks for code quality
        
        Args:
            zip_file: ZIP archive to add files to
            config: Project configuration
            context: Template rendering context
        """
        project_name = config.project_name
        
        # Docker files
        if context["has_docker"]:
            template = self.env.get_template("optional/Dockerfile.jinja2")
            zip_file.writestr(f"{project_name}/Dockerfile", template.render(context))
            template = self.env.get_template("optional/docker-compose.yml.jinja2")
            zip_file.writestr(f"{project_name}/docker-compose.yml", template.render(context))
            zip_file.writestr(f"{project_name}/.dockerignore", "__pycache__\n*.pyc\n*.pyo\n*.pyd\n.Python\nenv/\nvenv/\n.git\n.gitignore\n")
        
        # Tests
        if config.include_tests:
            zip_file.writestr(f"{project_name}/tests/__init__.py", "")
            template = self.env.get_template("optional/test_main.py.jinja2")
            zip_file.writestr(f"{project_name}/tests/test_main.py", template.render(context))
            template = self.env.get_template("optional/conftest.py.jinja2")
            zip_file.writestr(f"{project_name}/tests/conftest.py", template.render(context))
        
        # CI/CD pipelines
        if config.ci_cd == "github-actions":
            template = self.env.get_template("ci_cd/github-actions.yml.jinja2")
            zip_file.writestr(f"{project_name}/.github/workflows/ci.yml", template.render(context))
        elif config.ci_cd == "gitlab-ci":
            template = self.env.get_template("ci_cd/gitlab-ci.yml.jinja2")
            zip_file.writestr(f"{project_name}/.gitlab-ci.yml", template.render(context))
        
        # Pre-commit hooks
        if context["has_pre_commit"]:
            pre_commit_config = """repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-added-large-files

- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black

- repo: https://github.com/pycqa/isort
  rev: 5.13.2
  hooks:
    - id: isort

- repo: https://github.com/pycqa/flake8
  rev: 7.0.0
  hooks:
    - id: flake8
      args: ['--max-line-length=100', '--ignore=E501,W503']
"""
            zip_file.writestr(f"{project_name}/.pre-commit-config.yaml", pre_commit_config)
