"""
Authentication utilities for password hashing and JWT tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from app.config import settings

# Use bcrypt directly instead of passlib to avoid initialization bug detection issues
# passlib's bcrypt backend tries to detect wrap bugs using long test strings (>72 bytes)
# which newer bcrypt versions reject, causing initialization failures.


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes if it's a string
    password_bytes = password.encode('utf-8') if isinstance(password, str) else password
    # Generate salt and hash password (bcrypt automatically handles salt)
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    # Return as string (bcrypt returns bytes)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        # Convert to bytes
        password_bytes = plain_password.encode('utf-8') if isinstance(plain_password, str) else plain_password
        hash_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
        # Verify password
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except (ValueError, TypeError):
        # Return False for any verification errors
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

