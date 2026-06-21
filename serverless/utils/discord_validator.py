"""
Discord Interaction Validator

Validates HTTP requests from Discord using Ed25519 signature verification.
Required for security - ensures requests actually come from Discord.
"""

import hmac
import hashlib
from typing import Optional


class DiscordValidator:
    """Validates Discord interaction requests using Ed25519 signature."""

    def __init__(self, public_key: str):
        """
        Initialize with Discord bot's PUBLIC_KEY from Developer Portal.
        
        Args:
            public_key: Discord app's PUBLIC_KEY
        """
        self.public_key = public_key

    def is_valid_request(
        self, signature: str, timestamp: str, body: str
    ) -> bool:
        """
        Validate Discord interaction request signature.

        Args:
            signature: X-Signature-Ed25519 header value
            timestamp: X-Signature-Timestamp header value
            body: Raw request body (as string)

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Ed25519 verification using nacl library
            import nacl.signing
            import nacl.exceptions

            # Message to verify is timestamp + body
            message = timestamp.encode() + body.encode()

            # Public key (convert hex string to bytes)
            verify_key = nacl.signing.VerifyKey(
                bytes.fromhex(self.public_key)
            )

            # Signature (convert hex string to bytes)
            sig_bytes = bytes.fromhex(signature)

            # Verify
            verify_key.verify(message, sig_bytes)
            return True
        except (nacl.exceptions.BadSignatureError, ValueError, TypeError):
            return False


def get_discord_validator(public_key: str) -> DiscordValidator:
    """Factory function to create validator."""
    return DiscordValidator(public_key)
