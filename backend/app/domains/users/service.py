"""
Service pour le domaine users - Logique métier des profils et préférences
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import logging

from .models import UserProfile, UserTradingPreferences
from .schemas import (
    UserProfileUpdate, ApiKeyUpdate, UserProfileResponse,
    UserTradingPreferencesCreate, UserTradingPreferencesUpdate,
    UserTradingPreferencesResponse, UserTradingPreferencesDefault
)
from ..auth.models import User
from ...core import encrypt_api_key

logger = logging.getLogger(__name__)


# ========== Helpers ==========

def _normalize_hyperliquid_address(address: Optional[str]) -> Optional[str]:
    """
    Normalise et valide une adresse publique Hyperliquid

    Args:
        address: Adresse à normaliser

    Returns:
        Adresse normalisée en lowercase ou None

    Raises:
        HTTPException: Si l'adresse est invalide
    """
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


def _serialize_preferences_for_db(preferences_data: dict) -> dict:
    """
    Sérialise les données de préférences pour le stockage en base

    Convertit les listes Python en JSON strings pour SQLAlchemy

    Args:
        preferences_data: Dictionnaire des préférences

    Returns:
        Dictionnaire sérialisé pour la base de données
    """
    serialized = preferences_data.copy()

    # Convertir les listes en JSON strings pour le stockage
    if 'preferred_assets' in serialized and isinstance(serialized['preferred_assets'], list):
        serialized['preferred_assets'] = json.dumps(serialized['preferred_assets'])

    if 'technical_indicators' in serialized and isinstance(serialized['technical_indicators'], list):
        serialized['technical_indicators'] = json.dumps(serialized['technical_indicators'])

    return serialized


# ========== Service UserProfile ==========

class UserService:
    """Service de gestion des profils utilisateurs"""

    @staticmethod
    def get_or_create_profile(db: Session, user: User) -> UserProfile:
        """
        Récupère ou crée le profil utilisateur

        Args:
            db: Session de base de données
            user: Instance du modèle User

        Returns:
            UserProfile: Profil de l'utilisateur
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

        if not profile:
            # Créer un profil vide
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
            logger.info(f"Profil créé pour l'utilisateur {user.id}")

        return profile

    @staticmethod
    def get_profile_response(db: Session, user: User) -> UserProfileResponse:
        """
        Récupère le profil complet avec clés masquées

        Args:
            db: Session de base de données
            user: Instance du modèle User

        Returns:
            UserProfileResponse: Profil avec clés masquées
        """
        profile = UserService.get_or_create_profile(db, user)
        return UserProfileResponse.from_user_and_profile(user, profile)

    @staticmethod
    def update_profile(
        db: Session,
        user: User,
        profile_update: UserProfileUpdate
    ) -> UserProfileResponse:
        """
        Met à jour le profil utilisateur (email, username)

        Args:
            db: Session de base de données
            user: Instance du modèle User
            profile_update: Données de mise à jour

        Returns:
            UserProfileResponse: Profil mis à jour avec clés masquées

        Raises:
            HTTPException: Si l'email ou le username existe déjà
        """
        update_data = profile_update.model_dump(exclude_unset=True)

        # Vérifier les doublons email/username
        if "email" in update_data or "username" in update_data:
            query = db.query(User).filter(User.id != user.id)

            if "email" in update_data:
                existing_email = query.filter(User.email == update_data["email"]).first()
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already in use"
                    )

            if "username" in update_data:
                existing_username = query.filter(User.username == update_data["username"]).first()
                if existing_username:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )

        # Mettre à jour les champs du User
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return UserService.get_profile_response(db, user)

    @staticmethod
    def update_api_keys(
        db: Session,
        user: User,
        api_keys: ApiKeyUpdate
    ) -> UserProfileResponse:
        """
        Met à jour les clés API de l'utilisateur

        ✅ OPTIMISATION : Méthode unifiée qui élimine la duplication (2× dans routes/users.py)

        Args:
            db: Session de base de données
            user: Instance du modèle User
            api_keys: Clés API à mettre à jour

        Returns:
            UserProfileResponse: Profil mis à jour avec clés masquées
        """
        # Récupérer ou créer le profil
        profile = UserService.get_or_create_profile(db, user)

        # Extraire les données à mettre à jour
        update_data = api_keys.model_dump(exclude_unset=True)

        # Mettre à jour les clés API
        for field, value in update_data.items():
            if field == "hyperliquid_public_address":
                # Normaliser et valider l'adresse
                profile.hyperliquid_public_address = _normalize_hyperliquid_address(value)

            elif field in ["hyperliquid_api_key", "anthropic_api_key", "coingecko_api_key"]:
                if value:
                    # Chiffrer la clé avant stockage
                    encrypted_value = encrypt_api_key(value)
                    setattr(profile, field, encrypted_value)
                elif value is None:
                    # Supprimer la clé
                    setattr(profile, field, None)

        db.commit()
        db.refresh(profile)

        return UserService.get_profile_response(db, user)


# ========== Service UserTradingPreferences ==========

class PreferencesService:
    """Service de gestion des préférences de trading"""

    @staticmethod
    def create_default_preferences(db: Session, user: User) -> UserTradingPreferences:
        """
        Crée des préférences par défaut pour un utilisateur

        ✅ OPTIMISATION : Logique métier déplacée du router vers le service

        Args:
            db: Session de base de données
            user: Instance du modèle User

        Returns:
            UserTradingPreferences: Préférences créées

        Raises:
            HTTPException: Si erreur de création
        """
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

    @staticmethod
    def get_preferences(db: Session, user: User) -> UserTradingPreferencesResponse:
        """
        Récupère les préférences de l'utilisateur

        Si l'utilisateur n'a pas de préférences, retourne les valeurs par défaut

        Args:
            db: Session de base de données
            user: Instance du modèle User

        Returns:
            UserTradingPreferencesResponse: Préférences de l'utilisateur
        """
        try:
            db_preferences = db.query(UserTradingPreferences).filter(
                UserTradingPreferences.user_id == user.id
            ).first()

            return UserTradingPreferencesResponse.from_db_model(db_preferences)

        except Exception as e:
            logger.error(f"Erreur récupération préférences pour utilisateur {user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la récupération des préférences"
            )

    @staticmethod
    def create_preferences(
        db: Session,
        user: User,
        preferences_data: UserTradingPreferencesCreate
    ) -> UserTradingPreferencesResponse:
        """
        Crée ou met à jour les préférences de trading

        Args:
            db: Session de base de données
            user: Instance du modèle User
            preferences_data: Données des préférences

        Returns:
            UserTradingPreferencesResponse: Préférences créées/mises à jour

        Raises:
            HTTPException: Si des préférences existent déjà
        """
        try:
            # Vérifier si des préférences existent déjà
            existing = db.query(UserTradingPreferences).filter(
                UserTradingPreferences.user_id == user.id
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Preferences already exist. Use PUT to update."
                )

            # Préparer les données pour la base de données
            pref_dict = preferences_data.model_dump()
            serialized_data = _serialize_preferences_for_db(pref_dict)

            # Créer les préférences
            db_preferences = UserTradingPreferences(
                user_id=user.id,
                **serialized_data
            )

            db.add(db_preferences)
            db.commit()
            db.refresh(db_preferences)

            logger.info(f"Préférences créées pour l'utilisateur {user.id}")
            return UserTradingPreferencesResponse.from_db_model(db_preferences)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur création préférences pour utilisateur {user.id}: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création des préférences: {str(e)}"
            )

    @staticmethod
    def update_preferences(
        db: Session,
        user: User,
        preferences_update: UserTradingPreferencesUpdate
    ) -> UserTradingPreferencesResponse:
        """
        Met à jour les préférences de trading

        Args:
            db: Session de base de données
            user: Instance du modèle User
            preferences_update: Données de mise à jour

        Returns:
            UserTradingPreferencesResponse: Préférences mises à jour
        """
        try:
            # Récupérer les préférences existantes
            db_preferences = db.query(UserTradingPreferences).filter(
                UserTradingPreferences.user_id == user.id
            ).first()

            # Créer les préférences si elles n'existent pas
            if not db_preferences:
                db_preferences = PreferencesService.create_default_preferences(db, user)

            # Mettre à jour les champs fournis
            update_data = preferences_update.model_dump(exclude_unset=True)
            serialized_data = _serialize_preferences_for_db(update_data)

            for field, value in serialized_data.items():
                setattr(db_preferences, field, value)

            db.commit()
            db.refresh(db_preferences)

            logger.info(f"Préférences mises à jour pour l'utilisateur {user.id}")
            return UserTradingPreferencesResponse.from_db_model(db_preferences)

        except Exception as e:
            logger.error(f"Erreur mise à jour préférences pour utilisateur {user.id}: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la mise à jour des préférences: {str(e)}"
            )

    @staticmethod
    def delete_preferences(db: Session, user: User) -> Dict[str, str]:
        """
        Supprime les préférences de l'utilisateur

        Args:
            db: Session de base de données
            user: Instance du modèle User

        Returns:
            dict: Message de confirmation
        """
        try:
            db_preferences = db.query(UserTradingPreferences).filter(
                UserTradingPreferences.user_id == user.id
            ).first()

            if not db_preferences:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Preferences not found"
                )

            db.delete(db_preferences)
            db.commit()

            logger.info(f"Préférences supprimées pour l'utilisateur {user.id}")
            return {"message": "Preferences deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur suppression préférences pour utilisateur {user.id}: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression des préférences"
            )

    @staticmethod
    def get_default_preferences() -> UserTradingPreferencesDefault:
        """
        Retourne les valeurs par défaut des préférences

        Returns:
            UserTradingPreferencesDefault: Valeurs par défaut
        """
        return UserTradingPreferencesDefault()
