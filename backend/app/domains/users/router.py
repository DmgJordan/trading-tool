"""
Router pour le domaine users - Endpoints des profils et préférences

✅ OPTIMISATION : Router mince qui délègue toute la logique aux services
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .schemas import (
    UserProfileUpdate, ApiKeyUpdate, UserProfileResponse,
    UserTradingPreferencesCreate, UserTradingPreferencesUpdate,
    UserTradingPreferencesResponse, UserTradingPreferencesDefault
)
from .service import UserService, PreferencesService
from ..auth.models import User
from ...core import get_db, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


# ========== Endpoints Profil Utilisateur ==========

@router.get("/me", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère le profil complet de l'utilisateur actuel

    ✅ SÉCURITÉ : Les clés API sont automatiquement masquées
    """
    return UserService.get_profile_response(db, current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour le profil utilisateur (email, username)
    """
    return UserService.update_profile(db, current_user, profile_update)


@router.put("/me/api-keys", response_model=UserProfileResponse)
async def update_api_keys(
    api_keys: ApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour les clés API de l'utilisateur

    ✅ OPTIMISATION : Utilise la méthode unifiée du service
    """
    return UserService.update_api_keys(db, current_user, api_keys)


# ========== Endpoints Préférences de Trading ==========

@router.get("/me/preferences", response_model=UserTradingPreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les préférences de trading de l'utilisateur actuel.
    Si l'utilisateur n'a pas de préférences, retourne les valeurs par défaut.
    """
    return PreferencesService.get_preferences(db, current_user)


@router.post("/me/preferences", response_model=UserTradingPreferencesResponse)
async def create_preferences(
    preferences_data: UserTradingPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée de nouvelles préférences de trading pour l'utilisateur actuel.
    Retourne une erreur si des préférences existent déjà (utiliser PUT pour mettre à jour).
    """
    return PreferencesService.create_preferences(db, current_user, preferences_data)


@router.put("/me/preferences", response_model=UserTradingPreferencesResponse)
async def update_preferences(
    preferences_update: UserTradingPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour les préférences de trading de l'utilisateur actuel.
    Crée des préférences par défaut si elles n'existent pas.
    """
    return PreferencesService.update_preferences(db, current_user, preferences_update)


@router.delete("/me/preferences")
async def delete_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime les préférences de trading de l'utilisateur actuel.
    Retourne les préférences aux valeurs par défaut lors du prochain accès.
    """
    return PreferencesService.delete_preferences(db, current_user)


@router.get("/me/preferences/default", response_model=UserTradingPreferencesDefault)
async def get_default_preferences():
    """
    Retourne les valeurs par défaut des préférences de trading.
    Utile pour afficher les valeurs par défaut dans l'interface utilisateur.
    """
    return PreferencesService.get_default_preferences()
