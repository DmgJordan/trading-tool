from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas.user import UserCreate, UserResponse, UserUpdate, ApiKeyUpdate, ApiKeyTest
from ..auth import get_current_user, get_password_hash, encrypt_api_key, decrypt_api_key


def _normalize_hyperliquid_address(address: str | None) -> str | None:
    if address is None:
        return None

    normalized = address.strip()
    if not normalized:
        return None

    if not normalized.startswith("0x") or len(normalized) != 42:
        raise HTTPException(
            status_code=400,
            detail="Adresse publique Hyperliquid invalide. Elle doit commencer par 0x et contenir 42 caractères."
        )

    try:
        int(normalized[2:], 16)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Adresse publique Hyperliquid invalide. Elle doit contenir uniquement des caractères hexadécimaux."
        )

    return normalized.lower()

router = APIRouter(prefix="/users", tags=["users"])

def _mask_api_keys_in_response(current_user: User) -> UserResponse:
    """Utilitaire pour masquer les clés API dans la réponse"""
    user_data = UserResponse.model_validate(current_user)

    # Masquer la clé Hyperliquid
    if current_user.hyperliquid_api_key:
        user_data.hyperliquid_api_key = "••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••"
        user_data.hyperliquid_api_key_status = "configured"
    else:
        user_data.hyperliquid_api_key = None
        user_data.hyperliquid_api_key_status = None

    # Masquer la clé Anthropic
    if current_user.anthropic_api_key:
        user_data.anthropic_api_key = "sk-ant-••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••"
        user_data.anthropic_api_key_status = "configured"
    else:
        user_data.anthropic_api_key = None
        user_data.anthropic_api_key_status = None

    # Masquer la clé CoinGecko
    if current_user.coingecko_api_key:
        user_data.coingecko_api_key = "CG-••••••••••••••••••••••••••••••••••••••"
        user_data.coingecko_api_key_status = "configured"
    else:
        user_data.coingecko_api_key = None
        user_data.coingecko_api_key_status = None

    return user_data

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return _mask_api_keys_in_response(current_user)

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mettre à jour les champs fournis
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "hyperliquid_public_address":
            setattr(current_user, field, _normalize_hyperliquid_address(value))
        elif field in ["hyperliquid_api_key", "anthropic_api_key", "coingecko_api_key"]:
            if value:
                encrypted_value = encrypt_api_key(value)
                setattr(current_user, field, encrypted_value)
            elif value is None:
                setattr(current_user, field, None)
        else:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return _mask_api_keys_in_response(current_user)

@router.put("/me/api-keys", response_model=UserResponse)
def update_user_api_keys(
    api_keys: ApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mettre à jour uniquement les clés API fournies
    update_data = api_keys.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "hyperliquid_public_address":
            setattr(current_user, field, _normalize_hyperliquid_address(value))
        elif field in ["hyperliquid_api_key", "anthropic_api_key", "coingecko_api_key"]:
            if value:
                encrypted_value = encrypt_api_key(value)
                setattr(current_user, field, encrypted_value)
            elif value is None:
                setattr(current_user, field, None)
        
    db.commit()
    db.refresh(current_user)

    return _mask_api_keys_in_response(current_user)
