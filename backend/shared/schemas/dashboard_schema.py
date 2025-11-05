"""
Dashboard Pydantic schemas for API validation.

This module defines Pydantic schemas for dashboard and analytics
API responses in the RealtorOS system.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_clients: int = Field(..., description="Total number of clients")
    active_clients: int = Field(..., description="Number of active clients")
    pending_tasks: int = Field(..., description="Number of pending tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    emails_sent_today: int = Field(..., description="Emails sent today")
    emails_sent_this_week: int = Field(..., description="Emails sent this week")
    open_rate: float = Field(..., description="Email open rate percentage")
    click_rate: float = Field(..., description="Email click rate percentage")
    conversion_rate: float = Field(..., description="Lead conversion rate percentage")

class ActivityItem(BaseModel):
    """Schema for activity feed items."""
    id: str
    type: str = Field(..., description="Type of activity (client_created, task_completed, email_sent, etc.)")
    description: str = Field(..., description="Human-readable description")
    timestamp: str = Field(..., description="ISO timestamp")
    client_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

