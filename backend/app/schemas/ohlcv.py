from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# Anciens modèles supprimés - remplacés par les nouveaux modèles multi-timeframes

class ExchangeInfo(BaseModel):
    """Modèle pour les informations d'un exchange"""
    name: str = Field(..., description="Nom de l'exchange")
    available: bool = Field(..., description="Si l'exchange est disponible")

class ExchangeListResponse(BaseModel):
    """Modèle pour la liste des exchanges disponibles"""
    status: str = Field(..., description="Statut de la requête")
    exchanges: List[str] = Field(..., description="Liste des exchanges disponibles")
    timeframes: List[str] = Field(..., description="Liste des timeframes disponibles")

class ExchangeSymbolsRequest(BaseModel):
    """Modèle pour demander les symboles d'un exchange"""
    exchange: str = Field(..., description="Nom de l'exchange")
    limit: Optional[int] = Field(default=20, le=100, description="Nombre de symboles à retourner")

class ExchangeSymbolsResponse(BaseModel):
    """Modèle pour la réponse des symboles d'un exchange"""
    status: str = Field(..., description="Statut de la requête")
    message: Optional[str] = Field(None, description="Message d'erreur si applicable")
    exchange: Optional[str] = Field(None, description="Nom de l'exchange")
    symbols: Optional[List[str]] = Field(None, description="Liste des symboles disponibles")
    total_available: Optional[int] = Field(None, description="Nombre total de symboles disponibles")

# Nouveaux modèles pour l'analyse multi-timeframes

class MAIndicators(BaseModel):
    """Modèle pour les moyennes mobiles"""
    ma20: float = Field(..., description="Moyenne mobile 20 périodes")
    ma50: float = Field(..., description="Moyenne mobile 50 périodes")
    ma200: float = Field(..., description="Moyenne mobile 200 périodes")

class VolumeIndicators(BaseModel):
    """Modèle pour les indicateurs de volume"""
    current: int = Field(..., description="Volume actuel")
    avg20: int = Field(..., description="Volume moyen sur 20 périodes")
    spike_ratio: float = Field(..., description="Ratio de spike de volume")

class CurrentPriceInfo(BaseModel):
    """Modèle pour les informations de prix actuel"""
    current_price: float = Field(..., description="Prix actuel")
    change_24h_percent: Optional[float] = Field(None, description="Variation 24h en %")
    volume_24h: Optional[float] = Field(None, description="Volume 24h")

class MainTFFeatures(BaseModel):
    """Modèle pour les features du timeframe principal"""
    ma: MAIndicators = Field(..., description="Moyennes mobiles")
    rsi14: float = Field(..., description="RSI 14 périodes")
    atr14: float = Field(..., description="ATR 14 périodes")
    volume: VolumeIndicators = Field(..., description="Indicateurs de volume")
    last_20_candles: List[List[float]] = Field(..., description="20 dernières bougies [ts, o, h, l, c, v]")

class HigherTFFeatures(BaseModel):
    """Modèle pour les features du timeframe supérieur"""
    tf: str = Field(..., description="Timeframe")
    ma: MAIndicators = Field(..., description="Moyennes mobiles")
    rsi14: float = Field(..., description="RSI 14 périodes")
    atr14: float = Field(..., description="ATR 14 périodes")
    structure: str = Field(..., description="Structure de marché (LH_LL, HL_HH, etc.)")
    nearest_resistance: float = Field(..., description="Résistance la plus proche")

class LowerTFFeatures(BaseModel):
    """Modèle pour les features du timeframe inférieur"""
    tf: str = Field(..., description="Timeframe")
    rsi14: float = Field(..., description="RSI 14 périodes")
    volume: VolumeIndicators = Field(..., description="Indicateurs de volume")
    last_20_candles: List[List[float]] = Field(..., description="20 dernières bougies [ts, o, h, l, c, v]")

# Versions allégées pour le frontend (sans les bougies)

class MainTFFeaturesLight(BaseModel):
    """Version allégée des features du timeframe principal (sans bougies)"""
    ma: MAIndicators = Field(..., description="Moyennes mobiles")
    rsi14: float = Field(..., description="RSI 14 périodes")
    atr14: float = Field(..., description="ATR 14 périodes")
    volume: VolumeIndicators = Field(..., description="Indicateurs de volume")

class LowerTFFeaturesLight(BaseModel):
    """Version allégée des features du timeframe inférieur (sans bougies)"""
    tf: str = Field(..., description="Timeframe")
    rsi14: float = Field(..., description="RSI 14 périodes")
    volume: VolumeIndicators = Field(..., description="Indicateurs de volume")

class MultiTimeframeRequest(BaseModel):
    """Modèle pour la requête d'analyse multi-timeframes"""
    exchange: str = Field(..., description="Nom de l'exchange")
    symbol: str = Field(..., description="Symbole du trading pair")
    profile: Literal["short", "medium", "long"] = Field(..., description="Profil de trading")

class MultiTimeframeResponse(BaseModel):
    """Modèle pour la réponse d'analyse multi-timeframes"""
    profile: str = Field(..., description="Profil de trading utilisé")
    symbol: str = Field(..., description="Ticker du symbole analysé")
    tf: str = Field(..., description="Timeframe principal")
    current_price: CurrentPriceInfo = Field(..., description="Prix actuel du symbole")
    features: MainTFFeatures = Field(..., description="Indicateurs du timeframe principal")
    higher_tf: HigherTFFeatures = Field(..., description="Contexte du timeframe supérieur")
    lower_tf: LowerTFFeatures = Field(..., description="Contexte du timeframe inférieur")