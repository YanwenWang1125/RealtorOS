"""Email service for sending and managing emails."""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from shared.models.email_log import EmailLog
from shared.schemas.email_schema import EmailSendRequest, EmailResponse
from shared.utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Initialize SES client with AWS credentials from environment
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.ses = boto3.client(
            'ses',
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.from_email = os.getenv("SES_FROM_EMAIL", "")
        self.from_name = os.getenv("SES_FROM_NAME", "")

    async def send_email(self, email_data: EmailSendRequest, agent) -> EmailResponse:
        from shared.models.agent import Agent
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

        try:
            # Send email via Amazon SES
            response = self.ses.send_email(
                Source=f"{agent.name} <{agent.email}>",
                Destination={'ToAddresses': [email_data.to_email]},
                Message={
                    'Subject': {'Data': email_data.subject},
                    'Body': {'Html': {'Data': email_data.body}}
                }
            )
            # Get MessageId from SES response
            message_id = response['MessageId']
            await self.update_email_status(email_log.id, "sent", ses_message_id=message_id)
        except NoCredentialsError as e:
            error_msg = "AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            logger.error(error_msg)
            await self.update_email_status(email_log.id, "failed", error_message=error_msg)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"AWS SES error ({error_code}): {error_message}")
            await self.update_email_status(email_log.id, "failed", error_message=f"{error_code}: {error_message}")
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

    async def update_email_status(self, email_id: int, status: str, ses_message_id: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        now = datetime.now(timezone.utc)
        stmt_select = select(EmailLog).where(EmailLog.id == email_id)
        result_select = await self.session.execute(stmt_select)
        email_log = result_select.scalar_one_or_none()
        
        if not email_log:
            return False
        
        update_values = {"status": status, "ses_message_id": ses_message_id, "error_message": error_message}
        if status == "sent" and email_log.sent_at is None:
            update_values["sent_at"] = now
        
        stmt = update(EmailLog).where(EmailLog.id == email_id).values(**update_values).execution_options(synchronize_session="fetch")
        await self.session.execute(stmt)
        await self.session.commit()
        return True

    async def process_webhook_event(self, event_data: dict) -> bool:
        # Support both SES SNS format and legacy SendGrid format
        message_id = (
            event_data.get("mail", {}).get("messageId") or  # SES SNS format
            event_data.get("ses_message_id") or  # Legacy format
            event_data.get("sg_message_id") or  # Legacy SendGrid format
            event_data.get("message_id")
        )
        event_type = (
            event_data.get("eventType", "").lower() or  # SES SNS format
            event_data.get("event", "").lower()  # Legacy format
        )
        
        if not message_id or not event_type:
            return False
        
        stmt = select(EmailLog).where(EmailLog.ses_message_id == message_id)
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

