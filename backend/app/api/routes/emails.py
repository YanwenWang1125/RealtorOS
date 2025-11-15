"""
Email management API routes.

This module provides endpoints for email generation, sending, and history
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.email_schema import EmailPreviewRequest, EmailPreviewResponse, EmailSendRequest, EmailResponse
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
@router.post("/preview", response_model=EmailPreviewResponse)
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
    
    # Check if client has unsubscribed - use getattr to handle cases where field might not exist
    email_unsubscribed = getattr(client, 'email_unsubscribed', False)
    if email_unsubscribed:
        raise HTTPException(
            status_code=400,
            detail="This client has unsubscribed from email follow-ups. Cannot send email."
        )
    
    task_stmt = select(Task).where(Task.id == request.task_id, Task.agent_id == agent.id)
    task_result = await scheduler_service.session.execute(task_stmt)
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Generate preview using AI agent
    try:
        preview = await ai_agent.generate_email_preview(client, task, agent, request.agent_instructions)
        
        # Ensure preview is a dictionary with required keys
        if not isinstance(preview, dict):
            logger.error(f"Invalid preview response type: {type(preview)}")
            raise HTTPException(status_code=500, detail="Invalid preview response from AI agent")
        
        if "body" not in preview or "subject" not in preview:
            logger.error(f"Preview missing required keys. Got keys: {list(preview.keys()) if preview else 'None'}")
            raise HTTPException(status_code=500, detail="Preview response missing required fields")
        
        # Format email with HTML template
        try:
            from app.constants.email_html_template import format_email_html
            html_body = format_email_html(
                email_body=preview.get("body", "") or "",
                agent_name=agent.name or "Real Estate Agent",
                agent_title=agent.title,
                agent_company=agent.company,
                agent_phone=agent.phone,
                agent_email=agent.email or ""
            )
        except Exception as e:
            logger.error(f"Error formatting email HTML template: {str(e)}", exc_info=True)
            # Fallback: use plain body as HTML body if template formatting fails
            html_body = preview.get("body", "") or ""
        
        # Return properly structured response
        return EmailPreviewResponse(
            subject=preview.get("subject", ""),
            body=preview.get("body", "") or "",
            html_body=html_body,
            preview=preview.get("preview")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating email preview: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate email preview: {str(e)}")

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
    
    try:
        # Verify task belongs to agent
        task_stmt = select(Task).where(Task.id == request.task_id, Task.agent_id == agent.id)
        task_result = await scheduler_service.session.execute(task_stmt)
        task = task_result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Check if task is already completed - don't send email if it is
        if task.status == "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Task {request.task_id} is already completed. Cannot send email for completed tasks."
            )
        
        # Check if client has unsubscribed
        from sqlalchemy import select
        from app.models.client import Client
        client_stmt = select(Client).where(
            Client.id == request.client_id,
            Client.agent_id == agent.id,
            Client.is_deleted == False  # noqa: E712
        )
        client_result = await scheduler_service.session.execute(client_stmt)
        client = client_result.scalar_one_or_none()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Safely check email_unsubscribed - use getattr to handle cases where field might not exist
        email_unsubscribed = getattr(client, 'email_unsubscribed', False)
        if email_unsubscribed:
            raise HTTPException(
                status_code=400,
                detail="This client has unsubscribed from email follow-ups. Cannot send email."
            )
        
        # Convert HTML to plain text if needed (we only send plain text emails)
        import re
        from html import unescape
        
        body_text = request.body or ""
        
        def _strip_html_tags(html_content):
            """Strip HTML tags to create plain text version."""
            if not html_content:
                return ""
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html_content)
            # Decode HTML entities
            text = unescape(text)
            # Replace multiple newlines with double newlines (paragraph breaks)
            text = re.sub(r'\n\s*\n+', '\n\n', text)
            # Clean up extra whitespace
            text = re.sub(r'[ \t]+', ' ', text)
            # Remove leading/trailing whitespace from each line
            lines = [line.strip() for line in text.split('\n')]
            text = '\n'.join(lines)
            return text.strip()
        
        # Check if body contains HTML tags
        has_html_tags = bool(re.search(r'<[a-z][\s\S]*?>', body_text, re.IGNORECASE))
        
        if has_html_tags:
            # Convert HTML to plain text
            logger.info("Body contains HTML tags, converting to plain text")
            plain_text_body = _strip_html_tags(body_text)
            request.body = plain_text_body
        else:
            # Already plain text, use as-is
            logger.debug("Body is already plain text, using as-is")
            request.body = body_text
        
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_email endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

class BulkDeleteRequest(BaseModel):
    ids: List[int]

@router.delete("/bulk")
async def bulk_delete_emails(
    request: BulkDeleteRequest = Body(...),
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    """Bulk delete multiple email logs."""
    if not request.ids:
        raise HTTPException(status_code=400, detail="No email IDs provided")
    
    deleted_count = 0
    failed_ids = []
    
    for email_id in request.ids:
        try:
            deleted = await email_service.delete_email(email_id, agent.id)
            if deleted:
                deleted_count += 1
            else:
                failed_ids.append(email_id)
        except Exception as e:
            logger.error(f"Error deleting email {email_id}: {str(e)}")
            failed_ids.append(email_id)
    
    return {
        "success": True,
        "deleted_count": deleted_count,
        "failed_ids": failed_ids,
        "total_requested": len(request.ids)
    }

# This route must be LAST to avoid matching /preview, /send, or /bulk as email_id
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

@router.delete("/{email_id}")
async def delete_email(
    email_id: int,
    agent: Agent = Depends(get_current_agent),
    email_service: EmailService = Depends(get_email_service)
):
    """Delete an email log."""
    deleted = await email_service.delete_email(email_id, agent.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"success": True}


