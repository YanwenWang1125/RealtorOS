"""
Integration tests for Agent API endpoints.
"""

import pytest
from httpx import AsyncClient
from app.main import app
from app.models.agent import Agent
from app.utils.auth import hash_password
from sqlalchemy import select, delete


@pytest.mark.asyncio
async def test_register_endpoint(db_session, async_client):
    """Test agent registration endpoint."""
    # Clean up agents table
    await db_session.execute(delete(Agent))
    await db_session.commit()
    
    response = await async_client.post(
        "/api/agents/register",
        json={
            "email": "newuser@example.com",
            "password": "secure_password_123",
            "name": "New User",
            "phone": "+1-555-0001",
            "title": "Real Estate Agent",
            "company": "Test Company"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "agent" in data
    assert data["agent"]["email"] == "newuser@example.com"
    assert data["agent"]["name"] == "New User"


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session, async_client):
    """Test registration with duplicate email fails."""
    # Clean up and create existing agent
    await db_session.execute(delete(Agent))
    
    existing_agent = Agent(
        email="existing@example.com",
        password_hash=hash_password("password"),
        name="Existing User",
        auth_provider="email"
    )
    db_session.add(existing_agent)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/agents/register",
        json={
            "email": "existing@example.com",
            "password": "password123",
            "name": "Another User"
        }
    )
    
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_endpoint(db_session, async_client):
    """Test agent login endpoint."""
    # Clean up and create test agent
    await db_session.execute(delete(Agent))
    
    agent = Agent(
        email="login@example.com",
        password_hash=hash_password("test_password"),
        name="Login User",
        auth_provider="email"
    )
    db_session.add(agent)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/agents/login",
        json={
            "email": "login@example.com",
            "password": "test_password"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["agent"]["email"] == "login@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(db_session, async_client):
    """Test login with wrong password fails."""
    # Clean up and create test agent
    await db_session.execute(delete(Agent))
    
    agent = Agent(
        email="user@example.com",
        password_hash=hash_password("correct_password"),
        name="Test User",
        auth_provider="email"
    )
    db_session.add(agent)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/agents/login",
        json={
            "email": "user@example.com",
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_endpoint(db_session, async_client):
    """Test getting current agent's profile."""
    # Clean up and create test agent
    await db_session.execute(delete(Agent))
    
    agent = Agent(
        email="profile@example.com",
        password_hash=hash_password("password"),
        name="Profile User",
        auth_provider="email"
    )
    db_session.add(agent)
    await db_session.commit()
    
    # Login first to get token
    login_response = await async_client.post(
        "/api/agents/login",
        json={
            "email": "profile@example.com",
            "password": "password"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get profile with token
    response = await async_client.get(
        "/api/agents/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["name"] == "Profile User"


@pytest.mark.asyncio
async def test_get_profile_unauthorized(async_client):
    """Test getting profile without token fails."""
    response = await async_client.get("/api/agents/me")
    assert response.status_code == 403  # Forbidden - no token provided


@pytest.mark.asyncio
async def test_get_profile_invalid_token(async_client):
    """Test getting profile with invalid token fails."""
    response = await async_client.get(
        "/api/agents/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_endpoint(db_session, async_client):
    """Test updating agent profile."""
    # Clean up and create test agent
    await db_session.execute(delete(Agent))
    
    agent = Agent(
        email="update@example.com",
        password_hash=hash_password("password"),
        name="Original Name",
        auth_provider="email"
    )
    db_session.add(agent)
    await db_session.commit()
    
    # Login first
    login_response = await async_client.post(
        "/api/agents/login",
        json={
            "email": "update@example.com",
            "password": "password"
        }
    )
    token = login_response.json()["access_token"]
    
    # Update profile
    response = await async_client.patch(
        "/api/agents/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Name",
            "phone": "+1-555-9999",
            "title": "Senior Agent",
            "company": "New Company",
            "bio": "Updated bio"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+1-555-9999"
    assert data["title"] == "Senior Agent"
    assert data["company"] == "New Company"
    assert data["bio"] == "Updated bio"


@pytest.mark.asyncio
async def test_google_login_endpoint(db_session, async_client):
    """Test Google OAuth login endpoint."""
    # Clean up agents
    await db_session.execute(delete(Agent))
    await db_session.commit()
    
    # Mock Google token verification
    from unittest.mock import patch
    with patch('app.services.agent_service.verify_google_token') as mock_verify:
        mock_verify.return_value = {
            'sub': 'google_123',
            'email': 'google@example.com',
            'name': 'Google User',
            'picture': 'https://example.com/avatar.jpg'
        }
        
        response = await async_client.post(
            "/api/agents/google",
            json={"credential": "google_id_token_here"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["agent"]["email"] == "google@example.com"
        assert data["agent"]["name"] == "Google User"
        assert data["agent"]["auth_provider"] == "google"


@pytest.mark.asyncio
async def test_google_login_invalid_token(db_session, async_client):
    """Test Google login with invalid token fails."""
    from unittest.mock import patch
    with patch('app.services.agent_service.verify_google_token') as mock_verify:
        mock_verify.return_value = None
        
        response = await async_client.post(
            "/api/agents/google",
            json={"credential": "invalid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(async_client):
    """Test that protected endpoints require authentication."""
    # Try to access clients endpoint without token
    response = await async_client.get("/api/clients")
    assert response.status_code == 403  # Forbidden - no token


@pytest.mark.asyncio
async def test_protected_endpoint_with_token(db_session, async_client):
    """Test that protected endpoints work with valid token."""
    # Clean up and create test agent
    await db_session.execute(delete(Agent))
    
    agent = Agent(
        email="test@example.com",
        password_hash=hash_password("password"),
        name="Test User",
        auth_provider="email"
    )
    db_session.add(agent)
    await db_session.commit()
    
    # Login to get token
    login_response = await async_client.post(
        "/api/agents/login",
        json={
            "email": "test@example.com",
            "password": "password"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = await async_client.get(
        "/api/clients",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should succeed (may be empty list, but not 401/403)
    assert response.status_code in [200, 404]  # 200 with empty list, or 404 if no clients

