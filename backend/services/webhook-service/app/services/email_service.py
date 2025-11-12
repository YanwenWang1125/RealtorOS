"""Email service for webhook processing."""

from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.email_log import EmailLog
from shared.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> bool:
        # SendGrid webhook format
        message_id = (
            event_data.get("sg_message_id") or  # SendGrid message ID
            event_data.get("message_id")
        )
        event_type = event_data.get("event", "").lower()
        
        if not message_id or not event_type:
            logger.warning(f"Invalid webhook event: missing message_id or event. Data: {event_data}")
            return False
        
        stmt = select(EmailLog).where(EmailLog.sendgrid_message_id == message_id)
        result = await self.session.execute(stmt)
        email_log = result.scalar_one_or_none()
        
        if not email_log:
            return False
        
        event_timestamp = None
        if "timestamp" in event_data:
            try:
                ts = event_data.get("timestamp")
                if isinstance(ts, (int, float)):
                    event_timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)
                elif isinstance(ts, str):
                    event_timestamp = datetime.fromtimestamp(int(ts), tz=timezone.utc)
            except:
                event_timestamp = datetime.now(timezone.utc)
        else:
            event_timestamp = datetime.now(timezone.utc)
        
        update_values = {"status": event_type}
        if event_type == "open" and email_log.opened_at is None:
            update_values["opened_at"] = event_timestamp
        if event_type == "click" and email_log.clicked_at is None:
            update_values["clicked_at"] = event_timestamp
        
        current_events = email_log.webhook_events if email_log.webhook_events else []
        if not isinstance(current_events, list):
            current_events = []
        current_events.append(event_data)
        update_values["webhook_events"] = current_events
        
        stmt = update(EmailLog).where(EmailLog.id == email_log.id).values(**update_values).execution_options(synchronize_session="fetch")
        await self.session.execute(stmt)
        await self.session.commit()
        return True

