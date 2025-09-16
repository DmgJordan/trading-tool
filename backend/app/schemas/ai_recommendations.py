from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from ..models.ai_recommendations import ActionType, RiskLevel

class AIRecommendationBase(BaseModel):
    """Schéma de base pour une recommandation IA"""
    action: ActionType = Field(description="Action recommandée: buy, sell ou hold")
    symbol: str = Field(max_length=50, description="Symbole de l'actif (ex: BTC, ETH)")
    confidence: int = Field(ge=0, le=100, description="Niveau de confiance 0-100")
    size_percentage: float = Field(ge=0.1, le=100.0, description="Taille de position en % du portefeuille")
    entry_price: Optional[float] = Field(None, gt=0, description="Prix d'entrée suggéré")
    stop_loss: Optional[float] = Field(None, gt=0, description="Prix stop-loss")
    take_profit1: Optional[float] = Field(None, gt=0, description="Premier niveau take-profit")
    take_profit2: Optional[float] = Field(None, gt=0, description="Deuxième niveau take-profit")
    take_profit3: Optional[float] = Field(None, gt=0, description="Troisième niveau take-profit")
    reasoning: Optional[str] = Field(None, max_length=2000, description="Explication de la recommandation")
    risk_level: RiskLevel = Field(description="Niveau de risque: low, medium ou high")

    @validator('symbol')
    def validate_symbol(cls, v):
        """Valide le format du symbole"""
        if not v or not v.strip():
            raise ValueError("Le symbole ne peut pas être vide")

        symbol = v.upper().strip()
        if not symbol.isalnum() or len(symbol) > 10:
            raise ValueError("Format de symbole invalide")

        return symbol

    @validator('take_profit2')
    def validate_take_profit2(cls, v, values):
        """Valide que take_profit2 > take_profit1"""
        if v is not None and 'take_profit1' in values and values['take_profit1'] is not None:
            if v <= values['take_profit1']:
                raise ValueError("take_profit2 doit être supérieur à take_profit1")
        return v

    @validator('take_profit3')
    def validate_take_profit3(cls, v, values):
        """Valide que take_profit3 > take_profit2"""
        if v is not None and 'take_profit2' in values and values['take_profit2'] is not None:
            if v <= values['take_profit2']:
                raise ValueError("take_profit3 doit être supérieur à take_profit2")
        return v

    @validator('stop_loss')
    def validate_stop_loss(cls, v, values):
        """Valide la cohérence du stop-loss avec l'action"""
        if v is not None and 'entry_price' in values and values['entry_price'] is not None:
            entry_price = values['entry_price']
            action = values.get('action')

            if action == ActionType.BUY and v >= entry_price:
                raise ValueError("Pour un achat, stop_loss doit être inférieur au prix d'entrée")
            elif action == ActionType.SELL and v <= entry_price:
                raise ValueError("Pour une vente, stop_loss doit être supérieur au prix d'entrée")

        return v

class AIRecommendationRequest(BaseModel):
    """Requête pour générer des recommandations IA"""
    symbols: Optional[List[str]] = Field(
        default=None,
        max_items=10,
        description="Symboles spécifiques à analyser (max 10). Si vide, utilise les préférences utilisateur"
    )
    max_recommendations: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Nombre maximum de recommandations à générer (1-20)"
    )
    force_refresh: bool = Field(
        default=False,
        description="Forcer une nouvelle analyse même si récente disponible"
    )

    @validator('symbols')
    def validate_symbols(cls, v):
        """Valide la liste des symboles"""
        if v is not None:
            normalized = []
            for symbol in v:
                if not symbol or not symbol.strip():
                    continue

                symbol = symbol.upper().strip()
                if not symbol.isalnum() or len(symbol) > 10:
                    raise ValueError(f"Format de symbole invalide: {symbol}")

                normalized.append(symbol)

            return list(set(normalized))  # Supprimer les doublons
        return v

class AIRecommendationResponse(AIRecommendationBase):
    """Réponse avec une recommandation IA enrichie"""
    id: int
    user_id: int
    market_data_timestamp: Optional[datetime]
    model_used: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AIRecommendationsListResponse(BaseModel):
    """Réponse avec liste de recommandations"""
    recommendations: List[AIRecommendationResponse]
    generation_timestamp: datetime
    context: dict = Field(description="Contexte utilisé pour la génération")

class AIAnalysisError(BaseModel):
    """Erreur d'analyse IA"""
    error_type: str = Field(description="Type d'erreur: api_error, quota_exceeded, parsing_error, etc.")
    message: str = Field(description="Message d'erreur détaillé")
    retry_after: Optional[int] = Field(None, description="Délai avant retry en secondes")

# Schémas pour validation du JSON retourné par l'IA
class RawAIRecommendation(BaseModel):
    """Format brut attendu de l'IA (validation du JSON)"""
    action: str = Field(description="buy, sell ou hold")
    symbol: str = Field(description="Symbole de l'actif")
    confidence: int = Field(ge=0, le=100, description="Niveau de confiance")
    size_percentage: float = Field(ge=0, le=100, description="Taille de position en %")
    entry_price: Optional[float] = Field(None, description="Prix d'entrée")
    stop_loss: Optional[float] = Field(None, description="Stop loss")
    take_profit1: Optional[float] = Field(None, description="Take profit 1")
    take_profit2: Optional[float] = Field(None, description="Take profit 2")
    take_profit3: Optional[float] = Field(None, description="Take profit 3")
    reasoning: Optional[str] = Field(None, description="Explication")
    risk_level: str = Field(description="low, medium ou high")

    @validator('action')
    def validate_action(cls, v):
        """Valide l'action"""
        if v.lower() not in ['buy', 'sell', 'hold']:
            raise ValueError(f"Action invalide: {v}. Doit être buy, sell ou hold")
        return v.lower()

    @validator('risk_level')
    def validate_risk_level(cls, v):
        """Valide le niveau de risque"""
        if v.lower() not in ['low', 'medium', 'high']:
            raise ValueError(f"Niveau de risque invalide: {v}. Doit être low, medium ou high")
        return v.lower()

class RawAIResponse(BaseModel):
    """Format brut complet de la réponse IA"""
    recommendations: List[RawAIRecommendation] = Field(min_items=1, max_items=20)

    @validator('recommendations')
    def validate_recommendations_not_empty(cls, v):
        """Valide que la liste n'est pas vide"""
        if not v:
            raise ValueError("La liste de recommandations ne peut pas être vide")
        return v

class AIGenerationContext(BaseModel):
    """Contexte utilisé pour la génération"""
    user_preferences: dict
    market_data_symbols: List[str]
    market_data_timestamp: datetime
    prompt_length: int
    model_used: str
    api_key_last_4: str  # Derniers 4 caractères de la clé API pour debug