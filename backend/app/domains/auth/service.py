"""
Service pour le domaine auth - Logique métier de l'authentification
"""

from datetime import timedelta
from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional

from .models import User
from .schemas import UserRegister, UserLogin, Token
from ...core import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    settings
)


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """
    Helper pour configurer le cookie refresh_token HttpOnly

    ✅ OPTIMISATION : Élimine la duplication de code (3× dans routes/auth.py)

    Args:
        response: Objet Response FastAPI
        refresh_token: Token de rafraîchissement à stocker
    """
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # TODO: True en production (HTTPS uniquement)
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 jours
        path="/",
    )


def clear_refresh_token_cookie(response: Response) -> None:
    """
    Helper pour supprimer le cookie refresh_token lors de la déconnexion

    Args:
        response: Objet Response FastAPI
    """
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        samesite="lax"
    )


class AuthService:
    """Service de gestion de l'authentification"""

    @staticmethod
    def register(db: Session, user_data: UserRegister, response: Response) -> Token:
        """
        Inscription d'un nouvel utilisateur

        Args:
            db: Session de base de données
            user_data: Données d'inscription
            response: Objet Response pour les cookies

        Returns:
            Token: Access et refresh tokens

        Raises:
            HTTPException: Si l'email ou le username existe déjà
        """
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()

        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Créer le nouvel utilisateur
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Créer les tokens
        access_token = create_access_token(data={"sub": str(db_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

        # Stocker refresh_token dans cookie HttpOnly
        set_refresh_token_cookie(response, refresh_token)

        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Authentifie un utilisateur par email et mot de passe

        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            password: Mot de passe en clair

        Returns:
            User: Utilisateur authentifié

        Raises:
            HTTPException: Si les credentials sont incorrects
        """
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @staticmethod
    def login(db: Session, credentials: UserLogin, response: Response) -> Token:
        """
        Connexion d'un utilisateur

        Args:
            db: Session de base de données
            credentials: Credentials de connexion
            response: Objet Response pour les cookies

        Returns:
            Token: Access et refresh tokens
        """
        # Authentifier l'utilisateur
        user = AuthService.authenticate_user(db, credentials.email, credentials.password)

        # Créer les tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Stocker refresh_token dans cookie HttpOnly
        set_refresh_token_cookie(response, refresh_token)

        return Token(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def refresh_tokens(refresh_token: str, response: Response, db: Session) -> Token:
        """
        Rafraîchit les tokens d'accès

        Args:
            refresh_token: Token de rafraîchissement
            response: Objet Response pour les cookies
            db: Session de base de données

        Returns:
            Token: Nouveaux access et refresh tokens

        Raises:
            HTTPException: Si le token est invalide ou expiré
        """
        try:
            # Vérifier le refresh token (type="refresh" pour refresh tokens)
            payload = verify_token(refresh_token, token_type="refresh")

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            user_id = payload.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )

            # Vérifier que l'utilisateur existe toujours
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            # Créer de nouveaux tokens
            new_access_token = create_access_token(data={"sub": str(user_id)})
            new_refresh_token = create_refresh_token(data={"sub": str(user_id)})

            # Stocker le nouveau refresh_token dans cookie HttpOnly
            set_refresh_token_cookie(response, new_refresh_token)

            return Token(access_token=new_access_token, refresh_token=new_refresh_token)
        except HTTPException:
            # Re-raise les HTTPException (déjà avec le bon status code)
            raise
        except Exception as e:
            # Toute autre erreur → 401
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token refresh failed: {str(e)}"
            )

    @staticmethod
    def logout(response: Response) -> dict:
        """
        Déconnexion de l'utilisateur

        Args:
            response: Objet Response pour supprimer les cookies

        Returns:
            dict: Message de confirmation
        """
        # Supprimer le cookie refresh_token
        clear_refresh_token_cookie(response)

        return {"message": "Successfully logged out"}
