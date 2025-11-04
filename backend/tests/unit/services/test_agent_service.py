"""
Unit tests for Agent service (authentication and profile management).
"""

import pytest
from fastapi import HTTPException, status
from app.services.agent_service import AgentService
from app.schemas.agent_schema import AgentCreate, AgentUpdate
from app.models.agent import Agent
from tests.fixtures.agent_fixtures import (
    sample_agent_data,
    sample_agent_update_data,
    sample_agent
)


class TestAgentService:
    """Test cases for Agent service."""

    @pytest.mark.asyncio
    async def test_register_email_success(self, test_session, sample_agent_data):
        """Test successful email/password registration."""
        service = AgentService(test_session)
        agent_create = AgentCreate(**sample_agent_data)
        
        result = await service.register_email(agent_create)
        
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.agent.email == sample_agent_data["email"]
        assert result.agent.name == sample_agent_data["name"]
        assert result.agent.auth_provider == "email"
        assert result.agent.id is not None

    @pytest.mark.asyncio
    async def test_register_email_duplicate(self, test_session, sample_agent_data):
        """Test registration with duplicate email fails."""
        service = AgentService(test_session)
        agent_create = AgentCreate(**sample_agent_data)
        
        # Register first time
        await service.register_email(agent_create)
        
        # Try to register again with same email
        with pytest.raises(HTTPException) as exc_info:
            await service.register_email(agent_create)
        
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "already registered" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_login_email_success(self, test_session, sample_agent_data):
        """Test successful email/password login."""
        service = AgentService(test_session)
        
        # Register first
        await service.register_email(AgentCreate(**sample_agent_data))
        
        # Login
        result = await service.login_email(
            sample_agent_data["email"],
            sample_agent_data["password"]
        )
        
        assert result.access_token is not None
        assert result.agent.email == sample_agent_data["email"]

    @pytest.mark.asyncio
    async def test_login_email_wrong_password(self, test_session, sample_agent_data):
        """Test login with wrong password fails."""
        service = AgentService(test_session)
        
        # Register first
        await service.register_email(AgentCreate(**sample_agent_data))
        
        # Try to login with wrong password
        with pytest.raises(HTTPException) as exc_info:
            await service.login_email(
                sample_agent_data["email"],
                "wrong_password"
            )
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_login_email_nonexistent(self, test_session):
        """Test login with non-existent email fails."""
        service = AgentService(test_session)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.login_email("nonexistent@example.com", "password")
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_login_google_new_user(self, test_session):
        """Test Google login creates new user."""
        service = AgentService(test_session)
        
        # Mock Google token verification
        from unittest.mock import patch
        with patch('app.services.agent_service.verify_google_token') as mock_verify:
            mock_verify.return_value = {
                'sub': 'google_123',
                'email': 'google@example.com',
                'name': 'Google User',
                'picture': 'https://example.com/avatar.jpg'
            }
            
            result = await service.login_google("google_token")
            
            assert result.access_token is not None
            assert result.agent.email == 'google@example.com'
            assert result.agent.name == 'Google User'
            assert result.agent.google_sub == 'google_123'
            assert result.agent.auth_provider == 'google'
            assert result.agent.avatar_url == 'https://example.com/avatar.jpg'

    @pytest.mark.asyncio
    async def test_login_google_existing_user(self, test_session):
        """Test Google login with existing user."""
        service = AgentService(test_session)
        
        # Create existing user
        from app.utils.auth import hash_password
        existing_agent = Agent(
            email="existing@example.com",
            password_hash=hash_password("password"),
            name="Existing User",
            auth_provider="email"
        )
        test_session.add(existing_agent)
        await test_session.commit()
        
        # Mock Google token verification
        from unittest.mock import patch
        with patch('app.services.agent_service.verify_google_token') as mock_verify:
            mock_verify.return_value = {
                'sub': 'google_123',
                'email': 'existing@example.com',
                'name': 'Updated Name',
                'picture': 'https://example.com/avatar.jpg'
            }
            
            result = await service.login_google("google_token")
            
            assert result.access_token is not None
            assert result.agent.email == 'existing@example.com'
            # Should update Google info
            assert result.agent.google_sub == 'google_123'
            assert result.agent.auth_provider == 'google'

    @pytest.mark.asyncio
    async def test_login_google_invalid_token(self, test_session):
        """Test Google login with invalid token fails."""
        service = AgentService(test_session)
        
        from unittest.mock import patch
        with patch('app.services.agent_service.verify_google_token') as mock_verify:
            mock_verify.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await service.login_google("invalid_token")
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_profile(self, test_session, sample_agent):
        """Test getting agent profile."""
        service = AgentService(test_session)
        
        profile = await service.get_profile(sample_agent.id)
        
        assert profile is not None
        assert profile.id == sample_agent.id
        assert profile.email == sample_agent.email

    @pytest.mark.asyncio
    async def test_get_profile_nonexistent(self, test_session):
        """Test getting non-existent profile returns None."""
        service = AgentService(test_session)
        
        profile = await service.get_profile(99999)
        assert profile is None

    @pytest.mark.asyncio
    async def test_update_profile(self, test_session, sample_agent, sample_agent_update_data):
        """Test updating agent profile."""
        service = AgentService(test_session)
        
        update_data = AgentUpdate(**sample_agent_update_data)
        updated = await service.update_profile(sample_agent.id, update_data)
        
        assert updated is not None
        assert updated.name == sample_agent_update_data["name"]
        assert updated.phone == sample_agent_update_data["phone"]
        assert updated.title == sample_agent_update_data["title"]
        assert updated.company == sample_agent_update_data["company"]
        assert updated.bio == sample_agent_update_data["bio"]

    @pytest.mark.asyncio
    async def test_update_profile_partial(self, test_session, sample_agent):
        """Test partial profile update."""
        service = AgentService(test_session)
        
        update_data = AgentUpdate(name="New Name Only")
        updated = await service.update_profile(sample_agent.id, update_data)
        
        assert updated is not None
        assert updated.name == "New Name Only"
        # Other fields should remain unchanged
        assert updated.email == sample_agent.email

    @pytest.mark.asyncio
    async def test_update_profile_nonexistent(self, test_session):
        """Test updating non-existent profile returns None."""
        service = AgentService(test_session)
        
        update_data = AgentUpdate(name="New Name")
        updated = await service.update_profile(99999, update_data)
        assert updated is None

