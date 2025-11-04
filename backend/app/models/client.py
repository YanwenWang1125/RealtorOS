"""
Client model using SQLAlchemy ORM for PostgreSQL.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    Index,
    ForeignKey,
)
from app.db.postgresql import Base


def utcnow():
    """Return timezone-aware UTC datetime for column defaults."""
    return datetime.now(timezone.utc)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    property_address = Column(String(200), nullable=False)
    property_type = Column(String(50), nullable=False)
    stage = Column(String(50), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    last_contacted = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)


# Composite indexes
Index("ix_clients_stage_is_deleted", Client.stage, Client.is_deleted)
Index("ix_clients_email_is_deleted", Client.email, Client.is_deleted)
Index("ix_clients_agent_stage", Client.agent_id, Client.stage)
