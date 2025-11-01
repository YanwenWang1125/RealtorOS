"""
Periodic Celery tasks for RealtorOS.

This module contains periodic tasks that run on a schedule
to process due tasks and maintain system health.
"""

import logging
from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.scheduler_service import SchedulerService
from app.db.postgresql import init_db, get_session
import asyncio

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_due_tasks(self):
    """
    Process all tasks that are due for execution.
    This task runs every minute via Celery Beat.
    
    Automatically generates and sends follow-up emails for due tasks.
    """
    async def _run():
        await init_db()
        async for session in get_session():
            svc = SchedulerService(session)
            count = await svc.process_and_send_due_emails()
            logger.info(f"Processed {count} due task(s) in this cycle")
            return count
    return asyncio.run(_run())

@celery_app.task(bind=True)
def cleanup_old_tasks(self):
    """
    Clean up old completed tasks to maintain database performance.
    This task runs daily.
    """
    async def _run():
        await init_db()
        async for session in get_session():
            # Implement cleanup if needed
            return True
    return asyncio.run(_run())

@celery_app.task(bind=True)
def health_check_task(self):
    """
    Perform system health checks.
    This task runs every 5 minutes.
    """
    async def _run():
        await init_db()
        return True
    return asyncio.run(_run())
