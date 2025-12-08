"""
Tests for enhanced error handling middleware
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from middleware.error_handler import (
    ValidationError,
    ValidationUtils,
    ResourceNotFoundError,
    ProjectGenerationError,
    RateLimitExceededError,
    ConfigurationError,
    BusinessLogicError
)


client = TestClient(app)


class TestExceptionClasses:
    """Test custom exception classes"""
    
    def test_validation_error(self):
        """Test ValidationError exception"""
        error = ValidationError(
            "Invalid input",
            details={"field": "test", "value": "invalid"}
        )
        assert error.status_code == 422
        assert error.error_code == "VALIDATION_ERROR"
        assert "field" in error.details
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError exception"""
        error = ResourceNotFoundError("User", "123")
        assert error.status_code == 404
        assert error.error_code == "RESOURCE_NOT_FOUND"
        assert "User" in error.message
    
    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError exception"""
        error = RateLimitExceededError(retry_after=120)
        assert error.status_code == 429
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.details["retry_after"] == 120
    
    def test_project_generation_error(self):
        """Test ProjectGenerationError exception"""
        error = ProjectGenerationError(
            "Failed to generate",
            details={"project": "test"}
        )
        assert error.status_code == 500
        assert error.error_code == "PROJECT_GENERATION_FAILED"


class TestValidationUtils:
    """Test ValidationUtils methods"""
    
    def test_validate_string_length_success(self):
        """Test successful string length validation"""
        ValidationUtils.validate_string_length("test", "field", 1, 10)
        # Should not raise
    
    def test_validate_string_length_too_short(self):
        """Test string too short validation"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_string_length("", "field", 1, 10)
        assert "at least 1 characters" in str(exc_info.value.message)
    
    def test_validate_string_length_too_long(self):
        """Test string too long validation"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_string_length("x" * 100, "field", 1, 10)
        assert "must not exceed" in str(exc_info.value.message)
    
    def test_validate_alphanumeric_success(self):
        """Test successful alphanumeric validation"""
        ValidationUtils.validate_alphanumeric("test_project-123", "field", "_-")
        # Should not raise
    
    def test_validate_alphanumeric_failure(self):
        """Test alphanumeric validation failure"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_alphanumeric("test@project!", "field", "_-")
        assert "must contain only" in str(exc_info.value.message)
    
    def test_validate_email_success(self):
        """Test successful email validation"""
        ValidationUtils.validate_email("test@example.com")
        # Should not raise
    
    def test_validate_email_failure(self):
        """Test email validation failure"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_email("invalid-email")
        assert "Invalid" in str(exc_info.value.message)
    
    def test_validate_choice_success(self):
        """Test successful choice validation"""
        ValidationUtils.validate_choice("option1", "field", ["option1", "option2"])
        # Should not raise
    
    def test_validate_choice_failure(self):
        """Test choice validation failure"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_choice("option3", "field", ["option1", "option2"])
        assert "Must be one of" in str(exc_info.value.message)
    
    def test_validate_file_size_success(self):
        """Test successful file size validation"""
        ValidationUtils.validate_file_size(5 * 1024 * 1024, max_size_mb=10)
        # Should not raise
    
    def test_validate_file_size_failure(self):
        """Test file size validation failure"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_file_size(15 * 1024 * 1024, max_size_mb=10)
        assert "exceeds maximum" in str(exc_info.value.message)
    
    def test_validate_non_empty_list_success(self):
        """Test successful non-empty list validation"""
        ValidationUtils.validate_non_empty_list(["item1", "item2"], "field")
        # Should not raise
    
    def test_validate_non_empty_list_failure(self):
        """Test non-empty list validation failure"""
        with pytest.raises(ValidationError) as exc_info:
            ValidationUtils.validate_non_empty_list([], "field")
        assert "at least one item" in str(exc_info.value.message)
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        result = ValidationUtils.sanitize_string("  test  ", max_length=10)
        assert result == "test"
        
        result = ValidationUtils.sanitize_string("x" * 100, max_length=10)
        assert len(result) == 10


class TestAPIErrorHandling:
    """Test API error handling"""
    
    def test_validation_error_response(self):
        """Test validation error response format"""
        response = client.post("/api/generate", json={
            "project_name": "",  # Invalid: too short
            "python_version": "3.11"
        })
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "request_id" in data["error"]
        assert "timestamp" in data["error"]
    
    def test_invalid_project_name(self):
        """Test invalid project name validation"""
        response = client.post("/api/generate", json={
            "project_name": "invalid@name!",
            "python_version": "3.11"
        })
        assert response.status_code == 422
    
    def test_project_name_too_long(self):
        """Test project name too long"""
        response = client.post("/api/generate", json={
            "project_name": "x" * 100,
            "python_version": "3.11"
        })
        assert response.status_code == 422
    
    def test_invalid_python_version(self):
        """Test invalid Python version"""
        response = client.post("/api/generate", json={
            "project_name": "test_project",
            "python_version": "2.7"  # Not supported
        })
        assert response.status_code == 422
    
    def test_invalid_database(self):
        """Test invalid database choice"""
        response = client.post("/api/generate", json={
            "project_name": "test_project",
            "python_version": "3.11",
            "database": "invalid_db"
        })
        assert response.status_code == 422
    
    def test_invalid_structure(self):
        """Test invalid structure choice"""
        response = client.post("/api/generate", json={
            "project_name": "test_project",
            "python_version": "3.11",
            "structure": "invalid_structure"
        })
        assert response.status_code == 422
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_options_endpoint(self):
        """Test options endpoint"""
        response = client.get("/api/options")
        assert response.status_code == 200
        data = response.json()
        assert "python_versions" in data
        assert "databases" in data
        assert "dependencies" in data


class TestRequestTracking:
    """Test request tracking middleware"""
    
    def test_request_id_in_response(self):
        """Test that request ID is included in response headers"""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
    
    def test_process_time_in_response(self):
        """Test that process time is included in response headers"""
        response = client.get("/health")
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
    
    def test_custom_request_id(self):
        """Test custom request ID from header"""
        custom_id = "custom-request-123"
        response = client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id


class TestErrorResponseFormat:
    """Test error response format consistency"""
    
    def test_error_response_structure(self):
        """Test that all error responses have consistent structure"""
        response = client.post("/api/generate", json={
            "project_name": "",
            "python_version": "3.11"
        })
        
        data = response.json()
        assert "error" in data
        error = data["error"]
        
        # Check required fields
        assert "message" in error
        assert "code" in error
        assert "type" in error
        assert "path" in error
        assert "timestamp" in error
        assert "request_id" in error
    
    def test_validation_error_details(self):
        """Test validation error includes detailed error information"""
        response = client.post("/api/generate", json={
            "project_name": "",
            "python_version": "3.11"
        })
        
        data = response.json()
        error = data["error"]
        assert "details" in error
        assert "errors" in error["details"]
        assert isinstance(error["details"]["errors"], list)
