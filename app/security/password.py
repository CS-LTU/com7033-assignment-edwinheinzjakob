"""
Password hashing and verification using Argon2
"""
import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import logging

logger = logging.getLogger(__name__)

class PasswordService:
    """Service for password hashing and verification"""
    
    def __init__(self):
        # Use Argon2id (recommended for password hashing)
        self.hasher = PasswordHasher(
            time_cost=2,          # Number of iterations
            memory_cost=65536,    # Memory usage in KB (64MB)
            parallelism=2,       # Number of parallel threads
            hash_len=32,         # Hash length
            salt_len=16          # Salt length
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            return self.hasher.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {str(e)}")
            raise
    
    def verify_password(self, password_hash: str, password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password_hash: Hashed password
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False
        except (InvalidHashError, Exception) as e:
            logger.warning(f"Password verification error: {str(e)}")
            return False
    
    def check_needs_rehash(self, password_hash: str) -> bool:
        """
        Check if password hash needs rehashing (e.g., after algorithm upgrade)
        
        Args:
            password_hash: Hashed password
            
        Returns:
            True if rehashing is needed
        """
        try:
            return self.hasher.check_needs_rehash(password_hash)
        except Exception as e:
            logger.warning(f"Error checking rehash: {str(e)}")
            return False

# Global instance
password_service = PasswordService()

