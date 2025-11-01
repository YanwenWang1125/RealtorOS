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
from app.api.dependencies import get_ai_agent, get_email_service, get_crm_service, get_scheduler_service

router = APIRouter()

@router.get("/", response_model=List[EmailResponse])
async def list_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    status: Optional[str] = None,
    email_service: EmailService = Depends(get_email_service)
):
    """List email history with pagination and filtering."""
    return await email_service.list_emails(page=page, limit=limit, client_id=client_id, status=status)

@router.post("/preview")
async def preview_email(
    request: EmailPreviewRequest,
    ai_agent: AIAgent = Depends(get_ai_agent),
    crm_service: CRMService = Depends(get_crm_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Generate and preview an email without sending."""
    from sqlalchemy import select
    from app.models.client import Client
    from app.models.task import Task
    
    # Get client and task
    client_stmt = select(Client).where(Client.id == request.client_id, Client.is_deleted == False)  # noqa: E712
    client_result = await crm_service.session.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    task_stmt = select(Task).where(Task.id == request.task_id)
    task_result = await scheduler_service.session.execute(task_stmt)
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Generate preview using AI agent
    preview = await ai_agent.generate_email_preview(client, task, request.agent_instructions)
    return preview

@router.post("/send")
async def send_email(
    request: EmailSendRequest,
    email_service: EmailService = Depends(get_email_service)
):
    """Generate and send an email."""
    return await email_service.send_email(request)

@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    email_service: EmailService = Depends(get_email_service)
):
    """Get a specific email by ID."""
    email = await email_service.get_email(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email
