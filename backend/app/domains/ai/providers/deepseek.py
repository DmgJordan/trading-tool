"""
Provider DeepSeek - Implémentation pour l'API DeepSeek

Provider préparé mais non implémenté (NotImplementedError).
Prêt pour implémentation future.
"""

from typing import Dict, Any, List
import logging

from .base import AIProvider

logger = logging.getLogger(__name__)


class DeepSeekProvider(AIProvider):
    """Provider pour l'API DeepSeek"""

    def __init__(self):
        self._base_url = "https://api.deepseek.com/v1"

    @property
    def provider_name(self) -> str:
        return "deepseek"

    @property
    def base_url(self) -> str:
        return self._base_url

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
        Génère une analyse avec DeepSeek

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            model: ID du modèle DeepSeek
            max_tokens: Nombre maximum de tokens
            temperature: Température (0-1)
            **kwargs: api_key (requis)

        Raises:
            NotImplementedError: Provider non implémenté
        """
        raise NotImplementedError(
            "Le provider DeepSeek n'est pas encore implémenté. "
            "Utilisez le provider Anthropic pour le moment."
        )

    async def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Teste la connexion avec l'API DeepSeek

        Args:
            api_key: Clé API à tester

        Raises:
            NotImplementedError: Provider non implémenté
        """
        raise NotImplementedError(
            "Le provider DeepSeek n'est pas encore implémenté. "
            "Utilisez le provider Anthropic pour le moment."
        )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des modèles DeepSeek disponibles

        Returns:
            Liste des modèles (préparée pour implémentation future)
        """
        return [
            {
                "id": "deepseek-chat",
                "name": "DeepSeek Chat",
                "description": "Modèle DeepSeek conversationnel (non implémenté)",
                "max_tokens": 4096,
                "timeout": 30.0,
                "implemented": False
            },
            {
                "id": "deepseek-coder",
                "name": "DeepSeek Coder",
                "description": "Modèle DeepSeek pour code (non implémenté)",
                "max_tokens": 16384,
                "timeout": 45.0,
                "implemented": False
            }
        ]

    def validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
        """
        Valide le format d'une clé API DeepSeek

        Args:
            api_key: Clé API à valider

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            # Format exact à déterminer lors de l'implémentation
            if len(api_key) < 10:
                return {
                    "status": "error",
                    "message": "Clé API DeepSeek trop courte"
                }

            return {
                "status": "success",
                "message": "Format de clé API DeepSeek valide (provider non implémenté)"
            }

        except Exception as e:
            logger.error(f"Erreur validation format clé API: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }
