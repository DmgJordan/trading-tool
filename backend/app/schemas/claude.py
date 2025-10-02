from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class ClaudeModel(str, Enum):
    HAIKU_35 = "claude-3-5-haiku-20241022"
    SONNET_45 = "claude-sonnet-4-5-20250929"
    OPUS_41 = "claude-opus-4-1-20250805"

class TradingAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"

class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"









# Schémas pour l'analyse single-asset avec données techniques

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
    current_price: Dict[str, Any] = Field(..., description="Prix actuel")
    features: Dict[str, Any] = Field(..., description="Indicateurs TF principal sans bougies")
    higher_tf: Dict[str, Any] = Field(..., description="Contexte TF supérieur")
    lower_tf: Dict[str, Any] = Field(..., description="Contexte TF inférieur sans bougies")

class SingleAssetAnalysisResponse(BaseModel):
    """Réponse d'analyse single-asset avec données techniques"""

    # Métadonnées
    request_id: str = Field(..., description="ID unique de la requête")
    timestamp: datetime = Field(..., description="Timestamp de l'analyse")
    model_used: ClaudeModel = Field(..., description="Modèle Claude utilisé")

    # Données de base
    ticker: str = Field(..., description="Ticker analysé")
    exchange: str = Field(..., description="Exchange utilisé")
    profile: str = Field(..., description="Profil de trading")

    # Données techniques allégées (pour frontend)
    technical_data: TechnicalDataLight = Field(..., description="Données techniques sans bougies")

    # Analyse Claude
    claude_analysis: str = Field(..., description="Analyse complète de Claude")

    # Métriques
    tokens_used: Optional[int] = Field(None, description="Tokens consommés")
    processing_time_ms: Optional[int] = Field(None, description="Temps de traitement")

    # Avertissements
    warnings: List[str] = Field(default=[], description="Avertissements")

# Nouveaux schémas pour les recommandations de trading structurées

class TradeDirection(str, Enum):
    LONG = "long"
    SHORT = "short"

class TradeRecommendation(BaseModel):
    """Recommandation de trading structurée"""

    # Paramètres d'entrée
    entry_price: float = Field(..., description="Prix d'entrée recommandé")
    direction: TradeDirection = Field(..., description="Direction du trade (long/short)")

    # Gestion des risques
    stop_loss: float = Field(..., description="Prix de stop-loss")
    take_profit_1: float = Field(..., description="Premier take-profit")
    take_profit_2: float = Field(..., description="Deuxième take-profit")
    take_profit_3: float = Field(..., description="Troisième take-profit")

    # Métriques
    confidence_level: int = Field(..., ge=0, le=100, description="Niveau de confiance (0-100)")
    risk_reward_ratio: float = Field(..., description="Ratio risque/récompense")
    portfolio_percentage: float = Field(..., ge=0.1, le=50.0, description="Pourcentage du portefeuille recommandé (0.1-50%)")

    # Contexte
    timeframe: str = Field(..., description="Horizon temporel du trade")
    reasoning: str = Field(..., description="Justification technique détaillée")

    @field_validator('risk_reward_ratio')
    @classmethod
    def validate_risk_reward(cls, v):
        """Valide que le ratio risque/récompense est positif"""
        if v <= 0:
            raise ValueError("Le ratio risque/récompense doit être positif")
        return v

    @field_validator('stop_loss', 'take_profit_1', 'take_profit_2', 'take_profit_3')
    @classmethod
    def validate_prices(cls, v, values):
        """Valide la cohérence des prix"""
        if v <= 0:
            raise ValueError("Les prix doivent être positifs")
        return v

class StructuredAnalysisResponse(BaseModel):
    """Réponse d'analyse avec recommandations de trading structurées"""

    # Métadonnées (comme avant)
    request_id: str = Field(..., description="ID unique de la requête")
    timestamp: datetime = Field(..., description="Timestamp de l'analyse")
    model_used: ClaudeModel = Field(..., description="Modèle Claude utilisé")

    # Données de base
    ticker: str = Field(..., description="Ticker analysé")
    exchange: str = Field(..., description="Exchange utilisé")
    profile: str = Field(..., description="Profil de trading")

    # Données techniques allégées (comme avant)
    technical_data: TechnicalDataLight = Field(..., description="Données techniques sans bougies")

    # Nouvelle structure d'analyse
    claude_analysis: str = Field(..., description="Analyse textuelle complète de Claude")
    trade_recommendations: List[TradeRecommendation] = Field(default=[], description="Recommandations de trading structurées")

    # Métriques
    tokens_used: Optional[int] = Field(None, description="Tokens consommés")
    processing_time_ms: Optional[int] = Field(None, description="Temps de traitement")

    # Avertissements
    warnings: List[str] = Field(default=[], description="Avertissements")