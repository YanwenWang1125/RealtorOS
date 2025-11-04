"""
Fixtures for agent-related test data.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from app.models.agent import Agent


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "email": "test@example.com",
        "password": "test_password_123",
        "name": "Test Agent",
        "phone": "+1-555-0123",
        "title": "Senior Real Estate Agent",
        "company": "Test Realty Co."
    }


@pytest.fixture
def sample_agent_update_data():
    """Sample agent update data for testing."""
    return {
        "name": "Updated Name",
        "phone": "+1-555-9999",
        "title": "Updated Title",
        "company": "Updated Company",
        "bio": "Updated bio text"
    }


@pytest_asyncio.fixture
async def sample_agent(test_session):
    """Create a sample agent in the database."""
    from app.utils.auth import hash_password
    
    agent = Agent(
        email="sample@example.com",
        password_hash=hash_password("password123"),
        name="Sample Agent",
        phone="+1-555-0000",
        title="Real Estate Agent",
        company="Sample Realty",
        auth_provider="email",
        is_active=True
    )
    test_session.add(agent)
    await test_session.commit()
    await test_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def system_agent(test_session):
    """Get or create the system agent."""
    from sqlalchemy import select
    
    stmt = select(Agent).where(Agent.email == "system@realtoros.com")
    result = await test_session.execute(stmt)
    agent = result.scalar_one_or_none()
    
    if not agent:
        agent = Agent(
            email="system@realtoros.com",
            name="System Agent",
            auth_provider="email",
            is_active=True
        )
        test_session.add(agent)
        await test_session.commit()
        await test_session.refresh(agent)
    
    return agent

