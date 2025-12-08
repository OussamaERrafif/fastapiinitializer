# Test Runner Scripts

## Quick Test Commands

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### Run specific test categories
```bash
# Run only unit tests
pytest tests/test_project_config.py tests/test_generator.py -v

# Run only API tests
pytest tests/test_api.py -v

# Run only tests matching a pattern
pytest -k "test_generate" -v
```

### Run with different output formats
```bash
# Verbose output
pytest -v

# Quiet output
pytest -q

# Show test durations
pytest --durations=10

# Show local variables on failure
pytest -l
```

### Coverage Commands
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Then open: htmlcov/index.html

# Generate XML coverage report (for CI)
pytest --cov=. --cov-report=xml

# Show coverage in terminal
pytest --cov=. --cov-report=term-missing

# Only show missing lines
pytest --cov=. --cov-report=term:skip-covered
```

### Advanced Testing
```bash
# Run in parallel (install pytest-xdist first: pip install pytest-xdist)
pytest -n auto

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff

# Show captured output for passed tests
pytest -s
```

## Test Files Overview

- **test_project_config.py** - Tests for configuration model validation (10 tests)
- **test_generator.py** - Tests for project generation logic (23 tests)
- **test_api.py** - Tests for FastAPI endpoints (17 tests)

## Coverage Report

Current coverage: **76%** overall

High coverage areas:
- ✅ models/project_config.py: **100%**
- ✅ services/generator.py: **98%**
- ✅ config.py: **100%**

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Scheduled runs (if configured)

## Common Issues

### Import Errors
```bash
pip install -r requirements.txt
```

### Template Not Found
Make sure you're in the project root directory.

### Python Version
Tests require Python 3.9+
