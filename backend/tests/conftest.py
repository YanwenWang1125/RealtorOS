"""
Pytest configuration and fixtures for RealtorOS tests.

This module provides root-level shared fixtures and test configuration.
Note: Unit tests should use fixtures from tests/unit/conftest.py
and integration tests should use fixtures from tests/integration/conftest.py.

This file serves as a fallback for any tests that need basic fixtures.
"""

import sys
from pathlib import Path
import os

# Set DATABASE_URL for testing BEFORE importing app modules
# This ensures that the settings are loaded with the correct DATABASE_URL
# Use TEST_DATABASE_URL if set, otherwise use SQLite in-memory database
test_db_url_env = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["DATABASE_URL"] = test_db_url_env

# Add backend directory to Python path so we can import app
# This ensures tests work when run directly with python or with pytest
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.db.postgresql import Base
# Import all models so they register with Base.metadata
from app.models import client, task, email_log, agent  # noqa: F401

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_session():
    """Create an in-memory SQLite async session for tests."""
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

@pytest_asyncio.fixture
async def client(test_session):
    """AsyncClient for API testing with dependency overrides."""
    from httpx import AsyncClient
    from app.main import app
    from app.api.dependencies import get_session
    
    # Override database session dependency
    async def override_get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    # Create async HTTP client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clear overrides after test
    app.dependency_overrides.clear()