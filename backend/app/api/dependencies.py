"""
API dependencies for RealtorOS.

This module provides dependency injection for services and database connections
used throughout the API routes.
"""

from fastapi import Depends
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.dashboard_service import DashboardService
from app.db.mongodb import get_database

def get_crm_service():
    """Get CRM service instance."""
    pass

def get_scheduler_service():
    """Get scheduler service instance."""
    pass

def get_ai_agent():
    """Get AI agent service instance."""
    pass

def get_email_service():
    """Get email service instance."""
    pass

def get_dashboard_service():
    """Get dashboard service instance."""
    pass
