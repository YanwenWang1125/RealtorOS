"""Webhook routes for SendGrid."""

from fastapi import APIRouter, Request, Header, Depends, HTTPException
from typing import Optional
import json
import os
from shared.schemas.webhook_schema import SendGridWebhookEvent
from shared.db.postgresql import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.email_service import EmailService

webhook_router = APIRouter()


async def get_email_service(session: AsyncSession = Depends(get_session)) -> EmailService:
    return EmailService(session)


@webhook_router.post("/sendgrid")
async def sendgrid_webhook(
    request: Request,
    email_service: EmailService = Depends(get_email_service),
    x_twilio_email_event_webhook_signature: Optional[str] = Header(None, alias="X-Twilio-Email-Event-Webhook-Signature"),
    x_twilio_email_event_webhook_timestamp: Optional[str] = Header(None, alias="X-Twilio-Email-Event-Webhook-Timestamp"),
):
    raw_body = await request.body()
    environment = os.getenv("ENVIRONMENT", "production")
    
    if environment == "development" and not x_twilio_email_event_webhook_signature:
        pass  # Skip verification in dev
    else:
        if not x_twilio_email_event_webhook_signature or not x_twilio_email_event_webhook_timestamp:
            raise HTTPException(status_code=401, detail="Missing required webhook headers")
    
    events_data = json.loads(raw_body.decode('utf-8'))
    if not isinstance(events_data, list):
        events_data = [events_data]
    
    processed_count = 0
    for event_dict in events_data:
        try:
            event = SendGridWebhookEvent(**event_dict)
            await email_service.process_webhook_event(event_dict)
            processed_count += 1
        except Exception:
            continue
    
    return {"status": "success", "processed": processed_count, "total": len(events_data)}

