from typing import Dict, Any
from ..connectors.anthropic_connector import AnthropicConnector
import logging

logger = logging.getLogger(__name__)

class ApiValidator:
    """Service de validation pour les APIs standard (clé API simple)"""

    def __init__(self):
        self.anthropic_connector = AnthropicConnector()

    async def validate_anthropic(self, api_key: str) -> Dict[str, Any]:
        """
        Valide la connexion à l'API Anthropic

        Args:
            api_key: Clé API Anthropic

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            result = await self.anthropic_connector.test_connection(api_key)

            # Enrichir le résultat avec des informations de validation
            if result["status"] == "success":
                result["validation"] = {
                    "api_type": "anthropic",
                    "connector_type": "standard_api",
                    "authentication_method": "api_key"
                }

            return result

        except Exception as e:
            logger.error(f"Erreur validation Anthropic: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }

    async def get_anthropic_models(self, api_key: str) -> Dict[str, Any]:
        """
        Récupère les modèles disponibles pour Anthropic

        Args:
            api_key: Clé API Anthropic

        Returns:
            Dict avec la liste des modèles
        """
        try:
            return await self.anthropic_connector.get_available_models(api_key)

        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    def validate_api_key_format(self, key: str, api_type: str = "anthropic") -> Dict[str, Any]:
        """
        Valide le format d'une clé API sans tester la connexion

        Args:
            key: Clé API à valider
            api_type: Type d'API (anthropic, openai, etc.)

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            if api_type.lower() == "anthropic":
                if not key.startswith('sk-ant-'):
                    return {
                        "status": "error",
                        "message": "Clé API Anthropic doit commencer par 'sk-ant-'"
                    }

                if len(key) < 20:
                    return {
                        "status": "error",
                        "message": "Clé API Anthropic trop courte"
                    }

                return {
                    "status": "success",
                    "message": "Format de clé API Anthropic valide"
                }

            elif api_type.lower() == "openai":
                if not key.startswith('sk-'):
                    return {
                        "status": "error",
                        "message": "Clé API OpenAI doit commencer par 'sk-'"
                    }

                if len(key) < 20:
                    return {
                        "status": "error",
                        "message": "Clé API OpenAI trop courte"
                    }

                return {
                    "status": "success",
                    "message": "Format de clé API OpenAI valide"
                }

            else:
                return {
                    "status": "error",
                    "message": f"Type d'API non supporté: {api_type}"
                }

        except Exception as e:
            logger.error(f"Erreur validation format clé API: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }