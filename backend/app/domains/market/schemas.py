from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# =============================================================================
# MARKET DATA SCHEMAS
# =============================================================================

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

# =============================================================================
# OHLCV SCHEMAS
# =============================================================================

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

# Versions allégées (sans bougies) pour Claude/IA
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

# =============================================================================
# TECHNICAL INDICATORS SCHEMAS
# =============================================================================

class RSIAnalysis(BaseModel):
    """Analyse RSI"""
    value: Optional[float] = Field(None, description="Valeur RSI (0-100)")
    interpretation: str = Field(..., description="Interprétation (Surachat, Survente, etc.)")
    signal: str = Field(..., description="Signal trading (ACHETER, VENDRE, NEUTRE)")

class MovingAveragesAnalysis(BaseModel):
    """Analyse des moyennes mobiles"""
    ma20: Optional[float] = Field(None, description="Moyenne mobile 20 périodes")
    ma50: Optional[float] = Field(None, description="Moyenne mobile 50 périodes")
    ma200: Optional[float] = Field(None, description="Moyenne mobile 200 périodes")
    current_price: Optional[float] = Field(None, description="Prix actuel pour comparaison")
    short_trend: str = Field(..., description="Tendance court terme (prix vs MA20)")
    medium_trend: str = Field(..., description="Tendance moyen terme (MA20 vs MA50)")
    long_trend: str = Field(..., description="Tendance long terme (MA50 vs MA200)")
    overall_signal: str = Field(..., description="Signal global des MA")
    crossover_20_50: Optional[str] = Field(None, description="Croisement MA20/MA50 (GOLDEN_CROSS, DEATH_CROSS)")
    crossover_50_200: Optional[str] = Field(None, description="Croisement MA50/MA200")

class VolumeAnalysis(BaseModel):
    """Analyse du volume"""
    current: float = Field(..., description="Volume actuel")
    avg20: float = Field(..., description="Volume moyen sur 20 périodes")
    spike_ratio: float = Field(..., description="Ratio volume actuel / moyenne")
    interpretation: str = Field(..., description="Interprétation du volume")
    signal: str = Field(..., description="Signal basé sur le volume")
    trend: str = Field(..., description="Tendance du volume (CROISSANT, DECROISSANT, STABLE)")
    trend_strength: float = Field(..., description="Force de la tendance volume (%)")
    price_change_percent: float = Field(..., description="Variation de prix pour contexte")

class SupportResistanceAnalysis(BaseModel):
    """Analyse support et résistance"""
    support_levels: List[float] = Field(..., description="Niveaux de support identifiés")
    resistance_levels: List[float] = Field(..., description="Niveaux de résistance identifiés")
    confidence_scores: List[float] = Field(..., description="Scores de confiance des niveaux")
    nearest_support: Optional[float] = Field(None, description="Support le plus proche en dessous du prix")
    nearest_resistance: Optional[float] = Field(None, description="Résistance la plus proche au-dessus du prix")
    total_levels: int = Field(..., description="Nombre total de niveaux détectés")

class OverallAnalysis(BaseModel):
    """Analyse globale combinant tous les indicateurs"""
    overall_signal: str = Field(..., description="Signal global (ACHAT_FORT, ACHAT, VENTE_FORTE, VENTE, NEUTRE)")
    signal_strength: int = Field(..., description="Force du signal (0-10)")
    active_signals: List[str] = Field(..., description="Liste des signaux actifs")
    score: int = Field(..., description="Score technique combiné")
    recommendation: str = Field(..., description="Recommandation textuelle")

class TechnicalAnalysis(BaseModel):
    """Analyse technique complète"""
    rsi: RSIAnalysis = Field(..., description="Analyse RSI")
    moving_averages: MovingAveragesAnalysis = Field(..., description="Analyse moyennes mobiles")
    volume_analysis: VolumeAnalysis = Field(..., description="Analyse du volume")
    support_resistance: SupportResistanceAnalysis = Field(..., description="Analyse support/résistance")
    overall_analysis: OverallAnalysis = Field(..., description="Analyse globale")
    analyzed_at: str = Field(..., description="Timestamp de l'analyse")
    data_points: int = Field(..., description="Nombre de bougies analysées")

# =============================================================================
# SCHEMAS FOR AI INTEGRATION
# =============================================================================

class ClaudeMarketData(BaseModel):
    """
    Données de marché enrichies pour l'analyse IA

    Utilisé par MarketService pour fournir des données formatées à l'IA
    """
    symbol: str = Field(..., description="Symbole de l'actif")
    name: str = Field(..., description="Nom de l'actif")
    current_price: float = Field(..., description="Prix actuel")
    price_change_24h: Optional[float] = Field(None, description="Variation 24h en %")
    volume_24h: Optional[float] = Field(None, description="Volume 24h")
    market_cap: Optional[float] = Field(None, description="Market cap")
    high_24h: Optional[float] = Field(None, description="Plus haut 24h")
    low_24h: Optional[float] = Field(None, description="Plus bas 24h")
    price_change_7d: Optional[float] = Field(None, description="Variation 7 jours")
    price_change_30d: Optional[float] = Field(None, description="Variation 30 jours")
    last_updated: datetime = Field(..., description="Dernière mise à jour")
