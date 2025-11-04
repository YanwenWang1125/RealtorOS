"""
API dependencies for RealtorOS.

This module provides dependency injection for services and database connections
used throughout the API routes.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.dashboard_service import DashboardService
from app.models.agent import Agent
from app.utils.auth import decode_access_token
from app.db.postgresql import get_session
from app.config import settings

async def get_crm_service(session: AsyncSession = Depends(get_session)):
    """Get CRM service instance."""
    return CRMService(session)

async def get_scheduler_service(session: AsyncSession = Depends(get_session)):
    """Get scheduler service instance."""
    return SchedulerService(session)

async def get_ai_agent():
    """Get AI agent service instance."""
    return AIAgent()

async def get_email_service(session: AsyncSession = Depends(get_session)):
    """Get email service instance."""
    return EmailService(session)

async def get_dashboard_service(session: AsyncSession = Depends(get_session)):
    """Get dashboard service instance."""
    return DashboardService(session)

# Authentication dependencies
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it

async def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> Agent:
    """Get the current authenticated agent from JWT token.
    
    In development mode, if no token is provided, returns the first active agent
    (usually the system agent) for easier development.
    """
    # Development mode: bypass auth if no token provided
    if settings.ENVIRONMENT == "development" and credentials is None:
        # Use test agent for development bypass
        test_email = "yanwenwang1125@gmail.com"
        stmt = select(Agent).where(
            Agent.email == test_email,
            Agent.is_active == True
        )
        result = await session.execute(stmt)
        agent = result.scalar_one_or_none()
        
        # Fallback to first active agent if test agent not found
        if agent is None:
            stmt = select(Agent).where(Agent.is_active == True).order_by(Agent.id).limit(1)
            result = await session.execute(stmt)
            agent = result.scalar_one_or_none()
        
        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No active agents found in database. Please run 'python -m app.db.ensure_agent' to create a test agent."
            )
        return agent
    
    # Production mode or if token is provided: require authentication
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    agent_id = payload.get("sub")
    if agent_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(Agent).where(Agent.id == int(agent_id), Agent.is_active == True)
    result = await session.execute(stmt)
    agent = result.scalar_one_or_none()

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return agent

# Add service for agent
async def get_agent_service(session: AsyncSession = Depends(get_session)):
    """Get agent service instance."""
    from app.services.agent_service import AgentService
    return AgentService(session)
