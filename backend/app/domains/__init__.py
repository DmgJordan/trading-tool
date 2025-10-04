"""
Module domains - Organisation par domaines métier (DDD)
Contient les domaines auth et users avec leurs models, schemas, services et routers
"""

from .auth import router as auth_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "users_router",
]
