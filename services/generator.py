"""
Project generator service.

Renders Jinja2 templates into an in-memory ZIP archive based on user config.
"""
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import io
import zipfile
from pathlib import Path

from models.project_config import ProjectConfig

# All dependency IDs the templates know about. Adding a new dep only requires
# adding it here — _build_context picks it up automatically.
_DEPENDENCY_IDS = [
    "sqlalchemy", "alembic", "tortoise",
    "jwt", "oauth2", "passlib",
    "celery", "arq", "redis",
    "graphql", "websockets", "cors",
    "logging", "prometheus", "sentry",
    "pytest", "docker", "pre-commit",
    "caching", "ratelimit",
]

# Absolute path so the generator works regardless of the process working directory.
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class ProjectGenerator:
    """Generates FastAPI projects from Jinja2 templates."""

    def __init__(self):
        self.template_dir = _TEMPLATES_DIR
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_project(self, config: ProjectConfig) -> io.BytesIO:
        """Generate a complete FastAPI project and return as a ZIP buffer."""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            context = self._build_context(config)
            self._add_core_files(zip_file, config, context)
            self._add_modules(zip_file, config, context)
            self._add_structure_files(zip_file, config, context)
            self._add_optional_files(zip_file, config, context)

        zip_buffer.seek(0)
        return zip_buffer

    def _build_context(self, config: ProjectConfig) -> Dict[str, Any]:
        """Build Jinja2 template context from project configuration."""
        deps = set(config.dependencies)

        # Automatically generate has_<dep> flags for all known dependency IDs.
        dep_flags: Dict[str, bool] = {
            f"has_{dep_id.replace('-', '_')}": dep_id in deps
            for dep_id in _DEPENDENCY_IDS
        }

        # Two deps have dual-path logic (also controlled by top-level toggles).
        dep_flags["has_logging"] = "logging" in deps or config.include_logging
        dep_flags["has_docker"] = "docker" in deps or config.include_docker

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
            "has_database": config.database != "none",
            **dep_flags,
        }

    def _add_core_files(
        self,
        zip_file: zipfile.ZipFile,
        config: ProjectConfig,
        context: Dict[str, Any],
    ) -> None:
        project_name = config.project_name
        for filename, template_name in [
            ("main.py", "main.py.jinja2"),
            ("requirements.txt", "requirements.txt.jinja2"),
            ("README.md", "README.md.jinja2"),
            (".gitignore", "gitignore.jinja2"),
            (".env.example", "env.example.jinja2"),
        ]:
            t = self.env.get_template(template_name)
            zip_file.writestr(f"{project_name}/{filename}", t.render(context))

    def _add_modules(
        self,
        zip_file: zipfile.ZipFile,
        config: ProjectConfig,
        context: Dict[str, Any],
    ) -> None:
        project_name = config.project_name

        module_map = [
            (context["has_database"],        "modules/database.py.jinja2",       "app/database.py"),
            (context["has_sqlalchemy"],      "modules/models.py.jinja2",         "app/models.py"),
            (context["has_jwt"],             "modules/auth.py.jinja2",           "app/auth.py"),
            (context["has_celery"],          "modules/celery_app.py.jinja2",     "app/celery_app.py"),
            (config.include_middleware,      "modules/middleware.py.jinja2",     "app/middleware.py"),
            (context["has_logging"],         "modules/logging_config.py.jinja2", "app/logging_config.py"),
            (context["has_ratelimit"],       "modules/rate_limiter.py.jinja2",   "app/rate_limiter.py"),
        ]

        for condition, template_name, output_path in module_map:
            if condition:
                t = self.env.get_template(template_name)
                zip_file.writestr(f"{project_name}/{output_path}", t.render(context))

        if context["has_logging"]:
            zip_file.writestr(f"{project_name}/logs/.gitkeep", "")

    def _add_structure_files(
        self,
        zip_file: zipfile.ZipFile,
        config: ProjectConfig,
        context: Dict[str, Any],
    ) -> None:
        project_name = config.project_name

        if config.structure == "minimal":
            zip_file.writestr(f"{project_name}/app/__init__.py", "")

        elif config.structure == "standard":
            zip_file.writestr(f"{project_name}/app/__init__.py", "")
            for fname, tname in [
                ("app/api.py",     "structures/standard/api.py.jinja2"),
                ("app/schemas.py", "structures/standard/schemas.py.jinja2"),
            ]:
                t = self.env.get_template(tname)
                zip_file.writestr(f"{project_name}/{fname}", t.render(context))

        elif config.structure in ("modular", "microservice"):
            for init_path in [
                "app/__init__.py",
                "app/api/__init__.py",
                "app/api/v1/__init__.py",
                "app/schemas/__init__.py",
                "app/core/__init__.py",
            ]:
                zip_file.writestr(f"{project_name}/{init_path}", "")

            api_template = (
                "structures/microservice/api_v1.py.jinja2"
                if config.structure == "microservice"
                else "structures/modular/api_v1.py.jinja2"
            )
            zip_file.writestr(
                f"{project_name}/app/api/v1/endpoints.py",
                self.env.get_template(api_template).render(context),
            )
            zip_file.writestr(
                f"{project_name}/app/core/config.py",
                self.env.get_template("structures/modular/config.py.jinja2").render(context),
            )

    def _add_optional_files(
        self,
        zip_file: zipfile.ZipFile,
        config: ProjectConfig,
        context: Dict[str, Any],
    ) -> None:
        project_name = config.project_name

        if context["has_docker"]:
            zip_file.writestr(
                f"{project_name}/Dockerfile",
                self.env.get_template("optional/Dockerfile.jinja2").render(context),
            )
            zip_file.writestr(
                f"{project_name}/docker-compose.yml",
                self.env.get_template("optional/docker-compose.yml.jinja2").render(context),
            )
            zip_file.writestr(
                f"{project_name}/.dockerignore",
                "__pycache__\n*.pyc\n*.pyo\n*.pyd\n.Python\nenv/\nvenv/\n.git\n.gitignore\n",
            )

        if config.include_tests:
            zip_file.writestr(f"{project_name}/tests/__init__.py", "")
            zip_file.writestr(
                f"{project_name}/tests/test_main.py",
                self.env.get_template("optional/test_main.py.jinja2").render(context),
            )
            zip_file.writestr(
                f"{project_name}/tests/conftest.py",
                self.env.get_template("optional/conftest.py.jinja2").render(context),
            )

        if config.ci_cd == "github-actions":
            zip_file.writestr(
                f"{project_name}/.github/workflows/ci.yml",
                self.env.get_template("ci_cd/github-actions.yml.jinja2").render(context),
            )
        elif config.ci_cd == "gitlab-ci":
            zip_file.writestr(
                f"{project_name}/.gitlab-ci.yml",
                self.env.get_template("ci_cd/gitlab-ci.yml.jinja2").render(context),
            )

        if context["has_pre_commit"]:
            pre_commit_config = (
                "repos:\n"
                "- repo: https://github.com/pre-commit/pre-commit-hooks\n"
                "  rev: v4.5.0\n"
                "  hooks:\n"
                "    - id: trailing-whitespace\n"
                "    - id: end-of-file-fixer\n"
                "    - id: check-yaml\n"
                "    - id: check-added-large-files\n"
                "\n"
                "- repo: https://github.com/psf/black\n"
                "  rev: 23.12.1\n"
                "  hooks:\n"
                "    - id: black\n"
                "\n"
                "- repo: https://github.com/pycqa/isort\n"
                "  rev: 5.13.2\n"
                "  hooks:\n"
                "    - id: isort\n"
                "\n"
                "- repo: https://github.com/pycqa/flake8\n"
                "  rev: 7.0.0\n"
                "  hooks:\n"
                "    - id: flake8\n"
                "      args: ['--max-line-length=100', '--ignore=E501,W503']\n"
            )
            zip_file.writestr(f"{project_name}/.pre-commit-config.yaml", pre_commit_config)
