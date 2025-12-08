"""
Configuration management for FastAPI Project Generator

This module defines application settings using Pydantic Settings for type-safe
configuration management. Settings can be overridden via environment variables
or a .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    
    All settings can be overridden via environment variables or .env file.
    Settings are loaded with the following priority:
    1. Environment variables
    2. .env file
    3. Default values defined here
    
    Attributes:
        app_name (str): Application name for display and logging
        app_version (str): Current version of the application
        debug (bool): Enable debug mode (detailed error messages, auto-reload)
        environment (str): Deployment environment (development, staging, production)
        
        host (str): Server host address to bind to
        port (int): Server port number to listen on
        reload (bool): Enable auto-reload on code changes (development only)
        
        cors_origins (List[str]): Allowed CORS origins (["*"] allows all)
        cors_allow_credentials (bool): Allow credentials in CORS requests
        cors_allow_methods (List[str]): Allowed HTTP methods for CORS
        cors_allow_headers (List[str]): Allowed headers for CORS
        
        max_project_name_length (int): Maximum length for project names
        temp_dir (str): Directory for temporary file storage during generation
        cleanup_temp_files (bool): Whether to clean up temporary files after generation
        
        rate_limit_enabled (bool): Enable rate limiting for API endpoints
        rate_limit_per_minute (int): Maximum requests per minute per client
        
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format (str): Log format type (json, text)
        
        secret_key (str): Secret key for security operations (CHANGE IN PRODUCTION!)
    """
    
    # Application Settings
    app_name: str = "FastAPIInitializer"
    app_version: str = "1"
    debug: bool = True
    environment: str = "development"
    
    # Server Settings
    host: str = "localhost"
    port: int = 8000
    reload: bool = True
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # File Generation Settings
    max_project_name_length: int = 50
    temp_dir: str = "./temp"
    cleanup_temp_files: bool = True
    
    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    
    class Config:
        """Pydantic configuration for settings loading"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance - import this throughout the application
settings = Settings()
