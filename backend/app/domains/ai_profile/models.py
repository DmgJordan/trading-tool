"""
Modèle pour la configuration IA de l'utilisateur

Ce modèle stocke les préférences IA de chaque utilisateur.
L'historique des recommandations sera dans un futur domaine séparé.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...core import Base


class AIProfile(Base):
    """Configuration IA de l'utilisateur"""
    __tablename__ = "ai_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)

    # Provider et modèle préférés
    preferred_provider = Column(
        String(20),
        nullable=False,
        default="anthropic",
        comment="Provider IA préféré (anthropic, openai, deepseek)"
    )
    preferred_model = Column(
        String(100),
        nullable=True,
        comment="Modèle IA préféré (ex: claude-sonnet-4-5-20250929)"
    )

    # Paramètres d'analyse
    risk_tolerance = Column(
        String(20),
        nullable=False,
        default="medium",
        comment="Tolérance au risque (low, medium, high)"
    )
    analysis_timeframe = Column(
        String(20),
        nullable=False,
        default="medium",
        comment="Horizon d'analyse préféré (short, medium, long)"
    )

    # Paramètres de recommandations
    max_recommendations_per_request = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Nombre max de recommandations par requête"
    )
    min_confidence_level = Column(
        Integer,
        nullable=False,
        default=70,
        comment="Niveau de confiance minimum (0-100)"
    )

    # Automatisation
    auto_trading = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Activer le trading automatique (non implémenté)"
    )
    auto_analysis_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Activer les analyses automatiques périodiques"
    )
    auto_analysis_frequency_hours = Column(
        Integer,
        nullable=True,
        default=24,
        comment="Fréquence des analyses auto (en heures)"
    )

    # Préférences de notification
    notify_on_new_recommendation = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Notifier lors de nouvelles recommandations"
    )
    notify_on_high_confidence = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Notifier uniquement pour haute confiance (85+)"
    )

    # Relations
    user = relationship("User", back_populates="ai_profile")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Index composé pour optimiser les requêtes
    __table_args__ = (
        Index('idx_user_provider', 'user_id', 'preferred_provider'),
    )

    def __repr__(self):
        return f"<AIProfile(user_id={self.user_id}, provider={self.preferred_provider}, model={self.preferred_model})>"

    @classmethod
    def get_default_values(cls) -> dict:
        """Retourne les valeurs par défaut pour un nouveau profil"""
        return {
            "preferred_provider": "anthropic",
            "preferred_model": "claude-sonnet-4-5-20250929",
            "risk_tolerance": "medium",
            "analysis_timeframe": "medium",
            "max_recommendations_per_request": 5,
            "min_confidence_level": 70,
            "auto_trading": False,
            "auto_analysis_enabled": False,
            "auto_analysis_frequency_hours": 24,
            "notify_on_new_recommendation": True,
            "notify_on_high_confidence": True,
        }
