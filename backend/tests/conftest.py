"""
Pytest configuration and fixtures for RealtorOS tests.

This module provides shared fixtures and test configuration
for all RealtorOS backend tests.
"""

import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.db.mongodb import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create a test database connection."""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[f"{settings.MONGODB_DB}_test"]
    
    yield db
    
    # Cleanup after test
    await client.drop_database(f"{settings.MONGODB_DB}_test")
    client.close()

@pytest.fixture
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

@pytest.fixture
async def sample_task_data():
    """Sample task data for testing."""
    return {
        "client_id": "507f1f77bcf86cd799439011",  # Valid ObjectId
        "followup_type": "Day 1",
        "scheduled_for": "2024-01-15T10:00:00Z",
        "status": "pending",
        "priority": "high",
        "notes": "Test task for unit testing"
    }
