"""
EmailLog model using SQLAlchemy ORM for PostgreSQL.
"""

from datetime import datetime, timezone
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


def utcnow():
    """Return timezone-aware UTC datetime for column defaults."""
    return datetime.now(timezone.utc)


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    from_name = Column(String(200), nullable=True)  # Store agent name at send time
    from_email = Column(String(255), nullable=True)  # Store agent email at send time
    to_email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, index=True)
    sendgrid_message_id = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    webhook_events = Column(JSON, nullable=True)


# Composite indexes
Index("ix_email_logs_status_client", EmailLog.status, EmailLog.client_id)
