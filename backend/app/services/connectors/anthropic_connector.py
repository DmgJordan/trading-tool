import httpx
import asyncio
import time
from typing import Dict, Any
from datetime import datetime
import logging
from ...schemas.claude import ClaudeModel

logger = logging.getLogger(__name__)

class AnthropicConnector:
    """Connector pour l'API Anthropic"""

    def __init__(self):
        self.base_url = "https://api.anthropic.com/v1"
        self.timeout = 30.0
        self.anthropic_version = "2023-06-01"

        # Configuration des timeouts par modèle
        self.model_timeouts = {
            ClaudeModel.HAIKU_35: 15.0,
            ClaudeModel.SONNET_45: 45.0,
            ClaudeModel.OPUS_41: 60.0
        }

        # Configuration des max_tokens par modèle
        self.model_max_tokens = {
            ClaudeModel.HAIKU_35: 3072,
            ClaudeModel.SONNET_45: 6144,
            ClaudeModel.OPUS_41: 8192
        }

    async def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Test rapide de connectivité avec l'API Anthropic

        Args:
            api_key: Clé API Anthropic à tester

        Returns:
            Dict avec le résultat du test
        """
        try:
            if not api_key or not api_key.startswith('sk-ant-'):
                return {
                    "status": "error",
                    "message": "Format de clé API invalide"
                }

            # Test minimal avec Haiku (le plus économique)
            messages = [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]

            request_payload = {
                "model": ClaudeModel.HAIKU_35.value,
                "max_tokens": 10,
                "messages": messages,
                "system": "Respond with just 'OK'."
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key,
                        "anthropic-version": self.anthropic_version
                    },
                    json=request_payload,
                    timeout=10.0
                )

                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": "Connexion réussie avec l'API Anthropic"
                    }
                elif response.status_code == 401:
                    return {
                        "status": "error",
                        "message": "Clé API invalide ou expirée"
                    }
                elif response.status_code == 429:
                    return {
                        "status": "error",
                        "message": "Limite de taux atteinte"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Erreur HTTP: {response.status_code}"
                    }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "Timeout lors du test de connexion"
            }
        except Exception as e:
            logger.error(f"Erreur test connexion: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    async def get_available_models(self, api_key: str) -> Dict[str, Any]:
        """
        Récupère la liste des modèles disponibles

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

    async def generate_analysis(
        self,
        api_key: str,
        system_prompt: str,
        user_prompt: str,
        model: ClaudeModel = ClaudeModel.SONNET_45
    ) -> Dict[str, Any]:
        """
        Méthode générique pour générer une analyse avec Claude

        Args:
            api_key: Clé API Anthropic
            system_prompt: Instructions système pour Claude
            user_prompt: Prompt utilisateur avec les données
            model: Modèle Claude à utiliser

        Returns:
            Dict avec le contenu de la réponse ou erreur
        """
        start_time = time.time()

        try:
            # Validation de la clé API
            if not api_key or not api_key.startswith('sk-ant-'):
                return {
                    "status": "error",
                    "message": "Clé API Anthropic invalide"
                }

            # Configuration selon le modèle
            timeout = self.model_timeouts.get(model, self.timeout)
            max_tokens = self.model_max_tokens.get(model, 3072)

            # Préparer la requête
            messages = [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]

            request_payload = {
                "model": model.value,
                "max_tokens": max_tokens,
                "messages": messages,
                "system": system_prompt,
                "temperature": 0.3
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key,
                        "anthropic-version": self.anthropic_version
                    },
                    json=request_payload,
                    timeout=timeout
                )

                processing_time_ms = int((time.time() - start_time) * 1000)

                if response.status_code == 200:
                    response_data = response.json()

                    # Extraire le contenu de la réponse
                    content_blocks = response_data.get("content", [])
                    if not content_blocks:
                        return {
                            "status": "error",
                            "message": "Réponse Claude vide"
                        }

                    # Concatener tous les blocs de texte
                    text_parts = []
                    for block in content_blocks:
                        if block.get("type") == "text" and "text" in block:
                            text_parts.append(block["text"])

                    content = "\n".join(text_parts).strip()

                    return {
                        "status": "success",
                        "content": content,
                        "tokens_used": response_data.get("usage", {}).get("output_tokens", 0),
                        "processing_time_ms": processing_time_ms
                    }

                elif response.status_code == 401:
                    return {
                        "status": "error",
                        "message": "Clé API Anthropic invalide ou expirée"
                    }

                elif response.status_code == 429:
                    return {
                        "status": "error",
                        "message": "Limite de taux API Anthropic atteinte. Veuillez réessayer plus tard."
                    }

                else:
                    error_detail = f"Code d'erreur HTTP: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message", error_detail)
                    except:
                        pass

                    return {
                        "status": "error",
                        "message": f"Erreur API Anthropic: {error_detail}"
                    }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": f"Timeout lors de l'analyse (>{timeout}s). Essayez un modèle plus rapide."
            }

        except httpx.RequestError as e:
            logger.error(f"Erreur requête Anthropic: {e}")
            return {
                "status": "error",
                "message": f"Erreur de connexion: {str(e)}"
            }

        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'analyse: {e}")
            return {
                "status": "error",
                "message": f"Erreur inattendue: {str(e)}"
            }