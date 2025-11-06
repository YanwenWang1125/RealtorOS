"""
PostgreSQL async database setup using SQLAlchemy 2.0.

Provides engine initialization, session factory, and FastAPI dependencies.
Shared across all microservices.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
import os
from typing import Optional

# SQLAlchemy Base for ORM models (can be imported by models if centralized)
Base = declarative_base()

engine: Optional[AsyncEngine] = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def _convert_to_async_url(database_url: str) -> str:
    """Convert database URL to use async driver if needed."""
    # If already using async driver, return as-is
    if "+asyncpg://" in database_url or "+psycopg://" in database_url:
        return database_url
    
    # Convert psycopg2 to asyncpg
    if "+psycopg2://" in database_url:
        return database_url.replace("+psycopg2://", "+asyncpg://")
    
    # Convert plain postgresql:// to postgresql+asyncpg://
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # If it's already async or unknown format, return as-is
    return database_url


async def init_db() -> None:
    """Initialize the async engine and session factory."""
    global engine, SessionLocal
    if engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Check if DATABASE_URL contains an unresolved Key Vault reference
        # This happens when Azure Container Apps doesn't resolve the reference properly
        if database_url.startswith("keyvaultref:") or database_url.startswith("secretref:"):
            raise ValueError(
                f"DATABASE_URL contains an unresolved Azure Key Vault reference: {database_url}\n"
                f"This indicates that the Azure Container App environment variable was not properly configured.\n"
                f"The environment variable should reference a secret that points to Key Vault, not contain the reference directly.\n"
                f"Please run the fix script: azure/deployment/fix-keyvault-references.ps1\n"
                f"Or manually configure the secret reference using:\n"
                f"  az containerapp secret set --name <app-name> --resource-group <rg> "
                f"--secrets \"database-url=keyvaultref:<kv-name>,secretname:PostgreSQL-ConnectionString\"\n"
                f"  az containerapp update --name <app-name> --resource-group <rg> "
                f"--set-env-vars \"DATABASE_URL=secretref:database-url\""
            )
        
        # Convert URL to use async driver (asyncpg)
        async_url = _convert_to_async_url(database_url)
        engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True,
        )
        SessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


async def close_db() -> None:
    """Dispose the engine and close all connections."""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None


async def get_session() -> AsyncSession:
    """FastAPI dependency that yields an AsyncSession."""
    if SessionLocal is None:
        # Lazy init safeguard in case lifespan wasn't called
        await init_db()
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session

