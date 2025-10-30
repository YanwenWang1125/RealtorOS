"""
API dependencies for RealtorOS.

This module provides dependency injection for services and database connections
used throughout the API routes.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.dashboard_service import DashboardService
from app.db.postgresql import get_session

async def get_crm_service(session: AsyncSession = Depends(get_session)):
    """Get CRM service instance."""
    return CRMService(session)

async def get_scheduler_service(session: AsyncSession = Depends(get_session)):
    """Get scheduler service instance."""
    return SchedulerService(session)

async def get_ai_agent():
    """Get AI agent service instance."""
    return AIAgent()

async def get_email_service(session: AsyncSession = Depends(get_session)):
    """Get email service instance."""
    return EmailService(session)

async def get_dashboard_service(session: AsyncSession = Depends(get_session)):
    """Get dashboard service instance."""
    return DashboardService(session)
