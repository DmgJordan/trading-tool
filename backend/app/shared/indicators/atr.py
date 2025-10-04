"""
Calcul de l'ATR (Average True Range) selon la méthode de Wilder
"""

from typing import List, Optional
from ..utils.formatters import round_decimal


def calculate_atr(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    period: int = 14
) -> Optional[float]:
    """
    Calcule l'ATR pour une série de données OHLC selon la méthode de Wilder

    Args:
        highs: Liste des prix les plus hauts
        lows: Liste des prix les plus bas
        closes: Liste des prix de clôture
        period: Période pour le calcul de l'ATR (défaut: 14)

    Returns:
        Valeur ATR, ou None si pas assez de données ou erreur

    Examples:
        >>> highs = [45, 46, 47, 46, 48, 49, 50, 51, 52, 51, 53, 54, 53, 55, 56]
        >>> lows = [44, 45, 45, 44, 46, 47, 48, 49, 50, 49, 51, 52, 51, 53, 54]
        >>> closes = [44.5, 45.5, 46, 45, 47, 48, 49, 50, 51, 50, 52, 53, 52, 54, 55]
        >>> atr = calculate_atr(highs, lows, closes, 14)
        >>> atr > 0
        True
    """
    # Validation des inputs
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None

    if len(highs) != len(lows) or len(highs) != len(closes):
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
            return None

        # Calculer l'ATR initial (SMA des 14 premiers TR)
        initial_atr = sum(true_ranges[:period]) / period

        # Appliquer la méthode de Wilder pour les valeurs suivantes
        # ATR[i] = (ATR[i-1] * (period-1) + TR[i]) / period
        current_atr = initial_atr

        for i in range(period, len(true_ranges)):
            current_atr = (current_atr * (period - 1) + true_ranges[i]) / period

        return round_decimal(current_atr, 2)

    except Exception:
        return None


def get_atr_interpretation(atr_value: float, current_price: float) -> str:
    """
    Retourne l'interprétation de l'ATR par rapport au prix actuel

    Args:
        atr_value: Valeur ATR
        current_price: Prix actuel

    Returns:
        Interprétation textuelle de la volatilité

    Examples:
        >>> get_atr_interpretation(150, 50000)  # ATR 150 sur BTC à 50k
        'Très faible volatilité'
        >>> get_atr_interpretation(1500, 50000)  # ATR 1500 sur BTC à 50k
        'Haute volatilité'
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


def get_atr_signal(current_atr: float, previous_atr: float) -> str:
    """
    Retourne le signal basé sur l'évolution de l'ATR

    Args:
        current_atr: ATR actuel
        previous_atr: ATR précédent

    Returns:
        Signal de volatilité

    Examples:
        >>> get_atr_signal(150, 100)  # ATR en forte hausse
        'VOLATILITE_CROISSANTE_FORTE'
        >>> get_atr_signal(100, 150)  # ATR en forte baisse
        'VOLATILITE_DECROISSANTE_FORTE'
        >>> get_atr_signal(105, 100)  # ATR stable
        'VOLATILITE_STABLE'
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
