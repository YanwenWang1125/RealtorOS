"""
Celery tasks for task scheduling.

This module contains Celery tasks for creating and managing
follow-up tasks in the RealtorOS system.
"""

from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.scheduler_service import SchedulerService
from app.db.postgresql import init_db, get_session
import asyncio

@celery_app.task(bind=True)
def create_followup_tasks_task(self, client_id: int):
    """
    Create all follow-up tasks for a new client.
    
    Args:
        client_id: The ID of the client to create tasks for
    """
    async def _run():
        await init_db()
        async for session in get_session():
            svc = SchedulerService(session)
            await svc.create_followup_tasks(client_id)
            return True
    return asyncio.run(_run())

@celery_app.task(bind=True)
def reschedule_task_task(self, task_id: int, new_date: str):
    """
    Reschedule a task to a new date.
    
    Args:
        task_id: The ID of the task to reschedule
        new_date: New scheduled date (ISO format string)
    """
    from datetime import datetime
    async def _run():
        await init_db()
        async for session in get_session():
            svc = SchedulerService(session)
            await svc.reschedule_task(task_id, datetime.fromisoformat(new_date))
            return True
    return asyncio.run(_run())

@celery_app.task(bind=True)
def mark_task_complete_task(self, task_id: int, notes: str = None):
    """
    Mark a task as completed.
    
    Args:
        task_id: The ID of the task to mark complete
        notes: Optional completion notes
    """
    async def _run():
        await init_db()
        async for session in get_session():
            svc = SchedulerService(session)
            await svc.update_task(task_id, type("Obj", (), {"model_dump": lambda self, **k: {"status": "completed", "notes": notes}})())
            return True
    return asyncio.run(_run())
