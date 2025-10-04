"""
Calcul du RSI (Relative Strength Index) selon la méthode de Wilder
"""

from typing import List, Optional
from ..utils.formatters import round_decimal


def calculate_rsi(closes: List[float], period: int = 14) -> Optional[float]:
    """
    Calcule le RSI pour une série de prix de clôture selon la méthode de Wilder

    Args:
        closes: Liste des prix de clôture (ordre chronologique)
        period: Période pour le calcul du RSI (défaut: 14)

    Returns:
        Valeur RSI entre 0 et 100, ou None si pas assez de données

    Examples:
        >>> closes = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84,
        ...           46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]
        >>> rsi = calculate_rsi(closes, 14)
        >>> 60 < rsi < 80  # RSI devrait être dans cette zone
        True
    """
    if len(closes) < period + 1:
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

        # Vérifier qu'on a assez de données
        if len(gains) < period:
            return None

        # Calculer les moyennes initiales (période complète)
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

        return round_decimal(rsi, 2)

    except Exception:
        return None


def get_rsi_interpretation(rsi_value: float) -> str:
    """
    Retourne l'interprétation du RSI

    Args:
        rsi_value: Valeur RSI (entre 0 et 100)

    Returns:
        Interprétation textuelle

    Examples:
        >>> get_rsi_interpretation(75)
        'Surachat'
        >>> get_rsi_interpretation(25)
        'Survente'
        >>> get_rsi_interpretation(55)
        'Haussier'
    """
    if rsi_value >= 70:
        return "Surachat"
    elif rsi_value <= 30:
        return "Survente"
    elif rsi_value >= 50:
        return "Haussier"
    else:
        return "Baissier"


def get_rsi_signal(rsi_value: float) -> str:
    """
    Retourne le signal trading basé sur RSI

    Args:
        rsi_value: Valeur RSI (entre 0 et 100)

    Returns:
        Signal de trading

    Examples:
        >>> get_rsi_signal(85)
        'VENDRE_FORT'
        >>> get_rsi_signal(72)
        'VENDRE'
        >>> get_rsi_signal(25)
        'ACHETER_FORT'
        >>> get_rsi_signal(50)
        'NEUTRE'
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
