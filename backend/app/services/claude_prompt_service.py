from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import logging
from ..schemas.claude import (
    ClaudeMarketData,
    ClaudeModel,
    PromptContext,
    GeneratedPrompt
)
from ..models.user_preferences import UserTradingPreferences

logger = logging.getLogger(__name__)

class ClaudePromptService:
    """Service de génération de prompts adaptatifs pour Claude"""

    def __init__(self):
        self.base_system_prompts = {
            ClaudeModel.HAIKU: self._get_haiku_system_prompt(),
            ClaudeModel.SONNET: self._get_sonnet_system_prompt(),
            ClaudeModel.SONNET_35: self._get_sonnet_35_system_prompt(),
            ClaudeModel.OPUS: self._get_opus_system_prompt()
        }

    def generate_trading_prompt(
        self,
        assets: List[str],
        model: ClaudeModel,
        market_data: Dict[str, ClaudeMarketData],
        user_preferences: Optional[UserTradingPreferences] = None,
        analysis_type: str = "detailed",
        custom_prompt: Optional[str] = None
    ) -> GeneratedPrompt:
        """
        Génère un prompt complet pour l'analyse trading

        Args:
            assets: Liste des actifs à analyser
            model: Modèle Claude à utiliser
            market_data: Données de marché par actif
            user_preferences: Préférences de l'utilisateur
            analysis_type: Type d'analyse (quick/detailed)
            custom_prompt: Instructions personnalisées

        Returns:
            Prompt généré avec contexte
        """
        try:
            # Prompt système adapté au modèle
            system_prompt = self.base_system_prompts.get(model, self.base_system_prompts[ClaudeModel.SONNET_35])

            # Construction du prompt utilisateur
            user_prompt = self._build_user_prompt(
                assets=assets,
                market_data=market_data,
                user_preferences=user_preferences,
                analysis_type=analysis_type,
                custom_prompt=custom_prompt
            )

            # Résumé du contexte
            context_summary = self._build_context_summary(
                assets=assets,
                market_data=market_data,
                user_preferences=user_preferences,
                analysis_type=analysis_type
            )

            # Estimation des tokens (approximative)
            estimated_tokens = self._estimate_tokens(system_prompt, user_prompt)

            return GeneratedPrompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                context_summary=context_summary,
                estimated_tokens=estimated_tokens
            )

        except Exception as e:
            logger.error(f"Erreur génération prompt: {e}")
            raise

    def _build_user_prompt(
        self,
        assets: List[str],
        market_data: Dict[str, ClaudeMarketData],
        user_preferences: Optional[UserTradingPreferences],
        analysis_type: str,
        custom_prompt: Optional[str]
    ) -> str:
        """Construit le prompt utilisateur principal"""

        sections = []

        # Section contexte utilisateur
        if user_preferences:
            sections.append(self._build_user_context_section(user_preferences))

        # Section données de marché
        if market_data:
            sections.append(self._build_market_data_section(market_data, assets))

        # Section instructions d'analyse
        sections.append(self._build_analysis_instructions(assets, analysis_type))

        # Section prompt personnalisé
        if custom_prompt:
            sections.append(f"INSTRUCTIONS ADDITIONNELLES:\n{custom_prompt}")

        # Section format de réponse
        sections.append(self._build_response_format_section(analysis_type))

        return "\n\n".join(sections)

    def _build_user_context_section(self, preferences: UserTradingPreferences) -> str:
        """Construit la section contexte utilisateur"""

        # Parser les préférences JSON
        preferred_assets = self._parse_json_field(preferences.preferred_assets, [])
        technical_indicators = self._parse_json_field(preferences.technical_indicators, [])

        context = f"""PROFIL TRADER:
• Tolérance au risque: {preferences.risk_tolerance.value}
• Horizon d'investissement: {self._format_investment_horizon(preferences.investment_horizon.value)}
• Style de trading: {preferences.trading_style.value}

PARAMÈTRES DE POSITION:
• Taille maximale de position: {preferences.max_position_size}% du portefeuille
• Stop-loss par défaut: {preferences.stop_loss_percentage}%
• Ratio risk/reward: {preferences.take_profit_ratio}:1

PRÉFÉRENCES:
• Actifs préférés: {', '.join(preferred_assets) if preferred_assets else 'Non spécifiés'}
• Indicateurs techniques: {', '.join(technical_indicators) if technical_indicators else 'RSI, MACD, SMA'}"""

        return context

    def _build_market_data_section(self, market_data: Dict[str, ClaudeMarketData], assets: List[str]) -> str:
        """Construit la section données de marché"""

        lines = ["DONNÉES DE MARCHÉ (CoinGecko):"]

        for asset in assets:
            data = market_data.get(asset)
            if data:
                price_change = f"({data.price_change_24h:+.2f}% 24h)" if data.price_change_24h else ""
                volume_str = f", Vol: ${self._format_large_number(data.volume_24h)}" if data.volume_24h else ""
                cap_str = f", Cap: ${self._format_large_number(data.market_cap)}" if data.market_cap else ""

                lines.append(f"• {asset} ({data.name}): ${data.current_price:,.2f} {price_change}{volume_str}{cap_str}")

                # Données additionnelles si disponibles
                if data.high_24h and data.low_24h:
                    lines.append(f"  Range 24h: ${data.low_24h:,.2f} - ${data.high_24h:,.2f}")

                if data.price_change_7d:
                    lines.append(f"  Variation 7j: {data.price_change_7d:+.2f}%")
            else:
                lines.append(f"• {asset}: Données non disponibles")

        return "\n".join(lines)

    def _build_analysis_instructions(self, assets: List[str], analysis_type: str) -> str:
        """Construit les instructions d'analyse"""

        if analysis_type == "quick":
            return f"""ANALYSE DEMANDÉE:
Effectuez une analyse trading concise des actifs {', '.join(assets)}.

Concentrez-vous sur:
1. Tendance générale et momentum
2. Niveaux de support/résistance clés
3. Signal d'entrée/sortie principal
4. Gestion des risques de base"""

        else:  # detailed
            return f"""ANALYSE DEMANDÉE:
Effectuez une analyse trading approfondie des actifs {', '.join(assets)}.

Analysez systématiquement:
1. **Analyse technique**: Tendances, indicateurs, niveaux clés
2. **Momentum de marché**: Volume, volatilité, sentiment
3. **Niveaux de prix critiques**: Support, résistance, zones de breakout
4. **Signaux d'entrée/sortie**: Timing optimal selon les préférences
5. **Gestion des risques**: Stop-loss, take-profit, position sizing
6. **Perspective temporelle**: Court, moyen et long terme
7. **Facteurs macro**: Impact du contexte économique général"""

    def _build_response_format_section(self, analysis_type: str) -> str:
        """Construit la section format de réponse"""

        if analysis_type == "quick":
            return """FORMAT DE RÉPONSE:
Structurez votre réponse en sections claires:

📊 **RÉSUMÉ MARCHÉ** (2-3 phrases)

🎯 **RECOMMANDATIONS PAR ACTIF**
Pour chaque actif:
• [SYMBOLE]: [ACTION] - [JUSTIFICATION]
• Entrée: $[PRIX] | Stop: $[PRIX] | Target: $[PRIX]

⚠️ **RISQUES PRINCIPAUX**

💡 **CONCLUSION**"""

        else:  # detailed
            return """FORMAT DE RÉPONSE:
Structurez votre analyse en sections détaillées:

📊 **ANALYSE DE MARCHÉ GÉNÉRALE**
Vue d'ensemble des conditions actuelles

🔍 **ANALYSE PAR ACTIF**
Pour chaque actif:
• **Analyse technique**: Tendances, indicateurs, patterns
• **Niveaux clés**: Support/résistance avec prix précis
• **Recommandation**: Action, timing, justification détaillée
• **Plan de position**: Entrée, stop-loss, take-profit, taille

📈 **STRATÉGIE GLOBALE**
Allocation suggérée entre les actifs

⚠️ **GESTION DES RISQUES**
Stratégies de protection adaptées au profil

🎯 **PLAN D'ACTION**
Étapes concrètes à suivre

💡 **CONCLUSION ET PERSPECTIVES**
Synthèse et vision à moyen terme"""

    def _get_haiku_system_prompt(self) -> str:
        """Prompt système optimisé pour Claude Haiku"""
        return """Tu es un analyste trading expert, spécialisé dans les analyses rapides et précises.

OBJECTIF: Fournir des analyses trading concises mais complètes, adaptées au profil de risque de l'utilisateur.

PRINCIPES:
• Privilégier la clarté et l'actionnable
• Utiliser les données de marché fournies
• Respecter les préférences de risque utilisateur
• Donner des niveaux de prix précis
• Justifier chaque recommandation

STYLE: Direct, facuel, sans jargon inutile. Concentré sur l'essentiel."""

    def _get_sonnet_system_prompt(self) -> str:
        """Prompt système optimisé pour Claude Sonnet"""
        return """Tu es un analyste trading professionnel avec une expertise approfondie des marchés financiers.

OBJECTIF: Fournir des analyses trading détaillées et nuancées, parfaitement adaptées au profil et aux préférences de l'utilisateur.

EXPERTISE:
• Analyse technique multi-timeframes
• Gestion des risques adaptative
• Psychologie des marchés
• Stratégies de position
• Timing d'entrée/sortie optimal

APPROCHE:
• Analyser tous les timeframes pertinents
• Intégrer l'analyse fondamentale au contexte
• Adapter les recommandations au profil de risque
• Proposer des alternatives selon les scénarios
• Justifier chaque décision avec des données

STYLE: Professionnel, pédagogique, structuré. Équilibre entre détail et lisibilité."""

    def _get_sonnet_35_system_prompt(self) -> str:
        """Prompt système optimisé pour Claude 3.5 Sonnet"""
        return """Tu es un analyste trading senior avec une vision holistique des marchés financiers.

OBJECTIF: Fournir des analyses trading de niveau institutionnel, intégrant tous les facteurs pertinents pour une prise de décision optimale.

COMPÉTENCES AVANCÉES:
• Analyse technique multi-dimensionnelle
• Corrélations inter-marchés
• Gestion de portefeuille dynamique
• Psychologie comportementale
• Timing de marché sophistiqué
• Backtesting mental des stratégies

MÉTHODOLOGIE:
• Analyse des données en contexte historique
• Évaluation des biais cognitifs potentiels
• Adaptation aux conditions de marché actuelles
• Intégration des facteurs macro et micro
• Optimisation risk-adjusted des recommandations
• Anticipation des scénarios alternatifs

STYLE: Expert mais accessible, nuancé, avec une perspective long-terme. Intègre l'incertitude et les probabilités."""

    def _get_opus_system_prompt(self) -> str:
        """Prompt système optimisé pour Claude Opus"""
        return """Tu es un analyste trading institutionnel de niveau élite, avec une compréhension systémique des marchés financiers.

OBJECTIF: Fournir des analyses trading exhaustives et sophistiquées, rivalisant avec les meilleures recherches institutionnelles.

EXPERTISE ÉLITE:
• Modélisation quantitative avancée
• Analyse des flux de capitaux
• Microstructure des marchés
• Stratégies multi-actifs complexes
• Gestion des risques stochastiques
• Alpha generation et factor investing
• Sentiment analysis et positionnement institutionnel

MÉTHODOLOGIE AVANCÉE:
• Analyse fractale multi-timeframes
• Intégration des régimes de marché
• Modélisation des corrélations dynamiques
• Évaluation de la liquidité et de l'impact
• Stress-testing des scénarios extrêmes
• Optimisation de Sharpe multi-contraintes
• Anticipation des changements de régime

PERSPECTIVE:
• Vision systémique des interconnexions
• Intégration de l'économie comportementale
• Prise en compte des facteurs géopolitiques
• Adaptation aux cycles macro-économiques
• Optimisation continue des processus

STYLE: Sophistiqué mais structuré, avec une profondeur analytique exceptionnelle. Intègre les nuances et les subtilités du trading professionnel."""

    def _format_investment_horizon(self, horizon: str) -> str:
        """Formate l'horizon d'investissement"""
        mapping = {
            "SHORT_TERM": "Court terme (< 1 mois)",
            "MEDIUM_TERM": "Moyen terme (1-12 mois)",
            "LONG_TERM": "Long terme (> 1 an)"
        }
        return mapping.get(horizon, horizon)

    def _format_large_number(self, number: float) -> str:
        """Formate les grands nombres en K, M, B"""
        if number >= 1e9:
            return f"{number/1e9:.1f}B"
        elif number >= 1e6:
            return f"{number/1e6:.1f}M"
        elif number >= 1e3:
            return f"{number/1e3:.1f}K"
        else:
            return f"{number:.0f}"

    def _parse_json_field(self, field_value: Optional[str], default: List[str]) -> List[str]:
        """Parse un champ JSON avec fallback"""
        if not field_value:
            return default

        try:
            parsed = json.loads(field_value)
            return parsed if isinstance(parsed, list) else default
        except (json.JSONDecodeError, TypeError):
            # Fallback: traiter comme une chaîne séparée par des virgules
            try:
                return [item.strip().upper() for item in field_value.split(',') if item.strip()]
            except:
                return default

    def _estimate_tokens(self, system_prompt: str, user_prompt: str) -> int:
        """Estimation approximative du nombre de tokens"""
        # Approximation: ~4 caractères par token pour du texte français/anglais
        total_chars = len(system_prompt) + len(user_prompt)
        return int(total_chars / 4)

    def _build_context_summary(
        self,
        assets: List[str],
        market_data: Dict[str, ClaudeMarketData],
        user_preferences: Optional[UserTradingPreferences],
        analysis_type: str
    ) -> str:
        """Construit un résumé du contexte"""

        parts = [
            f"Actifs: {', '.join(assets)}",
            f"Type: {analysis_type}"
        ]

        if user_preferences:
            parts.append(f"Profil: {user_preferences.risk_tolerance.value}/{user_preferences.trading_style.value}")

        if market_data:
            parts.append(f"Données marché: {len(market_data)} actifs")

        return " | ".join(parts)