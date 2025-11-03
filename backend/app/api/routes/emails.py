"""
Email management API routes.

This module provides endpoints for email generation, sending, and history
in the RealtorOS CRM system.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from typing import List, Optional
import json
from app.schemas.email_schema import EmailPreviewRequest, EmailSendRequest, EmailResponse
from app.schemas.webhook_schema import SendGridWebhookEvent
from app.services.ai_agent import AIAgent
from app.services.email_service import EmailService
from app.services.crm_service import CRMService
from app.services.scheduler_service import SchedulerService
from app.api.dependencies import get_ai_agent, get_email_service, get_crm_service, get_scheduler_service
from app.utils.webhook_security import verify_sendgrid_signature
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Separate router for webhook endpoints (public, no /api prefix)
webhook_router = APIRouter()

@webhook_router.get("/sendgrid/test")
async def test_webhook_endpoint():
    """Test endpoint to verify webhook URL is accessible."""
    return {
        "status": "ok",
        "message": "Webhook endpoint is accessible",
        "endpoint": "/webhook/sendgrid",
        "note": "For local development, use ngrok or similar to expose this URL to SendGrid"
    }

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
    email_service: EmailService = Depends(get_email_service),
    scheduler_service: SchedulerService = Depends(get_scheduler_service)
):
    """Generate and send an email, then mark the associated task as completed."""
    from datetime import datetime, timezone
    from sqlalchemy import update
    from app.models.task import Task
    
    # Send the email
    email_response = await email_service.send_email(request)
    
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


@webhook_router.post("/sendgrid")
async def sendgrid_webhook(
    request: Request,
    email_service: EmailService = Depends(get_email_service),
    x_twilio_email_event_webhook_signature: Optional[str] = Header(None, alias="X-Twilio-Email-Event-Webhook-Signature"),
    x_twilio_email_event_webhook_timestamp: Optional[str] = Header(None, alias="X-Twilio-Email-Event-Webhook-Timestamp"),
):
    """
    SendGrid webhook endpoint for email engagement tracking.
    
    This endpoint receives POST requests from SendGrid with email event data
    (opened, clicked, bounced, delivered, etc.). The endpoint verifies the
    ECDSA signature to ensure requests are authentic.
    
    Events processed:
    - processed: Message received, ready for delivery
    - delivered: Successfully delivered
    - open: Recipient opened email
    - click: Recipient clicked link
    - bounce: Server rejected message
    - dropped: Message dropped (invalid email, spam)
    - deferred: Temporarily rejected
    - spamreport: Marked as spam
    
    Security:
    - Verifies ECDSA signature using SENDGRID_WEBHOOK_VERIFICATION_KEY
    - Validates timestamp (rejects requests older than 10 minutes)
    - Returns 401 if signature verification fails
    
    Returns:
        HTTP 200: Events processed successfully
        HTTP 401: Signature verification failed
        HTTP 400: Invalid request format
    """
    try:
        # Get raw request body for signature verification
        raw_body = await request.body()
        
        # Extract required headers
        signature = x_twilio_email_event_webhook_signature
        timestamp = x_twilio_email_event_webhook_timestamp
        
        # In development, allow bypassing signature verification for testing
        # In production, signature verification is required
        if settings.ENVIRONMENT == "development" and not signature:
            logger.warning("Running in development mode - signature verification bypassed")
        else:
            if not signature or not timestamp:
                logger.warning("Missing required webhook headers: signature or timestamp")
                raise HTTPException(
                    status_code=401,
                    detail="Missing required webhook headers"
                )
            
            # Verify ECDSA signature
            public_key = settings.SENDGRID_WEBHOOK_VERIFICATION_KEY
            if public_key and not verify_sendgrid_signature(raw_body, signature, timestamp, public_key):
                logger.warning(
                    f"Webhook signature verification failed. "
                    f"Signature: {signature[:20]}..., Timestamp: {timestamp}"
                )
                raise HTTPException(
                    status_code=401,
                    detail="Invalid webhook signature"
                )
            elif not public_key:
                logger.warning("SENDGRID_WEBHOOK_VERIFICATION_KEY not set - skipping signature verification")
        
        # Parse webhook payload (array of events)
        try:
            events_data = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook payload as JSON: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON payload"
            )
        
        # Validate events_data is a list
        if not isinstance(events_data, list):
            events_data = [events_data]
        
        # Process each event
        processed_count = 0
        failed_count = 0
        
        for event_dict in events_data:
            try:
                # Validate event structure using Pydantic schema
                event = SendGridWebhookEvent(**event_dict)
                
                # Process webhook event
                success = await email_service.process_webhook_event(event_dict)
                
                if success:
                    processed_count += 1
                    logger.info(
                        f"Successfully processed webhook event: {event.event} "
                        f"for message {event.sg_message_id}"
                    )
                else:
                    failed_count += 1
                    logger.warning(
                        f"Failed to process webhook event: {event.event} "
                        f"for message {event.sg_message_id}"
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Error processing webhook event: {e}",
                    exc_info=True,
                    extra={"event_data": event_dict}
                )
                # Continue processing remaining events
        
        logger.info(
            f"Webhook processing complete: {processed_count} succeeded, "
            f"{failed_count} failed out of {len(events_data)} events"
        )
        
        # Always return 200 to prevent SendGrid retries
        # (even if some events failed, we've logged them)
        return {
            "status": "success",
            "processed": processed_count,
            "failed": failed_count,
            "total": len(events_data)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in webhook endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing webhook"
        )
