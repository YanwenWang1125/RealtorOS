"""
Agent model for realtor authentication and profiles.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Index,
)
from shared.db.postgresql import Base


def utcnow():
    """Return timezone-aware UTC datetime for column defaults."""
    return datetime.now(timezone.utc)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    google_sub = Column(String(255), nullable=True, unique=True, index=True)  # Google's user ID
    avatar_url = Column(String(500), nullable=True)
    auth_provider = Column(String(20), nullable=False, default='email')  # 'email' or 'google'

    # Profile information
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    title = Column(String(100), nullable=True)  # e.g., "Senior Real Estate Agent"
    company = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


# Composite indexes
Index("ix_agents_email_active", Agent.email, Agent.is_active)
Index("ix_agents_google_sub_active", Agent.google_sub, Agent.is_active)

