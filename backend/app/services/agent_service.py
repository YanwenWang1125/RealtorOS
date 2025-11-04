"""
Agent service for authentication and profile management.
"""

from typing import Optional
from datetime import timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.agent import Agent
from app.schemas.agent_schema import (
    AgentCreate, AgentUpdate, AgentResponse, TokenResponse
)
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.google_oauth import verify_google_token
from app.config import settings


class AgentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_email(self, agent_data: AgentCreate) -> TokenResponse:
        """Register a new agent with email/password."""
        # Check if email already exists
        stmt = select(Agent).where(Agent.email == agent_data.email)
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create new agent
        agent = Agent(
            email=agent_data.email,
            password_hash=hash_password(agent_data.password),
            name=agent_data.name,
            phone=agent_data.phone,
            title=agent_data.title,
            company=agent_data.company,
            auth_provider='email'
        )
        self.session.add(agent)
        await self.session.commit()
        await self.session.refresh(agent)

        # Generate token
        access_token = create_access_token(
            data={"sub": str(agent.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        agent_response = AgentResponse.model_validate(agent)
        return TokenResponse(access_token=access_token, agent=agent_response)

    async def login_email(self, email: str, password: str) -> TokenResponse:
        """Login with email/password."""
        stmt = select(Agent).where(
            Agent.email == email,
            Agent.is_active == True,
            Agent.auth_provider == 'email'
        )
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent or not agent.password_hash or not verify_password(password, agent.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = create_access_token(
            data={"sub": str(agent.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        agent_response = AgentResponse.model_validate(agent)
        return TokenResponse(access_token=access_token, agent=agent_response)

    async def login_google(self, google_token: str) -> TokenResponse:
        """Login or register with Google OAuth."""
        # Verify Google token
        try:
            google_info = verify_google_token(google_token)
        except ValueError as e:
            # Configuration error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        if not google_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token. Please ensure the token is valid and the backend GOOGLE_CLIENT_ID matches the frontend NEXT_PUBLIC_GOOGLE_CLIENT_ID."
            )

        # Try to find existing agent by google_sub or email
        stmt = select(Agent).where(
            (Agent.google_sub == google_info['sub']) | (Agent.email == google_info['email'])
        )
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if agent:
            # Update Google info if needed
            if not agent.google_sub:
                agent.google_sub = google_info['sub']
                agent.auth_provider = 'google'
            if not agent.avatar_url and google_info.get('picture'):
                agent.avatar_url = google_info['picture']
            await self.session.commit()
            await self.session.refresh(agent)
        else:
            # Create new agent
            agent = Agent(
                email=google_info['email'],
                google_sub=google_info['sub'],
                name=google_info['name'],
                avatar_url=google_info.get('picture'),
                auth_provider='google',
                is_active=True
            )
            self.session.add(agent)
            await self.session.commit()
            await self.session.refresh(agent)

        # Generate token
        access_token = create_access_token(
            data={"sub": str(agent.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        agent_response = AgentResponse.model_validate(agent)
        return TokenResponse(access_token=access_token, agent=agent_response)

    async def get_profile(self, agent_id: int) -> Optional[AgentResponse]:
        """Get agent profile by ID."""
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return None

        return AgentResponse.model_validate(agent)

    async def update_profile(self, agent_id: int, agent_data: AgentUpdate) -> Optional[AgentResponse]:
        """Update agent profile."""
        stmt = select(Agent).where(Agent.id == agent_id)
        result = await self.session.execute(stmt)
        agent = result.scalar_one_or_none()

        if not agent:
            return None

        # Update fields
        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)

        await self.session.commit()
        await self.session.refresh(agent)

        return AgentResponse.model_validate(agent)

