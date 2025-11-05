"""
Auth Service - moved from app/services/auth_service.py to avoid naming conflict.
This is a wrapper that imports from the actual service.
"""

from ...services.auth_service import AuthService

__all__ = ["AuthService"]

