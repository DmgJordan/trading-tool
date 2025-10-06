"""
Router pour la gestion des profils IA utilisateur
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import logging

from ...core import get_db, get_current_user
from ...domains.auth.models import User

from .schemas import (
    AIProfileCreate,
    AIProfileUpdate,
    AIProfileResponse,
    AIProfileValidationInfo,
)
from .service import AIProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-profile", tags=["ai-profile"])

# Instance du service (singleton)
ai_profile_service = AIProfileService()


@router.get("/me", response_model=AIProfileResponse)
async def get_my_ai_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère le profil IA de l'utilisateur actuel

    Crée automatiquement un profil avec valeurs par défaut si inexistant.
    """
    try:
        logger.info(f"Récupération profil IA pour utilisateur {current_user.id}")

        profile = ai_profile_service.get_or_create_profile(current_user.id, db)

        return AIProfileResponse.from_orm(profile)

    except Exception as e:
        logger.error(f"Erreur récupération profil IA utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du profil IA"
        )


@router.put("/me", response_model=AIProfileResponse)
async def update_my_ai_profile(
    profile_data: AIProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour le profil IA de l'utilisateur actuel

    Crée automatiquement un profil si inexistant avant de le mettre à jour.
    """
    try:
        logger.info(f"Mise à jour profil IA pour utilisateur {current_user.id}")

        # S'assurer que le profil existe
        ai_profile_service.get_or_create_profile(current_user.id, db)

        # Mettre à jour le profil
        updated_profile = ai_profile_service.update_profile(
            current_user.id,
            profile_data,
            db
        )

        logger.info(f"Profil IA mis à jour avec succès pour utilisateur {current_user.id}")

        return AIProfileResponse.from_orm(updated_profile)

    except ValueError as ve:
        logger.warning(f"Erreur métier mise à jour profil IA utilisateur {current_user.id}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour profil IA utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du profil IA"
        )


@router.post("/me", response_model=AIProfileResponse)
async def create_my_ai_profile(
    profile_data: AIProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un profil IA pour l'utilisateur actuel

    Erreur si un profil existe déjà. Utilisez PUT /me pour mettre à jour.
    """
    try:
        logger.info(f"Création profil IA pour utilisateur {current_user.id}")

        profile = ai_profile_service.create_profile(
            current_user.id,
            profile_data,
            db
        )

        logger.info(f"Profil IA créé avec succès pour utilisateur {current_user.id}")

        return AIProfileResponse.from_orm(profile)

    except ValueError as ve:
        logger.warning(f"Erreur création profil IA utilisateur {current_user.id}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as e:
        logger.error(f"Erreur création profil IA utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du profil IA"
        )


@router.delete("/me")
async def reset_my_ai_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset le profil IA de l'utilisateur aux valeurs par défaut

    Supprime le profil existant et en crée un nouveau avec valeurs par défaut.
    """
    try:
        logger.info(f"Reset profil IA pour utilisateur {current_user.id}")

        profile = ai_profile_service.reset_to_defaults(current_user.id, db)

        logger.info(f"Profil IA reset avec succès pour utilisateur {current_user.id}")

        return {
            "message": "Profil IA reset aux valeurs par défaut",
            "profile": AIProfileResponse.from_orm(profile)
        }

    except Exception as e:
        logger.error(f"Erreur reset profil IA utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du reset du profil IA"
        )


@router.get("/validation-info", response_model=AIProfileValidationInfo)
async def get_validation_info():
    """
    Retourne les informations de validation pour le profil IA

    Utile pour construire l'interface utilisateur avec les bonnes contraintes.
    """
    return AIProfileValidationInfo()


@router.get("/default")
async def get_default_values():
    """
    Retourne les valeurs par défaut pour un profil IA

    Utile pour pré-remplir les formulaires.
    """
    from .models import AIProfile

    return {
        "default_values": AIProfile.get_default_values(),
        "description": "Valeurs par défaut utilisées lors de la création d'un profil"
    }
