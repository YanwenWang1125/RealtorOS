"""
Pytest configuration and fixtures for integration tests.

This module provides shared fixtures for integration tests that use real database
connections and test interactions between multiple components.
"""

import sys
from pathlib import Path

# Add backend directory to Python path so we can import app
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app
from app.db import postgresql
from sqlalchemy import delete
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog
from app.models.agent import Agent

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a real database session for integration testing."""
    await postgresql.init_db()
    if postgresql.SessionLocal is None:
        raise RuntimeError("Database not initialized. SessionLocal is None.")
    
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

