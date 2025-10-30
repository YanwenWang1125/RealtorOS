"""
Task model using SQLAlchemy ORM for PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from app.db.postgresql import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    email_sent_id = Column(Integer, ForeignKey("email_logs.id"), nullable=True)
    followup_type = Column(String(50), nullable=False)
    scheduled_for = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    priority = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# Composite indexes
Index("ix_tasks_client_status", Task.client_id, Task.status)
Index("ix_tasks_scheduled_status", Task.scheduled_for, Task.status)
