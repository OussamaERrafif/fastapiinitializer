"""
Available options data for project generation.

Single source of truth for all valid choices exposed via /api/options.
Constants are imported by ProjectConfig validators to stay in sync.
"""
from models.project_config import (
    VALID_PYTHON_VERSIONS,
    VALID_DATABASES,
    VALID_STRUCTURES,
    AvailableOptions,
    DependencyOption,
    TemplateOption,
    CICDOption,
)

AVAILABLE_OPTIONS = AvailableOptions(
    python_versions=VALID_PYTHON_VERSIONS,
    databases=VALID_DATABASES,
    dependencies=[
        # Database / ORM
        DependencyOption(id="sqlalchemy", name="SQLAlchemy", description="SQL toolkit and ORM", category="database"),
        DependencyOption(id="alembic", name="Alembic", description="Database migrations", category="database"),
        DependencyOption(id="tortoise", name="Tortoise ORM", description="Async ORM", category="database"),
        # Authentication
        DependencyOption(id="jwt", name="JWT Auth", description="JSON Web Token authentication", category="auth"),
        DependencyOption(id="oauth2", name="OAuth2", description="OAuth2 authentication", category="auth"),
        DependencyOption(id="passlib", name="Passlib", description="Password hashing", category="auth"),
        # Caching & Queues
        DependencyOption(id="redis", name="Redis", description="Caching and message broker", category="cache"),
        DependencyOption(id="celery", name="Celery", description="Distributed task queue", category="tasks"),
        DependencyOption(id="arq", name="ARQ", description="Async task queue with Redis", category="tasks"),
        # API Features
        DependencyOption(id="graphql", name="GraphQL", description="GraphQL support with Strawberry", category="api"),
        DependencyOption(id="websockets", name="WebSockets", description="WebSocket support", category="api"),
        DependencyOption(id="cors", name="CORS", description="Cross-Origin Resource Sharing", category="api"),
        # Monitoring & Logging
        DependencyOption(id="logging", name="Structured Logging", description="JSON logging with Loguru", category="monitoring"),
        DependencyOption(id="prometheus", name="Prometheus", description="Metrics and monitoring", category="monitoring"),
        DependencyOption(id="sentry", name="Sentry", description="Error tracking", category="monitoring"),
        # Development
        DependencyOption(id="pytest", name="Pytest", description="Testing framework", category="dev"),
        DependencyOption(id="docker", name="Docker", description="Docker configuration", category="dev"),
        DependencyOption(id="pre-commit", name="Pre-commit", description="Git hooks for code quality", category="dev"),
        # Performance
        DependencyOption(id="caching", name="HTTP Caching", description="Response caching layer", category="performance"),
        DependencyOption(id="ratelimit", name="Rate Limiting", description="API rate limiting", category="performance"),
    ],
    structures=VALID_STRUCTURES,
    templates=[
        TemplateOption(id="blank", name="Blank Project", description="Start from scratch"),
        TemplateOption(id="crud", name="CRUD API", description="Complete CRUD operations"),
        TemplateOption(id="microservice", name="Microservice", description="Production microservice"),
        TemplateOption(id="monolith", name="Monolith", description="Full-featured application"),
        TemplateOption(id="api-gateway", name="API Gateway", description="Gateway pattern"),
    ],
    ci_cd=[
        CICDOption(id="github-actions", name="GitHub Actions", description="CI/CD with GitHub"),
        CICDOption(id="gitlab-ci", name="GitLab CI", description="CI/CD with GitLab"),
        CICDOption(id="none", name="None", description="No CI/CD"),
    ],
)
