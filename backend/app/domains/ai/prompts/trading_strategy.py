"""
Prompts pour la génération de recommandations de trading

Migré depuis app/services/ai_trading_service.py (lignes 195-285)
"""

import json
from typing import Dict, Any, List, Optional


def get_trading_strategy_prompt(
    market_data: List[Any],  # List[MarketData]
    preferences: Optional[Any] = None,  # Optional[UserTradingPreferences]
    max_recommendations: int = 5
) -> str:
    """
    Génère le prompt pour la génération de recommandations de trading multi-actifs

    Args:
        market_data: Liste des données de marché récentes
        preferences: Préférences de trading de l'utilisateur (optionnel)
        max_recommendations: Nombre maximum de recommandations à générer

    Returns:
        Prompt utilisateur complet pour la génération de recommandations
    """

    # Header du prompt
    prompt = """Tu es un expert en analyse technique et fondamentale des cryptomonnaies.
Ton rôle est de générer des recommandations de trading précises et personnalisées.

ANALYSE REQUISE:
- Évalue les tendances du marché
- Considère les niveaux de support/résistance
- Analyse le momentum et la volatilité
- Prends en compte le profil de risque de l'utilisateur
- Recommande une gestion de risque appropriée

"""

    # Profil utilisateur
    if preferences:
        prompt += f"""
PROFIL UTILISATEUR:
- Tolérance au risque: {preferences.risk_tolerance.value}
- Horizon d'investissement: {preferences.investment_horizon.value}
- Style de trading: {preferences.trading_style.value}
- Taille max de position: {preferences.max_position_size}%
- Stop-loss habituel: {preferences.stop_loss_percentage}%
- Ratio take-profit: {preferences.take_profit_ratio}

"""
        if preferences.technical_indicators:
            try:
                indicators = json.loads(preferences.technical_indicators)
                prompt += f"- Indicateurs préférés: {', '.join(indicators)}\n"
            except:
                pass

    # Données de marché
    prompt += "\nDONNÉES DE MARCHÉ RÉCENTES:\n"
    for data in market_data:
        change_str = f"{data.price_change_24h:+.2f}%" if data.price_change_24h else "N/A"
        volume_str = f"${data.volume_24h_usd:,.0f}" if data.volume_24h_usd else "N/A"
        market_cap_str = f"${data.market_cap_usd:,.0f}" if data.market_cap_usd else "N/A"

        prompt += f"""
{data.symbol}:
- Prix: ${data.price_usd:,.2f} ({change_str} 24h)
- Volume 24h: {volume_str}
- Market Cap: {market_cap_str}
- Source: {data.source}
- Timestamp: {data.data_timestamp.strftime('%Y-%m-%d %H:%M UTC')}
"""

    # Contrainte max position size
    max_position_size = preferences.max_position_size if preferences else 10

    # Instructions de format
    prompt += f"""
INSTRUCTIONS DE GÉNÉRATION:
1. Génère entre 1 et {max_recommendations} recommandations maximum
2. Privilégie la qualité à la quantité
3. Adapte les recommandations au profil de risque
4. Fournis des prix d'entrée, stop-loss et take-profit réalistes
5. Explique clairement ton raisonnement

FORMAT DE RÉPONSE OBLIGATOIRE (JSON strict):
{{
  "recommendations": [
    {{
      "action": "buy|sell|hold",
      "symbol": "BTC",
      "confidence": 85,
      "size_percentage": 15.0,
      "entry_price": 45000.0,
      "stop_loss": 43000.0,
      "take_profit1": 48000.0,
      "take_profit2": 50000.0,
      "take_profit3": 52000.0,
      "reasoning": "Analyse technique et fondamentale détaillée...",
      "risk_level": "low|medium|high"
    }}
  ]
}}

CONTRAINTES:
- confidence: 0-100
- size_percentage: adapté au profil de risque (max {max_position_size}%)
- Cohérence prix d'entrée/stop-loss/take-profit
- risk_level cohérent avec l'action

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""

    return prompt


def get_trading_strategy_prompt_simple(
    symbols: List[str],
    max_recommendations: int = 5
) -> str:
    """
    Version simplifiée du prompt sans données de marché ni préférences

    Args:
        symbols: Liste des symboles à analyser
        max_recommendations: Nombre maximum de recommandations

    Returns:
        Prompt simplifié
    """

    prompt = f"""Tu es un expert en trading crypto.

Génère des recommandations de trading pour les symboles suivants:
{', '.join(symbols)}

FORMAT DE RÉPONSE (JSON):
{{
  "recommendations": [
    {{
      "action": "buy|sell|hold",
      "symbol": "BTC",
      "confidence": 85,
      "size_percentage": 10.0,
      "entry_price": 45000.0,
      "stop_loss": 43000.0,
      "take_profit1": 48000.0,
      "take_profit2": 50000.0,
      "take_profit3": 52000.0,
      "reasoning": "Justification détaillée...",
      "risk_level": "low|medium|high"
    }}
  ]
}}

Maximum {max_recommendations} recommandations.
Réponds UNIQUEMENT avec le JSON."""

    return prompt
