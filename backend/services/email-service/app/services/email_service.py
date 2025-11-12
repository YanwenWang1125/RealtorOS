"""Email service for sending and managing emails (SendGrid)."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import os
import asyncio
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail
from shared.models.email_log import EmailLog
from shared.schemas.email_schema import EmailSendRequest, EmailResponse
from shared.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Initialize SendGrid client with API key from environment
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if not sendgrid_api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")
        self.sg = SendGridAPIClient(sendgrid_api_key)
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "RealtorOS")

    async def send_email(self, email_data: EmailSendRequest, agent) -> EmailResponse:
        from shared.models.agent import Agent
        # Use verified SendGrid email but display agent name with "via company name"
        company_name = agent.company if agent.company else "RealtorOS"
        display_name = f"{agent.name} via {company_name}"
        
        email_log = await self.log_email(
            task_id=email_data.task_id,
            client_id=email_data.client_id,
            agent_id=agent.id,
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body,
            from_name=display_name,
            from_email=self.from_email,
        )

        try:
            # Send email via SendGrid using verified sender email (non-blocking)
            def _send_email():
                message = Mail(
                    from_email=(self.from_email, display_name),
                    to_emails=email_data.to_email,
                    subject=email_data.subject,
                    html_content=email_data.body
                )
                response = self.sg.send(message)
                return response
            # Run blocking SendGrid call in thread pool to avoid blocking event loop
            response = await asyncio.to_thread(_send_email)
            # SendGrid returns status code 202 on success
            # The actual message ID (sg_message_id) will be provided via webhook events
            # For now, we mark as sent and the webhook will update with the actual message ID
            if response.status_code in [200, 202]:
                await self.update_email_status(email_log.id, "sent", sendgrid_message_id=None)
            else:
                error_msg = f"SendGrid returned status code {response.status_code}: {response.body.decode('utf-8') if response.body else 'Unknown error'}"
                logger.error(error_msg)
                await self.update_email_status(email_log.id, "failed", error_message=error_msg)
        except SendGridException as e:
            error_msg = f"SendGrid error: {str(e)}"
            logger.error(error_msg)
            await self.update_email_status(email_log.id, "failed", error_message=error_msg)
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}", exc_info=True)
            await self.update_email_status(email_log.id, "failed", error_message=str(e))
        
        await self.session.refresh(email_log)
        return EmailResponse.model_validate(email_log.__dict__, from_attributes=True)

    async def get_email(self, email_id: int, agent_id: int) -> Optional[EmailResponse]:
        stmt = select(EmailLog).where(EmailLog.id == email_id, EmailLog.agent_id == agent_id)
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
        stmt_select = select(EmailLog).where(EmailLog.id == email_id)
        result_select = await self.session.execute(stmt_select)
        email_log = result_select.scalar_one_or_none()
        
        if not email_log:
            logger.warning(f"Email log not found for id: {email_id}")
            return False
        
        update_values = {
            "status": status,
            "sendgrid_message_id": sendgrid_message_id,
            "error_message": error_message
        }
        if status == "sent" and email_log.sent_at is None:
            update_values["sent_at"] = now
        
        stmt = update(EmailLog).where(EmailLog.id == email_id).values(**update_values).execution_options(synchronize_session="fetch")
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a SendGrid webhook event and update the corresponding EmailLog record.
        
        Args:
            event_data: Dictionary containing SendGrid webhook event data
            
        Returns:
            True if event was processed successfully, False otherwise
        """
        # SendGrid webhook format
        message_id = (
            event_data.get("sg_message_id") or  # SendGrid message ID
            event_data.get("message_id")
        )
        event_type = event_data.get("event", "").lower()
        
        if not message_id or not event_type:
            logger.warning(f"Invalid webhook event: missing message_id or event. Data: {event_data}")
            return False
        
        # Find the email log by sendgrid_message_id or by email address and timestamp
        stmt = select(EmailLog).where(EmailLog.sendgrid_message_id == message_id)
        result = await self.session.execute(stmt)
        email_log = result.scalar_one_or_none()
        
        # If not found by message_id, try to find by email address (for first webhook event)
        if not email_log and message_id:
            # Try to find by recipient email and recent timestamp (within last hour)
            recipient_email = event_data.get("email")
            if recipient_email:
                one_hour_ago = datetime.now(timezone.utc).timestamp() - 3600
                event_ts = event_data.get("timestamp", 0)
                if isinstance(event_ts, str):
                    try:
                        event_ts = int(event_ts)
                    except ValueError:
                        event_ts = 0
                
                if event_ts > one_hour_ago:
                    stmt = select(EmailLog).where(
                        EmailLog.to_email == recipient_email,
                        EmailLog.sendgrid_message_id.is_(None),
                        EmailLog.created_at >= datetime.fromtimestamp(event_ts - 3600, tz=timezone.utc)
                    ).order_by(EmailLog.created_at.desc()).limit(1)
                    result = await self.session.execute(stmt)
                    email_log = result.scalar_one_or_none()
                    if email_log:
                        # Update with the message_id from webhook
                        update_stmt = (
                            update(EmailLog)
                            .where(EmailLog.id == email_log.id)
                            .values(sendgrid_message_id=message_id)
                            .execution_options(synchronize_session="fetch")
                        )
                        await self.session.execute(update_stmt)
                        await self.session.commit()
                        await self.session.refresh(email_log)
        
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
