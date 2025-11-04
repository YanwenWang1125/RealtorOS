"""
Unit tests for authentication utilities (password hashing and JWT tokens).
"""

import pytest
from datetime import timedelta
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from app.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test that password hashing produces different output each time."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        # But both should be verifiable
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "my_secure_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_hash_password_unicode(self):
        """Test password hashing with unicode characters."""
        password = "密码123!@#"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "123"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expires_delta(self):
        """Test creating token with custom expiration."""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        assert isinstance(token, str)

    def test_decode_access_token_valid(self):
        """Test decoding a valid access token."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    def test_decode_access_token_invalid(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        assert decoded is None

    def test_decode_access_token_expired(self):
        """Test decoding an expired token."""
        data = {"sub": "123"}
        # Create token with very short expiration (1 second)
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta=expires_delta)
        
        # Wait for token to expire
        import time
        time.sleep(2)
        
        decoded = decode_access_token(token)
        # Should return None for expired token
        assert decoded is None

    def test_token_contains_agent_id(self):
        """Test that token contains agent ID in 'sub' field."""
        agent_id = 42
        data = {"sub": str(agent_id)}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == str(agent_id)

