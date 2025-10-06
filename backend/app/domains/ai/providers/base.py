"""
Interface de base pour les providers IA

Définit le contrat que tous les providers doivent implémenter.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AIProvider(ABC):
    """Interface abstraite pour les providers IA"""

    @abstractmethod
    async def analyze(
        self,
        prompt: str,
        system_prompt: str,
        model: str,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère une analyse avec le modèle IA

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            model: Identifiant du modèle à utiliser
            max_tokens: Nombre maximum de tokens
            temperature: Température (créativité)
            **kwargs: Paramètres additionnels spécifiques au provider

        Returns:
            Dict avec:
                - status: "success" ou "error"
                - content: Texte de la réponse (si succès)
                - tokens_used: Nombre de tokens utilisés (si succès)
                - processing_time_ms: Temps de traitement (si succès)
                - message: Message d'erreur (si erreur)

        Raises:
            ValueError: En cas d'erreur de validation
            Exception: En cas d'erreur inattendue
        """
        pass

    @abstractmethod
    async def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Teste la connexion avec l'API du provider

        Args:
            api_key: Clé API à tester

        Returns:
            Dict avec:
                - status: "success" ou "error"
                - message: Message descriptif
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des modèles disponibles pour ce provider

        Returns:
            Liste de dicts contenant:
                - id: Identifiant du modèle
                - name: Nom du modèle
                - description: Description
                - max_tokens: Tokens maximum supportés
                - cost_per_token: Coût approximatif (optionnel)
        """
        pass

    @abstractmethod
    def validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
        """
        Valide le format de la clé API sans tester la connexion

        Args:
            api_key: Clé API à valider

        Returns:
            Dict avec:
                - status: "success" ou "error"
                - message: Message de validation
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nom du provider (ex: 'anthropic', 'openai', 'deepseek')"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """URL de base de l'API"""
        pass
