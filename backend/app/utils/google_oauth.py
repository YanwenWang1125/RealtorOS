"""
Google OAuth verification utilities.
"""

from google.auth.transport import requests
from google.oauth2 import id_token
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google ID token and return user info.

    Returns:
        dict with keys: sub (Google user ID), email, name, picture
        None if verification fails
    """
    if not settings.GOOGLE_CLIENT_ID or settings.GOOGLE_CLIENT_ID == "":
        logger.error("GOOGLE_CLIENT_ID is not configured in backend .env file")
        raise ValueError("GOOGLE_CLIENT_ID is not configured. Google OAuth is not available.")
    
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Verify the token was issued by Google
        if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.warning(f"Invalid token issuer: {idinfo.get('iss')}")
            return None

        return {
            'sub': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', idinfo['email'].split('@')[0]),
            'picture': idinfo.get('picture')
        }
    except ValueError as e:
        logger.error(f"Google token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Google token verification: {str(e)}")
        return None

