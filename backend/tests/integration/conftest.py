"""
Pytest configuration and fixtures for integration tests.

This module provides shared fixtures for integration tests that use real database
connections and test interactions between multiple components.
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
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
import warnings
from httpx import AsyncClient
from app.main import app
from app.db import postgresql
from app.config import settings
from sqlalchemy import delete
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog
from app.models.agent import Agent

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Create a real database session for integration testing.

    ⚠️ WARNING: This fixture DELETES ALL DATA from the database before and after each test!
    Make sure you're using a TEST database, not your production/development database.

    To use a separate test database, set TEST_DATABASE_URL or DATABASE_URL in your environment.
    """
    # Determine which database URL to use for testing
    test_db_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

    # If no database URL is set, use SQLite in-memory database (for CI/CD and local testing)
    if not test_db_url:
        test_db_url = "sqlite+aiosqlite:///:memory:"

    # Safety check: Warn if using production database
    # Allow URLs containing "production" or "prod" as part of a larger word (e.g., "_production@")
    # but block standalone database names that indicate production
    db_url_lower = test_db_url.lower()
    # Skip safety check for SQLite (in-memory or file-based test databases)
    if not db_url_lower.startswith("sqlite"):
        # Extract the database name from the URL (part after the last slash)
        # e.g., postgresql://user:pass@host:port/database_name
        if "/" in db_url_lower:
            db_name = db_url_lower.split("/")[-1].split("?")[0]
            # Check if the database name itself is "production", "prod", or "live"
            if db_name in ["production", "prod", "live"]:
                pytest.fail(
                    "❌ SAFETY CHECK FAILED: Integration tests detected PRODUCTION database!\n"
                    f"Database name '{db_name}' indicates a production database.\n"
                    "Integration tests DELETE ALL DATA. Use a TEST database instead.\n"
                    "Set TEST_DATABASE_URL or DATABASE_URL (test) in your environment."
                )

    # Override settings.DATABASE_URL with the test database URL
    original_db_url = settings.DATABASE_URL
    settings.DATABASE_URL = test_db_url

    # Reset the database engine to use the test database
    await postgresql.close_db()
    await postgresql.init_db()
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")

    # Create all tables if using SQLite (for in-memory testing)
    if test_db_url.startswith("sqlite"):
        async with postgresql.engine.begin() as conn:
            await conn.run_sync(postgresql.Base.metadata.create_all)

    try:
        async with postgresql.SessionLocal() as session:
            # Clean up before each test (order matters due to foreign keys)
            # Use TRUNCATE CASCADE to handle circular dependencies (Task <-> EmailLog)
            # This will delete all rows and handle foreign key constraints automatically
            from sqlalchemy import text

            # Delete in order, handling foreign key constraints
            # First, clear the circular reference by nullifying Task.email_sent_id
            await session.execute(text("UPDATE tasks SET email_sent_id = NULL"))
            # Now we can safely delete EmailLog (which references Task, but we'll delete Task next)
            await session.execute(delete(EmailLog))
            # Delete Task (no longer has email_sent_id references)
            await session.execute(delete(Task))
            # Delete Client (references Agent)
            await session.execute(delete(Client))
            # Don't delete system agent, only delete test agents
            await session.execute(delete(Agent).where(Agent.email != 'system@realtoros.com'))
            await session.commit()
            yield session
            # Clean up after each test (same order)
            await session.execute(text("UPDATE tasks SET email_sent_id = NULL"))
            await session.execute(delete(EmailLog))
            await session.execute(delete(Task))
            await session.execute(delete(Client))
            await session.execute(delete(Agent).where(Agent.email != 'system@realtoros.com'))
            await session.commit()
    finally:
        # Restore original DATABASE_URL
        settings.DATABASE_URL = original_db_url
        await postgresql.close_db()
        await postgresql.init_db()

@pytest_asyncio.fixture
async def async_client(db_session):
    """Create an AsyncClient for API testing with database dependency override."""
    # Override the get_session dependency to use the test session
    from app.db.postgresql import get_session
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
        yield client

    # Clean up the override after the test
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def authenticated_client(db_session, async_client):
    """Create an authenticated AsyncClient with a test agent."""
    from app.utils.auth import hash_password
    from sqlalchemy import delete

    # Clean up and create test agent
    await db_session.execute(delete(Agent))
    await db_session.commit()

    test_agent = Agent(
        email="test-agent@example.com",
        password_hash=hash_password("test_password"),
        name="Test Agent",
        auth_provider="email"
    )
    db_session.add(test_agent)
    await db_session.commit()
    await db_session.refresh(test_agent)

    # Login to get token
    login_response = await async_client.post(
        "/api/agents/login",
        json={
            "email": "test-agent@example.com",
            "password": "test_password"
        }
    )
    token_data = login_response.json()
    token = token_data["access_token"]

    # Add auth header to client
    async_client.headers["Authorization"] = f"Bearer {token}"

    yield async_client

    # Clean up auth header
    async_client.headers.pop("Authorization", None)

