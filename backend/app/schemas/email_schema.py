"""
Email Pydantic schemas for API validation.

This module defines Pydantic schemas for email-related API requests
and responses in the RealtorOS system.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class EmailPreviewRequest(BaseModel):
    """Schema for email preview requests."""
    client_id: str = Field(..., description="Client ID")
    task_id: str = Field(..., description="Task ID")
    agent_instructions: Optional[str] = Field(None, max_length=500)

class EmailSendRequest(BaseModel):
    """Schema for email send requests."""
    client_id: str = Field(..., description="Client ID")
    task_id: str = Field(..., description="Task ID")
    agent_instructions: Optional[str] = Field(None, max_length=500)

class EmailResponse(BaseModel):
    """Schema for email API responses."""
    id: str
    task_id: str
    client_id: str
    to_email: EmailStr
    subject: str
    body: str
    status: str
    sendgrid_message_id: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
