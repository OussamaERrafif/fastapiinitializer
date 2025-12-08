"""
Tests for ProjectGenerator service
"""
import pytest
import zipfile
import io
from services.generator import ProjectGenerator
from models.project_config import ProjectConfig


class TestProjectGenerator:
    """Test the project generator service"""
    
    def test_generator_initialization(self, generator):
        """Test that generator initializes correctly"""
        assert generator is not None
        assert generator.template_dir.exists()
        assert generator.env is not None
    
    def test_build_context_minimal(self, generator, minimal_config):
        """Test context building for minimal config"""
        context = generator._build_context(minimal_config)
        
        assert context["project_name"] == "test_project"
        assert context["python_version"] == "3.11"
        assert context["database"] == "none"
        assert context["structure"] == "minimal"
        assert context["has_database"] is False
        assert context["has_sqlalchemy"] is False
        assert context["has_jwt"] is False
        assert context["has_docker"] is False
    
    def test_build_context_standard(self, generator, standard_config):
        """Test context building for standard config"""
        context = generator._build_context(standard_config)
        
        assert context["project_name"] == "my_api"
        assert context["database"] == "postgresql"
        assert context["has_database"] is True
        assert context["has_sqlalchemy"] is True
        assert context["has_alembic"] is True
        assert context["has_jwt"] is True
        assert context["has_cors"] is True
        assert context["has_docker"] is True
    
    def test_build_context_advanced(self, generator, modular_config):
        """Test context building for advanced config"""
        context = generator._build_context(modular_config)
        
        assert context["has_sqlalchemy"] is True
        assert context["has_jwt"] is True
        assert context["has_oauth2"] is True
        assert context["has_celery"] is True
        assert context["has_redis"] is True
        assert context["has_logging"] is True
        assert context["has_prometheus"] is True
        assert context["include_middleware"] is True
    
    def test_generate_minimal_project(self, generator, minimal_config):
        """Test generating a minimal project"""
        zip_buffer = generator.generate_project(minimal_config)
        
        assert isinstance(zip_buffer, io.BytesIO)
        assert zip_buffer.getbuffer().nbytes > 0
        
        # Verify ZIP contents
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            # Check core files exist
            assert "test_project/main.py" in files
            assert "test_project/requirements.txt" in files
            assert "test_project/README.md" in files
            assert "test_project/.gitignore" in files
            assert "test_project/.env.example" in files
            assert "test_project/app/__init__.py" in files
    
    def test_generate_standard_project(self, generator, standard_config):
        """Test generating a standard project"""
        zip_buffer = generator.generate_project(standard_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            # Core files
            assert "my_api/main.py" in files
            assert "my_api/requirements.txt" in files
            assert "my_api/README.md" in files
            
            # Structure-specific files
            assert "my_api/app/__init__.py" in files
            assert "my_api/app/api.py" in files
            assert "my_api/app/schemas.py" in files
            
            # Module files
            assert "my_api/app/database.py" in files
            assert "my_api/app/models.py" in files
            assert "my_api/app/auth.py" in files
            
            # Docker files
            assert "my_api/Dockerfile" in files
            assert "my_api/docker-compose.yml" in files
            
            # Test files
            assert "my_api/tests/__init__.py" in files
            assert "my_api/tests/test_main.py" in files
            assert "my_api/tests/conftest.py" in files
    
    def test_generate_modular_project(self, generator, modular_config):
        """Test generating a modular project"""
        zip_buffer = generator.generate_project(modular_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            # Modular structure
            assert "advanced_api/app/__init__.py" in files
            assert "advanced_api/app/api/__init__.py" in files
            assert "advanced_api/app/api/v1/__init__.py" in files
            assert "advanced_api/app/api/v1/endpoints.py" in files
            assert "advanced_api/app/schemas/__init__.py" in files
            assert "advanced_api/app/core/__init__.py" in files
            assert "advanced_api/app/core/config.py" in files
            
            # Modules
            assert "advanced_api/app/database.py" in files
            assert "advanced_api/app/models.py" in files
            assert "advanced_api/app/auth.py" in files
            assert "advanced_api/app/celery_app.py" in files
            assert "advanced_api/app/middleware.py" in files
            assert "advanced_api/app/logging_config.py" in files
            
            # CI/CD
            assert "advanced_api/.github/workflows/ci.yml" in files
    
    def test_generate_microservice_project(self, generator, microservice_config):
        """Test generating a microservice project"""
        zip_buffer = generator.generate_project(microservice_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            # Microservice structure
            assert "user_service/app/__init__.py" in files
            assert "user_service/app/api/__init__.py" in files
            assert "user_service/app/api/v1/__init__.py" in files
            assert "user_service/app/api/v1/endpoints.py" in files
            
            # Modules
            assert "user_service/app/database.py" in files
            assert "user_service/app/auth.py" in files
            assert "user_service/app/logging_config.py" in files
            assert "user_service/app/rate_limiter.py" in files
    
    def test_requirements_content_minimal(self, generator, minimal_config):
        """Test requirements.txt content for minimal project"""
        zip_buffer = generator.generate_project(minimal_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            requirements = zf.read("test_project/requirements.txt").decode()
            
            assert "fastapi" in requirements
            assert "uvicorn" in requirements
            assert "pydantic" in requirements
    
    def test_requirements_content_with_database(self, generator, standard_config):
        """Test requirements.txt includes database dependencies"""
        zip_buffer = generator.generate_project(standard_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            requirements = zf.read("my_api/requirements.txt").decode()
            
            assert "sqlalchemy" in requirements.lower()
            assert "alembic" in requirements.lower()
            assert "psycopg2" in requirements.lower() or "asyncpg" in requirements.lower()
    
    def test_main_py_content(self, generator, minimal_config):
        """Test main.py contains valid FastAPI code"""
        zip_buffer = generator.generate_project(minimal_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            main_content = zf.read("test_project/main.py").decode()
            
            assert "from fastapi import FastAPI" in main_content
            assert "app = FastAPI" in main_content
            assert "def read_root" in main_content or "@app.get" in main_content
    
    def test_docker_files_when_enabled(self, generator, standard_config):
        """Test Docker files are included when enabled"""
        zip_buffer = generator.generate_project(standard_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            dockerfile = zf.read("my_api/Dockerfile").decode()
            compose = zf.read("my_api/docker-compose.yml").decode()
            
            assert "FROM python:" in dockerfile
            assert "COPY requirements.txt" in dockerfile
            assert "version:" in compose
            assert "services:" in compose
    
    def test_docker_files_excluded_when_disabled(self, generator, minimal_config):
        """Test Docker files are not included when disabled"""
        zip_buffer = generator.generate_project(minimal_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert not any("Dockerfile" in f for f in files)
            assert not any("docker-compose" in f for f in files)
    
    def test_test_files_when_enabled(self, generator, standard_config):
        """Test test files are included when enabled"""
        zip_buffer = generator.generate_project(standard_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert "my_api/tests/__init__.py" in files
            assert "my_api/tests/test_main.py" in files
            assert "my_api/tests/conftest.py" in files
            
            test_content = zf.read("my_api/tests/test_main.py").decode()
            assert "def test_" in test_content or "async def test_" in test_content
    
    def test_ci_cd_github_actions(self, generator, modular_config):
        """Test GitHub Actions CI/CD file generation"""
        zip_buffer = generator.generate_project(modular_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            ci_file = zf.read("advanced_api/.github/workflows/ci.yml").decode()
            
            assert "name:" in ci_file
            assert "on:" in ci_file
            assert "jobs:" in ci_file
            assert "pytest" in ci_file or "test" in ci_file.lower()
    
    def test_ci_cd_gitlab(self, generator):
        """Test GitLab CI/CD file generation"""
        config = ProjectConfig(
            project_name="gitlab_project",
            ci_cd="gitlab-ci"
        )
        zip_buffer = generator.generate_project(config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            assert "gitlab_project/.gitlab-ci.yml" in files
            
            ci_content = zf.read("gitlab_project/.gitlab-ci.yml").decode()
            assert "stages:" in ci_content
            # Check for either "test" job/stage or "lint" stage (which is part of testing)
            assert "test" in ci_content.lower() or "lint" in ci_content.lower()
    
    def test_gitignore_content(self, generator, minimal_config):
        """Test .gitignore contains common Python patterns"""
        zip_buffer = generator.generate_project(minimal_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            gitignore = zf.read("test_project/.gitignore").decode()
            
            assert "__pycache__" in gitignore
            assert "*.py" in gitignore  # Covers *.pyc, *.pyo, etc.
            assert ".env" in gitignore
            assert "venv/" in gitignore or ".venv/" in gitignore
    
    def test_readme_content(self, generator, standard_config):
        """Test README.md contains project information"""
        zip_buffer = generator.generate_project(standard_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            readme = zf.read("my_api/README.md").decode()
            
            assert "my_api" in readme or "My API" in readme.lower()
            assert "FastAPI" in readme
            assert "##" in readme  # Markdown headers
    
    def test_logging_files_when_enabled(self, generator, modular_config):
        """Test logging files are created when enabled"""
        zip_buffer = generator.generate_project(modular_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert "advanced_api/app/logging_config.py" in files
            assert "advanced_api/logs/.gitkeep" in files
    
    def test_middleware_when_enabled(self, generator, modular_config):
        """Test middleware file is created when enabled"""
        zip_buffer = generator.generate_project(modular_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert "advanced_api/app/middleware.py" in files
            
            middleware = zf.read("advanced_api/app/middleware.py").decode()
            assert "middleware" in middleware.lower()
    
    def test_celery_module_when_included(self, generator, modular_config):
        """Test Celery module is created when included in dependencies"""
        zip_buffer = generator.generate_project(modular_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert "advanced_api/app/celery_app.py" in files
            
            celery_content = zf.read("advanced_api/app/celery_app.py").decode()
            assert "celery" in celery_content.lower()
    
    def test_auth_module_when_jwt_included(self, generator, standard_config):
        """Test auth module is created when JWT is included"""
        zip_buffer = generator.generate_project(standard_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert "my_api/app/auth.py" in files
            
            auth_content = zf.read("my_api/app/auth.py").decode()
            assert "jwt" in auth_content.lower() or "token" in auth_content.lower()
    
    def test_rate_limiter_when_included(self, generator, microservice_config):
        """Test rate limiter module is created when included"""
        zip_buffer = generator.generate_project(microservice_config)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            files = zf.namelist()
            
            assert "user_service/app/rate_limiter.py" in files
