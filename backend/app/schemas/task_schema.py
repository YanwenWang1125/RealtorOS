"""
Task Pydantic schemas for API validation.

This module defines Pydantic schemas for task-related API requests
and responses in the RealtorOS system.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    """Base task schema with common fields."""
    client_id: int = Field(..., description="Client ID")
    followup_type: str = Field(..., pattern=r'^(Day 1|Day 3|Week 1|Week 2|Month 1|Custom)$')
    scheduled_for: datetime = Field(..., description="When the task should be executed")
    notes: Optional[str] = Field(None, max_length=500)
    priority: str = Field(..., pattern=r'^(high|medium|low)$')

class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    status: Optional[str] = Field(None, pattern=r'^(pending|completed|skipped|cancelled)$')
    scheduled_for: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = Field(None, pattern=r'^(high|medium|low)$')

class TaskResponse(TaskBase):
    """Schema for task API responses."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    email_sent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
