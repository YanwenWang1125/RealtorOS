"""
Email log model for MongoDB.

This module defines the EmailLog document model for storing
email sending history and tracking in MongoDB.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.client import PyObjectId

class EmailLog(BaseModel):
    """Email log document model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    task_id: PyObjectId = Field(..., description="Reference to Task document")
    client_id: PyObjectId = Field(..., description="Reference to Client document")
    to_email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    status: str = Field(..., regex=r'^(queued|sent|failed|bounced|delivered|opened|clicked)$')
    sendgrid_message_id: Optional[str] = Field(None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    error_message: Optional[str] = Field(None, max_length=500)
    retry_count: int = Field(default=0)
    webhook_events: list = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
