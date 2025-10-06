"""
Service métier pour la gestion des profils IA utilisateur
"""

import logging
from sqlalchemy.orm import Session
from typing import Optional

from .models import AIProfile
from .schemas import AIProfileCreate, AIProfileUpdate, AIProfileResponse

logger = logging.getLogger(__name__)


class AIProfileService:
    """Service pour gérer les profils IA utilisateur"""

    def get_or_create_profile(self, user_id: int, db: Session) -> AIProfile:
        """
        Récupère le profil IA de l'utilisateur ou en crée un nouveau avec valeurs par défaut

        Args:
            user_id: ID de l'utilisateur
            db: Session de base de données

        Returns:
            Profil IA de l'utilisateur
        """
        try:
            # Vérifier si le profil existe déjà
            profile = db.query(AIProfile).filter(AIProfile.user_id == user_id).first()

            if profile:
                logger.info(f"Profil IA existant récupéré pour utilisateur {user_id}")
                return profile

            # Créer un nouveau profil avec valeurs par défaut
            default_values = AIProfile.get_default_values()
            new_profile = AIProfile(
                user_id=user_id,
                **default_values
            )

            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)

            logger.info(f"Nouveau profil IA créé pour utilisateur {user_id}")
            return new_profile

        except Exception as e:
            db.rollback()
            logger.error(f"Erreur get_or_create_profile pour utilisateur {user_id}: {e}")
            raise

    def get_profile(self, user_id: int, db: Session) -> Optional[AIProfile]:
        """
        Récupère le profil IA de l'utilisateur

        Args:
            user_id: ID de l'utilisateur
            db: Session de base de données

        Returns:
            Profil IA ou None si non trouvé
        """
        try:
            profile = db.query(AIProfile).filter(AIProfile.user_id == user_id).first()
            return profile

        except Exception as e:
            logger.error(f"Erreur get_profile pour utilisateur {user_id}: {e}")
            raise

    def create_profile(
        self,
        user_id: int,
        profile_data: AIProfileCreate,
        db: Session
    ) -> AIProfile:
        """
        Crée un nouveau profil IA pour l'utilisateur

        Args:
            user_id: ID de l'utilisateur
            profile_data: Données du profil
            db: Session de base de données

        Returns:
            Profil IA créé

        Raises:
            ValueError: Si un profil existe déjà
        """
        try:
            # Vérifier qu'il n'existe pas déjà
            existing = db.query(AIProfile).filter(AIProfile.user_id == user_id).first()
            if existing:
                raise ValueError("Un profil IA existe déjà pour cet utilisateur")

            # Créer le nouveau profil
            new_profile = AIProfile(
                user_id=user_id,
                **profile_data.dict()
            )

            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)

            logger.info(f"Profil IA créé pour utilisateur {user_id}")
            return new_profile

        except Exception as e:
            db.rollback()
            logger.error(f"Erreur create_profile pour utilisateur {user_id}: {e}")
            raise

    def update_profile(
        self,
        user_id: int,
        profile_data: AIProfileUpdate,
        db: Session
    ) -> AIProfile:
        """
        Met à jour le profil IA de l'utilisateur

        Args:
            user_id: ID de l'utilisateur
            profile_data: Données à mettre à jour
            db: Session de base de données

        Returns:
            Profil IA mis à jour

        Raises:
            ValueError: Si le profil n'existe pas
        """
        try:
            # Récupérer le profil existant
            profile = db.query(AIProfile).filter(AIProfile.user_id == user_id).first()

            if not profile:
                raise ValueError("Aucun profil IA trouvé pour cet utilisateur")

            # Mettre à jour uniquement les champs fournis
            update_data = profile_data.dict(exclude_unset=True)

            for field, value in update_data.items():
                setattr(profile, field, value)

            db.commit()
            db.refresh(profile)

            logger.info(f"Profil IA mis à jour pour utilisateur {user_id}")
            return profile

        except Exception as e:
            db.rollback()
            logger.error(f"Erreur update_profile pour utilisateur {user_id}: {e}")
            raise

    def delete_profile(self, user_id: int, db: Session) -> bool:
        """
        Supprime le profil IA de l'utilisateur (reset aux valeurs par défaut)

        Args:
            user_id: ID de l'utilisateur
            db: Session de base de données

        Returns:
            True si supprimé avec succès
        """
        try:
            profile = db.query(AIProfile).filter(AIProfile.user_id == user_id).first()

            if not profile:
                logger.warning(f"Aucun profil IA à supprimer pour utilisateur {user_id}")
                return False

            db.delete(profile)
            db.commit()

            logger.info(f"Profil IA supprimé pour utilisateur {user_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Erreur delete_profile pour utilisateur {user_id}: {e}")
            raise

    def reset_to_defaults(self, user_id: int, db: Session) -> AIProfile:
        """
        Reset le profil IA aux valeurs par défaut

        Args:
            user_id: ID de l'utilisateur
            db: Session de base de données

        Returns:
            Profil IA avec valeurs par défaut
        """
        try:
            # Supprimer le profil existant
            self.delete_profile(user_id, db)

            # Créer un nouveau profil avec valeurs par défaut
            return self.get_or_create_profile(user_id, db)

        except Exception as e:
            logger.error(f"Erreur reset_to_defaults pour utilisateur {user_id}: {e}")
            raise
