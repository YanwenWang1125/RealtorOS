"""
Pytest configuration and fixtures for unit tests.

This module provides shared fixtures for unit tests that use in-memory databases
and mocked dependencies. Unit tests should be fast and isolated.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so we can import app
# This ensures tests work when run directly with python or with pytest
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.postgresql import Base
# Import all models so they register with Base.metadata
from app.models import client, task, email_log  # noqa: F401

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_session():
    """Create an in-memory SQLite async session for unit tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        # Create tables for all models (all use the same Base.metadata)
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def sample_client_data():
    """Sample client data for testing."""
    return {
        "name": "Test Client",
        "email": "test@example.com",
        "phone": "+1-555-0123",
        "property_address": "123 Test St, Test City, ST 12345",
        "property_type": "residential",
        "stage": "lead",
        "notes": "Test client for unit testing"
    }

@pytest_asyncio.fixture
async def sample_task_data():
    """Sample task data for testing."""
    return {
        "client_id": 1,
        "followup_type": "Day 1",
        "scheduled_for": "2024-01-15T10:00:00Z",
        "priority": "high",
        "notes": "Test task for unit testing"
    }

