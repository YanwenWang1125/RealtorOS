"""
EmailLog model using SQLAlchemy ORM for PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
)
from app.db.postgresql import Base


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    to_email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, index=True)
    sendgrid_message_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    webhook_events = Column(JSON, nullable=True)


# Composite indexes
Index("ix_email_logs_status_client", EmailLog.status, EmailLog.client_id)
