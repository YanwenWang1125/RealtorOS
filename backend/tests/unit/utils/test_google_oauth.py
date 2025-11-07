"""
Unit tests for Google OAuth verification utilities.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.utils.google_oauth import verify_google_token
from app.config import settings


class TestGoogleOAuth:
    """Test Google OAuth token verification."""

    def test_verify_google_token_no_client_id(self):
        """Test that verification fails when GOOGLE_CLIENT_ID is not set."""
        # Temporarily set GOOGLE_CLIENT_ID to None
        original = settings.GOOGLE_CLIENT_ID
        settings.GOOGLE_CLIENT_ID = None
        
        try:
            with pytest.raises(ValueError, match="GOOGLE_CLIENT_ID is not configured"):
                verify_google_token("dummy_token")
        finally:
            settings.GOOGLE_CLIENT_ID = original

    @patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id_123')
    @patch('app.utils.google_oauth.id_token.verify_oauth2_token')
    def test_verify_google_token_valid(self, mock_verify):
        """Test verification of a valid Google token."""
        # Mock Google's token verification
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'sub': 'google_user_123',
            'email': 'user@gmail.com',
            'name': 'Test User',
            'picture': 'https://example.com/avatar.jpg'
        }
        
        result = verify_google_token("valid_token")
        
        assert result is not None
        assert result['sub'] == 'google_user_123'
        assert result['email'] == 'user@gmail.com'
        assert result['name'] == 'Test User'
        assert result['picture'] == 'https://example.com/avatar.jpg'
        
        # Verify the function was called with correct parameters
        mock_verify.assert_called_once()
        call_args = mock_verify.call_args
        assert call_args[0][0] == "valid_token"
        assert call_args[0][2] == 'test_client_id_123'

    @patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id_123')
    @patch('app.utils.google_oauth.id_token.verify_oauth2_token')
    def test_verify_google_token_invalid_issuer(self, mock_verify):
        """Test verification fails for invalid issuer."""
        mock_verify.return_value = {
            'iss': 'invalid_issuer.com',
            'sub': 'user_123',
            'email': 'user@example.com'
        }
        
        result = verify_google_token("invalid_token")
        assert result is None

    @patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id_123')
    @patch('app.utils.google_oauth.id_token.verify_oauth2_token')
    def test_verify_google_token_missing_name(self, mock_verify):
        """Test that missing name uses email prefix."""
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'sub': 'user_123',
            'email': 'testuser@gmail.com'
            # No 'name' field
        }
        
        result = verify_google_token("token")
        assert result is not None
        assert result['name'] == 'testuser'  # Should use email prefix

    @patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id_123')
    @patch('app.utils.google_oauth.id_token.verify_oauth2_token')
    def test_verify_google_token_value_error(self, mock_verify):
        """Test that ValueError from Google API returns None."""
        mock_verify.side_effect = ValueError("Invalid token")
        
        result = verify_google_token("invalid_token")
        assert result is None

    @patch.object(settings, 'GOOGLE_CLIENT_ID', 'test_client_id_123')
    @patch('app.utils.google_oauth.id_token.verify_oauth2_token')
    def test_verify_google_token_https_issuer(self, mock_verify):
        """Test that https://accounts.google.com issuer is accepted."""
        mock_verify.return_value = {
            'iss': 'https://accounts.google.com',
            'sub': 'user_123',
            'email': 'user@gmail.com'
        }
        
        result = verify_google_token("token")
        assert result is not None

