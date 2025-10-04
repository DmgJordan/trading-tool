"""
Schémas Pydantic pour le domaine auth - Authentification et tokens JWT
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserLogin(BaseModel):
    """Schéma pour la connexion utilisateur"""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """Schéma pour l'inscription utilisateur"""
    email: EmailStr
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Valide que le username a une longueur minimale"""
        if len(v) < 3:
            raise ValueError('Le nom d\'utilisateur doit contenir au moins 3 caractères')
        if len(v) > 50:
            raise ValueError('Le nom d\'utilisateur ne peut pas dépasser 50 caractères')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valide que le mot de passe respecte les critères de sécurité"""
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        return v


class Token(BaseModel):
    """Schéma pour la réponse de connexion avec tokens JWT"""
    access_token: str
    refresh_token: Optional[str] = None  # Optionnel car peut être dans cookie HttpOnly
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schéma pour le refresh d'un token"""
    refresh_token: str


class UserAuthResponse(BaseModel):
    """Schéma pour les informations utilisateur après authentification"""
    id: int
    email: EmailStr
    username: str

    class Config:
        from_attributes = True
