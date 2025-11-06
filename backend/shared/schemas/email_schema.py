"""
Email Pydantic schemas for API validation.

This module defines Pydantic schemas for email-related API requests
and responses in the RealtorOS system.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class EmailPreviewRequest(BaseModel):
    """Schema for email preview requests."""
    client_id: int = Field(..., description="Client ID")
    task_id: int = Field(..., description="Task ID")
    agent_instructions: Optional[str] = Field(None, max_length=500)

class EmailSendRequest(BaseModel):
    """Schema for email send requests."""
    client_id: int = Field(..., description="Client ID")
    task_id: int = Field(..., description="Task ID")
    to_email: EmailStr = Field(..., description="Recipient email")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (HTML)")
    agent_instructions: Optional[str] = Field(None, max_length=500)

class EmailResponse(BaseModel):
    """Schema for email API responses."""
    id: int
    agent_id: int
    task_id: int
    client_id: int
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    to_email: EmailStr
    subject: str
    body: str
    status: str
    ses_message_id: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

