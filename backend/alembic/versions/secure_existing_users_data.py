"""Secure existing user data by hashing passwords and encrypting API keys

Revision ID: secure_existing_data
Revises: 53f1744da98d
Create Date: 2025-09-14 22:45:00.000000

"""
from typing import Sequence, Union
import base64
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from cryptography.fernet import Fernet
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = 'secure_existing_data'
down_revision: Union[str, Sequence[str], None] = '53f1744da98d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def get_encryption_key():
    """Get encryption key for API keys"""
    encryption_key = "your-encryption-key-32-chars-long"  # Should match config.py
    key = encryption_key.encode()
    if len(key) != 32:
        key = base64.urlsafe_b64encode(key.ljust(32)[:32])
    else:
        key = base64.urlsafe_b64encode(key)
    return key

def upgrade() -> None:
    """Secure existing user data"""
    # Setup encryption and password hashing
    cipher_suite = Fernet(get_encryption_key())
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    connection = op.get_bind()

    # Get all existing users
    result = connection.execute(text("SELECT id, hashed_password, hyperliquid_api_key, anthropic_api_key FROM users"))
    users = result.fetchall()

    for user in users:
        user_id, current_password, hyperliquid_key, anthropic_key = user

        # Hash password if it's not already hashed (bcrypt hashes start with $2b$)
        if current_password and not current_password.startswith('$2b$'):
            hashed_password = pwd_context.hash(current_password)
            connection.execute(
                text("UPDATE users SET hashed_password = :hashed_password WHERE id = :user_id"),
                {"hashed_password": hashed_password, "user_id": user_id}
            )

        # Encrypt API keys if they exist and are not already encrypted
        if hyperliquid_key:
            try:
                # Try to decrypt - if it fails, it's probably not encrypted
                cipher_suite.decrypt(hyperliquid_key.encode())
            except:
                # Not encrypted, so encrypt it
                encrypted_key = cipher_suite.encrypt(hyperliquid_key.encode()).decode()
                connection.execute(
                    text("UPDATE users SET hyperliquid_api_key = :encrypted_key WHERE id = :user_id"),
                    {"encrypted_key": encrypted_key, "user_id": user_id}
                )

        if anthropic_key:
            try:
                # Try to decrypt - if it fails, it's probably not encrypted
                cipher_suite.decrypt(anthropic_key.encode())
            except:
                # Not encrypted, so encrypt it
                encrypted_key = cipher_suite.encrypt(anthropic_key.encode()).decode()
                connection.execute(
                    text("UPDATE users SET anthropic_api_key = :encrypted_key WHERE id = :user_id"),
                    {"encrypted_key": encrypted_key, "user_id": user_id}
                )

def downgrade() -> None:
    """Downgrade is not supported for security reasons"""
    pass