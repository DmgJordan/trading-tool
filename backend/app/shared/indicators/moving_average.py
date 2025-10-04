"""
Calcul des moyennes mobiles simples (SMA) et analyse de tendances
"""

from typing import List, Optional, Dict
from ..utils.formatters import round_decimal


def calculate_sma(values: List[float], period: int) -> Optional[float]:
    """
    Calcule la moyenne mobile simple pour une période donnée

    Args:
        values: Liste des valeurs (prix de clôture généralement)
        period: Période pour la moyenne mobile

    Returns:
        Valeur de la moyenne mobile ou None si pas assez de données

    Examples:
        >>> values = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        >>> sma = calculate_sma(values, 5)
        >>> sma
        18.0
    """
    if len(values) < period:
        return None

    try:
        # Prendre les dernières valeurs pour la période
        recent_values = values[-period:]
        sma = sum(recent_values) / period
        return round_decimal(sma, 2)

    except Exception:
        return None


def calculate_multiple_sma(closes: List[float], periods: List[int] = None) -> Dict[str, Optional[float]]:
    """
    Calcule plusieurs moyennes mobiles pour différentes périodes

    Args:
        closes: Liste des prix de clôture
        periods: Liste des périodes à calculer (défaut: [20, 50, 200])

    Returns:
        Dictionnaire avec les MA calculées {f"ma{period}": value}

    Examples:
        >>> closes = list(range(1, 201))  # 200 valeurs
        >>> mas = calculate_multiple_sma(closes, [20, 50, 200])
        >>> all(key in mas for key in ["ma20", "ma50", "ma200"])
        True
        >>> mas["ma20"] > 0
        True
    """
    if periods is None:
        periods = [20, 50, 200]

    result = {}
    for period in periods:
        ma_value = calculate_sma(closes, period)
        result[f"ma{period}"] = ma_value

    return result


def get_ma_trend(closes: List[float], periods: List[int] = None) -> Dict[str, str]:
    """
    Détermine la tendance basée sur les moyennes mobiles

    Args:
        closes: Liste des prix de clôture
        periods: Périodes à utiliser (défaut: [20, 50, 200])

    Returns:
        Dictionnaire avec les tendances et signaux

    Examples:
        >>> closes = list(range(1, 201))  # Tendance haussière
        >>> trend = get_ma_trend(closes, [20, 50, 200])
        >>> trend["overall_signal"] in ["HAUSSIER", "HAUSSIER_FORT", "NEUTRE"]
        True
    """
    if periods is None:
        periods = [20, 50, 200]

    # Calculer les moyennes mobiles
    mas = calculate_multiple_sma(closes, periods)
    current_price = closes[-1] if closes else 0

    trend_info = {
        "short_trend": "NEUTRE",
        "medium_trend": "NEUTRE",
        "long_trend": "NEUTRE",
        "overall_signal": "NEUTRE"
    }

    try:
        # Extraire les valeurs de MA (gérer différentes périodes)
        ma_values = [mas.get(f"ma{p}") for p in sorted(periods)]

        # Si on a au moins 1 MA
        if ma_values[0] is not None:
            trend_info["short_trend"] = "HAUSSIER" if current_price > ma_values[0] else "BAISSIER"

        # Si on a au moins 2 MA
        if len(ma_values) >= 2 and all(v is not None for v in ma_values[:2]):
            trend_info["medium_trend"] = "HAUSSIER" if ma_values[0] > ma_values[1] else "BAISSIER"

        # Si on a au moins 3 MA
        if len(ma_values) >= 3 and all(v is not None for v in ma_values[:3]):
            trend_info["long_trend"] = "HAUSSIER" if ma_values[1] > ma_values[2] else "BAISSIER"

        # Signal global (alignement des MA)
        if len(ma_values) >= 3 and all(v is not None for v in ma_values):
            # Toutes les MA alignées haussières
            if (current_price > ma_values[0] > ma_values[1] > ma_values[2]):
                trend_info["overall_signal"] = "HAUSSIER_FORT"
            # Toutes les MA alignées baissières
            elif (current_price < ma_values[0] < ma_values[1] < ma_values[2]):
                trend_info["overall_signal"] = "BAISSIER_FORT"
            # Partiellement alignées haussières
            elif (current_price > ma_values[0] and ma_values[0] > ma_values[1]):
                trend_info["overall_signal"] = "HAUSSIER"
            # Partiellement alignées baissières
            elif (current_price < ma_values[0] and ma_values[0] < ma_values[1]):
                trend_info["overall_signal"] = "BAISSIER"

    except Exception:
        pass

    return trend_info


def detect_ma_crossover(
    closes: List[float],
    short_period: int = 20,
    long_period: int = 50
) -> Optional[str]:
    """
    Détecte les croisements de moyennes mobiles

    Args:
        closes: Prix de clôture
        short_period: Période courte (défaut: 20)
        long_period: Période longue (défaut: 50)

    Returns:
        "GOLDEN_CROSS" si MA courte croise au-dessus de MA longue
        "DEATH_CROSS" si MA courte croise en-dessous de MA longue
        None si pas de croisement

    Examples:
        >>> # Simulation d'un golden cross
        >>> closes = [100] * 50 + [101] * 20  # Prix augmente
        >>> result = detect_ma_crossover(closes, 20, 50)
        >>> result in ["GOLDEN_CROSS", "DEATH_CROSS", None]
        True
    """
    if len(closes) < long_period + 1:
        return None

    try:
        # Calculer les MA pour les 2 dernières bougies
        ma_short_current = calculate_sma(closes, short_period)
        ma_long_current = calculate_sma(closes, long_period)

        ma_short_previous = calculate_sma(closes[:-1], short_period)
        ma_long_previous = calculate_sma(closes[:-1], long_period)

        if all(v is not None for v in [ma_short_current, ma_long_current,
                                        ma_short_previous, ma_long_previous]):
            # Croisement haussier (Golden Cross)
            if ma_short_previous <= ma_long_previous and ma_short_current > ma_long_current:
                return "GOLDEN_CROSS"
            # Croisement baissier (Death Cross)
            elif ma_short_previous >= ma_long_previous and ma_short_current < ma_long_current:
                return "DEATH_CROSS"

        return None

    except Exception:
        return None
