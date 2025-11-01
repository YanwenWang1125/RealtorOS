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
        from datetime import datetime, timedelta, timezone
        
        total_clients = await self._scalar(select(func.count(Client.id)).where(Client.is_deleted == False))  # noqa: E712
        active_clients = await self._scalar(
            select(func.count(Client.id)).where(
                Client.is_deleted == False,  # noqa: E712
                Client.stage.in_(["lead", "negotiating", "under_contract"])
            )
        )
        pending_tasks = await self._scalar(select(func.count(Task.id)).where(Task.status == "pending"))
        completed_tasks = await self._scalar(select(func.count(Task.id)).where(Task.status == "completed"))
        
        # Emails sent today (timezone-aware UTC)
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        emails_sent_today = await self._scalar(
            select(func.count(EmailLog.id)).where(
                EmailLog.status == "sent",
                EmailLog.created_at >= today_start,
                EmailLog.created_at < today_end
            )
        )
        
        # Emails sent this week
        week_start = today_start - timedelta(days=today_start.weekday())
        emails_sent_this_week = await self._scalar(
            select(func.count(EmailLog.id)).where(
                EmailLog.status == "sent",
                EmailLog.created_at >= week_start
            )
        )
        
        # Open rate and click rate
        total_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.status.in_(["sent", "delivered", "opened", "clicked"])))
        opened_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.status == "opened"))
        clicked_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.status == "clicked"))
        
        open_rate = (opened_emails or 0) / (total_emails or 1) * 100 if total_emails else 0.0
        click_rate = (clicked_emails or 0) / (total_emails or 1) * 100 if total_emails else 0.0
        
        # Conversion rate (leads that became closed)
        total_leads = await self._scalar(
            select(func.count(Client.id)).where(
                Client.stage == "lead",
                Client.is_deleted == False  # noqa: E712
            )
        )
        closed_deals = await self._scalar(
            select(func.count(Client.id)).where(
                Client.stage == "closed",
                Client.is_deleted == False  # noqa: E712
            )
        )
        conversion_rate = (closed_deals or 0) / (total_leads or 1) * 100 if total_leads else 0.0
        
        return DashboardStats(
            total_clients=total_clients or 0,
            active_clients=active_clients or 0,
            pending_tasks=pending_tasks or 0,
            completed_tasks=completed_tasks or 0,
            emails_sent_today=emails_sent_today or 0,
            emails_sent_this_week=emails_sent_this_week or 0,
            open_rate=round(open_rate, 2),
            click_rate=round(click_rate, 2),
            conversion_rate=round(conversion_rate, 2)
        )

    async def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity feed with client information."""
        from app.models.client import Client
        
        # Get recent emails with client joins
        stmt = (
            select(EmailLog, Client.name)
            .join(Client, EmailLog.client_id == Client.id)
            .order_by(EmailLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        
        activities = []
        for email_log, client_name in rows:
            activities.append({
                "type": "email",
                "subject": email_log.subject,
                "to": email_log.to_email,
                "status": email_log.status,
                "at": email_log.created_at.isoformat() if email_log.created_at else None,
                "client_name": client_name,
                "client_id": email_log.client_id
            })
        
        return activities

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
