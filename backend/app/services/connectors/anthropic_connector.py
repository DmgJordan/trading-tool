import httpx
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AnthropicConnector:
    """Connector pour l'API Anthropic"""

    def __init__(self):
        self.base_url = "https://api.anthropic.com/v1"
        self.timeout = 10.0

    async def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Test la connexion à l'API Anthropic

        Args:
            api_key: Clé API Anthropic

        Returns:
            Dict avec status et message
        """
        try:
            # Validation basique du format de clé API
            if not api_key or not api_key.startswith('sk-ant-'):
                return {
                    "status": "error",
                    "message": "Format de clé API Anthropic invalide (doit commencer par sk-ant-)"
                }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Test"}]
                    },
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "Connexion Anthropic réussie !",
                        "data": {
                            "model_used": "claude-3-haiku-20240307",
                            "api_version": "2023-06-01"
                        }
                    }
                elif response.status_code == 401:
                    return {
                        "status": "error",
                        "message": "Clé API Anthropic invalide ou expirée"
                    }
                elif response.status_code == 429:
                    return {
                        "status": "error",
                        "message": "Limite de taux API Anthropic atteinte"
                    }
                else:
                    error_detail = "Erreur inconnue"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message", error_detail)
                    except:
                        pass

                    return {
                        "status": "error",
                        "message": f"Échec de la connexion Anthropic: {error_detail}"
                    }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "Timeout lors de la connexion à Anthropic"
            }
        except httpx.RequestError as e:
            logger.error(f"Erreur de requête Anthropic: {e}")
            return {
                "status": "error",
                "message": f"Erreur de connexion: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erreur inattendue Anthropic: {e}")
            return {
                "status": "error",
                "message": f"Erreur inattendue: {str(e)}"
            }

    async def get_available_models(self, api_key: str) -> Dict[str, Any]:
        """
        Récupère la liste des modèles disponibles (si l'endpoint existe)

        Args:
            api_key: Clé API Anthropic

        Returns:
            Dict avec la liste des modèles ou erreur
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={
                        "X-API-Key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return {
                        "status": "success",
                        "data": response.json()
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Impossible de récupérer les modèles: {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }