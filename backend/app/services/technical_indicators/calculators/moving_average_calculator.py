from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class MovingAverageCalculator:
    """Calculateur de moyennes mobiles simples (SMA)"""

    def calculate_sma(self, values: List[float], period: int) -> Optional[float]:
        """
        Calcule la moyenne mobile simple pour une période donnée

        Args:
            values: Liste des valeurs (prix de clôture généralement)
            period: Période pour la moyenne mobile

        Returns:
            Valeur de la moyenne mobile ou None si pas assez de données
        """
        if len(values) < period:
            logger.warning(f"Pas assez de données pour MA{period} ({len(values)} < {period})")
            return None

        try:
            # Prendre les dernières valeurs pour la période
            recent_values = values[-period:]
            sma = sum(recent_values) / period
            return round(sma, 2)

        except Exception as e:
            logger.error(f"Erreur calcul SMA{period}: {e}")
            return None

    def get_ma20_ma50_ma200(self, closes: List[float]) -> Dict[str, Optional[float]]:
        """
        Calcule les moyennes mobiles 20, 50 et 200 périodes

        Args:
            closes: Liste des prix de clôture

        Returns:
            Dictionnaire contenant ma20, ma50, ma200
        """
        result = {
            "ma20": self.calculate_sma(closes, 20),
            "ma50": self.calculate_sma(closes, 50),
            "ma200": self.calculate_sma(closes, 200)
        }

        logger.info(f"Moyennes mobiles calculées: MA20={result['ma20']}, MA50={result['ma50']}, MA200={result['ma200']}")
        return result

    def get_ma_trend(self, closes: List[float]) -> Dict[str, str]:
        """
        Détermine la tendance basée sur les moyennes mobiles

        Args:
            closes: Liste des prix de clôture

        Returns:
            Dictionnaire avec les tendances et signaux
        """
        mas = self.get_ma20_ma50_ma200(closes)
        current_price = closes[-1] if closes else 0

        trend_info = {
            "short_trend": "NEUTRE",
            "medium_trend": "NEUTRE",
            "long_trend": "NEUTRE",
            "overall_signal": "NEUTRE"
        }

        try:
            # Tendance court terme (prix vs MA20)
            if mas["ma20"] is not None:
                if current_price > mas["ma20"]:
                    trend_info["short_trend"] = "HAUSSIER"
                else:
                    trend_info["short_trend"] = "BAISSIER"

            # Tendance moyen terme (MA20 vs MA50)
            if mas["ma20"] is not None and mas["ma50"] is not None:
                if mas["ma20"] > mas["ma50"]:
                    trend_info["medium_trend"] = "HAUSSIER"
                else:
                    trend_info["medium_trend"] = "BAISSIER"

            # Tendance long terme (MA50 vs MA200)
            if mas["ma50"] is not None and mas["ma200"] is not None:
                if mas["ma50"] > mas["ma200"]:
                    trend_info["long_trend"] = "HAUSSIER"
                else:
                    trend_info["long_trend"] = "BAISSIER"

            # Signal global (alignement des MA)
            if (mas["ma20"] is not None and mas["ma50"] is not None and mas["ma200"] is not None):
                if (current_price > mas["ma20"] > mas["ma50"] > mas["ma200"]):
                    trend_info["overall_signal"] = "HAUSSIER_FORT"
                elif (current_price < mas["ma20"] < mas["ma50"] < mas["ma200"]):
                    trend_info["overall_signal"] = "BAISSIER_FORT"
                elif (current_price > mas["ma20"] and mas["ma20"] > mas["ma50"]):
                    trend_info["overall_signal"] = "HAUSSIER"
                elif (current_price < mas["ma20"] and mas["ma20"] < mas["ma50"]):
                    trend_info["overall_signal"] = "BAISSIER"

        except Exception as e:
            logger.error(f"Erreur analyse tendance MA: {e}")

        return trend_info

    def detect_ma_crossover(self, closes: List[float], short_period: int = 20, long_period: int = 50) -> Optional[str]:
        """
        Détecte les croisements de moyennes mobiles

        Args:
            closes: Prix de clôture
            short_period: Période courte
            long_period: Période longue

        Returns:
            "GOLDEN_CROSS" si MA courte croise au-dessus de MA longue
            "DEATH_CROSS" si MA courte croise en-dessous de MA longue
            None si pas de croisement
        """
        if len(closes) < long_period + 1:
            return None

        try:
            # Calculer les MA pour les 2 dernières bougies
            ma_short_current = self.calculate_sma(closes, short_period)
            ma_long_current = self.calculate_sma(closes, long_period)

            ma_short_previous = self.calculate_sma(closes[:-1], short_period)
            ma_long_previous = self.calculate_sma(closes[:-1], long_period)

            if all(v is not None for v in [ma_short_current, ma_long_current, ma_short_previous, ma_long_previous]):
                # Croisement haussier (Golden Cross)
                if ma_short_previous <= ma_long_previous and ma_short_current > ma_long_current:
                    return "GOLDEN_CROSS"
                # Croisement baissier (Death Cross)
                elif ma_short_previous >= ma_long_previous and ma_short_current < ma_long_current:
                    return "DEATH_CROSS"

            return None

        except Exception as e:
            logger.error(f"Erreur détection croisement MA: {e}")
            return None