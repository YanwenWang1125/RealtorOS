"""
Agent Pydantic schemas for API validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AgentCreate(BaseModel):
    """Schema for email/password registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)


class AgentLogin(BaseModel):
    """Schema for email/password login."""
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    """Schema for Google OAuth login."""
    credential: str  # Google ID token


class AgentUpdate(BaseModel):
    """Schema for updating agent profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None


class AgentResponse(BaseModel):
    """Schema for agent API responses."""
    id: int
    email: EmailStr
    name: str
    phone: Optional[str]
    title: Optional[str]
    company: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    google_sub: Optional[str]  # Google's user ID (for OAuth users)
    auth_provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for authentication response."""
    access_token: str
    token_type: str = "bearer"
    agent: AgentResponse

