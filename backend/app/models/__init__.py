"""
Database models package for RealtorOS.

This package contains all SQLAlchemy ORM models for PostgreSQL.
All models use the same Base from app.db.postgresql.
"""

from app.models.client import Client  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.email_log import EmailLog  # noqa: F401

