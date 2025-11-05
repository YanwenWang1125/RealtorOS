"""
Email management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from shared.schemas.email_schema import EmailPreviewRequest, EmailSendRequest, EmailResponse
from shared.models.agent import Agent
from shared.auth.jwt_auth import get_current_agent
from shared.db.postgresql import get_session
from ...services.email_service import EmailService
from ...services.ai_agent import AIAgent
from sqlalchemy import select
from shared.models.client import Client
from shared.models.task import Task

router = APIRouter()


async def get_email_service(session: AsyncSession = Depends(get_session)) -> EmailService:
    return EmailService(session)


async def get_ai_agent() -> AIAgent:
    return AIAgent()


@router.get("/", response_model=List[EmailResponse])
async def list_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    return await email_service.list_emails(agent.id, page=page, limit=limit, client_id=client_id, status=status)


@router.post("/preview")
async def preview_email(
    request: EmailPreviewRequest,
    agent: Agent = Depends(get_current_agent),
    ai_agent: AIAgent = Depends(get_ai_agent),
    session: AsyncSession = Depends(get_session)
):
    client_stmt = select(Client).where(Client.id == request.client_id, Client.agent_id == agent.id, Client.is_deleted == False)
    client_result = await session.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    task_stmt = select(Task).where(Task.id == request.task_id, Task.agent_id == agent.id)
    task_result = await session.execute(task_stmt)
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    preview = await ai_agent.generate_email_preview(client, task, agent, request.agent_instructions)
    return preview


@router.post("/send", response_model=EmailResponse)
async def send_email(
    request: EmailSendRequest,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    return await email_service.send_email(request, agent)


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: int,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    email = await email_service.get_email(email_id, agent.id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email

