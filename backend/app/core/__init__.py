"""
Core module - Architecture DDD simplifiée
Contient les composants fondamentaux de l'application
"""

# Configuration
from .config import Settings, settings

# Database
from .database import Base, engine, SessionLocal

# Security
from .security import (
    verify_password,
    get_password_hash,
    encrypt_api_key,
    decrypt_api_key,
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_user,
)

# Exceptions
from .exceptions import (
    AppException,
    UnauthorizedException,
    NotFoundException,
    ForbiddenException,
    ValidationException,
)

# Dependencies
from .deps import get_db, get_current_user

__all__ = [
    # Configuration
    "Settings",
    "settings",
    # Database
    "Base",
    "engine",
    "SessionLocal",
    # Security
    "verify_password",
    "get_password_hash",
    "encrypt_api_key",
    "decrypt_api_key",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "authenticate_user",
    # Exceptions
    "AppException",
    "UnauthorizedException",
    "NotFoundException",
    "ForbiddenException",
    "ValidationException",
    # Dependencies
    "get_db",
    "get_current_user",
]
