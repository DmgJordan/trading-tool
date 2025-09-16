from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging

from ..database import get_db
from ..models.user import User
from ..models.user_preferences import UserTradingPreferences
from ..schemas.user_preferences import (
    UserTradingPreferencesResponse,
    UserTradingPreferencesCreate,
    UserTradingPreferencesUpdate,
    UserTradingPreferencesDefault
)
from ..auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users/me/preferences", tags=["user-preferences"])

def _serialize_preferences_for_db(preferences_data: dict) -> dict:
    """Sérialise les données de préférences pour le stockage en base"""
    serialized = preferences_data.copy()

    # Convertir les listes en JSON strings pour le stockage
    if 'preferred_assets' in serialized and isinstance(serialized['preferred_assets'], list):
        serialized['preferred_assets'] = json.dumps(serialized['preferred_assets'])

    if 'technical_indicators' in serialized and isinstance(serialized['technical_indicators'], list):
        serialized['technical_indicators'] = json.dumps(serialized['technical_indicators'])

    return serialized

def _create_default_preferences(db: Session, user: User) -> UserTradingPreferences:
    """Crée des préférences par défaut pour un utilisateur"""
    try:
        default_data = UserTradingPreferencesDefault()

        db_preferences = UserTradingPreferences(
            user_id=user.id,
            risk_tolerance=default_data.risk_tolerance,
            investment_horizon=default_data.investment_horizon,
            trading_style=default_data.trading_style,
            max_position_size=default_data.max_position_size,
            stop_loss_percentage=default_data.stop_loss_percentage,
            take_profit_ratio=default_data.take_profit_ratio,
            preferred_assets=json.dumps(default_data.preferred_assets),
            technical_indicators=json.dumps(default_data.technical_indicators)
        )

        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)

        logger.info(f"Préférences par défaut créées pour l'utilisateur {user.id}")
        return db_preferences

    except Exception as e:
        logger.error(f"Erreur création préférences par défaut pour utilisateur {user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création des préférences par défaut"
        )

@router.get("/", response_model=UserTradingPreferencesResponse)
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les préférences de trading de l'utilisateur actuel.
    Si l'utilisateur n'a pas de préférences, retourne les valeurs par défaut.
    """
    try:
        # Chercher les préférences existantes
        db_preferences = db.query(UserTradingPreferences).filter(
            UserTradingPreferences.user_id == current_user.id
        ).first()

        if not db_preferences:
            # Créer automatiquement des préférences par défaut
            db_preferences = _create_default_preferences(db, current_user)

        return UserTradingPreferencesResponse.from_db_model(db_preferences)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération préférences utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des préférences"
        )

@router.put("/", response_model=UserTradingPreferencesResponse)
def update_user_preferences(
    preferences_update: UserTradingPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour les préférences de trading de l'utilisateur actuel.
    Crée automatiquement les préférences si elles n'existent pas.
    """
    try:
        # Chercher les préférences existantes
        db_preferences = db.query(UserTradingPreferences).filter(
            UserTradingPreferences.user_id == current_user.id
        ).first()

        if not db_preferences:
            # Créer d'abord des préférences par défaut
            db_preferences = _create_default_preferences(db, current_user)

        # Mettre à jour les champs fournis
        update_data = preferences_update.model_dump(exclude_unset=True)

        if update_data:
            serialized_data = _serialize_preferences_for_db(update_data)

            for field, value in serialized_data.items():
                if hasattr(db_preferences, field):
                    setattr(db_preferences, field, value)

            db.commit()
            db.refresh(db_preferences)

            logger.info(f"Préférences mises à jour pour l'utilisateur {current_user.id}: {list(update_data.keys())}")

        return UserTradingPreferencesResponse.from_db_model(db_preferences)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour préférences utilisateur {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour des préférences"
        )

@router.post("/", response_model=UserTradingPreferencesResponse)
def create_user_preferences(
    preferences_create: UserTradingPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée ou remplace complètement les préférences de trading de l'utilisateur actuel.
    """
    try:
        # Vérifier si des préférences existent déjà
        existing_preferences = db.query(UserTradingPreferences).filter(
            UserTradingPreferences.user_id == current_user.id
        ).first()

        if existing_preferences:
            # Supprimer les anciennes préférences
            db.delete(existing_preferences)

        # Créer les nouvelles préférences
        preferences_data = preferences_create.model_dump()
        serialized_data = _serialize_preferences_for_db(preferences_data)

        db_preferences = UserTradingPreferences(
            user_id=current_user.id,
            **serialized_data
        )

        db.add(db_preferences)
        db.commit()
        db.refresh(db_preferences)

        logger.info(f"Nouvelles préférences créées pour l'utilisateur {current_user.id}")
        return UserTradingPreferencesResponse.from_db_model(db_preferences)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur création préférences utilisateur {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création des préférences"
        )

@router.delete("/")
def reset_user_preferences_to_default(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remet les préférences de trading de l'utilisateur aux valeurs par défaut.
    """
    try:
        # Supprimer les préférences existantes
        existing_preferences = db.query(UserTradingPreferences).filter(
            UserTradingPreferences.user_id == current_user.id
        ).first()

        if existing_preferences:
            db.delete(existing_preferences)

        # Créer de nouvelles préférences par défaut
        db_preferences = _create_default_preferences(db, current_user)

        logger.info(f"Préférences réinitialisées pour l'utilisateur {current_user.id}")
        return {
            "status": "success",
            "message": "Préférences réinitialisées aux valeurs par défaut",
            "preferences": UserTradingPreferencesResponse.from_db_model(db_preferences)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur réinitialisation préférences utilisateur {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la réinitialisation des préférences"
        )

@router.get("/default", response_model=UserTradingPreferencesDefault)
def get_default_preferences():
    """
    Récupère les valeurs par défaut des préférences de trading.
    Utile pour l'interface utilisateur.
    """
    return UserTradingPreferencesDefault()

@router.get("/validation-info")
def get_preferences_validation_info():
    """
    Récupère les informations de validation pour les préférences.
    Utile pour l'interface utilisateur pour afficher les contraintes.
    """
    return {
        "risk_tolerance_options": ["LOW", "MEDIUM", "HIGH"],
        "investment_horizon_options": ["SHORT_TERM", "MEDIUM_TERM", "LONG_TERM"],
        "trading_style_options": ["CONSERVATIVE", "BALANCED", "AGGRESSIVE"],
        "constraints": {
            "max_position_size": {"min": 0.1, "max": 100.0, "unit": "%"},
            "stop_loss_percentage": {"min": 0.1, "max": 50.0, "unit": "%"},
            "take_profit_ratio": {"min": 0.1, "max": 10.0, "unit": "ratio"},
            "preferred_assets": {"max_items": 20},
            "technical_indicators": {"max_items": 15}
        },
        "supported_technical_indicators": [
            "RSI", "MACD", "SMA", "EMA", "BB", "STOCH", "ADX", "CCI", "ROC",
            "WILLIAMS", "ATR", "VWAP", "OBV", "TRIX", "CHAIKIN"
        ]
    }