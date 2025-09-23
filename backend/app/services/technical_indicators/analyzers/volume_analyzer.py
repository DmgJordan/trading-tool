from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VolumeAnalyzer:
    """Analyseur de volume pour identifier les pics et tendances"""

    def __init__(self):
        self.default_period = 20

    def analyze_volume(self, volumes: List[float], period: int = None) -> Dict[str, float]:
        """
        Analyse le volume actuel par rapport à la moyenne

        Args:
            volumes: Liste des volumes (ordre chronologique)
            period: Période pour la moyenne (défaut: 20)

        Returns:
            Dictionnaire avec current, avg20, spike_ratio
        """
        if period is None:
            period = self.default_period

        if len(volumes) == 0:
            logger.warning("Aucune donnée de volume fournie")
            return {
                "current": 0.0,
                "avg20": 0.0,
                "spike_ratio": 0.0
            }

        try:
            current_volume = volumes[-1]

            # Calculer la moyenne des 20 dernières périodes
            if len(volumes) >= period:
                avg_volume = sum(volumes[-period:]) / period
            else:
                # Si pas assez de données, utiliser toutes les données disponibles
                avg_volume = sum(volumes) / len(volumes)

            # Calculer le ratio spike (current/average)
            spike_ratio = current_volume / avg_volume if avg_volume > 0 else 0.0

            result = {
                "current": round(current_volume, 2),
                "avg20": round(avg_volume, 2),
                "spike_ratio": round(spike_ratio, 2)
            }

            logger.info(f"Analyse volume: {result}")
            return result

        except Exception as e:
            logger.error(f"Erreur analyse volume: {e}")
            return {
                "current": 0.0,
                "avg20": 0.0,
                "spike_ratio": 0.0
            }

    def get_volume_interpretation(self, spike_ratio: float) -> str:
        """
        Interprète le ratio de volume

        Args:
            spike_ratio: Ratio volume actuel / moyenne

        Returns:
            Interprétation textuelle
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

    def get_volume_signal(self, spike_ratio: float, price_change_percent: float = 0) -> str:
        """
        Génère un signal basé sur le volume et la variation de prix

        Args:
            spike_ratio: Ratio de volume
            price_change_percent: Variation de prix en pourcentage

        Returns:
            Signal de trading basé sur le volume
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

        except Exception as e:
            logger.error(f"Erreur signal volume: {e}")
            return "NEUTRE"

    def detect_volume_trend(self, volumes: List[float], period: int = 10) -> Dict[str, any]:
        """
        Détecte la tendance du volume sur une période

        Args:
            volumes: Liste des volumes
            period: Période d'analyse

        Returns:
            Dictionnaire avec la tendance et la force
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
                "strength": round(abs(normalized_slope), 2),
                "description": f"Volume {trend.lower()} avec force {abs(normalized_slope):.1f}%"
            }

        except Exception as e:
            logger.error(f"Erreur détection tendance volume: {e}")
            return {
                "trend": "NEUTRE",
                "strength": 0.0,
                "description": "Erreur de calcul"
            }