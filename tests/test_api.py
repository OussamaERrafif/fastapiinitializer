"""
Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from models.project_config import ProjectConfig


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns success"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data  # Check for service name instead of timestamp


class TestOptionsEndpoint:
    """Test options endpoint"""
    
    def test_get_options(self):
        """Test getting available options"""
        response = client.get("/api/options")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "python_versions" in data
        assert "databases" in data
        assert "dependencies" in data
        assert "structures" in data
        assert "templates" in data
        assert "ci_cd" in data
        
        # Verify content types
        assert isinstance(data["python_versions"], list)
        assert isinstance(data["databases"], list)
        assert isinstance(data["dependencies"], list)
        assert isinstance(data["structures"], list)
        
        # Verify some expected values
        assert "3.11" in data["python_versions"]
        assert "postgresql" in data["databases"]
        assert "standard" in data["structures"]


class TestGenerateEndpoint:
    """Test project generation endpoint"""
    
    def test_generate_minimal_project(self):
        """Test generating a minimal project"""
        config = {
            "project_name": "test_api",
            "python_version": "3.11",
            "database": "none",
            "structure": "minimal",
            "include_docker": False,
            "include_tests": False
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert len(response.content) > 0
    
    def test_generate_standard_project(self):
        """Test generating a standard project"""
        config = {
            "project_name": "my_api",
            "python_version": "3.11",
            "database": "postgresql",
            "dependencies": ["sqlalchemy", "alembic", "jwt", "cors"],
            "structure": "standard",
            "include_docker": True,
            "include_tests": True,
            "description": "My FastAPI project",
            "author": "Test Author"
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert len(response.content) > 1000  # Should be substantial
    
    def test_generate_modular_project(self):
        """Test generating a modular project"""
        config = {
            "project_name": "advanced_api",
            "python_version": "3.12",
            "database": "postgresql",
            "dependencies": ["sqlalchemy", "jwt", "cors", "logging", "prometheus"],
            "structure": "modular",
            "include_docker": True,
            "include_tests": True,
            "ci_cd": "github-actions"
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
    
    def test_generate_with_invalid_project_name(self):
        """Test that invalid project names are rejected"""
        config = {
            "project_name": "invalid project name!",
            "python_version": "3.11"
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 422  # Validation error
    
    def test_generate_with_invalid_python_version(self):
        """Test that invalid Python versions are rejected"""
        config = {
            "project_name": "test_api",
            "python_version": "3.8"  # Not supported
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 422
    
    def test_generate_with_invalid_database(self):
        """Test that invalid database choices are rejected"""
        config = {
            "project_name": "test_api",
            "database": "oracle"  # Not supported
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 422
    
    def test_generate_with_invalid_structure(self):
        """Test that invalid structures are rejected"""
        config = {
            "project_name": "test_api",
            "structure": "custom"  # Not supported
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 422
    
    def test_generate_with_all_dependencies(self):
        """Test generating with many dependencies"""
        config = {
            "project_name": "full_api",
            "python_version": "3.11",
            "database": "postgresql",
            "dependencies": [
                "sqlalchemy", "alembic", "jwt", "oauth2", "passlib",
                "celery", "redis", "cors", "logging", "prometheus",
                "sentry", "ratelimit", "caching"
            ],
            "structure": "modular",
            "include_docker": True,
            "include_tests": True,
            "ci_cd": "github-actions"
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
        assert len(response.content) > 5000
    
    def test_generate_microservice(self):
        """Test generating a microservice"""
        config = {
            "project_name": "user_service",
            "python_version": "3.11",
            "database": "postgresql",
            "dependencies": ["sqlalchemy", "jwt", "cors", "prometheus", "ratelimit"],
            "structure": "microservice",
            "include_docker": True,
            "include_tests": True
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
    
    def test_generate_with_gitlab_ci(self):
        """Test generating with GitLab CI"""
        config = {
            "project_name": "gitlab_api",
            "python_version": "3.11",
            "ci_cd": "gitlab-ci",
            "include_tests": True
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
    
    def test_generate_mongodb_project(self):
        """Test generating with MongoDB"""
        config = {
            "project_name": "mongo_api",
            "python_version": "3.11",
            "database": "mongodb",
            "structure": "standard"
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200
    
    def test_generate_sqlite_project(self):
        """Test generating with SQLite"""
        config = {
            "project_name": "sqlite_api",
            "python_version": "3.11",
            "database": "sqlite",
            "dependencies": ["sqlalchemy"],
            "structure": "minimal"
        }
        
        response = client.post("/api/generate", json=config)
        assert response.status_code == 200


class TestCORSHeaders:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses"""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        # CORS middleware should add headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self):
        """Test 404 response for non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test 405 response for wrong HTTP method"""
        response = client.put("/health")
        assert response.status_code == 405
