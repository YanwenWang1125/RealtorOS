"""Dashboard service for analytics."""

from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from shared.schemas.dashboard_schema import DashboardStats
from shared.models.client import Client
from shared.models.task import Task
from shared.models.email_log import EmailLog
from datetime import datetime, timedelta, timezone


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_stats(self, agent_id: int) -> DashboardStats:
        total_clients = await self._scalar(select(func.count(Client.id)).where(Client.agent_id == agent_id, Client.is_deleted == False))
        active_clients = await self._scalar(select(func.count(Client.id)).where(Client.agent_id == agent_id, Client.is_deleted == False, Client.stage.in_(["lead", "negotiating", "under_contract"])))
        pending_tasks = await self._scalar(select(func.count(Task.id)).where(Task.agent_id == agent_id, Task.status == "pending"))
        completed_tasks = await self._scalar(select(func.count(Task.id)).where(Task.agent_id == agent_id, Task.status == "completed"))
        
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        emails_sent_today = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.agent_id == agent_id, EmailLog.status == "sent", EmailLog.created_at >= today_start))
        week_start = today_start - timedelta(days=today_start.weekday())
        emails_sent_this_week = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.agent_id == agent_id, EmailLog.status == "sent", EmailLog.created_at >= week_start))
        
        total_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.agent_id == agent_id, EmailLog.status.in_(["sent", "delivered", "opened", "clicked"])))
        opened_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.agent_id == agent_id, EmailLog.status == "opened"))
        clicked_emails = await self._scalar(select(func.count(EmailLog.id)).where(EmailLog.agent_id == agent_id, EmailLog.status == "clicked"))
        
        open_rate = (opened_emails or 0) / (total_emails or 1) * 100 if total_emails else 0.0
        click_rate = (clicked_emails or 0) / (total_emails or 1) * 100 if total_emails else 0.0
        
        total_leads = await self._scalar(select(func.count(Client.id)).where(Client.agent_id == agent_id, Client.stage == "lead", Client.is_deleted == False))
        closed_deals = await self._scalar(select(func.count(Client.id)).where(Client.agent_id == agent_id, Client.stage == "closed", Client.is_deleted == False))
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

    async def get_recent_activity(self, agent_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        stmt = select(EmailLog, Client.name).join(Client, EmailLog.client_id == Client.id).where(EmailLog.agent_id == agent_id).order_by(EmailLog.created_at.desc()).limit(limit)
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

    async def _scalar(self, stmt) -> int:
        result = await self.session.execute(stmt)
        return result.scalar() or 0

