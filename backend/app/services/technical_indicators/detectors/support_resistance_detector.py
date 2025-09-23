from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

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

class SupportResistanceDetector:
    """Détecteur de niveaux de support et résistance basé sur les points pivots"""

    def __init__(self):
        self.min_touches = 2  # Minimum de touches pour valider un niveau
        self.price_tolerance_percent = 0.5  # Tolérance de prix pour grouper les niveaux
        self.lookback_window = 5  # Fenêtre pour identifier les pivots

    def detect_levels(self, ohlcv_data: List[Dict]) -> Dict[str, any]:
        """
        Détecte les niveaux de support et résistance

        Args:
            ohlcv_data: Liste des données OHLCV avec timestamp, open, high, low, close, volume

        Returns:
            Dictionnaire avec support_levels, resistance_levels, confidence_scores
        """
        if len(ohlcv_data) < self.lookback_window * 2 + 1:
            logger.warning("Pas assez de données pour détecter support/résistance")
            return {
                "support_levels": [],
                "resistance_levels": [],
                "confidence_scores": []
            }

        try:
            # 1. Identifier les points pivots
            pivot_points = self._identify_pivot_points(ohlcv_data)

            # 2. Grouper les pivots proches en niveaux
            levels = self._group_pivots_into_levels(pivot_points)

            # 3. Calculer les scores de confiance
            validated_levels = self._calculate_confidence_scores(levels, ohlcv_data)

            # 4. Filtrer les niveaux significatifs
            significant_levels = self._filter_significant_levels(validated_levels)

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

            logger.info(f"Détectés: {len(support_levels)} supports, {len(resistance_levels)} résistances")

            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "confidence_scores": confidence_scores
            }

        except Exception as e:
            logger.error(f"Erreur détection support/résistance: {e}")
            return {
                "support_levels": [],
                "resistance_levels": [],
                "confidence_scores": []
            }

    def _identify_pivot_points(self, ohlcv_data: List[Dict]) -> List[PivotPoint]:
        """Identifie les points pivots (hauts et bas locaux)"""
        pivots = []

        for i in range(self.lookback_window, len(ohlcv_data) - self.lookback_window):
            candle = ohlcv_data[i]
            high_price = candle['high']
            low_price = candle['low']
            volume = candle['volume']

            # Vérifier si c'est un pivot haut (résistance potentielle)
            is_pivot_high = True
            for j in range(i - self.lookback_window, i + self.lookback_window + 1):
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
            for j in range(i - self.lookback_window, i + self.lookback_window + 1):
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

    def _group_pivots_into_levels(self, pivots: List[PivotPoint]) -> List[SupportResistanceLevel]:
        """Groupe les pivots proches en niveaux de support/résistance"""
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
                if price_diff_percent <= self.price_tolerance_percent:
                    similar_pivots.append(other_pivot)
                    used_pivots.add(j)

            # Créer un niveau si au moins 2 touches
            if len(similar_pivots) >= self.min_touches:
                # Calculer le prix moyen pondéré par le volume
                total_volume = sum(p.volume for p in similar_pivots)
                if total_volume > 0:
                    weighted_price = sum(p.price * p.volume for p in similar_pivots) / total_volume
                else:
                    weighted_price = sum(p.price for p in similar_pivots) / len(similar_pivots)

                level = SupportResistanceLevel(
                    price=round(weighted_price, 2),
                    is_resistance=pivot.is_high,
                    confidence_score=0.0,  # Sera calculé plus tard
                    touches=len(similar_pivots),
                    volume_confirmation=total_volume,
                    first_occurrence=min(p.index for p in similar_pivots),
                    last_occurrence=max(p.index for p in similar_pivots)
                )
                levels.append(level)

        return levels

    def _calculate_confidence_scores(self, levels: List[SupportResistanceLevel], ohlcv_data: List[Dict]) -> List[SupportResistanceLevel]:
        """Calcule les scores de confiance pour chaque niveau"""
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
            level.confidence_score = round(min(score, 100), 2)

        return levels

    def _filter_significant_levels(self, levels: List[SupportResistanceLevel]) -> List[SupportResistanceLevel]:
        """Filtre les niveaux significatifs basés sur la confiance"""
        # Seuil minimum de confiance
        min_confidence = 30.0

        # Filtrer par confiance
        significant_levels = [level for level in levels if level.confidence_score >= min_confidence]

        # Trier par score de confiance décroissant
        significant_levels.sort(key=lambda x: x.confidence_score, reverse=True)

        # Limiter le nombre de niveaux (max 5 supports + 5 résistances)
        supports = [l for l in significant_levels if not l.is_resistance][:5]
        resistances = [l for l in significant_levels if l.is_resistance][:5]

        return supports + resistances

    def get_nearest_levels(self, current_price: float, levels: List[SupportResistanceLevel]) -> Dict[str, Optional[float]]:
        """
        Trouve les niveaux de support et résistance les plus proches du prix actuel

        Args:
            current_price: Prix actuel
            levels: Liste des niveaux détectés

        Returns:
            Dictionnaire avec nearest_support et nearest_resistance
        """
        supports = [l for l in levels if not l.is_resistance and l.price < current_price]
        resistances = [l for l in levels if l.is_resistance and l.price > current_price]

        nearest_support = max(supports, key=lambda x: x.price).price if supports else None
        nearest_resistance = min(resistances, key=lambda x: x.price).price if resistances else None

        return {
            "nearest_support": nearest_support,
            "nearest_resistance": nearest_resistance
        }