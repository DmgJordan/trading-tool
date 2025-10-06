"""
Service d'orchestration IA

Migré depuis:
- app/services/ai_trading_service.py
- app/routes/claude.py (logique métier)
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from ...domains.auth.models import User
from ...domains.users.models import UserTradingPreferences
from ...domains.market.models import MarketData
from ...domains.market.service import MarketService
from ...core import decrypt_api_key

from .schemas import (
    AIProviderType,
    ClaudeModel,
    SingleAssetAnalysisRequest,
    StructuredAnalysisResponse,
    TechnicalDataLight,
    TradeRecommendation,
)
from .providers import AnthropicProvider
from .providers.openai import OpenAIProvider
from .providers.deepseek import DeepSeekProvider
from .prompts import get_system_prompt, get_market_analysis_prompt

logger = logging.getLogger(__name__)


class AIService:
    """Service d'orchestration pour les analyses IA"""

    def __init__(self):
        self.market_service = MarketService()

        # Initialiser les providers disponibles
        self.providers = {
            AIProviderType.ANTHROPIC: AnthropicProvider(),
            AIProviderType.OPENAI: OpenAIProvider(),
            AIProviderType.DEEPSEEK: DeepSeekProvider(),
        }

        # Modèle par défaut (pour compatibilité)
        self.default_model = "claude-sonnet-4-5-20250929"
        self.max_tokens = 4000
        self.timeout = 30.0

    def _get_provider(
        self,
        provider_type: AIProviderType = AIProviderType.ANTHROPIC
    ) -> Any:  # AIProvider
        """
        Récupère le provider IA spécifié

        Args:
            provider_type: Type de provider à utiliser

        Returns:
            Instance du provider

        Raises:
            ValueError: Si le provider n'existe pas ou n'est pas implémenté
        """
        provider = self.providers.get(provider_type)
        if not provider:
            raise ValueError(f"Provider {provider_type} non disponible")

        return provider

    async def _get_user_api_key(
        self,
        user: User,
        provider_type: AIProviderType = AIProviderType.ANTHROPIC
    ) -> str:
        """
        Récupère et déchiffre la clé API de l'utilisateur

        Args:
            user: Utilisateur authentifié
            provider_type: Type de provider

        Returns:
            Clé API déchiffrée

        Raises:
            ValueError: Si la clé API n'est pas configurée
        """
        if provider_type == AIProviderType.ANTHROPIC:
            if not user.anthropic_api_key:
                raise ValueError("Clé API Anthropic non configurée")
            return decrypt_api_key(user.anthropic_api_key)
        # Autres providers à implémenter
        else:
            raise ValueError(f"Provider {provider_type} non supporté pour récupération clé API")

    # ═══════════════════════════════════════════════════════════════
    # ANALYSE SINGLE-ASSET (migré depuis claude.py)
    # ═══════════════════════════════════════════════════════════════

    async def analyze_single_asset(
        self,
        request: SingleAssetAnalysisRequest,
        user: User,
        db: Session
    ) -> StructuredAnalysisResponse:
        """
        Analyse complète d'un seul actif avec données techniques multi-timeframes

        Migré depuis app/routes/claude.py::analyze_single_asset_with_technical

        Args:
            request: Paramètres de l'analyse
            user: Utilisateur authentifié
            db: Session de base de données

        Returns:
            Analyse structurée avec recommandations
        """
        request_id = str(uuid.uuid4())
        start_time = datetime.now()

        logger.info(f"Analyse single-asset {request_id}: {request.ticker} - {request.profile}")

        try:
            # 1. Récupérer la clé API
            api_key = await self._get_user_api_key(user, AIProviderType.ANTHROPIC)

            # 2. Récupérer données techniques multi-timeframes (600 bougies par TF)
            technical_data = await self.market_service.get_multi_timeframe_analysis(
                exchange_name=request.exchange,
                symbol=request.ticker,
                profile=request.profile
            )

            if "status" in technical_data and technical_data["status"] == "error":
                raise ValueError(f"Erreur récupération données techniques: {technical_data['message']}")

            # 3. Préparer les prompts
            system_prompt = get_system_prompt(request.model.value)
            user_prompt = get_market_analysis_prompt(
                technical_data=technical_data,
                ticker=request.ticker,
                profile=request.profile,
                exchange=request.exchange,
                custom_prompt=request.custom_prompt
            )

            # 4. Appeler le provider IA
            provider = self._get_provider(AIProviderType.ANTHROPIC)
            ai_response = await provider.analyze(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=request.model.value,
                max_tokens=self.max_tokens,
                temperature=0.3,
                api_key=api_key
            )

            if ai_response["status"] != "success":
                raise ValueError(f"Erreur analyse IA: {ai_response.get('message', 'Erreur inconnue')}")

            # 5. Préparer données techniques allégées (sans bougies pour frontend)
            technical_light = TechnicalDataLight(
                symbol=technical_data.get("symbol", request.ticker),
                profile=technical_data.get("profile", request.profile),
                tf=technical_data.get("tf", ""),
                current_price=technical_data.get("current_price", {}),
                features={
                    "ma": technical_data.get("features", {}).get("ma", {}),
                    "rsi14": technical_data.get("features", {}).get("rsi14", 0),
                    "atr14": technical_data.get("features", {}).get("atr14", 0),
                    "volume": technical_data.get("features", {}).get("volume", {}),
                },
                higher_tf={
                    "tf": technical_data.get("higher_tf", {}).get("tf", ""),
                    "ma": technical_data.get("higher_tf", {}).get("ma", {}),
                    "rsi14": technical_data.get("higher_tf", {}).get("rsi14", 0),
                    "atr14": technical_data.get("higher_tf", {}).get("atr14", 0),
                    "structure": technical_data.get("higher_tf", {}).get("structure", ""),
                    "nearest_resistance": technical_data.get("higher_tf", {}).get("nearest_resistance", 0),
                },
                lower_tf={
                    "tf": technical_data.get("lower_tf", {}).get("tf", ""),
                    "rsi14": technical_data.get("lower_tf", {}).get("rsi14", 0),
                    "volume": technical_data.get("lower_tf", {}).get("volume", {}),
                }
            )

            # 6. Parser la réponse structurée de l'IA
            trade_recommendations = []
            analysis_text = ai_response.get("content", "")

            try:
                # Nettoyer et extraire le JSON
                content_clean = analysis_text.strip()
                start_idx = content_clean.find("{")
                end_idx = content_clean.rfind("}") + 1

                if start_idx != -1 and end_idx != 0:
                    json_content = content_clean[start_idx:end_idx]
                    structured_response = json.loads(json_content)

                    # Valider et construire les recommandations
                    for rec_data in structured_response.get("trade_recommendations", []):
                        try:
                            trade_rec = TradeRecommendation(**rec_data)
                            trade_recommendations.append(trade_rec)
                        except Exception as e:
                            logger.warning(f"Recommandation trade invalide ignorée: {e}")
                            continue

                    # Extraire analysis_text du JSON
                    analysis_text = structured_response.get("analysis_text", analysis_text)

            except json.JSONDecodeError as e:
                logger.warning(f"Erreur parsing JSON IA: {e}")
                # Garder analysis_text brut et array vide
            except Exception as e:
                logger.error(f"Erreur inattendue parsing IA: {e}")

            # 7. Calculer métriques de performance
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            tokens_used = ai_response.get("tokens_used", 0)

            # 8. Construire réponse finale
            response = StructuredAnalysisResponse(
                request_id=request_id,
                timestamp=start_time,
                model_used=request.model,
                ticker=request.ticker,
                exchange=request.exchange,
                profile=request.profile,
                technical_data=technical_light,
                claude_analysis=analysis_text,
                trade_recommendations=trade_recommendations,
                tokens_used=tokens_used,
                processing_time_ms=int(processing_time),
                warnings=[]
            )

            logger.info(
                f"Analyse {request_id} terminée - "
                f"Tokens: {tokens_used}, Temps: {int(processing_time)}ms, "
                f"Recommandations: {len(trade_recommendations)}"
            )

            return response

        except ValueError as ve:
            logger.error(f"Erreur analyse single-asset {request_id}: {ve}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue analyze_single_asset {request_id}: {e}")
            raise

    # ═══════════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════════

    async def test_provider_connection(
        self,
        api_key: str,
        provider_type: AIProviderType = AIProviderType.ANTHROPIC
    ) -> Dict[str, Any]:
        """
        Teste la connexion avec un provider IA

        Args:
            api_key: Clé API à tester
            provider_type: Type de provider

        Returns:
            Résultat du test
        """
        try:
            provider = self._get_provider(provider_type)
            result = await provider.test_connection(api_key)
            return result

        except Exception as e:
            logger.error(f"Erreur test connexion {provider_type}: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Retourne la liste des providers disponibles"""
        providers_info = []

        for provider_type, provider in self.providers.items():
            providers_info.append({
                "provider_type": provider_type.value,
                "name": provider.provider_name,
                "models": provider.get_available_models(),
                "base_url": provider.base_url,
            })

        return providers_info
