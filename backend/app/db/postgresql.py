"""
PostgreSQL async database setup using SQLAlchemy 2.0.

Provides engine initialization, session factory, and FastAPI dependencies.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.config import settings

# SQLAlchemy Base for ORM models (can be imported by models if centralized)
Base = declarative_base()

engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Initialize the async engine and session factory."""
    global engine, SessionLocal
    if engine is None:
        engine = create_async_engine(
            settings.DATABASE_URL,
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


