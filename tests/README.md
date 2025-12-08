# FastAPI Starter Generator - Test Suite

This directory contains the comprehensive test suite for the FastAPI Starter Generator.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_project_config.py   # Tests for ProjectConfig model validation
├── test_generator.py        # Tests for ProjectGenerator service
└── test_api.py              # Tests for FastAPI endpoints
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_generator.py
```

### Run specific test class
```bash
pytest tests/test_generator.py::TestProjectGenerator
```

### Run specific test
```bash
pytest tests/test_generator.py::TestProjectGenerator::test_generate_minimal_project
```

### Run with verbose output
```bash
pytest -v
```

### Run tests matching a pattern
```bash
pytest -k "test_generate"
```

### Show test coverage in terminal
```bash
pytest --cov=. --cov-report=term-missing
```

## Test Categories

### Unit Tests

**test_project_config.py** - Tests for configuration validation:
- Project name validation
- Python version validation
- Database validation
- Structure validation
- Default values
- Optional fields

**test_generator.py** - Tests for project generator:
- Context building
- Project generation for different structures
- Template rendering
- File inclusion/exclusion logic
- Module generation
- Docker file generation
- CI/CD file generation

**test_api.py** - Tests for API endpoints:
- Health check endpoint
- Options endpoint
- Generate endpoint
- Error handling
- CORS configuration

## Test Fixtures

The `conftest.py` file provides reusable fixtures:

- `template_dir`: Path to templates directory
- `generator`: ProjectGenerator instance
- `minimal_config`: Minimal project configuration
- `standard_config`: Standard project configuration
- `modular_config`: Modular project configuration
- `microservice_config`: Microservice project configuration

## Coverage Goals

Target: **90%+ code coverage**

Current coverage includes:
- ✅ Model validation
- ✅ Template rendering
- ✅ Project generation
- ✅ API endpoints
- ✅ Error handling

## Writing New Tests

When adding new features, ensure:

1. Add tests for new models/validators
2. Add tests for new template logic
3. Add tests for new API endpoints
4. Update fixtures as needed
5. Maintain >90% coverage

Example test structure:
```python
def test_new_feature(generator, standard_config):
    """Test description"""
    # Arrange
    config = standard_config
    
    # Act
    result = generator.some_method(config)
    
    # Assert
    assert result is not None
    assert result.some_property == expected_value
```

## Continuous Integration

Tests are run automatically on:
- Every commit (if CI/CD is configured)
- Pull requests
- Before deployment

## Common Issues

**Import Errors**: Make sure you're in the project root and dependencies are installed:
```bash
pip install -r requirements.txt
```

**Template Not Found**: Ensure templates directory exists and contains all required templates.

**ZIP File Errors**: Check that all template files are valid Jinja2 templates.

## Test Data

Tests use:
- In-memory configurations (no file I/O)
- Temporary ZIP buffers
- Mock data where appropriate
- Real templates from the templates/ directory
