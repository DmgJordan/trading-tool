"""
Analyse de volume pour identifier les pics, tendances et signaux
"""

from typing import List, Dict, Union
from ..utils.formatters import round_decimal


def analyze_volume(volumes: List[float], period: int = 20) -> Dict[str, float]:
    """
    Analyse le volume actuel par rapport à la moyenne

    Args:
        volumes: Liste des volumes (ordre chronologique)
        period: Période pour la moyenne (défaut: 20)

    Returns:
        Dictionnaire avec current, avg20, spike_ratio

    Examples:
        >>> volumes = [100] * 19 + [200]  # Dernier volume doublé
        >>> result = analyze_volume(volumes, 20)
        >>> result["spike_ratio"] > 1.8  # Spike détecté
        True
    """
    if len(volumes) == 0:
        return {
            "current": 0.0,
            "avg20": 0.0,
            "spike_ratio": 0.0
        }

    try:
        current_volume = volumes[-1]

        # Calculer la moyenne des N dernières périodes
        if len(volumes) >= period:
            avg_volume = sum(volumes[-period:]) / period
        else:
            # Si pas assez de données, utiliser toutes les données disponibles
            avg_volume = sum(volumes) / len(volumes)

        # Calculer le ratio spike (current/average)
        spike_ratio = current_volume / avg_volume if avg_volume > 0 else 0.0

        result = {
            "current": round_decimal(current_volume, 2),
            "avg20": round_decimal(avg_volume, 2),
            "spike_ratio": round_decimal(spike_ratio, 2)
        }

        return result

    except Exception:
        return {
            "current": 0.0,
            "avg20": 0.0,
            "spike_ratio": 0.0
        }


def get_volume_interpretation(spike_ratio: float) -> str:
    """
    Interprète le ratio de volume

    Args:
        spike_ratio: Ratio volume actuel / moyenne

    Returns:
        Interprétation textuelle

    Examples:
        >>> get_volume_interpretation(3.5)
        'Volume extrême'
        >>> get_volume_interpretation(1.0)
        'Volume normal+'
        >>> get_volume_interpretation(0.3)
        'Volume très faible'
    """
    if spike_ratio >= 3.0:
        return "Volume extrême"
    elif spike_ratio >= 2.0:
        return "Volume très élevé"
    elif spike_ratio >= 1.5:
        return "Volume élevé"
    elif spike_ratio >= 1.0:
        return "Volume normal+"
    elif spike_ratio >= 0.7:
        return "Volume normal"
    elif spike_ratio >= 0.5:
        return "Volume faible"
    else:
        return "Volume très faible"


def get_volume_signal(spike_ratio: float, price_change_percent: float = 0) -> str:
    """
    Génère un signal basé sur le volume et la variation de prix

    Args:
        spike_ratio: Ratio de volume
        price_change_percent: Variation de prix en pourcentage

    Returns:
        Signal de trading basé sur le volume

    Examples:
        >>> get_volume_signal(2.5, 3.0)  # Volume élevé + prix en hausse
        'BREAKOUT_HAUSSIER'
        >>> get_volume_signal(2.5, -3.0)  # Volume élevé + prix en baisse
        'BREAKOUT_BAISSIER'
        >>> get_volume_signal(0.5, 0)  # Volume faible
        'CONSOLIDATION'
    """
    try:
        # Volume très élevé avec mouvement de prix
        if spike_ratio >= 2.0:
            if price_change_percent > 2:
                return "BREAKOUT_HAUSSIER"
            elif price_change_percent < -2:
                return "BREAKOUT_BAISSIER"
            else:
                return "VOLUME_SUSPECT"  # Volume élevé sans mouvement = suspect

        # Volume élevé
        elif spike_ratio >= 1.5:
            if price_change_percent > 1:
                return "MOMENTUM_HAUSSIER"
            elif price_change_percent < -1:
                return "MOMENTUM_BAISSIER"
            else:
                return "ACCUMULATION"

        # Volume faible
        elif spike_ratio < 0.7:
            return "CONSOLIDATION"

        else:
            return "NEUTRE"

    except Exception:
        return "NEUTRE"


def detect_volume_trend(volumes: List[float], period: int = 10) -> Dict[str, Union[str, float]]:
    """
    Détecte la tendance du volume sur une période (régression linéaire simple)

    Args:
        volumes: Liste des volumes
        period: Période d'analyse (défaut: 10)

    Returns:
        Dictionnaire avec la tendance, la force et la description

    Examples:
        >>> volumes = [100 + i*10 for i in range(15)]  # Volume croissant
        >>> result = detect_volume_trend(volumes, 10)
        >>> result["trend"]
        'CROISSANT'
    """
    if len(volumes) < period:
        return {
            "trend": "NEUTRE",
            "strength": 0.0,
            "description": "Pas assez de données"
        }

    try:
        recent_volumes = volumes[-period:]

        # Calculer la tendance (régression linéaire simple)
        n = len(recent_volumes)
        x_values = list(range(n))

        # Calcul de la pente
        x_mean = sum(x_values) / n
        y_mean = sum(recent_volumes) / n

        numerator = sum((x_values[i] - x_mean) * (recent_volumes[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Normaliser la pente par rapport à la moyenne des volumes
        normalized_slope = (slope / y_mean) * 100 if y_mean > 0 else 0

        # Déterminer la tendance
        if normalized_slope > 5:
            trend = "CROISSANT"
        elif normalized_slope < -5:
            trend = "DECROISSANT"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "strength": round_decimal(abs(normalized_slope), 2),
            "description": f"Volume {trend.lower()} avec force {abs(normalized_slope):.1f}%"
        }

    except Exception:
        return {
            "trend": "NEUTRE",
            "strength": 0.0,
            "description": "Erreur de calcul"
        }
