from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class OHLCVCandle(BaseModel):
    """Modèle pour une bougie OHLCV individuelle"""
    timestamp: int = Field(..., description="Timestamp Unix en millisecondes")
    datetime: str = Field(..., description="Date et heure au format ISO")
    open: float = Field(..., description="Prix d'ouverture")
    high: float = Field(..., description="Prix le plus haut")
    low: float = Field(..., description="Prix le plus bas")
    close: float = Field(..., description="Prix de fermeture")
    volume: float = Field(..., description="Volume échangé")

class CCXTTestRequest(BaseModel):
    """Modèle pour la requête de test CCXT"""
    exchange: str = Field(..., description="Nom de l'exchange (ex: binance)")
    symbol: str = Field(..., description="Symbole du trading pair (ex: BTC/USDT)")
    timeframe: str = Field(..., description="Période (ex: 1h, 1d)")
    limit: Optional[int] = Field(default=50, le=500, description="Nombre de bougies à récupérer (max 500)")

class CurrentPriceInfo(BaseModel):
    """Modèle pour les informations de prix actuel"""
    current_price: float = Field(..., description="Prix actuel (dernier trade)")
    bid: Optional[float] = Field(None, description="Prix d'achat le plus élevé")
    ask: Optional[float] = Field(None, description="Prix de vente le plus bas")
    change_24h_percent: Optional[float] = Field(None, description="Variation 24h en pourcentage")
    volume_24h: Optional[float] = Field(None, description="Volume 24h")
    timestamp: Optional[int] = Field(None, description="Timestamp du prix")
    datetime: Optional[str] = Field(None, description="Date/heure du prix")

class CCXTTestResponse(BaseModel):
    """Modèle pour la réponse du test CCXT"""
    status: str = Field(..., description="Statut de la requête (success/error)")
    message: str = Field(..., description="Message descriptif")
    exchange: Optional[str] = Field(None, description="Nom de l'exchange utilisé")
    symbol: Optional[str] = Field(None, description="Symbole demandé")
    timeframe: Optional[str] = Field(None, description="Timeframe utilisée")
    count: Optional[int] = Field(None, description="Nombre de bougies retournées")
    data: Optional[List[OHLCVCandle]] = Field(None, description="Données OHLCV")
    current_price_info: Optional[CurrentPriceInfo] = Field(None, description="Informations prix actuel")

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