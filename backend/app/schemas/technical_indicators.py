from pydantic import BaseModel, Field
from typing import List, Optional

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