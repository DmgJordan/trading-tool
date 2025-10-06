"""
Prompts pour l'analyse de marché technique

Migré depuis app/routes/claude.py (lignes 218-363)
"""

import json
from typing import Dict, Any, Optional


def get_market_analysis_prompt(
    technical_data: Dict[str, Any],
    ticker: str,
    profile: str,
    exchange: str,
    custom_prompt: Optional[str] = None
) -> str:
    """
    Génère le prompt pour l'analyse technique d'un actif unique

    Args:
        technical_data: Données techniques multi-timeframes depuis MarketService
        ticker: Symbole de l'actif (ex: BTC/USDT)
        profile: Profil de trading (short, medium, long)
        exchange: Exchange utilisé
        custom_prompt: Instructions additionnelles optionnelles

    Returns:
        Prompt utilisateur complet pour l'analyse
    """

    # Récupérer le prix actuel depuis technical_data
    current_price_info = technical_data.get('current_price', {})
    current_price = current_price_info.get('current_price', 'N/A')

    # Récupérer le timeframe principal
    main_tf = technical_data.get('tf', 'N/A')

    prompt = f"""
ANALYSE TECHNIQUE - {ticker}
Profil: {profile.upper()} | Exchange: {exchange} | Prix actuel: ${current_price}

═══════════════════════════════════════════════════════════════
⚡ PHILOSOPHIE DE RECOMMANDATION
═══════════════════════════════════════════════════════════════

Tu es un analyste PRO, pas un robot qui doit toujours proposer des trades.
Ta réputation dépend de la QUALITÉ, pas de la quantité.

• Array vide [] est une RÉPONSE VALIDE et RESPECTABLE
• Proposer 0 trade en période d'incertitude montre ton PROFESSIONNALISME
• Proposer 2-3 trades quand contexte riche montre ta COMPÉTENCE
• Ne recommande QUE les setups où tu as 70+ confidence

⚠️ RÈGLE D'OR : En cas de doute, NE PAS recommander. Mieux vaut 0 trade que 1 mauvais trade.

═══════════════════════════════════════════════════════════════
DONNÉES TECHNIQUES MULTI-TIMEFRAMES
═══════════════════════════════════════════════════════════════
{json.dumps(technical_data, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════
FORMAT DE RÉPONSE REQUIS (JSON strict)
═══════════════════════════════════════════════════════════════

// EXEMPLES selon contexte de marché:

// CAS 1 - Aucune opportunité (incertitude/consolidation) :
{{
  "analysis_text": "Analyse détaillée...",
  "trade_recommendations": []
}}

// CAS 2 - Une seule opportunité claire :
{{
  "analysis_text": "Analyse détaillée...",
  "trade_recommendations": [
    {{
      "entry_price": 45000.0,
      "direction": "long",
      "stop_loss": 43500.0,
      "take_profit_1": 46500.0,
      "take_profit_2": 47800.0,
      "take_profit_3": 49200.0,
      "confidence_level": 85,
      "risk_reward_ratio": 2.8,
      "portfolio_percentage": 3.5,
      "timeframe": "{main_tf}",
      "reasoning": "Justification technique détaillée (200-300 mots)..."
    }}
  ]
}}

// CAS 3 - Opportunités multiples (contextes/niveaux différents) :
{{
  "analysis_text": "Analyse détaillée...",
  "trade_recommendations": [
    {{
      "entry_price": 44500.0,
      "direction": "long",
      "confidence_level": 78,
      "reasoning": "Setup conservateur sur support..."
    }},
    {{
      "entry_price": 46000.0,
      "direction": "long",
      "confidence_level": 82,
      "reasoning": "Setup breakout résistance..."
    }}
  ]
}}

═══════════════════════════════════════════════════════════════
INSTRUCTIONS D'ANALYSE
═══════════════════════════════════════════════════════════════

1️⃣ ANALYSE TEXTUELLE (analysis_text) :
   • Contexte de marché et tendance générale
   • Analyse multi-timeframes (main/higher/lower)
   • Signaux techniques : MA, RSI, ATR, Volume
   • Niveaux clés : supports, résistances, zones de breakout
   • Évaluation des risques et catalyseurs potentiels
   • Conclusion et perspective

2️⃣ DÉCISION DE RECOMMANDATION :

   🚫 SITUATIONS OÙ NE PAS RECOMMANDER (array vide []) :

   • Incertitude : RSI neutre (40-60) + pas de tendance claire
   • Consolidation : Prix coincé entre MA, range étroit (<3% amplitude)
   • Signaux contradictoires : Divergence entre timeframes
   • Volatilité excessive : ATR > 2× moyenne récente
   • Volume anémique : < 50% de la moyenne 20 périodes
   • Confluence insuffisante : < 3 indicateurs alignés
   • Post-mouvement violent : Besoin de stabilisation (< 24h)
   • Zone de résistance/support majeur sans catalyseur

   ✅ SI CONTEXTE FAVORABLE - Identifier opportunités (1 à 3 max) :

   Opportunité UNIQUE (1 trade) :
   • Setup évident avec forte conviction (85+ confidence)
   • Une seule direction claire sur le timeframe principal

   Opportunités MULTIPLES (2-3 trades) :
   • Plusieurs niveaux techniques valides (ex: support + breakout)
   • Setups sur différents timeframes complémentaires
   • Approches différentes (conservateur 75% vs agressif 85%)
   • Scénarios alternatifs (long pullback vs long breakout)

   Pour chaque trade :
   • Entry : Niveau technique précis (prix exact)
   • Stop-loss : Sous structure ou 1-2× ATR
   • Take-profits : TP1 conservateur, TP2 principal, TP3 extension
   • Confidence : 70-100 (85+ pour haute conviction)
   • Portfolio % : 1.0-5.0% (ajusté selon confidence et R/R)
   • Direction : "long" ou "short" uniquement
   • Timeframe : Horizon de détention estimé
   • Reasoning : Justification détaillée (200-300 mots)

3️⃣ VALIDATION STRICTE (checklist obligatoire) :

   Pour qu'un trade soit RECOMMANDABLE :
   ✅ Confluence : 3+ indicateurs alignés (MA, RSI, Volume, Structure)
   ✅ Timing : Momentum favorable + volume confirmé
   ✅ Structure : Support/résistance claire OU breakout valide
   ✅ Multi-TF : Cohérence entre timeframes (pas de divergence majeure)
   ✅ R/R ratio : Minimum 1.5:1 (idéal 2:1+)
   ✅ Invalidation claire : SL défini par niveau technique évident

   RED FLAGS (disqualifient automatiquement) :
   ❌ Volume < 50% de la moyenne 20 périodes
   ❌ RSI dans zone neutre (40-60) sans catalyseur fort
   ❌ Prix coincé entre MA majeures (indécision)
   ❌ Divergences bearish/bullish non résolues
   ❌ Consolidation post-mouvement violent (< 24h)
   ❌ Confluence < 3 indicateurs
   ❌ Ratio R/R < 1.5:1

⚠️ RÈGLES STRICTES :
   • Réponds UNIQUEMENT avec le JSON valide
   • Pas de texte avant/après le JSON
   • Calcul R/R : (TP_moyen - Entry) / (Entry - SL)
   • Prix réalistes basés sur données fournies
   • Array vide [] est PRÉFÉRABLE à un trade médiocre"""

    # Ajouter instructions personnalisées si fournies
    if custom_prompt:
        prompt += f"\n\n=== INSTRUCTIONS ADDITIONNELLES ===\n{custom_prompt}"

    return prompt
