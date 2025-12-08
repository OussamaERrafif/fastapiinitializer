# Contributing to FastAPI Initializer

First off, thank you for considering contributing to FastAPI Initializer! 🎉

It's people like you that make FastAPI Initializer such a great tool. We welcome contributions from everyone, whether it's a bug report, feature suggestion, documentation improvement, or code contribution.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Improving Documentation](#improving-documentation)
  - [Contributing Code](#contributing-code)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Style Guide](#python-style-guide)
  - [Documentation Style](#documentation-style)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and constructive
- **Focus on what is best** for the community
- **Show empathy** towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g., Windows 10, macOS 12.0, Ubuntu 20.04]
- Python Version: [e.g., 3.12]
- Browser: [e.g., Chrome 120, Firefox 121]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Features

We love to hear your ideas for new features! Before creating a feature request:

1. **Check existing issues** to see if it's already been suggested
2. **Clearly describe the feature** and its use case
3. **Explain why it would be useful** to most users

**Feature Request Template:**

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Add any other context, mockups, or examples about the feature request.
```

### Improving Documentation

Documentation improvements are always welcome! This includes:

- Fixing typos or grammatical errors
- Adding examples or clarifications
- Improving the README
- Adding or updating API documentation
- Creating tutorials or guides

### Contributing Code

1. **Find an issue to work on** or create a new one
2. **Comment on the issue** to let others know you're working on it
3. **Fork the repository**
4. **Create a feature branch**
5. **Make your changes**
6. **Test your changes**
7. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.12+ (recommended) or Python 3.9+
- Git
- pip

### Setup Steps

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/fastapiinitializer.git
   cd fastapiinitializer
   ```

2. **Create a virtual environment**

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   uvicorn main:app --reload
   ```

5. **Run tests**

   ```bash
   pytest
   ```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update the README.md** if needed
5. **Follow the style guidelines** below
6. **Write a clear PR description** explaining:
   - What changes you made
   - Why you made them
   - Any relevant issue numbers

### PR Title Format

Use clear, descriptive titles:

- `fix: Correct typo in README`
- `feat: Add PostgreSQL connection pooling`
- `docs: Update installation instructions`
- `test: Add tests for project generator`
- `refactor: Improve error handling middleware`

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Motivation and Context
Why is this change required? What problem does it solve?

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## Style Guidelines

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

**Example:**

```
feat: Add JWT token refresh endpoint

- Implement refresh token logic
- Add tests for token refresh
- Update authentication documentation

Closes #123
```

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Group in order: standard library, third-party, local
- **Quotes**: Prefer double quotes for strings
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

**Example:**

```python
from typing import List, Optional
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from models.project_config import ProjectConfig


class ProjectGenerator:
    """Generate FastAPI projects from templates."""
    
    MAX_PROJECT_NAME_LENGTH = 50
    
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
    
    def generate_project(self, config: ProjectConfig) -> bytes:
        """Generate a project ZIP file based on configuration."""
        # Implementation here
        pass
```

### Documentation Style

- Use **docstrings** for all public modules, functions, classes, and methods
- Follow **Google style** for docstrings
- Add **type hints** to function signatures
- Keep comments clear and concise

**Example:**

```python
def render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template with the given context.
    
    Args:
        template_name: Name of the template file
        context: Dictionary of variables to pass to template
        
    Returns:
        Rendered template as string
        
    Raises:
        TemplateNotFoundError: If template doesn't exist
    """
    # Implementation here
    pass
```

## Project Structure

Understanding the project structure will help you navigate the codebase:

```
fastapiinitializer/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration management
├── models/                  # Pydantic models
│   └── project_config.py
├── services/                # Business logic
│   └── generator.py         # Project generation service
├── middleware/              # Custom middleware
│   └── error_handler.py
├── templates/               # Jinja2 templates for code generation
│   ├── main.py.jinja2
│   ├── modules/
│   ├── structures/
│   └── optional/
├── client/                  # Frontend HTML/CSS/JS
│   └── index.html
└── tests/                   # Test suite
    ├── test_api.py
    ├── test_generator.py
    └── conftest.py
```

## Testing

We use **pytest** for testing. Please add tests for any new features:

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_generator.py

# Run specific test
pytest tests/test_api.py::test_generate_endpoint

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures from `conftest.py`
- Aim for high test coverage

**Example:**

```python
import pytest
from fastapi.testclient import TestClient


def test_generate_project_success(client: TestClient):
    """Test successful project generation."""
    response = client.post(
        "/api/generate",
        json={
            "project_name": "test_api",
            "python_version": "3.12",
            "structure": "standard",
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
```

## Community

### Getting Help

- **GitHub Discussions**: For questions and general discussions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: Contact maintainers via GitHub

### Recognition

Contributors will be:
- Listed in the project's contributors page
- Mentioned in release notes for significant contributions
- Given credit in the README

---

## Thank You! 🙏

Your contributions make this project better for everyone. We appreciate your time and effort!

**Happy Coding! 🚀**
