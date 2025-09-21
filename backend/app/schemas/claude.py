from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

class ClaudeModel(str, Enum):
    HAIKU = "claude-3-haiku-20240307"
    SONNET = "claude-3-sonnet-20240229"
    SONNET_35 = "claude-3-5-sonnet-20241022"
    OPUS = "claude-3-opus-20240229"

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

class ClaudeAnalysisRequest(BaseModel):
    """Requête d'analyse trading vers Claude"""

    assets: List[str] = Field(
        ...,
        description="Liste des actifs à analyser",
        min_items=1,
        max_items=10
    )

    model: ClaudeModel = Field(
        default=ClaudeModel.SONNET_35,
        description="Modèle Claude à utiliser"
    )

    analysis_type: Literal["quick", "detailed"] = Field(
        default="detailed",
        description="Type d'analyse demandée"
    )

    custom_prompt: Optional[str] = Field(
        default=None,
        description="Prompt personnalisé additionnel",
        max_length=1000
    )

    include_market_data: bool = Field(
        default=True,
        description="Inclure les données de marché CoinGecko"
    )

    use_user_preferences: bool = Field(
        default=True,
        description="Utiliser les préférences utilisateur"
    )

    @field_validator('assets')
    @classmethod
    def validate_assets(cls, v):
        """Valide la liste des actifs"""
        if not v:
            raise ValueError("Au moins un actif doit être spécifié")

        # Normaliser en majuscules
        normalized = [asset.upper().strip() for asset in v]

        # Supprimer les doublons
        unique_assets = list(set(normalized))

        if len(unique_assets) != len(normalized):
            raise ValueError("Des actifs en doublon ont été détectés")

        return unique_assets

class ClaudeMarketData(BaseModel):
    """Données de marché pour un actif"""

    symbol: str = Field(..., description="Symbole de l'actif")
    name: str = Field(..., description="Nom complet de l'actif")
    current_price: float = Field(..., description="Prix actuel en USD")
    price_change_24h: Optional[float] = Field(None, description="Variation 24h en %")
    volume_24h: Optional[float] = Field(None, description="Volume 24h en USD")
    market_cap: Optional[float] = Field(None, description="Capitalisation de marché")
    last_updated: datetime = Field(..., description="Dernière mise à jour")

    # Données techniques additionnelles
    high_24h: Optional[float] = Field(None, description="Plus haut 24h")
    low_24h: Optional[float] = Field(None, description="Plus bas 24h")
    price_change_7d: Optional[float] = Field(None, description="Variation 7j en %")
    price_change_30d: Optional[float] = Field(None, description="Variation 30j en %")

class ClaudeRecommendation(BaseModel):
    """Recommandation structurée pour un actif"""

    asset: str = Field(..., description="Symbole de l'actif")
    action: TradingAction = Field(..., description="Action recommandée")
    confidence: ConfidenceLevel = Field(..., description="Niveau de confiance")

    # Niveaux de prix
    entry_price: Optional[float] = Field(None, description="Prix d'entrée suggéré")
    stop_loss: Optional[float] = Field(None, description="Stop loss suggéré")
    take_profit: Optional[float] = Field(None, description="Take profit suggéré")

    # Justification
    reasoning: str = Field(..., description="Justification de la recommandation")
    key_factors: List[str] = Field(default=[], description="Facteurs clés de décision")

    # Métadonnées
    time_horizon: Optional[str] = Field(None, description="Horizon temporel")
    risk_level: Optional[str] = Field(None, description="Niveau de risque")

class ClaudeAnalysisResponse(BaseModel):
    """Réponse complète d'analyse Claude"""

    # Métadonnées de la requête
    request_id: str = Field(..., description="ID unique de la requête")
    timestamp: datetime = Field(..., description="Timestamp de l'analyse")
    model_used: ClaudeModel = Field(..., description="Modèle Claude utilisé")
    assets_analyzed: List[str] = Field(..., description="Actifs analysés")

    # Analyse textuelle complète
    full_analysis: str = Field(..., description="Analyse complète en texte")

    # Éléments structurés
    recommendations: List[ClaudeRecommendation] = Field(
        default=[],
        description="Recommandations structurées par actif"
    )

    market_summary: str = Field(..., description="Résumé du marché")
    risk_assessment: str = Field(..., description="Évaluation des risques")

    # Données de marché utilisées
    market_data: Dict[str, ClaudeMarketData] = Field(
        default={},
        description="Données de marché par actif"
    )

    # Préférences utilisateur appliquées
    user_preferences_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Résumé des préférences utilisateur utilisées"
    )

    # Métriques techniques
    tokens_used: Optional[int] = Field(None, description="Tokens consommés")
    processing_time_ms: Optional[int] = Field(None, description="Temps de traitement en ms")

    # Avertissements et limitations
    warnings: List[str] = Field(default=[], description="Avertissements éventuels")
    limitations: List[str] = Field(default=[], description="Limitations de l'analyse")

class ClaudeAnalysisHistory(BaseModel):
    """Historique d'une analyse passée"""

    id: int = Field(..., description="ID de l'analyse")
    user_id: int = Field(..., description="ID de l'utilisateur")
    timestamp: datetime = Field(..., description="Date/heure de l'analyse")
    assets: List[str] = Field(..., description="Actifs analysés")
    model_used: ClaudeModel = Field(..., description="Modèle utilisé")

    # Résumé de l'analyse (pour la liste)
    summary: str = Field(..., description="Résumé court de l'analyse")
    recommendations_count: int = Field(..., description="Nombre de recommandations")

    # Lien vers l'analyse complète
    analysis_url: Optional[str] = Field(None, description="URL de l'analyse complète")

class ClaudeErrorResponse(BaseModel):
    """Réponse d'erreur Claude"""

    error_type: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails additionnels")
    timestamp: datetime = Field(default_factory=datetime.now)

    # Suggestions de résolution
    suggestions: List[str] = Field(default=[], description="Suggestions pour résoudre l'erreur")

# Schémas pour la génération de prompts
class PromptContext(BaseModel):
    """Contexte pour la génération de prompts"""

    user_preferences: Optional[Dict[str, Any]] = Field(None)
    market_data: Dict[str, ClaudeMarketData] = Field(default={})
    analysis_type: str = Field(default="detailed")
    custom_instructions: Optional[str] = Field(None)

class GeneratedPrompt(BaseModel):
    """Prompt généré pour Claude"""

    system_prompt: str = Field(..., description="Prompt système")
    user_prompt: str = Field(..., description="Prompt utilisateur")
    context_summary: str = Field(..., description="Résumé du contexte")
    estimated_tokens: Optional[int] = Field(None, description="Estimation des tokens")