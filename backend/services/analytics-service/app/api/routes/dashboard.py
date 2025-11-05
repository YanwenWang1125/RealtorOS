"""Dashboard routes."""

from fastapi import APIRouter, Depends, Query
from shared.schemas.dashboard_schema import DashboardStats
from shared.models.agent import Agent
from shared.auth.jwt_auth import get_current_agent
from shared.db.postgresql import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.dashboard_service import DashboardService

router = APIRouter()


async def get_dashboard_service(session: AsyncSession = Depends(get_session)) -> DashboardService:
    return DashboardService(session)


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    agent: Agent = Depends(get_current_agent),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    return await dashboard_service.get_dashboard_stats(agent.id)


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(10),
    agent: Agent = Depends(get_current_agent),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    return await dashboard_service.get_recent_activity(agent.id, limit=limit)

