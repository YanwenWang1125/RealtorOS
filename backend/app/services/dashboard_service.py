"""
Dashboard service for analytics and statistics (SQLAlchemy aggregations).
"""

from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.dashboard_schema import DashboardStats
from app.models.client import Client
from app.models.task import Task
from app.models.email_log import EmailLog


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_stats(self) -> DashboardStats:
        total_clients = await self._scalar(select(func.count(Client.id)).where(Client.is_deleted == False))  # noqa: E712
        open_tasks = await self._scalar(select(func.count(Task.id)).where(Task.status == "pending"))
        sent_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.status == "sent"))
        return DashboardStats(total_clients=total_clients or 0, open_tasks=open_tasks or 0, sent_emails=sent_emails or 0)

    async def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        # Simple example: recent emails
        stmt = select(EmailLog).order_by(EmailLog.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        emails = result.scalars().all()
        return [
            {"type": "email", "subject": e.subject, "to": e.to_email, "status": e.status, "at": e.created_at}
            for e in emails
        ]

    async def get_client_stats(self) -> Dict[str, int]:
        stages = ["lead", "negotiating", "under_contract", "closed", "lost"]
        stats: Dict[str, int] = {}
        for s in stages:
            count = await self._scalar(
                select(func.count(Client.id)).where(Client.stage == s, Client.is_deleted == False)  # noqa: E712
            )
            stats[s] = count or 0
        return stats

    async def get_task_stats(self) -> Dict[str, int]:
        statuses = ["pending", "completed", "skipped", "cancelled"]
        stats: Dict[str, int] = {}
        for s in statuses:
            count = await self._scalar(select(func.count(Task.id)).where(Task.status == s))
            stats[s] = count or 0
        return stats

    async def get_email_stats(self) -> Dict[str, int]:
        statuses = ["queued", "sent", "failed", "bounced", "delivered", "opened", "clicked"]
        stats: Dict[str, int] = {}
        for s in statuses:
            count = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.status == s))
            stats[s] = count or 0
        return stats

    async def _scalar(self, stmt) -> int:
        result = await self.session.execute(stmt)
        return result.scalar()
