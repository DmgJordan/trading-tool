"""
Provider Anthropic - Implémentation pour l'API Claude

Migré depuis:
- app/services/connectors/anthropic_connector.py
- app/services/validators/api_validator.py (partie Anthropic)
"""

import httpx
import asyncio
import time
from typing import Dict, Any, List
import logging

from .base import AIProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    """Provider pour l'API Anthropic (Claude)"""

    def __init__(self):
        self._base_url = "https://api.anthropic.com/v1"
        self._anthropic_version = "2023-06-01"
        self._default_timeout = 30.0

        # Configuration des timeouts par modèle
        self.model_timeouts = {
            "claude-3-5-haiku-20241022": 15.0,
            "claude-sonnet-4-5-20250929": 45.0,
            "claude-opus-4-1-20250805": 60.0,
        }

        # Configuration des max_tokens par modèle
        self.model_max_tokens = {
            "claude-3-5-haiku-20241022": 3072,
            "claude-sonnet-4-5-20250929": 6144,
            "claude-opus-4-1-20250805": 8192,
        }

    @property
    def provider_name(self) -> str:
        return "anthropic"

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
        Génère une analyse avec Claude

        Args:
            prompt: Prompt utilisateur
            system_prompt: Instructions système
            model: ID du modèle Claude (ex: claude-sonnet-4-5-20250929)
            max_tokens: Nombre maximum de tokens
            temperature: Température (0-1)
            **kwargs: api_key (requis)

        Returns:
            Dict avec status, content, tokens_used, processing_time_ms
        """
        start_time = time.time()

        try:
            # Récupérer la clé API depuis kwargs
            api_key = kwargs.get("api_key")
            if not api_key:
                return {
                    "status": "error",
                    "message": "Clé API Anthropic manquante"
                }

            # Validation de la clé API
            if not api_key.startswith('sk-ant-'):
                return {
                    "status": "error",
                    "message": "Clé API Anthropic invalide"
                }

            # Configuration selon le modèle
            timeout = self.model_timeouts.get(model, self._default_timeout)
            if max_tokens == 4000:  # Si valeur par défaut, utiliser celle du modèle
                max_tokens = self.model_max_tokens.get(model, 3072)

            # Préparer la requête
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            request_payload = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
                "system": system_prompt,
                "temperature": temperature
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key,
                        "anthropic-version": self._anthropic_version
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
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 10,
                "messages": messages,
                "system": "Respond with just 'OK'."
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self._base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key,
                        "anthropic-version": self._anthropic_version
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

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste des modèles Claude disponibles

        Returns:
            Liste des modèles avec leurs caractéristiques
        """
        return [
            {
                "id": "claude-3-5-haiku-20241022",
                "name": "Claude 3.5 Haiku",
                "description": "Analyse rapide et concise - Modèle le plus économique",
                "max_tokens": 3072,
                "timeout": 15.0,
                "use_case": "Analyses rapides, réponses courtes"
            },
            {
                "id": "claude-sonnet-4-5-20250929",
                "name": "Claude Sonnet 4.5",
                "description": "Analyse équilibrée et détaillée - Recommandé par défaut",
                "max_tokens": 6144,
                "timeout": 45.0,
                "use_case": "Analyses complètes, qualité institutionnelle"
            },
            {
                "id": "claude-opus-4-1-20250805",
                "name": "Claude Opus 4.1",
                "description": "Analyse institutionnelle sophistiquée - Modèle le plus puissant",
                "max_tokens": 8192,
                "timeout": 60.0,
                "use_case": "Analyses exhaustives, recherche quantitative"
            }
        ]

    def validate_api_key_format(self, api_key: str) -> Dict[str, Any]:
        """
        Valide le format d'une clé API Anthropic sans tester la connexion

        Args:
            api_key: Clé API à valider

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            if not api_key.startswith('sk-ant-'):
                return {
                    "status": "error",
                    "message": "Clé API Anthropic doit commencer par 'sk-ant-'"
                }

            if len(api_key) < 20:
                return {
                    "status": "error",
                    "message": "Clé API Anthropic trop courte"
                }

            return {
                "status": "success",
                "message": "Format de clé API Anthropic valide"
            }

        except Exception as e:
            logger.error(f"Erreur validation format clé API: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }
