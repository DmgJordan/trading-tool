"""
Provider OpenAI - Implémentation pour l'API GPT

Provider préparé mais non implémenté (NotImplementedError).
Prêt pour implémentation future.
"""

from typing import Dict, Any, List
import logging

from .base import AIProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """Provider pour l'API OpenAI (GPT-4, GPT-3.5, etc.)"""

    def __init__(self):
        self._base_url = "https://api.openai.com/v1"

    @property
    def provider_name(self) -> str:
        return "openai"

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
        Génère une analyse avec GPT

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            model: ID du modèle GPT (ex: gpt-4-turbo, gpt-3.5-turbo)
            max_tokens: Nombre maximum de tokens
            temperature: Température (0-1)
            **kwargs: api_key (requis)

        Raises:
            NotImplementedError: Provider non implémenté
        """
        raise NotImplementedError(
            "Le provider OpenAI n'est pas encore implémenté. "
            "Utilisez le provider Anthropic pour le moment."
        )

    async def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Teste la connexion avec l'API OpenAI

        Args:
            api_key: Clé API à tester

        Raises:
            NotImplementedError: Provider non implémenté
        """
        raise NotImplementedError(
            "Le provider OpenAI n'est pas encore implémenté. "
            "Utilisez le provider Anthropic pour le moment."
        )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des modèles GPT disponibles

        Returns:
            Liste des modèles (préparée pour implémentation future)
        """
        return [
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Modèle GPT-4 optimisé (non implémenté)",
                "max_tokens": 4096,
                "timeout": 30.0,
                "implemented": False
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Modèle GPT-4 standard (non implémenté)",
                "max_tokens": 8192,
                "timeout": 45.0,
                "implemented": False
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Modèle GPT-3.5 optimisé (non implémenté)",
                "max_tokens": 4096,
                "timeout": 20.0,
                "implemented": False
            }
        ]

    def validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
        """
        Valide le format d'une clé API OpenAI

        Args:
            api_key: Clé API à valider

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            if not api_key.startswith('sk-'):
                return {
                    "status": "error",
                    "message": "Clé API OpenAI doit commencer par 'sk-'"
                }

            if len(api_key) < 20:
                return {
                    "status": "error",
                    "message": "Clé API OpenAI trop courte"
                }

            return {
                "status": "success",
                "message": "Format de clé API OpenAI valide (provider non implémenté)"
            }

        except Exception as e:
            logger.error(f"Erreur validation format clé API: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }
