"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException
from shared.schemas.agent_schema import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentLogin,
    GoogleLoginRequest,
    TokenResponse
)
from shared.models.agent import Agent
from shared.auth.jwt_auth import get_current_agent
from shared.db.postgresql import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.auth_service import AuthService

router = APIRouter()


async def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Get auth service instance."""
    return AuthService(session)


@router.post("/register", response_model=TokenResponse)
async def register_agent(
    agent_data: AgentCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new agent with email/password."""
    return await auth_service.register_email(agent_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: AgentLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with email/password."""
    return await auth_service.login_email(credentials.email, credentials.password)


@router.post("/google", response_model=TokenResponse)
async def google_login(
    request: GoogleLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login or register with Google OAuth."""
    try:
        return await auth_service.login_google(request.credential)
    except HTTPException as e:
        # Re-raise HTTP exceptions as-is
        raise e
    except Exception as e:
        # Log unexpected errors
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in Google login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during Google authentication: {str(e)}"
        )


@router.get("/me", response_model=AgentResponse)
async def get_my_profile(agent: Agent = Depends(get_current_agent)):
    """Get current authenticated agent's profile."""
    return AgentResponse.model_validate(agent)


@router.patch("/me", response_model=AgentResponse)
async def update_my_profile(
    agent_data: AgentUpdate,
    agent: Agent = Depends(get_current_agent),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update current agent's profile."""
    updated = await auth_service.update_profile(agent.id, agent_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated

