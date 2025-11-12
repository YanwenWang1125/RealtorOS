"""
Email service for sending and managing emails (SQLAlchemy + SendGrid).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email_log import EmailLog
from app.models.task import Task
from app.models.agent import Agent
from app.schemas.email_schema import EmailSendRequest, EmailResponse
from app.config import settings
from sendgrid import SendGridAPIClient, SendGridException
from sendgrid.helpers.mail import Mail
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Initialize SendGrid client with API key from settings
        # Use dummy values in test environment if not set
        api_key = settings.SENDGRID_API_KEY or ""
        try:
            # Only initialize SendGrid client if we have a valid API key
            # This prevents errors during initialization if the key is missing
            if api_key and api_key != "":
                self.sg = SendGridAPIClient(api_key)
            else:
                self.sg = None
                logger.warning("SendGrid API key not set. Email sending will not work.")
        except Exception as e:
            logger.warning(f"Failed to initialize SendGrid client: {e}. Email sending will not work.")
            self.sg = None
        self.from_email = settings.SENDGRID_FROM_EMAIL or "test@example.com"
        self.from_name = settings.SENDGRID_FROM_NAME

    async def send_email(self, email_data: EmailSendRequest, agent: Agent) -> EmailResponse:
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
            # Check if SendGrid client is initialized
            if not self.sg:
                error_msg = "SendGrid client not initialized. Please configure SENDGRID_API_KEY."
                logger.error(error_msg)
                await self.update_email_status(email_log.id, "failed", error_message=error_msg)
                await self.session.refresh(email_log)
                return EmailResponse.model_validate(email_log.__dict__, from_attributes=True)
            
            # Send email via SendGrid using verified sender email (non-blocking)
            import asyncio
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
        
        # Refresh email_log to get updated timestamps
        await self.session.refresh(email_log)

        return EmailResponse.model_validate(email_log.__dict__, from_attributes=True)

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
        # If message_id is not set yet, try to find by email and recent timestamp
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
        
        # Handle unsubscribe event - mark client as unsubscribed
        client_unsubscribed = False
        client_resubscribed = False
        if event_type in ["unsubscribe", "group_unsubscribe"]:
            from sqlalchemy import select, update
            from app.models.client import Client
            
            # Find client by email address
            recipient_email = event_data.get("email")
            if recipient_email:
                client_stmt = select(Client).where(
                    Client.email == recipient_email,
                    Client.agent_id == email_log.agent_id,
                    Client.is_deleted == False  # noqa: E712
                )
                client_result = await self.session.execute(client_stmt)
                client = client_result.scalar_one_or_none()
                
                # Use getattr to safely check email_unsubscribed field
                email_unsubscribed = getattr(client, 'email_unsubscribed', False) if client else False
                if client and not email_unsubscribed:
                    # Mark client as unsubscribed (will commit with email_log update)
                    update_client_stmt = (
                        update(Client)
                        .where(Client.id == client.id)
                        .values(email_unsubscribed=True)
                        .execution_options(synchronize_session="fetch")
                    )
                    await self.session.execute(update_client_stmt)
                    client_unsubscribed = True
                    logger.info(f"Marking client {client.id} ({client.email}) as unsubscribed due to {event_type} event")
        
        # Handle resubscribe event - mark client as subscribed again
        if event_type == "group_resubscribe":
            from sqlalchemy import select, update
            from app.models.client import Client
            
            # Find client by email address
            recipient_email = event_data.get("email")
            if recipient_email:
                client_stmt = select(Client).where(
                    Client.email == recipient_email,
                    Client.agent_id == email_log.agent_id,
                    Client.is_deleted == False  # noqa: E712
                )
                client_result = await self.session.execute(client_stmt)
                client = client_result.scalar_one_or_none()
                
                # Use getattr to safely check email_unsubscribed field
                email_unsubscribed = getattr(client, 'email_unsubscribed', False) if client else False
                if client and email_unsubscribed:
                    # Mark client as subscribed again (will commit with email_log update)
                    update_client_stmt = (
                        update(Client)
                        .where(Client.id == client.id)
                        .values(email_unsubscribed=False)
                        .execution_options(synchronize_session="fetch")
                    )
                    await self.session.execute(update_client_stmt)
                    client_resubscribed = True
                    logger.info(f"Marking client {client.id} ({client.email}) as resubscribed")
        
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

    async def delete_email(self, email_id: int, agent_id: int) -> bool:
        """
        Delete an email log and clear the reference from associated task.
        Returns True if email was found and deleted, False otherwise.
        """
        # First check if email exists and belongs to the agent
        email = await self.get_email(email_id, agent_id)
        if email is None:
            return False
        
        # Clear the reference from any task that points to this email
        await self.session.execute(
            update(Task)
            .where(Task.email_sent_id == email_id)
            .values(email_sent_id=None)
        )
        
        # Delete the email log
        await self.session.execute(
            delete(EmailLog).where(
                EmailLog.id == email_id,
                EmailLog.agent_id == agent_id
            )
        )
        
        await self.session.commit()
        return True
