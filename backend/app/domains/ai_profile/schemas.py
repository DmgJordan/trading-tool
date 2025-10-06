"""
Schémas Pydantic pour le profil IA utilisateur
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class AIProfileBase(BaseModel):
    """Schéma de base pour le profil IA"""

    preferred_provider: Literal["anthropic", "openai", "deepseek"] = Field(
        default="anthropic",
        description="Provider IA préféré"
    )
    preferred_model: Optional[str] = Field(
        None,
        max_length=100,
        description="Modèle IA préféré (ex: claude-sonnet-4-5-20250929)"
    )
    risk_tolerance: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Tolérance au risque"
    )
    analysis_timeframe: Literal["short", "medium", "long"] = Field(
        default="medium",
        description="Horizon d'analyse préféré"
    )
    max_recommendations_per_request: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Nombre max de recommandations par requête (1-20)"
    )
    min_confidence_level: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Niveau de confiance minimum (0-100)"
    )
    auto_trading: bool = Field(
        default=False,
        description="Activer le trading automatique (non implémenté)"
    )
    auto_analysis_enabled: bool = Field(
        default=False,
        description="Activer les analyses automatiques périodiques"
    )
    auto_analysis_frequency_hours: Optional[int] = Field(
        default=24,
        ge=1,
        le=168,
        description="Fréquence des analyses auto (1-168 heures)"
    )
    notify_on_new_recommendation: bool = Field(
        default=True,
        description="Notifier lors de nouvelles recommandations"
    )
    notify_on_high_confidence: bool = Field(
        default=True,
        description="Notifier uniquement pour haute confiance (85+)"
    )


class AIProfileCreate(AIProfileBase):
    """Schéma pour la création d'un profil IA"""
    pass


class AIProfileUpdate(BaseModel):
    """Schéma pour la mise à jour partielle d'un profil IA"""

    preferred_provider: Optional[Literal["anthropic", "openai", "deepseek"]] = None
    preferred_model: Optional[str] = Field(None, max_length=100)
    risk_tolerance: Optional[Literal["low", "medium", "high"]] = None
    analysis_timeframe: Optional[Literal["short", "medium", "long"]] = None
    max_recommendations_per_request: Optional[int] = Field(None, ge=1, le=20)
    min_confidence_level: Optional[int] = Field(None, ge=0, le=100)
    auto_trading: Optional[bool] = None
    auto_analysis_enabled: Optional[bool] = None
    auto_analysis_frequency_hours: Optional[int] = Field(None, ge=1, le=168)
    notify_on_new_recommendation: Optional[bool] = None
    notify_on_high_confidence: Optional[bool] = None


class AIProfileResponse(AIProfileBase):
    """Schéma pour la réponse avec profil IA complet"""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AIProfileValidationInfo(BaseModel):
    """Informations sur les contraintes de validation"""

    providers: list = ["anthropic", "openai", "deepseek"]
    risk_levels: list = ["low", "medium", "high"]
    timeframes: list = ["short", "medium", "long"]
    max_recommendations_range: dict = {"min": 1, "max": 20}
    confidence_range: dict = {"min": 0, "max": 100}
    auto_frequency_range: dict = {"min": 1, "max": 168, "unit": "hours"}
    default_values: dict = {
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
