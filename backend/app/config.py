"""
Configuration management for RealtorOS.

This module handles environment variables and application configuration
using Pydantic settings for validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_TITLE: str = "RealtorOS API"
    API_VERSION: str = "0.1.0"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://mongo:27017"
    MONGODB_DB: str = "realtoros"
    
    # Redis & Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 500
    
    # SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "agent@realtoros.app"
    SENDGRID_FROM_NAME: str = "RealtorOS"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
