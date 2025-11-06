"""
Email management API routes.

This module provides endpoints for email generation, sending, and history
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.email_schema import EmailPreviewRequest, EmailSendRequest, EmailResponse
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.api.dependencies import get_ai_agent, get_email_service, get_crm_service, get_scheduler_service, get_current_agent
from app.models.agent import Agent
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/", response_model=List[EmailResponse])
async def list_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    status: Optional[str] = None,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    """List email history with pagination and filtering."""
    return await email_service.list_emails(agent.id, page=page, limit=limit, client_id=client_id, status=status)

# IMPORTANT: /preview and /send must be defined BEFORE /{email_id} 
# to avoid FastAPI matching "preview" or "send" as email_id
@router.post("/preview")
async def preview_email(
    request: EmailPreviewRequest,
    agent: Agent = Depends(get_current_agent),
    ai_agent: AIAgent = Depends(get_ai_agent),
    crm_service: CRMService = Depends(get_crm_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Generate and preview an email without sending."""
    from sqlalchemy import select
    from app.models.client import Client
    from app.models.task import Task
    
    # Get client and task (verify they belong to agent)
    client_stmt = select(Client).where(
        Client.id == request.client_id,
        Client.agent_id == agent.id,
        Client.is_deleted == False  # noqa: E712
    )
    client_result = await crm_service.session.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    task_stmt = select(Task).where(Task.id == request.task_id, Task.agent_id == agent.id)
    task_result = await scheduler_service.session.execute(task_stmt)
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Generate preview using AI agent
    preview = await ai_agent.generate_email_preview(client, task, agent, request.agent_instructions)
    return preview

@router.post("/send")
async def send_email(
    request: EmailSendRequest,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Generate and send an email, then mark the associated task as completed."""
    from datetime import datetime, timezone
    from sqlalchemy import select, update
    from app.models.task import Task
    
    # Verify task belongs to agent
    task_stmt = select(Task).where(Task.id == request.task_id, Task.agent_id == agent.id)
    task_result = await scheduler_service.session.execute(task_stmt)
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Send the email
    email_response = await email_service.send_email(request, agent)
    
    # If email was sent successfully, update the task to completed
    if email_response.status == "sent" and request.task_id:
        try:
            now = datetime.now(timezone.utc)
            stmt = (
                update(Task)
                .where(Task.id == request.task_id)
                .values(
                    status="completed",
                    email_sent_id=email_response.id,
                    completed_at=now
                )
                .execution_options(synchronize_session="fetch")
            )
            await scheduler_service.session.execute(stmt)
            await scheduler_service.session.commit()
            logger.info(f"Marked task {request.task_id} as completed after sending email {email_response.id}")
        except Exception as e:
            # Log error but don't fail the email send response
            logger.error(f"Failed to mark task {request.task_id} as completed: {str(e)}", exc_info=True)
    
    return email_response

# This route must be LAST to avoid matching /preview or /send as email_id
@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    """Get a specific email by ID."""
    email = await email_service.get_email(email_id, agent.id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


