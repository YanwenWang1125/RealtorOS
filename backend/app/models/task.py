"""
Task model for MongoDB.

This module defines the Task document model for storing
follow-up task information in MongoDB.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.client import PyObjectId

class Task(BaseModel):
    """Task document model for MongoDB."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    client_id: PyObjectId = Field(..., description="Reference to Client document")
    followup_type: str = Field(..., regex=r'^(Day 1|Day 3|Week 1|Week 2|Month 1|Custom)$')
    scheduled_for: datetime = Field(..., description="When the task should be executed")
    status: str = Field(..., regex=r'^(pending|completed|skipped|cancelled)$')
    email_sent_id: Optional[PyObjectId] = Field(None, description="Reference to EmailLog document")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    priority: str = Field(..., regex=r'^(high|medium|low)$')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
