"""
FastAPI Project Generator - Main Application
Like Spring Initializr but for FastAPI projects
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import io
import logging

from services.generator import ProjectGenerator
from models.project_config import ProjectConfig, AvailableOptions
from config import settings
from middleware.error_handler import (
    AppException,
    ProjectGenerationError,
    ValidationError,
    ResourceNotFoundError,
    RateLimitExceededError,
    ConfigurationError,
    BusinessLogicError,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    RequestTrackingMiddleware,
    ValidationUtils
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Generate ready-to-run FastAPI starter projects",
    version=settings.app_version,
    debug=settings.debug
)

# Add request tracking middleware (should be first)
app.add_middleware(RequestTrackingMiddleware)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

generator = ProjectGenerator()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serve the main UI
    
    Returns:
        HTMLResponse: The main HTML page for the project generator interface
        
    Raises:
        ResourceNotFoundError: If the index.html file is not found
        HTTPException: If there's an error reading the file
    """
    try:
        with open("client/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("index.html not found")
        raise ResourceNotFoundError("UI file", "client/index.html")
    except Exception as e:
        logger.error(f"Error reading index.html: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error loading UI"
        )


@app.get("/icon.svg")
async def get_icon():
    """
    Serve the favicon icon
    
    Returns:
        Response: The SVG icon file
        
    Raises:
        ResourceNotFoundError: If the icon.svg file is not found
    """
    from fastapi.responses import FileResponse
    import os
    
    icon_path = "icon.svg"
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/svg+xml")
    else:
        logger.error("icon.svg not found")
        raise ResourceNotFoundError("Icon file", "icon.svg")


@app.get("/api/options", response_model=AvailableOptions)
async def get_options():
    """
    Get available project configuration options
    
    Returns all available choices for:
    - Python versions (3.9, 3.10, 3.11, 3.12)
    - Database types (PostgreSQL, MySQL, SQLite, MongoDB, Redis, None)
    - Dependencies (ORMs, auth, caching, monitoring, etc.)
    - Project structures (minimal, standard, modular, microservice)
    - Project templates (blank, CRUD, microservice, etc.)
    - CI/CD options (GitHub Actions, GitLab CI, None)
    
    Returns:
        AvailableOptions: Complete list of all available configuration options
    """
    return {
        "python_versions": ["3.12", "3.11", "3.10", "3.9"],
        "databases": ["none", "postgresql", "mysql", "sqlite", "mongodb", "redis"],
        "dependencies": [
            # Core ORM & DB
            {"id": "sqlalchemy", "name": "SQLAlchemy", "description": "SQL toolkit and ORM", "category": "database"},
            {"id": "alembic", "name": "Alembic", "description": "Database migrations", "category": "database"},
            {"id": "tortoise", "name": "Tortoise ORM", "description": "Async ORM", "category": "database"},
            
            # Authentication
            {"id": "jwt", "name": "JWT Auth", "description": "JSON Web Token authentication", "category": "auth"},
            {"id": "oauth2", "name": "OAuth2", "description": "OAuth2 authentication", "category": "auth"},
            {"id": "passlib", "name": "Passlib", "description": "Password hashing", "category": "auth"},
            
            # Caching & Queues
            {"id": "redis", "name": "Redis", "description": "Caching and message broker", "category": "cache"},
            {"id": "celery", "name": "Celery", "description": "Distributed task queue", "category": "tasks"},
            {"id": "arq", "name": "ARQ", "description": "Async task queue with Redis", "category": "tasks"},
            
            # API Features
            {"id": "graphql", "name": "GraphQL", "description": "GraphQL support with Strawberry", "category": "api"},
            {"id": "websockets", "name": "WebSockets", "description": "WebSocket support", "category": "api"},
            {"id": "cors", "name": "CORS", "description": "Cross-Origin Resource Sharing", "category": "api"},
            
            # Monitoring & Logging
            {"id": "logging", "name": "Structured Logging", "description": "JSON logging with Loguru", "category": "monitoring"},
            {"id": "prometheus", "name": "Prometheus", "description": "Metrics and monitoring", "category": "monitoring"},
            {"id": "sentry", "name": "Sentry", "description": "Error tracking", "category": "monitoring"},
            
            # Development
            {"id": "pytest", "name": "Pytest", "description": "Testing framework", "category": "dev"},
            {"id": "docker", "name": "Docker", "description": "Docker configuration", "category": "dev"},
            {"id": "pre-commit", "name": "Pre-commit", "description": "Git hooks for code quality", "category": "dev"},
            
            # Performance
            {"id": "caching", "name": "HTTP Caching", "description": "Response caching layer", "category": "performance"},
            {"id": "ratelimit", "name": "Rate Limiting", "description": "API rate limiting", "category": "performance"},
        ],
        "structures": ["minimal", "standard", "modular", "microservice"],
        "templates": [
            {"id": "blank", "name": "Blank Project", "description": "Start from scratch"},
            {"id": "crud", "name": "CRUD API", "description": "Complete CRUD operations"},
            {"id": "microservice", "name": "Microservice", "description": "Production microservice"},
            {"id": "monolith", "name": "Monolith", "description": "Full-featured application"},
            {"id": "api-gateway", "name": "API Gateway", "description": "Gateway pattern"},
        ],
        "ci_cd": [
            {"id": "github-actions", "name": "GitHub Actions", "description": "CI/CD with GitHub"},
            {"id": "gitlab-ci", "name": "GitLab CI", "description": "CI/CD with GitLab"},
            {"id": "none", "name": "None", "description": "No CI/CD"},
        ]
    }


@app.post("/api/generate")
async def generate_project(config: ProjectConfig):
    """
    Generate and return a FastAPI project as ZIP file
    
    This endpoint performs the following:
    1. Validates the project configuration (name, Python version, database, structure)
    2. Generates project files from templates based on selected options
    3. Creates a ZIP archive with all generated files
    4. Returns the ZIP file as a downloadable stream
    
    Args:
        config (ProjectConfig): Project configuration including:
            - project_name: Name of the project (alphanumeric, underscore, hyphen allowed)
            - python_version: Target Python version (3.9, 3.10, 3.11, 3.12)
            - database: Database choice (none, postgresql, mysql, sqlite, mongodb, redis)
            - dependencies: List of optional dependencies to include
            - structure: Project structure type (minimal, standard, modular, microservice)
            - include_docker: Whether to include Docker configuration
            - include_tests: Whether to include test suite
    
    Returns:
        StreamingResponse: ZIP file containing the generated project
        
    Raises:
        ValidationError: If configuration validation fails
        ProjectGenerationError: If project generation fails
    """
    logger.info(f"Generating project: {config.project_name}")
    
    # Enhanced validation using ValidationUtils
    try:
        # Validate project name length
        ValidationUtils.validate_string_length(
            config.project_name, 
            "project_name",
            min_length=1,
            max_length=settings.max_project_name_length
        )
        
        # Validate project name format
        ValidationUtils.validate_alphanumeric(
            config.project_name,
            "project_name",
            allow_special="_-"
        )
        
        # Validate Python version
        ValidationUtils.validate_choice(
            config.python_version,
            "python_version",
            ["3.9", "3.10", "3.11", "3.12"]
        )
        
        # Validate database choice
        ValidationUtils.validate_choice(
            config.database,
            "database",
            ["none", "postgresql", "mysql", "sqlite", "mongodb", "redis"]
        )
        
        # Validate structure choice
        ValidationUtils.validate_choice(
            config.structure,
            "structure",
            ["minimal", "standard", "modular", "microservice"]
        )
        
    except ValidationError:
        raise
    
    try:
        # Generate project files
        zip_buffer = generator.generate_project(config)
        
        logger.info(f"Successfully generated project: {config.project_name}")
        
        # Return as downloadable ZIP
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={config.project_name}.zip"
            }
        )
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error generating project {config.project_name}: {str(e)}")
        raise ProjectGenerationError(
            f"Failed to generate project: {str(e)}",
            details={"project_name": config.project_name, "error": str(e)}
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Used for monitoring service availability and health status.
    Can be used by load balancers, monitoring tools, or orchestration platforms.
    
    Returns:
        dict: Service status and name
            - status: "healthy" if service is running
            - service: Name of the service
    """
    return {"status": "healthy", "service": "FastAPI Project Generator"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    if settings.reload:
        # Use import string for reload functionality
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload
        )
    else:
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port
        )
