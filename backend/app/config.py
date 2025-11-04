"""
Configuration management for RealtorOS.

This module handles environment variables and application configuration
using Pydantic settings for validation and type safety.
All configuration values are loaded from .env file using python-dotenv.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the backend directory (parent of app/)
# env_path = Path(__file__).parent.parent / ".env"

# # Check if .env file exists
# if not env_path.exists():
#     raise FileNotFoundError(
#         f".env file not found at {env_path}. "
#         f"Please create a .env file based on .env.example"
#     )

# load_dotenv(dotenv_path=env_path)

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables via .env file.
    
    All values must be provided in the .env file. No defaults are provided.
    """
    
    # FastAPI - Required
    ENVIRONMENT: str = Field(description="Application environment (development/production/test)")
    DEBUG: bool = Field(description="Enable debug mode (true/false)")
    API_TITLE: str = Field(description="API title")
    API_VERSION: str = Field(description="API version")
    
    # Database (PostgreSQL) - Required
    DATABASE_URL: str = Field(description="PostgreSQL database connection URL")
    
    # Redis & Celery - Required
    REDIS_URL: str = Field(description="Redis connection URL")
    CELERY_BROKER_URL: str = Field(description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(description="Celery result backend URL")
    
    # OpenAI - Required for email generation
    OPENAI_API_KEY: str = Field(description="OpenAI API key (required for email generation)")
    OPENAI_MODEL: str = Field(description="OpenAI model to use")
    OPENAI_MAX_TOKENS: int = Field(description="Maximum tokens for OpenAI requests")
    
    # SendGrid - Required for sending emails
    SENDGRID_API_KEY: str = Field(description="SendGrid API key (required for sending emails)")
    SENDGRID_FROM_EMAIL: str = Field(description="Default sender email address")
    SENDGRID_FROM_NAME: str = Field(description="Default sender name")
    SENDGRID_WEBHOOK_VERIFICATION_KEY: Optional[str] = Field(default=None, description="SendGrid webhook ECDSA public key for signature verification (optional in development)")
    
    # Google OAuth - Optional (can be set later for Google Sign-In)
    GOOGLE_CLIENT_ID: Optional[str] = Field(default="", description="Google OAuth Client ID (optional)")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default="", description="Google OAuth Client Secret (optional)")
    
    # Logging - Required
    LOG_LEVEL: str = Field(description="Logging level (DEBUG/INFO/WARNING/ERROR)")
    
    # Security - Required
    SECRET_KEY: str = Field(description="Secret key for JWT tokens and encryption")
    ALGORITHM: str = Field(description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(description="JWT access token expiration time in minutes")
    
    # CORS - Required, stored as comma-separated string in .env, parsed as list
    # Access via settings.get_cors_origins() to get as list
    CORS_ORIGINS: str = Field(description="Allowed CORS origins as comma-separated string")
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from comma-separated string to list."""
        if not self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS is required in .env file")
        if isinstance(self.CORS_ORIGINS, str):
            origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            if not origins:
                raise ValueError("CORS_ORIGINS cannot be empty")
            return origins
        elif isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        raise ValueError(f"Invalid CORS_ORIGINS format: {type(self.CORS_ORIGINS)}")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

# Initialize settings - will raise ValidationError if any required field is missing
try:
    settings = Settings()
except Exception as e:
    raise ValueError(
        f"Failed to load configuration from .env file: {e}\n"
        f"Please ensure all required fields are set in your .env file\n"
        f"You can copy .env.example to .env as a starting point."
    ) from e

# Validate critical settings
if settings.ENVIRONMENT not in ["development", "production", "test"]:
    raise ValueError(f"ENVIRONMENT must be one of: development, production, test. Got: {settings.ENVIRONMENT}")

if settings.ENVIRONMENT == "production" and settings.DEBUG:
    raise ValueError("DEBUG must be False in production environment")

if not settings.OPENAI_API_KEY and settings.ENVIRONMENT != "test":
    import warnings
    warnings.warn("OPENAI_API_KEY is not set. Email generation will not work.")

if not settings.SENDGRID_API_KEY and settings.ENVIRONMENT != "test":
    import warnings
    warnings.warn("SENDGRID_API_KEY is not set. Email sending will not work.")

if settings.ENVIRONMENT == "production" and len(settings.SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long in production")
