"""
Google OAuth verification utilities.
"""

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.auth import jwt as google_jwt
from typing import Optional
import logging
import time
import os
import requests

logger = logging.getLogger(__name__)


def verify_google_token(token: str) -> Optional[dict]:
    """
    Verify Google ID token and return user info.
    
    Handles clock skew errors by allowing a small time window (leeway) for token validation.

    Returns:
        dict with keys: sub (Google user ID), email, name, picture
        None if verification fails
    """
    google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not google_client_id or google_client_id == "":
        logger.error("GOOGLE_CLIENT_ID is not configured in environment variables")
        raise ValueError("GOOGLE_CLIENT_ID is not configured. Google OAuth is not available.")
    
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            google_client_id
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
        error_msg = str(e)
        
        # Check if this is a clock skew error ("Token used too early")
        if "Token used too early" in error_msg or "too early" in error_msg.lower():
            logger.warning(f"Clock skew detected: {error_msg}. Attempting verification with leeway...")
            
            try:
                # Decode without verification to inspect claims
                unverified = google_jwt.decode(token, verify=False)
                iat = unverified.get('iat')
                current_time = int(time.time())
                
                # If the token was issued within the next 10 seconds, allow it (clock skew tolerance)
                if iat and current_time < iat <= current_time + 10:
                    logger.info(f"Token issued {iat - current_time} seconds in the future, allowing with clock skew tolerance")
                    
                    # Use PyJWT directly with Google's certificate discovery and leeway
                    # PyJWT is available as a dependency of google-auth
                    import jwt as pyjwt
                    from cryptography import x509
                    
                    # Get the key ID from the token header
                    unverified_header = pyjwt.get_unverified_header(token)
                    kid = unverified_header.get('kid')
                    
                    if not kid:
                        logger.error("Token missing key ID (kid) in header")
                        return None
                    
                    # Get Google's public keys from their certificate endpoint
                    certs_url = 'https://www.googleapis.com/oauth2/v1/certs'
                    certs_response = requests.get(certs_url)
                    certs_response.raise_for_status()
                    certs = certs_response.json()
                    
                    # Find the matching certificate
                    cert_pem = certs.get(kid)
                    if not cert_pem:
                        logger.error(f"Certificate not found for key ID: {kid}")
                        return None
                    
                    # Parse the PEM certificate and extract the public key
                    try:
                        cert_obj = x509.load_pem_x509_certificate(cert_pem.encode('utf-8'))
                        public_key = cert_obj.public_key()
                    except Exception as cert_error:
                        logger.error(f"Failed to parse certificate: {str(cert_error)}")
                        return None
                    
                    # Decode and verify with leeway (10 seconds for clock skew)
                    decoded = pyjwt.decode(
                        token,
                        public_key,
                        algorithms=['RS256'],
                        audience=google_client_id,
                        options={
                            "verify_signature": True,
                            "verify_exp": True,
                            "verify_iat": True,
                            "verify_aud": True,
                            "verify_iss": False,  # We'll check issuer manually
                        },
                        leeway=10  # Allow 10 seconds of clock skew
                    )
                    
                    # Verify issuer manually
                    if decoded.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
                        logger.warning(f"Invalid token issuer: {decoded.get('iss')}")
                        return None
                    
                    return {
                        'sub': decoded['sub'],
                        'email': decoded['email'],
                        'name': decoded.get('name', decoded['email'].split('@')[0]),
                        'picture': decoded.get('picture')
                    }
                else:
                    logger.error(f"Token clock skew too large: iat={iat}, current={current_time}, diff={iat - current_time if iat else 'N/A'}")
                    return None
            except Exception as decode_error:
                logger.error(f"Failed to verify token with clock skew tolerance: {str(decode_error)}")
                return None
        
        logger.error(f"Google token verification failed: {error_msg}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during Google token verification: {str(e)}")
        return None

