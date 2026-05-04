"""
FastAPI Project Generator
Like Spring Initializr but for FastAPI projects.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import io
import logging

from services.generator import ProjectGenerator, _TEMPLATES_DIR
from models.project_config import ProjectConfig, AvailableOptions
from models.options_data import AVAILABLE_OPTIONS
from config import settings
from middleware.error_handler import (
    AppException,
    ProjectGenerationError,
    ResourceNotFoundError,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    RequestTrackingMiddleware,
)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup checks ───────────────────────────────────────────────────
    if not _TEMPLATES_DIR.exists():
        raise RuntimeError(f"Templates directory not found: {_TEMPLATES_DIR}")
    if not Path("client/index.html").exists():
        logger.warning("client/index.html not found — UI will not be available")
    settings.warn_if_insecure()
    logger.info(f"Starting {settings.app_name} v{settings.app_version} ({settings.environment})")
    yield


app = FastAPI(
    title=settings.app_name,
    description="Generate ready-to-run FastAPI starter projects",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Serve CSS, JS, and other static assets from the client/ directory.
app.mount("/static", StaticFiles(directory="client"), name="static")

generator = ProjectGenerator()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main UI."""
    try:
        with open("client/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("client/index.html not found")
        raise ResourceNotFoundError("UI file", "client/index.html")
    except Exception as e:
        logger.error(f"Error reading index.html: {e}")
        raise HTTPException(status_code=500, detail="Error loading UI")


@app.get("/icon.svg")
async def get_icon():
    """Serve the favicon."""
    icon_path = Path("icon.svg")
    if icon_path.exists():
        return FileResponse(str(icon_path), media_type="image/svg+xml")
    raise ResourceNotFoundError("Icon file", "icon.svg")


@app.get("/api/options", response_model=AvailableOptions)
async def get_options():
    """Return all available project configuration options."""
    return AVAILABLE_OPTIONS


@app.post("/api/generate")
async def generate_project(config: ProjectConfig):
    """
    Generate and return a FastAPI project as a ZIP file.

    Pydantic validates all fields before this handler runs — no manual
    re-validation needed here.
    """
    logger.info(f"Generating project: {config.project_name}")
    try:
        zip_buffer = generator.generate_project(config)
        logger.info(f"Successfully generated project: {config.project_name}")
        return StreamingResponse(
            io.BytesIO(zip_buffer.getvalue()),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={config.project_name}.zip"
            },
        )
    except Exception as e:
        logger.error(f"Error generating project {config.project_name}: {e}")
        raise ProjectGenerationError(
            f"Failed to generate project: {e}",
            details={"project_name": config.project_name, "error": str(e)},
        )


@app.get("/health")
async def health_check():
    """Health check for load balancers and monitoring."""
    return {"status": "healthy", "service": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
