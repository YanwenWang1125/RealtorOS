"""
Pydantic schemas for SendGrid webhook events.

This module defines the structure of webhook events received from SendGrid
for email engagement tracking (opened, clicked, bounced, delivered, etc.).
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SendGridWebhookEvent(BaseModel):
    """
    SendGrid webhook event model.
    
    Represents a single event from SendGrid's Event Webhook API.
    Events include: processed, delivered, open, click, bounce, dropped,
    deferred, spamreport, unsubscribe, group_unsubscribe, group_resubscribe.
    """
    
    email: str = Field(..., description="Recipient email address")
    timestamp: int = Field(..., description="Unix timestamp of the event")
    event: str = Field(..., description="Event type (open, click, delivered, etc.)")
    sg_message_id: str = Field(..., description="SendGrid message ID")
    sg_event_id: Optional[str] = Field(None, description="SendGrid event ID")
    
    # Optional fields for different event types
    url: Optional[str] = Field(None, description="Clicked URL (for click events)")
    ip: Optional[str] = Field(None, description="IP address of the recipient")
    useragent: Optional[str] = Field(None, description="User agent string")
    
    # Additional metadata
    reason: Optional[str] = Field(None, description="Bounce reason (for bounce events)")
    status: Optional[str] = Field(None, description="Status code (for bounce events)")
    type: Optional[str] = Field(None, description="Bounce type (for bounce events)")
    
    # Additional fields that may be present
    category: Optional[list] = Field(None, description="Email categories")
    unique_arg: Optional[Dict[str, Any]] = Field(None, description="Unique arguments")
    asm_group_id: Optional[int] = Field(None, description="Unsubscribe group ID")
    
    @field_validator('event')
    @classmethod
    def validate_event(cls, v: str) -> str:
        """Validate event type."""
        valid_events = [
            'processed',
            'delivered',
            'open',
            'click',
            'bounce',
            'dropped',
            'deferred',
            'spamreport',
            'unsubscribe',
            'group_unsubscribe',
            'group_resubscribe',
            'unsubscribe',
        ]
        event_lower = v.lower()
        if event_lower not in valid_events:
            # Log warning but allow through (in case SendGrid adds new events)
            import logging
            logging.getLogger(__name__).warning(f"Unknown event type: {v}")
        return event_lower
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "recipient@example.com",
                "timestamp": 1513299569,
                "event": "open",
                "sg_message_id": "filter0001-17677-5F1B7A37-1-0",
                "sg_event_id": "event_id_here",
                "ip": "255.255.255.255",
                "useragent": "Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0",
                "url": "http://example.com"  # for click events
            }
        }

