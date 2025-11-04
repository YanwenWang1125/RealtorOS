"""
Email service for sending and managing emails (SQLAlchemy + SendGrid).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email_log import EmailLog
from app.models.agent import Agent
from app.schemas.email_schema import EmailSendRequest, EmailResponse
from app.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME

    async def send_email(self, email_data: EmailSendRequest, agent: Agent) -> EmailResponse:
        email_log = await self.log_email(
            task_id=email_data.task_id,
            client_id=email_data.client_id,
            agent_id=agent.id,
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body,
            from_name=agent.name,
            from_email=agent.email,
        )

        message = Mail(
            from_email=(agent.email, agent.name),
            to_emails=email_data.to_email,
            subject=email_data.subject,
            html_content=email_data.body,
        )
        try:
            response = self.sg.send(message)
            message_id = response.headers.get("X-Message-Id") or response.headers.get("X-Message-ID")
            await self.update_email_status(email_log.id, "sent", sendgrid_message_id=message_id)
        except Exception as e:
            await self.update_email_status(email_log.id, "failed", error_message=str(e))
        
        # Refresh email_log to get updated timestamps
        await self.session.refresh(email_log)

        return EmailResponse.model_validate(email_log.__dict__, from_attributes=True)

    async def get_email(self, email_id: int) -> Optional[EmailResponse]:
        stmt = select(EmailLog).where(EmailLog.id == email_id)
        result = await self.session.execute(stmt)
        email = result.scalar_one_or_none()
        if email is None:
            return None
        return EmailResponse.model_validate(email.__dict__, from_attributes=True)

    async def list_emails(self, agent_id: int, page: int = 1, limit: int = 10, client_id: Optional[int] = None, status: Optional[str] = None) -> List[EmailResponse]:
        offset = (page - 1) * limit
        stmt = select(EmailLog).where(EmailLog.agent_id == agent_id)
        if client_id:
            stmt = stmt.where(EmailLog.client_id == client_id)
        if status:
            stmt = stmt.where(EmailLog.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        emails = result.scalars().all()
        return [EmailResponse.model_validate(e.__dict__, from_attributes=True) for e in emails]

    async def get_email(self, email_id: int, agent_id: int) -> Optional[EmailResponse]:
        stmt = select(EmailLog).where(EmailLog.id == email_id, EmailLog.agent_id == agent_id)
        result = await self.session.execute(stmt)
        email = result.scalar_one_or_none()
        if email is None:
            return None
        return EmailResponse.model_validate(email.__dict__, from_attributes=True)

    async def log_email(self, task_id: int, client_id: int, agent_id: int, to_email: str, subject: str, body: str, from_name: str, from_email: str) -> EmailLog:
        email = EmailLog(
            task_id=task_id,
            client_id=client_id,
            agent_id=agent_id,
            to_email=to_email,
            subject=subject,
            body=body,
            from_name=from_name,
            from_email=from_email,
            status="queued",
        )
        self.session.add(email)
        await self.session.commit()
        await self.session.refresh(email)
        return email

    async def update_email_status(self, email_id: int, status: str, sendgrid_message_id: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        now = datetime.now(timezone.utc)
        
        # Fetch current email log to check existing timestamps
        stmt_select = select(EmailLog).where(EmailLog.id == email_id)
        result_select = await self.session.execute(stmt_select)
        email_log = result_select.scalar_one_or_none()
        
        if not email_log:
            logger.warning(f"Email log not found for id: {email_id}")
            return False
        
        # Prepare update values
        update_values = {
            "status": status,
            "sendgrid_message_id": sendgrid_message_id,
            "error_message": error_message
        }
        
        # Set timestamp based on status (only if not already set)
        if status == "sent" and email_log.sent_at is None:
            update_values["sent_at"] = now
        elif status == "opened" and email_log.opened_at is None:
            update_values["opened_at"] = now
        elif status == "clicked" and email_log.clicked_at is None:
            update_values["clicked_at"] = now
        
        stmt = (
            update(EmailLog)
            .where(EmailLog.id == email_id)
            .values(**update_values)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a SendGrid webhook event and update the corresponding EmailLog record.
        
        Updates:
        - opened_at: Set to event timestamp when event == "open" (first open only)
        - clicked_at: Set to event timestamp when event == "click" (first click only)
        - webhook_events: Append entire event object to JSON array
        - status: Update to event type (delivered, opened, clicked, bounced, etc.)
        
        Args:
            event_data: Dictionary containing webhook event data
            
        Returns:
            True if event was processed successfully, False otherwise
        """
        message_id = event_data.get("sg_message_id") or event_data.get("message_id")
        event_type = event_data.get("event", "").lower()
        
        if not message_id or not event_type:
            logger.warning(f"Invalid webhook event: missing message_id or event. Data: {event_data}")
            return False
        
        # Find the email log by sendgrid_message_id
        stmt = select(EmailLog).where(EmailLog.sendgrid_message_id == message_id)
        result = await self.session.execute(stmt)
        email_log = result.scalar_one_or_none()
        
        if not email_log:
            logger.warning(f"Email log not found for message_id: {message_id}")
            return False
        
        # Parse timestamp from event (Unix timestamp)
        event_timestamp = None
        if "timestamp" in event_data:
            try:
                ts = event_data.get("timestamp")
                if isinstance(ts, (int, float)):
                    event_timestamp = datetime.fromtimestamp(ts, tz=timezone.utc)
                elif isinstance(ts, str):
                    event_timestamp = datetime.fromtimestamp(int(ts), tz=timezone.utc)
            except (ValueError, TypeError, OSError) as e:
                logger.warning(f"Failed to parse timestamp from event: {ts}, error: {e}")
                event_timestamp = datetime.now(timezone.utc)
        else:
            event_timestamp = datetime.now(timezone.utc)
        
        # Prepare update values
        update_values = {"status": event_type}
        
        # Handle opened_at timestamp (first open only)
        if event_type == "open" and email_log.opened_at is None:
            update_values["opened_at"] = event_timestamp
            logger.info(f"Email {email_log.id} opened at {event_timestamp}")
        
        # Handle clicked_at timestamp (first click only)
        if event_type == "click" and email_log.clicked_at is None:
            update_values["clicked_at"] = event_timestamp
            logger.info(f"Email {email_log.id} clicked at {event_timestamp}")
        
        # Append event to webhook_events JSON array
        current_events = email_log.webhook_events if email_log.webhook_events else []
        if not isinstance(current_events, list):
            current_events = []
        
        # Add full event data to the array
        current_events.append(event_data)
        update_values["webhook_events"] = current_events
        
        # Map event types to status values
        # Keep status as the event type (open, click, delivered, bounce, etc.)
        # This allows tracking the latest event state
        
        # Update the email log
        stmt = (
            update(EmailLog)
            .where(EmailLog.id == email_log.id)
            .values(**update_values)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        
        logger.info(
            f"Processed webhook event: {event_type} for email {email_log.id} "
            f"(message_id: {message_id})"
        )
        return True
