"""
Field-level encryption for sensitive data in MongoDB
"""

import base64
import logging
import os

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncryptionService:
    """Service for encrypting/decrypting sensitive fields"""

    def __init__(self, key=None):
        """
        Initialize encryption service

        Args:
            key: Encryption key (Fernet key). If None, generates or loads from env
        """
        if key is None:
            key = os.environ.get("ENCRYPTION_KEY")
            if key:
                # Key is base64-encoded string
                self.key = key.encode()
            else:
                # Generate new key (only for development)
                logger.warning(
                    "No encryption key found. Generating new key for development."
                )
                self.key = Fernet.generate_key()
                logger.warning(f"Generated key: {self.key.decode()}")
        else:
            self.key = key.encode() if isinstance(key, str) else key

        self.cipher = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        """
        Encrypt sensitive data

        Args:
            data: Plain text data to encrypt

        Returns:
            Encrypted data (base64 encoded)
        """
        if not data:
            return data
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data

        Args:
            encrypted_data: Encrypted data (base64 encoded)

        Returns:
            Decrypted plain text data
        """
        if not encrypted_data:
            return encrypted_data
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key

        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()


# Global instance (will be initialized with app config)
encryption_service = None


def init_encryption_service(key=None):
    """Initialize global encryption service"""
    global encryption_service
    encryption_service = EncryptionService(key)
    return encryption_service
