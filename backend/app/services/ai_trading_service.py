import json
import hashlib
import httpx
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from ..models.user import User
from ..models.user_preferences import UserTradingPreferences
from ..models.market_data import MarketData
from ..models.ai_recommendations import AIRecommendation, ActionType, RiskLevel
from ..schemas.ai_recommendations import (
    RawAIResponse,
    AIRecommendationRequest,
    AIRecommendationsListResponse,
    AIAnalysisError,
    AIGenerationContext
)
from ..auth import decrypt_api_key

logger = logging.getLogger(__name__)

class AITradingService:
    """Service d'analyse IA pour générer des recommandations de trading"""

    def __init__(self):
        self.anthropic_base_url = "https://api.anthropic.com/v1"
        self.timeout = 30.0
        self.max_tokens = 4000
        self.model = "claude-sonnet-4-20250514"  # Modèle Claude 4 le plus récent et performant

    async def generate_recommendations(
        self,
        user: User,
        request: AIRecommendationRequest,
        db: Session
    ) -> AIRecommendationsListResponse:
        """
        Génère des recommandations de trading personnalisées pour un utilisateur

        Args:
            user: Utilisateur authentifié
            request: Paramètres de la requête
            db: Session de base de données

        Returns:
            Liste des recommandations générées

        Raises:
            HTTPException: En cas d'erreur (API, quota, parsing, etc.)
        """
        try:
            # 1. Vérifier la clé API Anthropic
            api_key = await self._get_user_anthropic_key(user)
            if not api_key:
                raise ValueError("Clé API Anthropic non configurée pour cet utilisateur")

            # 2. Récupérer les préférences utilisateur
            preferences = await self._get_user_preferences(user, db)

            # 3. Déterminer les symboles à analyser
            symbols = await self._determine_symbols(request, preferences)

            # 4. Récupérer les données de marché récentes
            market_data = await self._get_recent_market_data(symbols, db)

            # 5. Vérifier si on a déjà des recommandations récentes (si pas force_refresh)
            if not request.force_refresh:
                recent_recommendations = await self._check_recent_recommendations(
                    user.id, symbols, db
                )
                if recent_recommendations:
                    return recent_recommendations

            # 6. Construire le prompt pour l'IA
            prompt = await self._build_trading_prompt(preferences, market_data, request)
            prompt_hash = self._calculate_prompt_hash(prompt)

            # 7. Appeler l'API Anthropic
            ai_response = await self._call_anthropic_api(api_key, prompt)

            # 8. Parser et valider la réponse
            recommendations = await self._parse_ai_response(ai_response)

            # 9. Enrichir avec des métadonnées et sauvegarder
            saved_recommendations = await self._save_recommendations(
                user.id, recommendations, market_data, prompt_hash, db
            )

            # 10. Construire la réponse finale
            context = AIGenerationContext(
                user_preferences=preferences.dict() if preferences else {},
                market_data_symbols=symbols,
                market_data_timestamp=max([md.data_timestamp for md in market_data]) if market_data else datetime.now(timezone.utc),
                prompt_length=len(prompt),
                model_used=self.model,
                api_key_last_4=api_key[-4:] if api_key else "****"
            )

            return AIRecommendationsListResponse(
                recommendations=saved_recommendations,
                generation_timestamp=datetime.now(timezone.utc),
                context=context.dict()
            )

        except Exception as e:
            logger.error(f"Erreur génération recommandations IA pour utilisateur {user.id}: {e}")
            raise

    async def _get_user_anthropic_key(self, user: User) -> Optional[str]:
        """Récupère et déchiffre la clé API Anthropic de l'utilisateur"""
        if not user.anthropic_api_key:
            return None

        try:
            return decrypt_api_key(user.anthropic_api_key)
        except Exception as e:
            logger.error(f"Erreur déchiffrement clé Anthropic utilisateur {user.id}: {e}")
            return None

    async def _get_user_preferences(self, user: User, db: Session) -> Optional[UserTradingPreferences]:
        """Récupère les préférences de trading de l'utilisateur"""
        return db.query(UserTradingPreferences).filter(
            UserTradingPreferences.user_id == user.id
        ).first()

    async def _determine_symbols(
        self,
        request: AIRecommendationRequest,
        preferences: Optional[UserTradingPreferences]
    ) -> List[str]:
        """Détermine les symboles à analyser selon la requête et les préférences"""
        if request.symbols:
            return request.symbols

        if preferences and preferences.preferred_assets:
            try:
                preferred = json.loads(preferences.preferred_assets)
                return preferred[:10]  # Max 10 symboles
            except (json.JSONDecodeError, TypeError):
                pass

        # Symboles par défaut si aucune préférence
        return ["BTC", "ETH", "SOL", "ADA", "DOT"]

    async def _get_recent_market_data(self, symbols: List[str], db: Session) -> List[MarketData]:
        """Récupère les données de marché récentes pour les symboles donnés"""
        # Récupérer les données les plus récentes pour chaque symbole (dernières 24h max)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

        market_data = []
        for symbol in symbols:
            latest = db.query(MarketData).filter(
                MarketData.symbol == symbol,
                MarketData.data_timestamp >= cutoff_time
            ).order_by(desc(MarketData.data_timestamp)).first()

            if latest:
                market_data.append(latest)

        return market_data

    async def _check_recent_recommendations(
        self,
        user_id: int,
        symbols: List[str],
        db: Session,
        hours_threshold: int = 2
    ) -> Optional[AIRecommendationsListResponse]:
        """Vérifie s'il existe des recommandations récentes pour éviter les doublons"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_threshold)

        recent = db.query(AIRecommendation).filter(
            AIRecommendation.user_id == user_id,
            AIRecommendation.created_at >= cutoff_time,
            AIRecommendation.symbol.in_(symbols)
        ).order_by(desc(AIRecommendation.created_at)).limit(10).all()

        if len(recent) >= 3:  # Si au moins 3 recommandations récentes
            from ..schemas.ai_recommendations import AIRecommendationResponse

            responses = [AIRecommendationResponse.from_orm(rec) for rec in recent]

            return AIRecommendationsListResponse(
                recommendations=responses,
                generation_timestamp=recent[0].created_at,
                context={"source": "cache", "cached_recommendations": len(recent)}
            )

        return None

    async def _build_trading_prompt(
        self,
        preferences: Optional[UserTradingPreferences],
        market_data: List[MarketData],
        request: AIRecommendationRequest
    ) -> str:
        """Construit le prompt détaillé pour l'analyse IA"""

        # Header du prompt
        prompt = """Tu es un expert en analyse technique et fondamentale des cryptomonnaies.
Ton rôle est de générer des recommandations de trading précises et personnalisées.

ANALYSE REQUISE:
- Évalue les tendances du marché
- Considère les niveaux de support/résistance
- Analyse le momentum et la volatilité
- Prends en compte le profil de risque de l'utilisateur
- Recommande une gestion de risque appropriée

"""

        # Profil utilisateur
        if preferences:
            prompt += f"""
PROFIL UTILISATEUR:
- Tolérance au risque: {preferences.risk_tolerance.value}
- Horizon d'investissement: {preferences.investment_horizon.value}
- Style de trading: {preferences.trading_style.value}
- Taille max de position: {preferences.max_position_size}%
- Stop-loss habituel: {preferences.stop_loss_percentage}%
- Ratio take-profit: {preferences.take_profit_ratio}

"""
            if preferences.technical_indicators:
                try:
                    indicators = json.loads(preferences.technical_indicators)
                    prompt += f"- Indicateurs préférés: {', '.join(indicators)}\n"
                except:
                    pass

        # Données de marché
        prompt += "\nDONNÉES DE MARCHÉ RÉCENTES:\n"
        for data in market_data:
            change_str = f"{data.price_change_24h:+.2f}%" if data.price_change_24h else "N/A"
            volume_str = f"${data.volume_24h_usd:,.0f}" if data.volume_24h_usd else "N/A"

            prompt += f"""
{data.symbol}:
- Prix: ${data.price_usd:,.2f} ({change_str} 24h)
- Volume 24h: {volume_str}
- Market Cap: ${data.market_cap_usd:,.0f}" if data.market_cap_usd else "N/A"
- Source: {data.source}
- Timestamp: {data.data_timestamp.strftime('%Y-%m-%d %H:%M UTC')}
"""

        # Instructions de format
        prompt += f"""
INSTRUCTIONS DE GÉNÉRATION:
1. Génère entre 1 et {request.max_recommendations} recommandations maximum
2. Privilégie la qualité à la quantité
3. Adapte les recommandations au profil de risque
4. Fournis des prix d'entrée, stop-loss et take-profit réalistes
5. Explique clairement ton raisonnement

FORMAT DE RÉPONSE OBLIGATOIRE (JSON strict):
{{
  "recommendations": [
    {{
      "action": "buy|sell|hold",
      "symbol": "BTC",
      "confidence": 85,
      "size_percentage": 15.0,
      "entry_price": 45000.0,
      "stop_loss": 43000.0,
      "take_profit1": 48000.0,
      "take_profit2": 50000.0,
      "take_profit3": 52000.0,
      "reasoning": "Analyse technique et fondamentale détaillée...",
      "risk_level": "low|medium|high"
    }}
  ]
}}

CONTRAINTES:
- confidence: 0-100
- size_percentage: adapté au profil de risque (max {preferences.max_position_size if preferences else 10}%)
- Cohérence prix d'entrée/stop-loss/take-profit
- risk_level cohérent avec l'action

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""

        return prompt

    def _calculate_prompt_hash(self, prompt: str) -> str:
        """Calcule un hash du prompt pour éviter les analyses en double"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]

    async def _call_anthropic_api(self, api_key: str, prompt: str) -> Dict[str, Any]:
        """Effectue l'appel à l'API Anthropic avec gestion d'erreurs complète"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.anthropic_base_url}/messages",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "temperature": 0.3,  # Peu de créativité pour plus de précision
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise ValueError("Clé API Anthropic invalide ou expirée")
                elif response.status_code == 429:
                    # Tenter de récupérer retry-after depuis les headers
                    retry_after = response.headers.get("retry-after", "60")
                    raise ValueError(f"Quota API Anthropic dépassé. Retry après {retry_after}s")
                elif response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Requête invalide")
                    raise ValueError(f"Erreur requête Anthropic: {error_msg}")
                else:
                    raise ValueError(f"Erreur API Anthropic: {response.status_code}")

        except asyncio.TimeoutError:
            raise ValueError("Timeout lors de l'appel à l'API Anthropic")
        except httpx.RequestError as e:
            raise ValueError(f"Erreur de connexion Anthropic: {str(e)}")

    async def _parse_ai_response(self, ai_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse et valide la réponse de l'API Anthropic"""
        try:
            # Extraire le contenu textuel
            content = ai_response.get("content", [])
            if not content or not isinstance(content, list):
                raise ValueError("Format de réponse Anthropic invalide: pas de contenu")

            text_content = ""
            for block in content:
                if block.get("type") == "text":
                    text_content = block.get("text", "")
                    break

            if not text_content:
                raise ValueError("Pas de contenu textuel dans la réponse Anthropic")

            # Nettoyer le texte et extraire le JSON
            text_content = text_content.strip()

            # Trouver le JSON (peut être entouré de texte)
            start = text_content.find("{")
            end = text_content.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("Aucun JSON valide trouvé dans la réponse")

            json_content = text_content[start:end]

            # Parser le JSON
            parsed_response = json.loads(json_content)

            # Valider avec Pydantic
            validated = RawAIResponse(**parsed_response)

            return [rec.dict() for rec in validated.recommendations]

        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            logger.error(f"Contenu reçu: {text_content[:500]}...")
            raise ValueError(f"Réponse JSON invalide de l'IA: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur parsing réponse IA: {e}")
            raise ValueError(f"Impossible de parser la réponse IA: {str(e)}")

    async def _save_recommendations(
        self,
        user_id: int,
        recommendations: List[Dict[str, Any]],
        market_data: List[MarketData],
        prompt_hash: str,
        db: Session
    ) -> List[Any]:  # Type sera AIRecommendationResponse après import
        """Sauvegarde les recommandations en base de données"""
        saved_recommendations = []
        market_timestamp = max([md.data_timestamp for md in market_data]) if market_data else datetime.now(timezone.utc)

        try:
            for rec_data in recommendations:
                # Utiliser les valeurs string directement
                db_recommendation = AIRecommendation(
                    user_id=user_id,
                    action=rec_data["action"],  # String directement
                    symbol=rec_data["symbol"].upper(),
                    confidence=rec_data["confidence"],
                    size_percentage=rec_data["size_percentage"],
                    entry_price=rec_data.get("entry_price"),
                    stop_loss=rec_data.get("stop_loss"),
                    take_profit1=rec_data.get("take_profit1"),
                    take_profit2=rec_data.get("take_profit2"),
                    take_profit3=rec_data.get("take_profit3"),
                    reasoning=rec_data.get("reasoning"),
                    risk_level=rec_data["risk_level"],  # String directement
                    market_data_timestamp=market_timestamp,
                    prompt_hash=prompt_hash,
                    model_used=self.model
                )

                db.add(db_recommendation)
                db.flush()  # Pour obtenir l'ID
                saved_recommendations.append(db_recommendation)

            db.commit()

            # Convertir en schémas de réponse
            from ..schemas.ai_recommendations import AIRecommendationResponse
            return [AIRecommendationResponse.from_orm(rec) for rec in saved_recommendations]

        except Exception as e:
            db.rollback()
            logger.error(f"Erreur sauvegarde recommandations: {e}")
            raise ValueError(f"Impossible de sauvegarder les recommandations: {str(e)}")

    async def get_user_recommendation_history(
        self,
        user: User,
        db: Session,
        limit: int = 50,
        symbol: Optional[str] = None
    ) -> List[Any]:  # Type sera AIRecommendationResponse
        """Récupère l'historique des recommandations d'un utilisateur"""
        query = db.query(AIRecommendation).filter(AIRecommendation.user_id == user.id)

        if symbol:
            query = query.filter(AIRecommendation.symbol == symbol.upper())

        recommendations = query.order_by(desc(AIRecommendation.created_at)).limit(limit).all()

        from ..schemas.ai_recommendations import AIRecommendationResponse
        return [AIRecommendationResponse.from_orm(rec) for rec in recommendations]