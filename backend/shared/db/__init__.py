"""
Shared database configuration for all microservices.
"""

from .postgresql import (
    Base,
    init_db,
    close_db,
    get_session,
    engine,
    SessionLocal,
)

__all__ = [
    "Base",
    "init_db",
    "close_db",
    "get_session",
    "engine",
    "SessionLocal",
]

