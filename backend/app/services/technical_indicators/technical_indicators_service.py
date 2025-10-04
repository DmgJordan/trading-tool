from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ...shared import (
    # RSI
    calculate_rsi,
    get_rsi_interpretation,
    get_rsi_signal,
    # Moving Averages
    calculate_multiple_sma,
    get_ma_trend,
    detect_ma_crossover,
    # Volume
    analyze_volume,
    get_volume_interpretation,
    get_volume_signal,
    detect_volume_trend,
    # Support/Resistance
    detect_levels,
    get_nearest_levels,
    SupportResistanceLevel,
    # Formatters
    round_decimal
)

logger = logging.getLogger(__name__)

class TechnicalIndicatorsService:
    """Service principal pour l'analyse technique des données OHLCV"""

    async def analyze_ohlcv_data(self, ohlcv_data: List[Dict], current_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Effectue une analyse technique complète des données OHLCV

        Args:
            ohlcv_data: Liste des données OHLCV avec timestamp, open, high, low, close, volume
            current_price: Prix actuel pour le contexte (optionnel)

        Returns:
            Dictionnaire contenant tous les indicateurs techniques
        """
        if not ohlcv_data:
            logger.warning("Aucune donnée OHLCV fournie pour l'analyse")
            return self._get_empty_analysis()

        try:
            logger.info(f"Analyse technique de {len(ohlcv_data)} bougies")

            # Extraire les données pour les calculs
            closes = [float(candle['close']) for candle in ohlcv_data]
            volumes = [float(candle['volume']) for candle in ohlcv_data]

            # Utiliser le dernier prix de clôture si pas de prix actuel fourni
            analysis_price = current_price if current_price is not None else closes[-1]

            # 1. Calcul RSI
            rsi_result = self._calculate_rsi_analysis(closes)

            # 2. Calcul des moyennes mobiles
            ma_result = self._calculate_moving_averages_analysis(closes, analysis_price)

            # 3. Analyse du volume
            volume_result = self._calculate_volume_analysis(volumes, closes)

            # 4. Détection support/résistance
            sr_result = self._calculate_support_resistance_analysis(ohlcv_data, analysis_price)

            # 5. Analyse globale et signaux
            overall_analysis = self._calculate_overall_analysis(rsi_result, ma_result, volume_result, sr_result)

            # Assembler le résultat final
            technical_analysis = {
                "rsi": rsi_result,
                "moving_averages": ma_result,
                "volume_analysis": volume_result,
                "support_resistance": sr_result,
                "overall_analysis": overall_analysis,
                "analyzed_at": datetime.utcnow().isoformat(),
                "data_points": len(ohlcv_data)
            }

            logger.info("Analyse technique terminée avec succès")
            return technical_analysis

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse technique: {e}")
            return self._get_empty_analysis()

    def _calculate_rsi_analysis(self, closes: List[float]) -> Dict[str, Any]:
        """Calcule l'analyse RSI"""
        try:
            rsi_value = calculate_rsi(closes)

            if rsi_value is None:
                return {"value": None, "interpretation": "Pas assez de données", "signal": "NEUTRE"}

            return {
                "value": rsi_value,
                "interpretation": get_rsi_interpretation(rsi_value),
                "signal": get_rsi_signal(rsi_value)
            }
        except Exception as e:
            logger.error(f"Erreur calcul RSI: {e}")
            return {"value": None, "interpretation": "Erreur", "signal": "NEUTRE"}

    def _calculate_moving_averages_analysis(self, closes: List[float], current_price: float) -> Dict[str, Any]:
        """Calcule l'analyse des moyennes mobiles"""
        try:
            # Calcul des moyennes mobiles
            mas = calculate_multiple_sma(closes, [20, 50, 200])

            # Analyse des tendances
            trend_info = get_ma_trend(closes, [20, 50, 200])

            # Détection des croisements
            golden_cross_20_50 = detect_ma_crossover(closes, 20, 50)
            golden_cross_50_200 = detect_ma_crossover(closes, 50, 200)

            return {
                "ma20": mas["ma20"],
                "ma50": mas["ma50"],
                "ma200": mas["ma200"],
                "current_price": current_price,
                "short_trend": trend_info["short_trend"],
                "medium_trend": trend_info["medium_trend"],
                "long_trend": trend_info["long_trend"],
                "overall_signal": trend_info["overall_signal"],
                "crossover_20_50": golden_cross_20_50,
                "crossover_50_200": golden_cross_50_200
            }
        except Exception as e:
            logger.error(f"Erreur calcul moyennes mobiles: {e}")
            return {
                "ma20": None, "ma50": None, "ma200": None,
                "current_price": current_price,
                "short_trend": "NEUTRE", "medium_trend": "NEUTRE", "long_trend": "NEUTRE",
                "overall_signal": "NEUTRE", "crossover_20_50": None, "crossover_50_200": None
            }

    def _calculate_volume_analysis(self, volumes: List[float], closes: List[float]) -> Dict[str, Any]:
        """Calcule l'analyse du volume"""
        try:
            # Analyse du volume actuel
            volume_analysis = analyze_volume(volumes)

            # Calcul de la variation de prix pour le signal volume
            price_change_percent = 0
            if len(closes) >= 2:
                price_change_percent = ((closes[-1] - closes[-2]) / closes[-2]) * 100

            # Interprétation et signal
            spike_ratio = volume_analysis["spike_ratio"]
            interpretation = get_volume_interpretation(spike_ratio)
            signal = get_volume_signal(spike_ratio, price_change_percent)

            # Tendance du volume
            volume_trend = detect_volume_trend(volumes)

            return {
                "current": volume_analysis["current"],
                "avg20": volume_analysis["avg20"],
                "spike_ratio": volume_analysis["spike_ratio"],
                "interpretation": interpretation,
                "signal": signal,
                "trend": volume_trend["trend"],
                "trend_strength": volume_trend["strength"],
                "price_change_percent": round_decimal(price_change_percent, 2)
            }
        except Exception as e:
            logger.error(f"Erreur analyse volume: {e}")
            return {
                "current": 0, "avg20": 0, "spike_ratio": 0,
                "interpretation": "Erreur", "signal": "NEUTRE",
                "trend": "NEUTRE", "trend_strength": 0, "price_change_percent": 0
            }

    def _calculate_support_resistance_analysis(self, ohlcv_data: List[Dict], current_price: float) -> Dict[str, Any]:
        """Calcule l'analyse support/résistance"""
        try:
            # Détection des niveaux avec la fonction pure
            sr_result = detect_levels(ohlcv_data)

            # Créer des objets SupportResistanceLevel pour get_nearest_levels
            levels = []

            # Ajouter les supports
            for price, confidence in zip(sr_result["support_levels"], sr_result["confidence_scores"]):
                level = SupportResistanceLevel(
                    price=price,
                    is_resistance=False,
                    confidence_score=confidence,
                    touches=2,  # Minimum
                    volume_confirmation=0,
                    first_occurrence=0,
                    last_occurrence=len(ohlcv_data) - 1
                )
                levels.append(level)

            # Ajouter les résistances
            for price, confidence in zip(sr_result["resistance_levels"], sr_result["confidence_scores"][len(sr_result["support_levels"]):]):
                level = SupportResistanceLevel(
                    price=price,
                    is_resistance=True,
                    confidence_score=confidence,
                    touches=2,
                    volume_confirmation=0,
                    first_occurrence=0,
                    last_occurrence=len(ohlcv_data) - 1
                )
                levels.append(level)

            # Trouver les niveaux les plus proches
            nearest = get_nearest_levels(current_price, levels)

            return {
                "support_levels": sr_result["support_levels"],
                "resistance_levels": sr_result["resistance_levels"],
                "confidence_scores": sr_result["confidence_scores"],
                "nearest_support": nearest["nearest_support"],
                "nearest_resistance": nearest["nearest_resistance"],
                "total_levels": len(sr_result["support_levels"]) + len(sr_result["resistance_levels"])
            }
        except Exception as e:
            logger.error(f"Erreur analyse support/résistance: {e}")
            return {
                "support_levels": [], "resistance_levels": [], "confidence_scores": [],
                "nearest_support": None, "nearest_resistance": None, "total_levels": 0
            }

    def _calculate_overall_analysis(self, rsi: Dict, ma: Dict, volume: Dict, sr: Dict) -> Dict[str, Any]:
        """Calcule une analyse globale et des signaux combinés"""
        try:
            signals = []
            score = 0

            # Analyse RSI
            if rsi["signal"] in ["ACHETER", "ACHETER_FORT"]:
                signals.append("RSI_HAUSSIER")
                score += 2 if rsi["signal"] == "ACHETER_FORT" else 1
            elif rsi["signal"] in ["VENDRE", "VENDRE_FORT"]:
                signals.append("RSI_BAISSIER")
                score -= 2 if rsi["signal"] == "VENDRE_FORT" else 1

            # Analyse moyennes mobiles
            if ma["overall_signal"] == "HAUSSIER_FORT":
                signals.append("MA_HAUSSIER_FORT")
                score += 3
            elif ma["overall_signal"] == "HAUSSIER":
                signals.append("MA_HAUSSIER")
                score += 2
            elif ma["overall_signal"] == "BAISSIER_FORT":
                signals.append("MA_BAISSIER_FORT")
                score -= 3
            elif ma["overall_signal"] == "BAISSIER":
                signals.append("MA_BAISSIER")
                score -= 2

            # Croisements de moyennes mobiles
            if ma["crossover_20_50"] == "GOLDEN_CROSS":
                signals.append("GOLDEN_CROSS_20_50")
                score += 2
            elif ma["crossover_20_50"] == "DEATH_CROSS":
                signals.append("DEATH_CROSS_20_50")
                score -= 2

            # Analyse volume
            if volume["signal"] in ["BREAKOUT_HAUSSIER", "MOMENTUM_HAUSSIER"]:
                signals.append(f"VOLUME_{volume['signal']}")
                score += 1
            elif volume["signal"] in ["BREAKOUT_BAISSIER", "MOMENTUM_BAISSIER"]:
                signals.append(f"VOLUME_{volume['signal']}")
                score -= 1

            # Signal global
            if score >= 5:
                overall_signal = "ACHAT_FORT"
            elif score >= 2:
                overall_signal = "ACHAT"
            elif score <= -5:
                overall_signal = "VENTE_FORTE"
            elif score <= -2:
                overall_signal = "VENTE"
            else:
                overall_signal = "NEUTRE"

            return {
                "overall_signal": overall_signal,
                "signal_strength": abs(score),
                "active_signals": signals,
                "score": score,
                "recommendation": self._get_recommendation(overall_signal, score)
            }

        except Exception as e:
            logger.error(f"Erreur analyse globale: {e}")
            return {
                "overall_signal": "NEUTRE", "signal_strength": 0,
                "active_signals": [], "score": 0,
                "recommendation": "Analyse impossible"
            }

    def _get_recommendation(self, signal: str, score: int) -> str:
        """Génère une recommandation textuelle"""
        recommendations = {
            "ACHAT_FORT": "Signal d'achat fort - Tous les indicateurs sont alignés positivement",
            "ACHAT": "Signal d'achat - Tendance haussière confirmée par plusieurs indicateurs",
            "VENTE_FORTE": "Signal de vente fort - Tous les indicateurs sont alignés négativement",
            "VENTE": "Signal de vente - Tendance baissière confirmée par plusieurs indicateurs",
            "NEUTRE": "Signal neutre - Indicateurs mixtes, attendre confirmation"
        }
        return recommendations.get(signal, "Aucune recommandation")

    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Retourne une analyse vide en cas d'erreur"""
        return {
            "rsi": {"value": None, "interpretation": "Non disponible", "signal": "NEUTRE"},
            "moving_averages": {
                "ma20": None, "ma50": None, "ma200": None, "current_price": None,
                "short_trend": "NEUTRE", "medium_trend": "NEUTRE", "long_trend": "NEUTRE",
                "overall_signal": "NEUTRE", "crossover_20_50": None, "crossover_50_200": None
            },
            "volume_analysis": {
                "current": 0, "avg20": 0, "spike_ratio": 0,
                "interpretation": "Non disponible", "signal": "NEUTRE",
                "trend": "NEUTRE", "trend_strength": 0, "price_change_percent": 0
            },
            "support_resistance": {
                "support_levels": [], "resistance_levels": [], "confidence_scores": [],
                "nearest_support": None, "nearest_resistance": None, "total_levels": 0
            },
            "overall_analysis": {
                "overall_signal": "NEUTRE", "signal_strength": 0,
                "active_signals": [], "score": 0,
                "recommendation": "Données insuffisantes pour l'analyse"
            },
            "analyzed_at": datetime.utcnow().isoformat(),
            "data_points": 0
        }