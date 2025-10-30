"""
Email service for sending and managing emails (SQLAlchemy + SendGrid).
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email_log import EmailLog
from app.schemas.email_schema import EmailSendRequest, EmailResponse
from app.config import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class EmailService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME

    async def send_email(self, email_data: EmailSendRequest) -> EmailResponse:
        email_log = await self.log_email(
            task_id=email_data.task_id,
            client_id=email_data.client_id,
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body,
        )

        message = Mail(
            from_email=(self.from_email, self.from_name),
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

        return EmailResponse.model_validate(email_log.__dict__, from_attributes=True)

    async def get_email(self, email_id: int) -> Optional[EmailResponse]:
        stmt = select(EmailLog).where(EmailLog.id == email_id)
        result = await self.session.execute(stmt)
        email = result.scalar_one_or_none()
        if email is None:
            return None
        return EmailResponse.model_validate(email.__dict__, from_attributes=True)

    async def list_emails(self, page: int = 1, limit: int = 10, client_id: Optional[int] = None, status: Optional[str] = None) -> List[EmailResponse]:
        offset = (page - 1) * limit
        stmt = select(EmailLog)
        if client_id:
            stmt = stmt.where(EmailLog.client_id == client_id)
        if status:
            stmt = stmt.where(EmailLog.status == status)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        emails = result.scalars().all()
        return [EmailResponse.model_validate(e.__dict__, from_attributes=True) for e in emails]

    async def log_email(self, task_id: int, client_id: int, to_email: str, subject: str, body: str) -> EmailLog:
        email = EmailLog(
            task_id=task_id,
            client_id=client_id,
            to_email=to_email,
            subject=subject,
            body=body,
            status="queued",
        )
        self.session.add(email)
        await self.session.commit()
        await self.session.refresh(email)
        return email

    async def update_email_status(self, email_id: int, status: str, sendgrid_message_id: Optional[str] = None, error_message: Optional[str] = None) -> bool:
        stmt = (
            update(EmailLog)
            .where(EmailLog.id == email_id)
            .values(status=status, sendgrid_message_id=sendgrid_message_id, error_message=error_message)
            .execution_options(synchronize_session="fetch")
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def process_webhook_event(self, event_data: Dict[str, Any]) -> bool:
        message_id = event_data.get("sg_message_id") or event_data.get("message_id")
        status = event_data.get("event")
        if not message_id or not status:
            return False
        stmt = (
            update(EmailLog)
            .where(EmailLog.sendgrid_message_id == message_id)
            .values(status=status)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return True
