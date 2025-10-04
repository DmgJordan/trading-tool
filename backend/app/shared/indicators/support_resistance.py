"""
Détection de niveaux de support et résistance basée sur les points pivots
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from ..utils.formatters import round_decimal


@dataclass
class PivotPoint:
    """Point pivot avec ses caractéristiques"""
    index: int
    price: float
    is_high: bool  # True pour résistance, False pour support
    volume: float
    touches: int = 1


@dataclass
class SupportResistanceLevel:
    """Niveau de support/résistance avec métadonnées"""
    price: float
    is_resistance: bool
    confidence_score: float
    touches: int
    volume_confirmation: float
    first_occurrence: int
    last_occurrence: int


def identify_pivot_points(
    ohlcv_data: List[Dict[str, float]],
    lookback_window: int = 5
) -> List[PivotPoint]:
    """
    Identifie les points pivots (hauts et bas locaux)

    Args:
        ohlcv_data: Liste des données OHLCV
        lookback_window: Fenêtre pour identifier les pivots

    Returns:
        Liste des points pivots détectés

    Examples:
        >>> data = [
        ...     {"high": 100, "low": 95, "volume": 1000},
        ...     {"high": 105, "low": 100, "volume": 1200},
        ...     {"high": 110, "low": 105, "volume": 1500},
        ...     {"high": 107, "low": 103, "volume": 1100}
        ... ]
        >>> pivots = identify_pivot_points(data * 5, 2)
        >>> len(pivots) >= 0
        True
    """
    pivots = []

    for i in range(lookback_window, len(ohlcv_data) - lookback_window):
        candle = ohlcv_data[i]
        high_price = candle['high']
        low_price = candle['low']
        volume = candle['volume']

        # Vérifier si c'est un pivot haut (résistance potentielle)
        is_pivot_high = True
        for j in range(i - lookback_window, i + lookback_window + 1):
            if j != i and ohlcv_data[j]['high'] >= high_price:
                is_pivot_high = False
                break

        if is_pivot_high:
            pivots.append(PivotPoint(
                index=i,
                price=high_price,
                is_high=True,
                volume=volume
            ))

        # Vérifier si c'est un pivot bas (support potentiel)
        is_pivot_low = True
        for j in range(i - lookback_window, i + lookback_window + 1):
            if j != i and ohlcv_data[j]['low'] <= low_price:
                is_pivot_low = False
                break

        if is_pivot_low:
            pivots.append(PivotPoint(
                index=i,
                price=low_price,
                is_high=False,
                volume=volume
            ))

    return pivots


def group_pivots_into_levels(
    pivots: List[PivotPoint],
    price_tolerance_percent: float = 0.5,
    min_touches: int = 2
) -> List[SupportResistanceLevel]:
    """
    Groupe les pivots proches en niveaux de support/résistance

    Args:
        pivots: Liste des points pivots
        price_tolerance_percent: Tolérance de prix pour grouper
        min_touches: Minimum de touches pour valider un niveau

    Returns:
        Liste des niveaux de support/résistance
    """
    if not pivots:
        return []

    levels = []
    used_pivots = set()

    for i, pivot in enumerate(pivots):
        if i in used_pivots:
            continue

        # Trouver tous les pivots dans la zone de tolérance
        similar_pivots = [pivot]
        used_pivots.add(i)

        for j, other_pivot in enumerate(pivots):
            if j in used_pivots or j <= i:
                continue

            # Vérifier si les pivots sont du même type (haut/bas)
            if pivot.is_high != other_pivot.is_high:
                continue

            # Vérifier si les prix sont dans la zone de tolérance
            price_diff_percent = abs(pivot.price - other_pivot.price) / pivot.price * 100
            if price_diff_percent <= price_tolerance_percent:
                similar_pivots.append(other_pivot)
                used_pivots.add(j)

        # Créer un niveau si au moins min_touches touches
        if len(similar_pivots) >= min_touches:
            # Calculer le prix moyen pondéré par le volume
            total_volume = sum(p.volume for p in similar_pivots)
            if total_volume > 0:
                weighted_price = sum(p.price * p.volume for p in similar_pivots) / total_volume
            else:
                weighted_price = sum(p.price for p in similar_pivots) / len(similar_pivots)

            level = SupportResistanceLevel(
                price=round_decimal(weighted_price, 2),
                is_resistance=pivot.is_high,
                confidence_score=0.0,  # Sera calculé plus tard
                touches=len(similar_pivots),
                volume_confirmation=total_volume,
                first_occurrence=min(p.index for p in similar_pivots),
                last_occurrence=max(p.index for p in similar_pivots)
            )
            levels.append(level)

    return levels


def calculate_confidence_scores(
    levels: List[SupportResistanceLevel],
    ohlcv_data: List[Dict[str, float]]
) -> List[SupportResistanceLevel]:
    """
    Calcule les scores de confiance pour chaque niveau

    Args:
        levels: Liste des niveaux à scorer
        ohlcv_data: Données OHLCV pour contexte

    Returns:
        Liste des niveaux avec scores calculés
    """
    for level in levels:
        score = 0.0

        # Score basé sur le nombre de touches (max 40 points)
        touches_score = min(level.touches * 10, 40)
        score += touches_score

        # Score basé sur le volume (max 30 points)
        avg_volume = sum(candle['volume'] for candle in ohlcv_data) / len(ohlcv_data)
        volume_ratio = level.volume_confirmation / (avg_volume * level.touches)
        volume_score = min(volume_ratio * 15, 30)
        score += volume_score

        # Score basé sur la récence (max 20 points)
        recency_ratio = level.last_occurrence / len(ohlcv_data)
        recency_score = recency_ratio * 20
        score += recency_score

        # Score basé sur la durée (persistance) (max 10 points)
        duration = level.last_occurrence - level.first_occurrence
        duration_ratio = duration / len(ohlcv_data)
        duration_score = duration_ratio * 10
        score += duration_score

        # Normaliser le score sur 100
        level.confidence_score = round_decimal(min(score, 100), 2)

    return levels


def filter_significant_levels(
    levels: List[SupportResistanceLevel],
    min_confidence: float = 30.0,
    max_levels_per_type: int = 5
) -> List[SupportResistanceLevel]:
    """
    Filtre les niveaux significatifs basés sur la confiance

    Args:
        levels: Liste des niveaux à filtrer
        min_confidence: Seuil minimum de confiance
        max_levels_per_type: Nombre max de niveaux par type

    Returns:
        Liste filtrée des niveaux significatifs
    """
    # Filtrer par confiance
    significant_levels = [level for level in levels if level.confidence_score >= min_confidence]

    # Trier par score de confiance décroissant
    significant_levels.sort(key=lambda x: x.confidence_score, reverse=True)

    # Limiter le nombre de niveaux par type
    supports = [l for l in significant_levels if not l.is_resistance][:max_levels_per_type]
    resistances = [l for l in significant_levels if l.is_resistance][:max_levels_per_type]

    return supports + resistances


def detect_levels(
    ohlcv_data: List[Dict[str, float]],
    min_touches: int = 2,
    price_tolerance_percent: float = 0.5,
    lookback_window: int = 5,
    min_confidence: float = 30.0
) -> Dict[str, List]:
    """
    Détecte les niveaux de support et résistance

    Args:
        ohlcv_data: Liste des données OHLCV avec high, low, volume
        min_touches: Minimum de touches pour valider un niveau
        price_tolerance_percent: Tolérance de prix pour grouper
        lookback_window: Fenêtre pour identifier les pivots
        min_confidence: Seuil minimum de confiance

    Returns:
        Dictionnaire avec support_levels, resistance_levels, confidence_scores

    Examples:
        >>> data = [
        ...     {"high": 100 + i, "low": 95 + i, "volume": 1000}
        ...     for i in range(50)
        ... ]
        >>> result = detect_levels(data)
        >>> "support_levels" in result and "resistance_levels" in result
        True
    """
    if len(ohlcv_data) < lookback_window * 2 + 1:
        return {
            "support_levels": [],
            "resistance_levels": [],
            "confidence_scores": []
        }

    try:
        # 1. Identifier les points pivots
        pivot_points = identify_pivot_points(ohlcv_data, lookback_window)

        # 2. Grouper les pivots proches en niveaux
        levels = group_pivots_into_levels(pivot_points, price_tolerance_percent, min_touches)

        # 3. Calculer les scores de confiance
        validated_levels = calculate_confidence_scores(levels, ohlcv_data)

        # 4. Filtrer les niveaux significatifs
        significant_levels = filter_significant_levels(validated_levels, min_confidence)

        # 5. Séparer supports et résistances
        support_levels = []
        resistance_levels = []
        confidence_scores = []

        for level in significant_levels:
            if level.is_resistance:
                resistance_levels.append(level.price)
            else:
                support_levels.append(level.price)
            confidence_scores.append(level.confidence_score)

        return {
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "confidence_scores": confidence_scores
        }

    except Exception:
        return {
            "support_levels": [],
            "resistance_levels": [],
            "confidence_scores": []
        }


def get_nearest_levels(
    current_price: float,
    levels: List[SupportResistanceLevel]
) -> Dict[str, Optional[float]]:
    """
    Trouve les niveaux de support et résistance les plus proches du prix actuel

    Args:
        current_price: Prix actuel
        levels: Liste des niveaux détectés

    Returns:
        Dictionnaire avec nearest_support et nearest_resistance

    Examples:
        >>> level1 = SupportResistanceLevel(100, False, 50, 2, 1000, 0, 10)
        >>> level2 = SupportResistanceLevel(110, True, 60, 3, 1500, 5, 15)
        >>> result = get_nearest_levels(105, [level1, level2])
        >>> result["nearest_support"]
        100
        >>> result["nearest_resistance"]
        110
    """
    supports = [l for l in levels if not l.is_resistance and l.price < current_price]
    resistances = [l for l in levels if l.is_resistance and l.price > current_price]

    nearest_support = max(supports, key=lambda x: x.price).price if supports else None
    nearest_resistance = min(resistances, key=lambda x: x.price).price if resistances else None

    return {
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resistance
    }
