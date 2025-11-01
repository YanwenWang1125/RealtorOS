"""
Webhook security utilities for SendGrid webhook signature verification.

This module provides ECDSA signature verification for SendGrid webhooks
to ensure requests are authentic and prevent replay attacks.
"""

import hashlib
import time
from typing import Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.exceptions import InvalidSignature
from app.utils.logger import get_logger

logger = get_logger(__name__)


def verify_sendgrid_signature(
    payload: bytes,
    signature: str,
    timestamp: str,
    public_key: str
) -> bool:
    """
    Verify SendGrid webhook signature using ECDSA.
    
    SendGrid uses ECDSA (Elliptic Curve Digital Signature Algorithm) with SHA-256
    to sign webhook payloads. The signature is computed over the concatenation of
    timestamp and raw request body.
    
    Process:
    1. Concatenate timestamp and payload: timestamp + payload
    2. Compute SHA-256 hash of the concatenated data
    3. Verify ECDSA signature against the hash using SendGrid's public key
    
    Args:
        payload: Raw request body bytes
        signature: Base64-encoded ECDSA signature from X-Twilio-Email-Event-Webhook-Signature header
        timestamp: Unix timestamp string from X-Twilio-Email-Event-Webhook-Timestamp header
        public_key: PEM-encoded ECDSA public key from SendGrid
        
    Returns:
        True if signature is valid, False otherwise
        
    Raises:
        ValueError: If signature or timestamp format is invalid
    """
    try:
        # Validate timestamp (prevent replay attacks)
        try:
            timestamp_int = int(timestamp)
            current_time = int(time.time())
            time_diff = abs(current_time - timestamp_int)
            
            # Reject requests older than 10 minutes
            MAX_AGE_SECONDS = 600
            if time_diff > MAX_AGE_SECONDS:
                logger.warning(
                    f"Webhook timestamp too old: {time_diff}s difference. "
                    f"Timestamp: {timestamp_int}, Current: {current_time}"
                )
                return False
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid timestamp format: {timestamp}, error: {e}")
            return False
        
        # Load public key from PEM format
        try:
            public_key_obj = serialization.load_pem_public_key(public_key.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to load public key: {e}")
            return False
        
        # Verify public key is ECDSA
        if not isinstance(public_key_obj, ec.EllipticCurvePublicKey):
            logger.error(f"Public key is not ECDSA: {type(public_key_obj)}")
            return False
        
        # Decode base64 signature
        import base64
        try:
            signature_bytes = base64.b64decode(signature)
        except Exception as e:
            logger.error(f"Failed to decode signature: {e}")
            return False
        
        # Parse ECDSA signature
        # SendGrid uses DER-encoded ECDSA signatures (most common format)
        # Signature format: DER-encoded sequence containing r and s integers
        try:
            from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
            # Decode DER-encoded signature
            r, s = decode_dss_signature(signature_bytes)
        except ValueError:
            # If DER format fails, try raw format (64 bytes: 32 for r, 32 for s)
            # This is a fallback for non-standard formats
            if len(signature_bytes) == 64:
                try:
                    r = int.from_bytes(signature_bytes[:32], 'big')
                    s = int.from_bytes(signature_bytes[32:], 'big')
                except Exception as e:
                    logger.error(f"Failed to parse raw signature format: {e}")
                    return False
            else:
                logger.error(
                    f"Invalid signature format. Expected DER-encoded or 64-byte raw format, "
                    f"got {len(signature_bytes)} bytes"
                )
                return False
        except Exception as e:
            logger.error(f"Failed to parse signature: {e}")
            return False
        
        # Create concatenated data: timestamp + payload
        timestamp_bytes = timestamp.encode('utf-8')
        data_to_verify = timestamp_bytes + payload
        
        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(data_to_verify)
        digest = hash_obj.digest()
        
        # Verify signature
        try:
            public_key_obj.verify(
                encode_dss_signature(r, s),
                digest,
                ec.ECDSA(hashes.SHA256())
            )
            logger.info(f"Webhook signature verified successfully. Timestamp: {timestamp}")
            return True
        except InvalidSignature:
            logger.warning("Webhook signature verification failed: Invalid signature")
            return False
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error during signature verification: {e}", exc_info=True)
        return False

