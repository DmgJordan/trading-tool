"""
Domaine AI - Infrastructure IA multi-providers

Ce domaine gère l'intégration avec différents providers d'IA (Anthropic, OpenAI, DeepSeek)
pour l'analyse de marché et la génération de recommandations de trading.

Responsabilités:
- Abstraction multi-providers (providers/)
- Gestion des prompts (prompts/)
- Orchestration des analyses IA
- Endpoints de génération
"""

from .router import router

__all__ = ["router"]
