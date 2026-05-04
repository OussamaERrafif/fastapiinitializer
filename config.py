"""
Configuration management for FastAPI Project Generator.

Settings are loaded in priority order:
1. Environment variables
2. .env file
3. Defaults defined here
"""
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "FastAPIInitializer"
    app_version: str = "1"
    debug: bool = True
    environment: str = "development"

    # Server
    host: str = "localhost"
    port: int = 8000
    reload: bool = True

    # CORS — wildcard origin + credentials is rejected by browsers; keep them separate.
    # In production, set CORS_ORIGINS to your actual frontend URL(s).
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = False
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # File generation
    max_project_name_length: int = 50
    temp_dir: str = "./temp"
    cleanup_temp_files: bool = True

    # Rate limiting
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security — MUST be changed in production via SECRET_KEY env var
    secret_key: str = "your-secret-key-here-change-in-production"

    def warn_if_insecure(self) -> None:
        if self.secret_key == "your-secret-key-here-change-in-production":
            logging.warning(
                "SECRET_KEY is set to the default placeholder. "
                "Set the SECRET_KEY environment variable before deploying to production."
            )


settings = Settings()
