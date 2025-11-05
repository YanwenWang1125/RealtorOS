"""
JWT token verification middleware for microservices.

This module provides authentication dependencies that can be used
across all microservices to verify JWT tokens.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os
import jwt
from shared.models.agent import Agent
from shared.db.postgresql import get_session


def get_secret_key() -> str:
    """Get JWT secret key from environment."""
    secret_key = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("JWT_SECRET or SECRET_KEY environment variable is required")
    return secret_key


def get_algorithm() -> str:
    """Get JWT algorithm from environment."""
    return os.getenv("JWT_ALGORITHM", "HS256")


security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Verify JWT token and return payload.
    
    Raises HTTPException if token is invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    secret_key = get_secret_key()
    algorithm = get_algorithm()
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_agent(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> Agent:
    """
    Get the current authenticated agent from JWT token.
    
    In development mode, if no token is provided, returns the first active agent
    (usually the system agent) for easier development.
    """
    environment = os.getenv("ENVIRONMENT", "production")
    
    # Development mode: bypass auth if no token provided
    if environment == "development" and credentials is None:
        # Use test agent for development bypass
        test_email = os.getenv("DEV_TEST_EMAIL", "yanwenwang1125@gmail.com")
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
    secret_key = get_secret_key()
    algorithm = get_algorithm()
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
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

