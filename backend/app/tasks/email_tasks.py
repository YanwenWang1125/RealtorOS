"""
Celery tasks for email processing.

This module contains Celery tasks for email generation and sending
in the RealtorOS system.
"""

from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.db.postgresql import init_db, get_session
import asyncio

@celery_app.task(bind=True, max_retries=3)
def generate_and_send_email_task(self, task_id: int):
    """
    Generate and send an email for a specific task.
    
    Args:
        task_id: The ID of the task to process
    """
    async def _run():
        await init_db()
        async for session in get_session():
            email_service = EmailService(session)
            agent = AIAgent()
            # Placeholder: generate content via agent using task_id, then send
            # Extend as needed to fetch client/task
            return True
    return asyncio.run(_run())

@celery_app.task(bind=True, max_retries=3)
def send_email_task(
    self,
    email_log_id: int,
    to_email: str,
    subject: str,
    body: str
):
    """
    Send an email via SendGrid.
    
    Args:
        email_log_id: ID of the email log record
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
    """
    async def _run():
        await init_db()
        async for session in get_session():
            email_service = EmailService(session)
            await email_service.update_email_status(email_log_id, "sent")
            return True
    return asyncio.run(_run())

@celery_app.task(bind=True, max_retries=3)
def process_sendgrid_webhook_task(self, event_type: str, email_log_id: int):
    """
    Process SendGrid webhook events.
    
    Args:
        event_type: Type of webhook event (delivered, opened, clicked, etc.)
        email_log_id: ID of the email log record to update
    """
    async def _run():
        await init_db()
        async for session in get_session():
            email_service = EmailService(session)
            await email_service.update_email_status(email_log_id, event_type)
            return True
    return asyncio.run(_run())
