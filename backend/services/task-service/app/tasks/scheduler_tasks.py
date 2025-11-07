"""
Celery tasks for task scheduling.
"""

from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.scheduler_service import SchedulerService
from shared.db.postgresql import init_db, get_session
import asyncio

@celery_app.task(bind=True)
def create_followup_tasks_task(self, client_id: int, agent_id: int):
    """
    Create all follow-up tasks for a new client.
    
    Args:
        client_id: The ID of the client to create tasks for
        agent_id: The ID of the agent
    """
    async def _run():
        await init_db()
        async for session in get_session():
            svc = SchedulerService(session)
            await svc.create_followup_tasks(client_id, agent_id)
            return True
    return asyncio.run(_run())

@celery_app.task(bind=True)
def reschedule_task_task(self, task_id: int, new_date: str, agent_id: int):
    """
    Reschedule a task to a new date.
    
    Args:
        task_id: The ID of the task to reschedule
        new_date: New scheduled date (ISO format string)
        agent_id: The ID of the agent who owns the task
    """
    from datetime import datetime
    async def _run():
        await init_db()
        async for session in get_session():
            svc = SchedulerService(session)
            await svc.reschedule_task(task_id, datetime.fromisoformat(new_date), agent_id)
            return True
    return asyncio.run(_run())

