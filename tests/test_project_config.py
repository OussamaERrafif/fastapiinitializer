"""
Tests for ProjectConfig model validation
"""
import pytest
from pydantic import ValidationError
from models.project_config import ProjectConfig


class TestProjectConfigValidation:
    """Test project configuration validation"""
    
    def test_valid_minimal_config(self):
        """Test creating a minimal valid configuration"""
        config = ProjectConfig(project_name="test_project")
        assert config.project_name == "test_project"
        assert config.python_version == "3.11"
        assert config.database == "none"
        assert config.structure == "standard"
        assert config.include_tests is True
    
    def test_project_name_validation(self):
        """Test project name validation rules"""
        # Valid names
        valid_names = ["my_project", "my-project", "MyProject123", "project_123"]
        for name in valid_names:
            config = ProjectConfig(project_name=name)
            assert config.project_name.islower()
            assert "_" in config.project_name or config.project_name.isalnum()
        
        # Invalid names
        invalid_names = ["my project", "my@project", "my.project", ""]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                ProjectConfig(project_name=name)
    
    def test_project_name_conversion(self):
        """Test that hyphens are converted to underscores"""
        config = ProjectConfig(project_name="my-test-project")
        assert config.project_name == "my_test_project"
        
        config = ProjectConfig(project_name="MyTestProject")
        assert config.project_name == "mytestproject"
    
    def test_python_version_validation(self):
        """Test Python version validation"""
        # Valid versions
        valid_versions = ["3.9", "3.10", "3.11", "3.12"]
        for version in valid_versions:
            config = ProjectConfig(project_name="test", python_version=version)
            assert config.python_version == version
        
        # Invalid versions
        invalid_versions = ["3.8", "3.13", "2.7", "3", "3.11.0"]
        for version in invalid_versions:
            with pytest.raises(ValidationError):
                ProjectConfig(project_name="test", python_version=version)
    
    def test_database_validation(self):
        """Test database validation"""
        # Valid databases
        valid_dbs = ["none", "postgresql", "mysql", "sqlite", "mongodb"]
        for db in valid_dbs:
            config = ProjectConfig(project_name="test", database=db)
            assert config.database == db
        
        # Invalid database
        with pytest.raises(ValidationError):
            ProjectConfig(project_name="test", database="oracle")
    
    def test_structure_validation(self):
        """Test structure validation"""
        # Valid structures
        valid_structures = ["minimal", "standard", "modular", "microservice"]
        for structure in valid_structures:
            config = ProjectConfig(project_name="test", structure=structure)
            assert config.structure == structure
        
        # Invalid structure
        with pytest.raises(ValidationError):
            ProjectConfig(project_name="test", structure="custom")
    
    def test_dependencies_list(self):
        """Test dependencies can be set as a list"""
        deps = ["sqlalchemy", "alembic", "jwt", "cors"]
        config = ProjectConfig(project_name="test", dependencies=deps)
        assert config.dependencies == deps
        assert len(config.dependencies) == 4
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        config = ProjectConfig(project_name="test")
        assert config.python_version == "3.11"
        assert config.database == "none"
        assert config.structure == "standard"
        assert config.template == "blank"
        assert config.ci_cd == "none"
        assert config.include_docker is False
        assert config.include_tests is True
        assert config.include_middleware is True
        assert config.include_logging is True
        assert config.description == "A FastAPI project"
        assert config.author == ""
        assert config.license == "MIT"
    
    def test_optional_fields(self):
        """Test optional fields can be set"""
        config = ProjectConfig(
            project_name="test",
            description="My custom API",
            author="John Doe",
            license="Apache-2.0"
        )
        assert config.description == "My custom API"
        assert config.author == "John Doe"
        assert config.license == "Apache-2.0"
    
    def test_boolean_flags(self):
        """Test boolean configuration flags"""
        config = ProjectConfig(
            project_name="test",
            include_docker=True,
            include_tests=False,
            include_middleware=False,
            include_logging=False
        )
        assert config.include_docker is True
        assert config.include_tests is False
        assert config.include_middleware is False
        assert config.include_logging is False
