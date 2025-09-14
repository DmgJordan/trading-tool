from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from ..auth import get_current_user, get_password_hash, encrypt_api_key, decrypt_api_key

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    # Déchiffrer les clés API avant de les retourner
    hyperliquid_key = decrypt_api_key(current_user.hyperliquid_api_key) if current_user.hyperliquid_api_key else None
    anthropic_key = decrypt_api_key(current_user.anthropic_api_key) if current_user.anthropic_api_key else None

    # Créer une copie pour éviter de modifier l'objet original
    user_data = UserResponse.model_validate(current_user)
    user_data.hyperliquid_api_key = hyperliquid_key
    user_data.anthropic_api_key = anthropic_key

    return user_data

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mettre à jour les champs fournis
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field in ["hyperliquid_api_key", "anthropic_api_key"] and value:
            # Chiffrer les clés API
            encrypted_value = encrypt_api_key(value)
            setattr(current_user, field, encrypted_value)
        else:
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    # Retourner les données déchiffrées
    hyperliquid_key = decrypt_api_key(current_user.hyperliquid_api_key) if current_user.hyperliquid_api_key else None
    anthropic_key = decrypt_api_key(current_user.anthropic_api_key) if current_user.anthropic_api_key else None

    user_data = UserResponse.model_validate(current_user)
    user_data.hyperliquid_api_key = hyperliquid_key
    user_data.anthropic_api_key = anthropic_key

    return user_data