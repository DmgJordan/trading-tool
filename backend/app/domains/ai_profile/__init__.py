"""
Domaine AI_PROFILE - Configuration utilisateur IA

Ce domaine gère les préférences et configurations IA de chaque utilisateur.

Responsabilités:
- Profil utilisateur pour l'IA (provider préféré, modèle, tolérance au risque)
- CRUD des préférences IA
- Endpoints de configuration

Note: L'historique des recommandations sera dans un futur domaine séparé.
"""

from .router import router

__all__ = ["router"]
