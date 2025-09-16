from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class MarketDataBase(BaseModel):
    """Schéma de base pour les données de marché"""
    symbol: str = Field(..., description="Symbole de la crypto (ex: BTC, ETH)")
    name: Optional[str] = Field(None, description="Nom complet de la crypto")
    price_usd: float = Field(..., description="Prix en USD")
    price_change_24h: Optional[float] = Field(None, description="Changement de prix en % sur 24h")
    price_change_24h_abs: Optional[float] = Field(None, description="Changement de prix absolu sur 24h")
    volume_24h_usd: Optional[float] = Field(None, description="Volume 24h en USD")
    market_cap_usd: Optional[float] = Field(None, description="Market cap en USD")
    source: str = Field(..., description="Source des données (coingecko, hyperliquid)")
    source_id: Optional[str] = Field(None, description="ID spécifique de la source")
    data_timestamp: datetime = Field(..., description="Timestamp des données")

class MarketDataCreate(MarketDataBase):
    """Schéma pour créer des données de marché"""
    raw_data: Optional[str] = Field(None, description="Données brutes JSON")

class MarketDataUpdate(BaseModel):
    """Schéma pour mettre à jour des données de marché"""
    price_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_24h_abs: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None

class MarketData(MarketDataBase):
    """Schéma complet des données de marché"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class MarketDataResponse(BaseModel):
    """Schéma de réponse pour une requête de données de marché"""
    status: Literal["success", "error"]
    message: str
    symbol: Optional[str] = None
    data: Optional[MarketData] = None
    historical_data: Optional[List[MarketData]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MarketDataRequest(BaseModel):
    """Schéma pour requêter des données de marché"""
    symbol: str = Field(..., description="Symbole à rechercher (ex: BTC, ETH)")
    source: Optional[Literal["coingecko", "hyperliquid", "auto"]] = Field(
        default="auto",
        description="Source préférée (auto = meilleure source disponible)"
    )
    include_historical: bool = Field(
        default=False,
        description="Inclure les données historiques"
    )
    hours_back: int = Field(
        default=24,
        description="Nombre d'heures d'historique à récupérer"
    )

class HistoricalDataRequest(BaseModel):
    """Schéma pour requêter des données historiques"""
    symbol: str = Field(..., description="Symbole à rechercher")
    from_date: Optional[datetime] = Field(None, description="Date de début")
    to_date: Optional[datetime] = Field(None, description="Date de fin")
    limit: int = Field(default=100, le=1000, description="Nombre maximum d'entrées")
    source: Optional[str] = Field(None, description="Filtrer par source")

class SupportedSymbolsResponse(BaseModel):
    """Schéma pour la liste des symboles supportés"""
    status: Literal["success", "error"]
    message: str
    coingecko_symbols: Optional[List[str]] = None
    hyperliquid_symbols: Optional[List[str]] = None
    total_symbols: int = 0

class MarketDataBatch(BaseModel):
    """Schéma pour traiter plusieurs symboles en lot"""
    symbols: List[str] = Field(..., max_items=50, description="Liste des symboles (max 50)")
    source: Optional[Literal["coingecko", "hyperliquid", "auto"]] = Field(default="auto")

class MarketDataBatchResponse(BaseModel):
    """Schéma de réponse pour les requêtes en lot"""
    status: Literal["success", "partial", "error"]
    message: str
    successful_count: int = 0
    failed_count: int = 0
    data: List[MarketData] = []
    errors: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)