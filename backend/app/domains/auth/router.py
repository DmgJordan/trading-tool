"""
Router pour le domaine auth - Endpoints d'authentification

✅ OPTIMISATION : Router mince qui délègue toute la logique au service
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from .schemas import UserRegister, UserLogin, Token, TokenRefresh, UserAuthResponse
from .service import AuthService
from ...core import get_db, get_current_user
from .models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Inscription utilisateur avec système hybride :
    - Access token retourné dans JSON (localStorage client)
    - Refresh token stocké dans cookie HttpOnly (sécurité SSR)
    """
    return AuthService.register(db, user_data, response)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authentification utilisateur avec système hybride :
    - Access token retourné dans JSON (localStorage client)
    - Refresh token stocké dans cookie HttpOnly (sécurité SSR)
    """
    return AuthService.login(db, credentials, response)


@router.post("/refresh", response_model=Token)
async def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    token_data: TokenRefresh = None
):
    """
    Rafraîchit les tokens JWT avec système hybride :
    - Accepte refresh_token depuis cookie HttpOnly OU body JSON
    - Priorité au cookie pour sécurité SSR
    - Retourne nouveaux access + refresh tokens
    """
    # Priorité au cookie HttpOnly (sécurité SSR)
    refresh_token_value = request.cookies.get("refresh_token")

    # Fallback au body si pas de cookie (compatibilité)
    if not refresh_token_value and token_data:
        refresh_token_value = token_data.refresh_token

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing (cookie or body required)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return AuthService.refresh_tokens(refresh_token_value, response, db)
    except HTTPException as e:
        # Supprimer cookie invalide si présent
        if request.cookies.get("refresh_token"):
            response.delete_cookie(key="refresh_token", path="/")
        raise e


@router.post("/logout")
async def logout(response: Response):
    """
    Déconnexion utilisateur avec système hybride :
    - Supprime le cookie refresh_token HttpOnly
    - Le client doit également supprimer localStorage (géré côté frontend)

    Note : Dans une implémentation complète avec blacklist, on ajouterait
    les tokens révoqués en base/cache (Redis) pour invalidation immédiate.
    """
    return AuthService.logout(response)


@router.get("/me", response_model=UserAuthResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Récupère les informations d'authentification de l'utilisateur actuel

    ✅ OPTIMISATION : Retourne uniquement les infos d'identité (pas les clés API)
    Les informations de profil complet sont disponibles sur GET /users/me
    """
    return UserAuthResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username
    )
