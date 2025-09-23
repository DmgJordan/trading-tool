from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class RSICalculator:
    """Calculateur RSI (Relative Strength Index) selon la méthode de Wilder"""

    def __init__(self):
        self.default_period = 14

    def calculate_rsi(self, closes: List[float], period: int = None) -> Optional[float]:
        """
        Calcule le RSI pour une série de prix de clôture

        Args:
            closes: Liste des prix de clôture (ordre chronologique)
            period: Période pour le calcul du RSI (défaut: 14)

        Returns:
            Valeur RSI entre 0 et 100, ou None si pas assez de données
        """
        if period is None:
            period = self.default_period

        if len(closes) < period + 1:
            logger.warning(f"Pas assez de données pour calculer RSI ({len(closes)} < {period + 1})")
            return None

        try:
            # Calculer les variations de prix
            price_changes = []
            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                price_changes.append(change)

            # Séparer gains et pertes
            gains = [max(change, 0) for change in price_changes]
            losses = [abs(min(change, 0)) for change in price_changes]

            # Calculer les moyennes initiales (période complète)
            if len(gains) < period:
                return None

            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period

            # Calculer RSI avec moyennes mobiles exponentielles de Wilder
            # Pour les valeurs suivantes, utiliser la formule de Wilder
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            # Éviter division par zéro
            if avg_loss == 0:
                return 100.0

            # Calculer RS et RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return round(rsi, 2)

        except Exception as e:
            logger.error(f"Erreur calcul RSI: {e}")
            return None

    def get_rsi_interpretation(self, rsi_value: float) -> str:
        """
        Retourne l'interprétation du RSI

        Args:
            rsi_value: Valeur RSI

        Returns:
            Interprétation textuelle
        """
        if rsi_value >= 70:
            return "Surachat"
        elif rsi_value <= 30:
            return "Survente"
        elif rsi_value >= 50:
            return "Haussier"
        else:
            return "Baissier"

    def get_rsi_signal(self, rsi_value: float) -> str:
        """
        Retourne le signal trading basé sur RSI

        Args:
            rsi_value: Valeur RSI

        Returns:
            Signal de trading
        """
        if rsi_value >= 80:
            return "VENDRE_FORT"
        elif rsi_value >= 70:
            return "VENDRE"
        elif rsi_value <= 20:
            return "ACHETER_FORT"
        elif rsi_value <= 30:
            return "ACHETER"
        else:
            return "NEUTRE"