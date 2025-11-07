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


def _convert_to_async_url(database_url: str) -> str:
    """Convert database URL to use async driver if needed."""
    # SQLite with aiosqlite is already async, return as-is
    if database_url.startswith("sqlite+aiosqlite://") or database_url.startswith("sqlite://"):
        return database_url

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
        # Convert URL to use async driver (asyncpg)
        async_url = _convert_to_async_url(settings.DATABASE_URL)

        # Configure engine based on database type
        engine_kwargs = {"echo": False}

        # SQLite doesn't support pool_pre_ping and needs different pool settings
        if async_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs["pool_pre_ping"] = True

        engine = create_async_engine(async_url, **engine_kwargs)
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


