"""
Local testing script for SendGrid webhook endpoint.

This script helps test the webhook endpoint locally before deploying.
Note: You'll need a valid signature from SendGrid to test signature verification.

Usage:
    python -m pytest tests/utils/test_webhook_local.py -v
    
Or run directly:
    python backend/tests/utils/test_webhook_local.py
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Test helper functions
def create_test_event(
    event_type: str = "open",
    sg_message_id: str = "test-message-123",
    email: str = "test@example.com",
    timestamp: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a test webhook event."""
    if timestamp is None:
        timestamp = int(time.time())
    
    event = {
        "event": event_type,
        "sg_message_id": sg_message_id,
        "timestamp": timestamp,
        "email": email,
        "sg_event_id": f"event-{timestamp}",
    }
    
    # Add optional fields based on event type
    if event_type == "click":
        event["url"] = kwargs.get("url", "http://example.com")
    if event_type in ["open", "click"]:
        event["ip"] = kwargs.get("ip", "192.168.1.1")
        event["useragent"] = kwargs.get("useragent", "Mozilla/5.0 Test Browser")
    
    event.update(kwargs)
    return event


def format_curl_command(
    url: str,
    events: list,
    signature: str = "YOUR_SIGNATURE_HERE",
    timestamp: str = None
) -> str:
    """Format a curl command for testing the webhook."""
    if timestamp is None:
        timestamp = str(int(time.time()))
    
    events_json = json.dumps(events, indent=2)
    
    return f"""curl -X POST {url} \\
  -H "Content-Type: application/json" \\
  -H "X-Twilio-Email-Event-Webhook-Signature: {signature}" \\
  -H "X-Twilio-Email-Event-Webhook-Timestamp: {timestamp}" \\
  -d '{json.dumps(events)}'"""


if __name__ == "__main__":
    # Example test events
    print("=" * 60)
    print("SendGrid Webhook Test Events")
    print("=" * 60)
    
    # Test event: Open
    open_event = create_test_event("open", "test-msg-001", "user@example.com")
    print("\n1. Open Event:")
    print(json.dumps(open_event, indent=2))
    
    # Test event: Click
    click_event = create_test_event(
        "click",
        "test-msg-001",
        "user@example.com",
        url="https://example.com/link"
    )
    print("\n2. Click Event:")
    print(json.dumps(click_event, indent=2))
    
    # Test event: Delivered
    delivered_event = create_test_event("delivered", "test-msg-001", "user@example.com")
    print("\n3. Delivered Event:")
    print(json.dumps(delivered_event, indent=2))
    
    # Example curl command
    print("\n" + "=" * 60)
    print("Example curl command for testing:")
    print("=" * 60)
    print("\nNote: Replace YOUR_SIGNATURE_HERE with actual signature from SendGrid")
    print("\n" + format_curl_command(
        "http://localhost:8000/webhook/sendgrid",
        [open_event]
    ))
    
    print("\n" + "=" * 60)
    print("Multiple Events (array):")
    print("=" * 60)
    print("\n" + format_curl_command(
        "http://localhost:8000/webhook/sendgrid",
        [delivered_event, open_event, click_event]
    ))

