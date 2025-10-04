from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from ..core import (
    get_db,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_token,
    get_current_user,
    encrypt_api_key,
    decrypt_api_key
)
from ..models.user import User
from ..schemas.auth import UserLogin, UserRegister, Token, TokenRefresh, UserProfile

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
    hashed_password = get_password_hash(user_data.password)

    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Créer les tokens
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    # ✅ NOUVEAU : Stocker refresh_token dans cookie HttpOnly
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,            # TODO: True en production (HTTPS uniquement)
        samesite="lax",
        max_age=7*24*60*60,      # 7 jours
        path="/",
    )

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authentification utilisateur avec système hybride :
    - Access token retourné dans JSON (localStorage client)
    - Refresh token stocké dans cookie HttpOnly (sécurité SSR)
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Créer les tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # ✅ NOUVEAU : Stocker refresh_token dans cookie HttpOnly
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,           # Protection XSS (pas accessible JS)
        secure=False,            # TODO: True en production (HTTPS uniquement)
        samesite="lax",          # Protection CSRF
        max_age=7*24*60*60,      # 7 jours (même durée que refresh token)
        path="/",                # Disponible pour toutes les routes
    )

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    token_data: TokenRefresh | None = None
):
    """
    Rafraîchissement des tokens avec système hybride :

    Priorité de lecture refresh_token :
    1. Cookie HttpOnly (recommandé, sécurisé)
    2. Body JSON (fallback pour compatibilité mobile/anciens clients)

    Le nouveau refresh_token est automatiquement mis à jour dans le cookie.
    """
    # 1. Essayer de lire depuis cookie (priorité)
    refresh_token_value = request.cookies.get("refresh_token")

    # 2. Fallback : lire depuis body JSON si cookie absent
    if not refresh_token_value and token_data:
        refresh_token_value = token_data.refresh_token

    # 3. Erreur si aucune source disponible
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing (cookie or body required)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier le refresh token
    try:
        token_payload = verify_token(refresh_token_value, "refresh")
    except HTTPException:
        # Supprimer cookie invalide si présent
        if request.cookies.get("refresh_token"):
            response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier que l'utilisateur existe toujours
    user = db.query(User).filter(User.id == token_payload["user_id"]).first()
    if not user:
        # Supprimer cookie si utilisateur n'existe plus
        if request.cookies.get("refresh_token"):
            response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Créer de nouveaux tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # ✅ NOUVEAU : Mettre à jour cookie avec nouveau refresh_token
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,            # TODO: True en production
        samesite="lax",
        max_age=7*24*60*60,      # 7 jours
        path="/",
    )

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    # Déchiffrer les clés API pour l'utilisateur
    hyperliquid_key = decrypt_api_key(current_user.hyperliquid_api_key) if current_user.hyperliquid_api_key else None
    anthropic_key = decrypt_api_key(current_user.anthropic_api_key) if current_user.anthropic_api_key else None

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        hyperliquid_api_key=hyperliquid_key,
        hyperliquid_public_address=current_user.hyperliquid_public_address,
        anthropic_api_key=anthropic_key
    )

@router.post("/logout")
async def logout(response: Response):
    """
    Déconnexion utilisateur avec système hybride :
    - Supprime le cookie refresh_token HttpOnly
    - Le client doit également supprimer localStorage (géré côté frontend)

    Note : Dans une implémentation complète avec blacklist, on ajouterait
    les tokens révoqués en base/cache (Redis) pour invalidation immédiate.
    """
    # Supprimer le cookie refresh_token
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax"
    )

    return {"message": "Successfully logged out"}
