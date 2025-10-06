"""
Prompts IA - Templates réutilisables

Centralise tous les prompts utilisés pour interagir avec les modèles IA.
"""

from .system_prompts import get_system_prompt
from .market_analysis import get_market_analysis_prompt
from .trading_strategy import get_trading_strategy_prompt
from .risk_assessment import get_risk_assessment_prompt

__all__ = [
    "get_system_prompt",
    "get_market_analysis_prompt",
    "get_trading_strategy_prompt",
    "get_risk_assessment_prompt",
]
