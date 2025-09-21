import httpx
import asyncio
import json
import time
from typing import Dict, Any, List
from datetime import datetime
import logging
from ...schemas.claude import ClaudeModel, GeneratedPrompt, ClaudeAnalysisResponse

logger = logging.getLogger(__name__)

class AnthropicConnector:
    """Connector pour l'API Anthropic"""

    def __init__(self):
        self.base_url = "https://api.anthropic.com/v1"
        self.timeout = 30.0  # Augmenté pour les analyses complexes
        self.anthropic_version = "2023-06-01"

        # Configuration des timeouts par modèle
        self.model_timeouts = {
            ClaudeModel.HAIKU: 15.0,
            ClaudeModel.SONNET: 30.0,
            ClaudeModel.SONNET_35: 45.0,
            ClaudeModel.OPUS: 60.0
        }

        # Configuration des max_tokens par modèle
        self.model_max_tokens = {
            ClaudeModel.HAIKU: 2048,
            ClaudeModel.SONNET: 3072,
            ClaudeModel.SONNET_35: 4096,
            ClaudeModel.OPUS: 4096
        }

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
                        "anthropic-version": self.anthropic_version
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

    async def generate_trading_analysis(
        self,
        api_key: str,
        prompt: GeneratedPrompt,
        model: ClaudeModel,
        request_id: str,
        assets: List[str]
    ) -> Dict[str, Any]:
        """
        Génère une analyse trading complète avec Claude

        Args:
            api_key: Clé API Anthropic
            prompt: Prompt généré pour l'analyse
            model: Modèle Claude à utiliser
            request_id: ID unique de la requête
            assets: Liste des actifs analysés

        Returns:
            Dict avec l'analyse complète ou erreur
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
                    "content": prompt.user_prompt
                }
            ]

            request_payload = {
                "model": model.value,
                "max_tokens": max_tokens,
                "messages": messages,
                "system": prompt.system_prompt,
                "temperature": 0.3,  # Cohérence pour analyses financières
                "stop_sequences": ["[END_ANALYSIS]"]
            }

            logger.info(f"Envoi requête Claude {model.value} pour analyse {request_id}")
            logger.debug(f"Payload: {json.dumps(request_payload, indent=2)}")

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
                    content = self._extract_content_from_response(response_data)

                    if not content:
                        return {
                            "status": "error",
                            "message": "Réponse Claude vide ou invalide"
                        }

                    # Traiter et structurer la réponse
                    analysis_response = self._process_claude_response(
                        content=content,
                        request_id=request_id,
                        model=model,
                        assets=assets,
                        processing_time_ms=processing_time_ms,
                        tokens_used=response_data.get("usage", {}).get("output_tokens", 0)
                    )

                    return {
                        "status": "success",
                        "data": analysis_response
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

                elif response.status_code == 400:
                    error_detail = "Requête invalide"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("error", {}).get("message", error_detail)
                    except:
                        pass

                    return {
                        "status": "error",
                        "message": f"Erreur dans la requête: {error_detail}"
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
            processing_time_ms = int((time.time() - start_time) * 1000)
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

    def _extract_content_from_response(self, response_data: Dict[str, Any]) -> str:
        """Extrait le contenu textuel de la réponse Claude"""
        try:
            content_blocks = response_data.get("content", [])

            if not content_blocks:
                return ""

            # Concatener tous les blocs de texte
            text_parts = []
            for block in content_blocks:
                if block.get("type") == "text" and "text" in block:
                    text_parts.append(block["text"])

            return "\n".join(text_parts).strip()

        except Exception as e:
            logger.error(f"Erreur extraction contenu: {e}")
            return ""

    def _process_claude_response(
        self,
        content: str,
        request_id: str,
        model: ClaudeModel,
        assets: List[str],
        processing_time_ms: int,
        tokens_used: int
    ) -> Dict[str, Any]:
        """
        Traite et structure la réponse brute de Claude

        Args:
            content: Contenu textuel de Claude
            request_id: ID de la requête
            model: Modèle utilisé
            assets: Actifs analysés
            processing_time_ms: Temps de traitement
            tokens_used: Tokens consommés

        Returns:
            Réponse structurée pour le frontend
        """
        try:
            # Pour l'instant, on retourne la réponse textuelle brute
            # TODO: Ajouter parsing intelligent pour extraire recommandations structurées

            # Extraire un résumé du marché (première section généralement)
            lines = content.split('\n')
            market_summary = ""
            risk_assessment = ""

            # Recherche basique de sections
            current_section = ""
            for line in lines:
                line_lower = line.lower().strip()

                if "résumé" in line_lower or "marché" in line_lower:
                    current_section = "market"
                elif "risque" in line_lower or "risk" in line_lower:
                    current_section = "risk"
                elif line.strip() and current_section == "market" and not market_summary:
                    market_summary = line.strip()
                elif line.strip() and current_section == "risk" and not risk_assessment:
                    risk_assessment = line.strip()

            if not market_summary:
                # Fallback: prendre les premières phrases significatives
                sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
                market_summary = sentences[0] + "." if sentences else "Analyse générée"

            if not risk_assessment:
                risk_assessment = "Veuillez consulter l'analyse complète pour l'évaluation des risques."

            # Recherche de recommandations basiques
            recommendations = self._extract_basic_recommendations(content, assets)

            # Détection d'avertissements
            warnings = []
            if "simulation" in content.lower() or "test" in content.lower():
                warnings.append("Cette analyse utilise des données de test")

            if len(content) < 500:
                warnings.append("Analyse plus courte que prévu")

            # Limitations
            limitations = [
                "Cette analyse est basée sur les données disponibles au moment de la génération",
                "Les marchés financiers sont imprévisibles et comportent des risques",
                "Cette analyse ne constitue pas un conseil en investissement"
            ]

            return {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "model_used": model.value,
                "assets_analyzed": assets,
                "full_analysis": content,
                "recommendations": recommendations,
                "market_summary": market_summary,
                "risk_assessment": risk_assessment,
                "market_data": {},  # À remplir par le service appelant
                "user_preferences_summary": None,  # À remplir par le service appelant
                "tokens_used": tokens_used,
                "processing_time_ms": processing_time_ms,
                "warnings": warnings,
                "limitations": limitations
            }

        except Exception as e:
            logger.error(f"Erreur traitement réponse: {e}")

            # Fallback minimal
            return {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "model_used": model.value,
                "assets_analyzed": assets,
                "full_analysis": content,
                "recommendations": [],
                "market_summary": "Analyse générée par Claude",
                "risk_assessment": "Consultez l'analyse complète",
                "market_data": {},
                "user_preferences_summary": None,
                "tokens_used": tokens_used,
                "processing_time_ms": processing_time_ms,
                "warnings": ["Erreur lors du traitement de la réponse"],
                "limitations": ["Cette analyse nécessite une vérification manuelle"]
            }

    def _extract_basic_recommendations(self, content: str, assets: List[str]) -> List[Dict[str, Any]]:
        """Extrait des recommandations basiques du texte"""
        recommendations = []

        try:
            lines = content.split('\n')

            for asset in assets:
                # Recherche basique de recommandations pour chaque actif
                for line in lines:
                    line_lower = line.lower()

                    if asset.lower() in line_lower:
                        action = "HOLD"  # Par défaut
                        reasoning = line.strip()

                        # Détection d'actions basiques
                        if any(word in line_lower for word in ["achat", "buy", "acheter"]):
                            action = "BUY"
                        elif any(word in line_lower for word in ["vente", "sell", "vendre"]):
                            action = "SELL"
                        elif any(word in line_lower for word in ["attendre", "wait"]):
                            action = "WAIT"

                        recommendations.append({
                            "asset": asset,
                            "action": action,
                            "confidence": "MEDIUM",
                            "entry_price": None,
                            "stop_loss": None,
                            "take_profit": None,
                            "reasoning": reasoning[:200],  # Limiter la longueur
                            "key_factors": [],
                            "time_horizon": None,
                            "risk_level": None
                        })
                        break  # Une seule recommandation par actif pour l'instant

        except Exception as e:
            logger.error(f"Erreur extraction recommandations: {e}")

        return recommendations