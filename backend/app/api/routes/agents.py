"""
Agent authentication and profile management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.agent_schema import (
    AgentCreate, AgentUpdate, AgentResponse, AgentLogin,
    GoogleLoginRequest, TokenResponse
)
from app.services.agent_service import AgentService
from app.api.dependencies import get_agent_service, get_current_agent
from app.models.agent import Agent

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register_agent(
    agent_data: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Register a new agent with email/password."""
    return await agent_service.register_email(agent_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: AgentLogin,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Login with email/password."""
    return await agent_service.login_email(credentials.email, credentials.password)


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Login or register with Google OAuth."""
    return await agent_service.login_google(request.credential)


@router.get("/me", response_model=AgentResponse)
async def get_my_profile(agent: Agent = Depends(get_current_agent)):
    """Get current authenticated agent's profile."""
    return AgentResponse.model_validate(agent)


@router.patch("/me", response_model=AgentResponse)
async def update_my_profile(
    agent_data: AgentUpdate,
    agent: Agent = Depends(get_current_agent),
    agent_service: AgentService = Depends(get_agent_service)
):
    """Update current agent's profile."""
    updated = await agent_service.update_profile(agent.id, agent_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated

