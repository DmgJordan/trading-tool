"""
Prompts pour l'évaluation des risques

Nouveau module pour évaluation sophistiquée des risques de trading.
"""

from typing import Dict, Any, List, Optional


def get_risk_assessment_prompt(
    position_size: float,
    entry_price: float,
    stop_loss: float,
    portfolio_value: float,
    leverage: float = 1.0
) -> str:
    """
    Génère un prompt pour évaluer le risque d'une position

    Args:
        position_size: Taille de la position en %
        entry_price: Prix d'entrée
        stop_loss: Stop-loss
        portfolio_value: Valeur du portefeuille
        leverage: Levier utilisé (défaut: 1.0)

    Returns:
        Prompt pour évaluation des risques
    """

    risk_amount = portfolio_value * (position_size / 100) * abs((entry_price - stop_loss) / entry_price)

    prompt = f"""Évalue le risque de cette position de trading:

PARAMÈTRES:
- Taille de position: {position_size}% du portefeuille
- Prix d'entrée: ${entry_price:,.2f}
- Stop-loss: ${stop_loss:,.2f}
- Valeur du portefeuille: ${portfolio_value:,.2f}
- Levier: {leverage}x
- Montant à risque: ${risk_amount:,.2f}

ANALYSE REQUISE:
1. Évalue si le ratio risque/récompense est acceptable
2. Détermine si la taille de position est appropriée
3. Identifie les risques potentiels (volatilité, liquidité, etc.)
4. Recommande des ajustements si nécessaire

FORMAT DE RÉPONSE (JSON):
{{
  "risk_level": "low|medium|high|extreme",
  "risk_score": 0-100,
  "recommendations": [
    "Recommandation 1",
    "Recommandation 2"
  ],
  "warnings": [
    "Avertissement si applicable"
  ],
  "adjusted_position_size": 5.0,
  "reasoning": "Analyse détaillée du risque..."
}}

Réponds UNIQUEMENT avec le JSON."""

    return prompt


def get_portfolio_risk_prompt(
    open_positions: List[Dict[str, Any]],
    portfolio_value: float
) -> str:
    """
    Génère un prompt pour évaluer le risque global du portefeuille

    Args:
        open_positions: Liste des positions ouvertes
        portfolio_value: Valeur totale du portefeuille

    Returns:
        Prompt pour évaluation risque portefeuille
    """

    total_exposure = sum(pos.get('size_percentage', 0) for pos in open_positions)

    positions_summary = "\n".join([
        f"- {pos.get('symbol', 'N/A')}: {pos.get('size_percentage', 0)}% "
        f"({pos.get('direction', 'N/A')}, entry: ${pos.get('entry_price', 0):,.2f})"
        for pos in open_positions
    ])

    prompt = f"""Évalue le risque global de ce portefeuille de trading:

PORTEFEUILLE:
- Valeur totale: ${portfolio_value:,.2f}
- Nombre de positions: {len(open_positions)}
- Exposition totale: {total_exposure:.1f}%

POSITIONS OUVERTES:
{positions_summary}

ANALYSE REQUISE:
1. Évalue la diversification du portefeuille
2. Identifie les corrélations entre positions
3. Calcule le risque total (VaR, drawdown potentiel)
4. Détermine si l'exposition est excessive
5. Recommande des ajustements de gestion de risque

FORMAT DE RÉPONSE (JSON):
{{
  "overall_risk": "low|medium|high|extreme",
  "diversification_score": 0-100,
  "correlation_risk": "low|medium|high",
  "max_drawdown_estimate": 15.5,
  "recommendations": [
    "Recommandation globale 1",
    "Recommandation globale 2"
  ],
  "should_reduce_exposure": true,
  "reasoning": "Analyse détaillée..."
}}

Réponds UNIQUEMENT avec le JSON."""

    return prompt


def get_market_regime_risk_prompt(
    market_conditions: Dict[str, Any]
) -> str:
    """
    Génère un prompt pour évaluer le risque selon le régime de marché

    Args:
        market_conditions: Conditions de marché actuelles

    Returns:
        Prompt pour évaluation risque de marché
    """

    prompt = f"""Évalue le risque de trading dans les conditions de marché actuelles:

CONDITIONS DE MARCHÉ:
{market_conditions}

ANALYSE REQUISE:
1. Identifie le régime de marché actuel (trending, ranging, volatile)
2. Évalue le sentiment global (fear, greed, neutral)
3. Détermine les risques macro (taux, inflation, réglementation)
4. Recommande une stratégie de gestion de risque adaptée

FORMAT DE RÉPONSE (JSON):
{{
  "market_regime": "trending|ranging|volatile|crisis",
  "sentiment": "extreme_fear|fear|neutral|greed|extreme_greed",
  "volatility_level": "low|medium|high|extreme",
  "recommended_max_exposure": 50.0,
  "recommended_risk_per_trade": 2.0,
  "caution_level": "low|medium|high|extreme",
  "reasoning": "Analyse du régime de marché..."
}}

Réponds UNIQUEMENT avec le JSON."""

    return prompt
