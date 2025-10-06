"""
Schémas pour le domaine AI

Fusion de :
- app/schemas/claude.py
- app/schemas/ai_recommendations.py
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

# Import des schémas market
from ..market.schemas import (
    CurrentPriceInfo,
    HigherTFFeatures,
    MainTFFeaturesLight,
    LowerTFFeaturesLight
)


# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════

class AIProviderType(str, Enum):
    """Types de providers IA disponibles"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"


class ClaudeModel(str, Enum):
    """Modèles Claude disponibles"""
    HAIKU_35 = "claude-3-5-haiku-20241022"
    SONNET_45 = "claude-sonnet-4-5-20250929"
    OPUS_41 = "claude-opus-4-1-20250805"


class TradeDirection(str, Enum):
    """Direction d'un trade"""
    LONG = "long"
    SHORT = "short"


class ActionType(str, Enum):
    """Types d'actions de trading (format alternatif)"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class RiskLevel(str, Enum):
    """Niveaux de risque"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Import des schémas market pour éviter duplication
from ..market.schemas import ClaudeMarketData


# ═══════════════════════════════════════════════════════════════
# SCHÉMAS POUR ANALYSE SINGLE-ASSET (migré depuis claude.py)
# ═══════════════════════════════════════════════════════════════

class SingleAssetAnalysisRequest(BaseModel):
    """Requête d'analyse pour un seul actif avec données techniques"""

    ticker: str = Field(..., description="Ticker du symbole (ex: BTC/USDT)")
    exchange: str = Field(default="binance", description="Exchange à utiliser")
    profile: Literal["short", "medium", "long"] = Field(..., description="Profil de trading")
    model: ClaudeModel = Field(default=ClaudeModel.SONNET_45, description="Modèle Claude")
    custom_prompt: Optional[str] = Field(None, description="Instructions additionnelles")

    @field_validator('ticker')
    @classmethod
    def validate_ticker(cls, v):
        """Valide et normalise le ticker"""
        return v.upper().strip()


class TechnicalDataLight(BaseModel):
    """Version allégée des données techniques (sans bougies)"""

    symbol: str = Field(..., description="Symbole analysé")
    profile: str = Field(..., description="Profil utilisé")
    tf: str = Field(..., description="Timeframe principal")
    current_price: CurrentPriceInfo = Field(..., description="Prix actuel")
    features: MainTFFeaturesLight = Field(..., description="Indicateurs TF principal sans bougies")
    higher_tf: HigherTFFeatures = Field(..., description="Contexte TF supérieur")
    lower_tf: LowerTFFeaturesLight = Field(..., description="Contexte TF inférieur sans bougies")


class TradeRecommendation(BaseModel):
    """
    Recommandation de trading unifiée

    Fusion de:
    - TradeRecommendation (claude.py)
    - AIRecommendationBase (ai_recommendations.py)
    """

    # Direction et action
    direction: Optional[TradeDirection] = Field(None, description="Direction du trade (long/short)")
    action: Optional[ActionType] = Field(None, description="Action recommandée (buy/sell/hold)")
    symbol: str = Field(..., description="Symbole de l'actif")

    # Paramètres d'entrée
    entry_price: float = Field(..., gt=0, description="Prix d'entrée recommandé")

    # Gestion des risques
    stop_loss: float = Field(..., gt=0, description="Prix de stop-loss")
    take_profit_1: float = Field(..., gt=0, description="Premier take-profit")
    take_profit_2: float = Field(..., gt=0, description="Deuxième take-profit")
    take_profit_3: float = Field(..., gt=0, description="Troisième take-profit")

    # Métriques
    confidence_level: int = Field(..., ge=0, le=100, description="Niveau de confiance (0-100)")
    risk_reward_ratio: float = Field(..., gt=0, description="Ratio risque/récompense")
    portfolio_percentage: float = Field(..., ge=0.1, le=50.0, description="Pourcentage du portefeuille (0.1-50%)")
    risk_level: RiskLevel = Field(..., description="Niveau de risque")

    # Contexte
    timeframe: str = Field(..., description="Horizon temporel du trade")
    reasoning: str = Field(..., max_length=2000, description="Justification technique détaillée")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Valide le format du symbole"""
        if not v or not v.strip():
            raise ValueError("Le symbole ne peut pas être vide")
        return v.upper().strip()

    @field_validator('take_profit_2')
    @classmethod
    def validate_take_profit2(cls, v, info):
        """Valide que take_profit2 > take_profit_1"""
        if 'take_profit_1' in info.data and v <= info.data['take_profit_1']:
            raise ValueError("take_profit_2 doit être supérieur à take_profit_1")
        return v

    @field_validator('take_profit_3')
    @classmethod
    def validate_take_profit3(cls, v, info):
        """Valide que take_profit3 > take_profit_2"""
        if 'take_profit_2' in info.data and v <= info.data['take_profit_2']:
            raise ValueError("take_profit_3 doit être supérieur à take_profit_2")
        return v


class StructuredAnalysisResponse(BaseModel):
    """Réponse d'analyse avec recommandations de trading structurées"""

    # Métadonnées
    request_id: str = Field(..., description="ID unique de la requête")
    timestamp: datetime = Field(..., description="Timestamp de l'analyse")
    model_used: ClaudeModel = Field(..., description="Modèle Claude utilisé")

    # Données de base
    ticker: str = Field(..., description="Ticker analysé")
    exchange: str = Field(..., description="Exchange utilisé")
    profile: str = Field(..., description="Profil de trading")

    # Données techniques allégées
    technical_data: TechnicalDataLight = Field(..., description="Données techniques sans bougies")

    # Analyse IA
    claude_analysis: str = Field(..., description="Analyse textuelle complète de Claude")
    trade_recommendations: List[TradeRecommendation] = Field(default=[], description="Recommandations structurées")

    # Métriques
    tokens_used: Optional[int] = Field(None, description="Tokens consommés")
    processing_time_ms: Optional[int] = Field(None, description="Temps de traitement")

    # Avertissements
    warnings: List[str] = Field(default=[], description="Avertissements")


# ═══════════════════════════════════════════════════════════════
# SCHÉMAS POUR TESTS ET VALIDATION
# ═══════════════════════════════════════════════════════════════

class AITestRequest(BaseModel):
    """Requête de test de connexion à un provider"""
    provider: AIProviderType = Field(default=AIProviderType.ANTHROPIC)
    api_key: str = Field(..., description="Clé API à tester")


class AITestResponse(BaseModel):
    """Réponse de test de connexion"""
    provider: AIProviderType
    status: Literal["success", "error"]
    message: str
    timestamp: datetime


class ProviderInfo(BaseModel):
    """Informations sur un provider IA"""
    name: str
    provider_type: AIProviderType
    available_models: List[dict]
    implemented: bool
    description: str
