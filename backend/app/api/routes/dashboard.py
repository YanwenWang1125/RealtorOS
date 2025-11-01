"""
Dashboard and analytics API routes.

This module provides endpoints for dashboard statistics and analytics
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends
from app.schemas.dashboard_schema import DashboardStats
from app.services.dashboard_service import DashboardService
from app.api.dependencies import get_dashboard_service

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get dashboard statistics and KPIs."""
    return await dashboard_service.get_dashboard_stats()

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get recent activity feed."""
    return await dashboard_service.get_recent_activity(limit=limit)
