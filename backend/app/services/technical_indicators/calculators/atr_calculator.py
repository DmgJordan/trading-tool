from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ATRCalculator:
    """Calculateur ATR (Average True Range) selon la méthode de Wilder"""

    def __init__(self):
        self.default_period = 14

    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = None) -> Optional[float]:
        """
        Calcule l'ATR pour une série de données OHLC selon la méthode de Wilder

        Args:
            highs: Liste des prix les plus hauts
            lows: Liste des prix les plus bas
            closes: Liste des prix de clôture
            period: Période pour le calcul de l'ATR (défaut: 14)

        Returns:
            Valeur ATR, ou None si pas assez de données
        """
        if period is None:
            period = self.default_period

        if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
            logger.warning(f"Pas assez de données pour calculer ATR ({len(highs)} < {period + 1})")
            return None

        if len(highs) != len(lows) or len(highs) != len(closes):
            logger.error("Les listes highs, lows et closes doivent avoir la même longueur")
            return None

        try:
            # Calculer les True Ranges
            true_ranges = []
            for i in range(1, len(highs)):
                # TR = max(H-L, |H-C_prev|, |L-C_prev|)
                tr1 = highs[i] - lows[i]  # High - Low
                tr2 = abs(highs[i] - closes[i-1])  # |High - Previous Close|
                tr3 = abs(lows[i] - closes[i-1])   # |Low - Previous Close|

                true_range = max(tr1, tr2, tr3)
                true_ranges.append(true_range)

            if len(true_ranges) < period:
                logger.warning(f"Pas assez de True Ranges pour calcul ATR ({len(true_ranges)} < {period})")
                return None

            # Calculer l'ATR initial (SMA des 14 premiers TR)
            initial_atr = sum(true_ranges[:period]) / period

            # Appliquer la méthode de Wilder pour les valeurs suivantes
            # ATR[i] = (ATR[i-1] * (period-1) + TR[i]) / period
            current_atr = initial_atr

            for i in range(period, len(true_ranges)):
                current_atr = (current_atr * (period - 1) + true_ranges[i]) / period

            return current_atr

        except Exception as e:
            logger.error(f"Erreur calcul ATR: {e}")
            return None

    def get_atr_interpretation(self, atr_value: float, current_price: float) -> str:
        """
        Retourne l'interprétation de l'ATR par rapport au prix actuel

        Args:
            atr_value: Valeur ATR
            current_price: Prix actuel

        Returns:
            Interprétation textuelle
        """
        if current_price <= 0:
            return "Prix invalide"

        atr_percentage = (atr_value / current_price) * 100

        if atr_percentage >= 3.0:
            return "Très haute volatilité"
        elif atr_percentage >= 2.0:
            return "Haute volatilité"
        elif atr_percentage >= 1.0:
            return "Volatilité modérée"
        elif atr_percentage >= 0.5:
            return "Faible volatilité"
        else:
            return "Très faible volatilité"

    def get_atr_signal(self, current_atr: float, previous_atr: float) -> str:
        """
        Retourne le signal basé sur l'évolution de l'ATR

        Args:
            current_atr: ATR actuel
            previous_atr: ATR précédent

        Returns:
            Signal de volatilité
        """
        if previous_atr <= 0:
            return "NEUTRE"

        change_percentage = ((current_atr - previous_atr) / previous_atr) * 100

        if change_percentage >= 20:
            return "VOLATILITE_CROISSANTE_FORTE"
        elif change_percentage >= 10:
            return "VOLATILITE_CROISSANTE"
        elif change_percentage <= -20:
            return "VOLATILITE_DECROISSANTE_FORTE"
        elif change_percentage <= -10:
            return "VOLATILITE_DECROISSANTE"
        else:
            return "VOLATILITE_STABLE"