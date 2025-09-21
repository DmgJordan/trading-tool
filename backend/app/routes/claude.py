from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import logging
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..models.user_preferences import UserTradingPreferences
from ..auth import get_current_user, decrypt_api_key
from ..schemas.claude import (
    ClaudeAnalysisRequest,
    ClaudeAnalysisResponse,
    ClaudeAnalysisHistory,
    ClaudeErrorResponse,
    ClaudeModel
)
from ..services.claude_prompt_service import ClaudePromptService
from ..services.market_data_service import MarketDataService
from ..services.connectors.anthropic_connector import AnthropicConnector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claude", tags=["claude"])

# Initialisation des services
prompt_service = ClaudePromptService()
market_service = MarketDataService()
anthropic_connector = AnthropicConnector()

@router.post("/analyze-trading", response_model=ClaudeAnalysisResponse)
async def analyze_trading_assets(
    request: ClaudeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyse trading complète d'actifs avec Claude AI

    Cette endpoint génère une analyse trading personnalisée en utilisant:
    - Les préférences de trading de l'utilisateur
    - Les données de marché CoinGecko en temps réel
    - Le modèle Claude sélectionné
    - Un prompt optimisé selon le type d'analyse
    """
    try:
        # Générer un ID unique pour cette requête
        request_id = str(uuid.uuid4())

        logger.info(f"Début analyse trading {request_id} pour utilisateur {current_user.id}")
        logger.info(f"Actifs: {request.assets}, Modèle: {request.model.value}")

        # 1. Vérifier la clé API Anthropic
        if not current_user.anthropic_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé API Anthropic configurée. Veuillez configurer votre clé API dans les paramètres."
            )

        # Déchiffrer la clé API
        try:
            api_key = decrypt_api_key(current_user.anthropic_api_key)
        except Exception as e:
            logger.error(f"Erreur déchiffrement clé API: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors du déchiffrement de la clé API"
            )

        # 2. Récupérer les préférences utilisateur (optionnel)
        user_preferences = None
        if request.use_user_preferences:
            user_preferences = db.query(UserTradingPreferences).filter(
                UserTradingPreferences.user_id == current_user.id
            ).first()

            if not user_preferences:
                logger.warning(f"Aucune préférence trouvée pour utilisateur {current_user.id}")

        # 3. Récupérer les données de marché CoinGecko (optionnel)
        market_data = {}
        if request.include_market_data:
            # Vérifier la clé API CoinGecko
            if current_user.coingecko_api_key:
                try:
                    coingecko_key = decrypt_api_key(current_user.coingecko_api_key)
                    market_data = await market_service.get_market_data_for_assets(
                        api_key=coingecko_key,
                        assets=request.assets
                    )
                    logger.info(f"Données marché récupérées pour {len(market_data)} actifs")
                except Exception as e:
                    logger.error(f"Erreur récupération données marché: {e}")
                    # Continuer sans les données de marché
            else:
                logger.warning("Aucune clé CoinGecko configurée, analyse sans données de marché")

        # 4. Générer le prompt adaptatif
        try:
            generated_prompt = prompt_service.generate_trading_prompt(
                assets=request.assets,
                model=request.model,
                market_data=market_data,
                user_preferences=user_preferences,
                analysis_type=request.analysis_type,
                custom_prompt=request.custom_prompt
            )
            logger.info(f"Prompt généré: {generated_prompt.estimated_tokens} tokens estimés")
        except Exception as e:
            logger.error(f"Erreur génération prompt: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la génération du prompt d'analyse"
            )

        # 5. Appeler Claude pour l'analyse
        try:
            analysis_result = await anthropic_connector.generate_trading_analysis(
                api_key=api_key,
                prompt=generated_prompt,
                model=request.model,
                request_id=request_id,
                assets=request.assets
            )

            if analysis_result["status"] != "success":
                error_msg = analysis_result.get("message", "Erreur inconnue lors de l'analyse")
                logger.error(f"Erreur Claude: {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)

            analysis_data = analysis_result["data"]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur appel Claude: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de l'appel à l'API Claude"
            )

        # 6. Enrichir la réponse avec les données contextuelles
        try:
            # Ajouter les données de marché utilisées
            analysis_data["market_data"] = {
                asset: {
                    "symbol": data.symbol,
                    "name": data.name,
                    "current_price": data.current_price,
                    "price_change_24h": data.price_change_24h,
                    "volume_24h": data.volume_24h,
                    "market_cap": data.market_cap,
                    "last_updated": data.last_updated.isoformat()
                }
                for asset, data in market_data.items()
            }

            # Ajouter résumé des préférences utilisateur
            if user_preferences:
                analysis_data["user_preferences_summary"] = {
                    "risk_tolerance": user_preferences.risk_tolerance.value,
                    "investment_horizon": user_preferences.investment_horizon.value,
                    "trading_style": user_preferences.trading_style.value,
                    "max_position_size": user_preferences.max_position_size,
                    "stop_loss_percentage": user_preferences.stop_loss_percentage,
                    "take_profit_ratio": user_preferences.take_profit_ratio
                }

        except Exception as e:
            logger.error(f"Erreur enrichissement réponse: {e}")
            # Continuer avec les données de base

        # 7. Logger le succès
        logger.info(
            f"Analyse {request_id} terminée avec succès - "
            f"Tokens: {analysis_data.get('tokens_used', 0)}, "
            f"Temps: {analysis_data.get('processing_time_ms', 0)}ms"
        )

        # 8. Retourner la réponse structurée
        return ClaudeAnalysisResponse(**analysis_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue dans analyze_trading_assets: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'analyse trading"
        )

@router.get("/analysis-history", response_model=List[ClaudeAnalysisHistory])
async def get_analysis_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des analyses Claude de l'utilisateur

    Note: Cette fonctionnalité nécessite l'implémentation d'un système
    de stockage des analyses en base de données (fonctionnalité future).
    """
    try:
        # TODO: Implémenter le stockage des analyses en base
        # Pour l'instant, retourner une liste vide
        logger.info(f"Demande historique analyses pour utilisateur {current_user.id}")

        return []

    except Exception as e:
        logger.error(f"Erreur récupération historique: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération de l'historique"
        )

@router.post("/test-connection")
async def test_claude_connection(
    model: ClaudeModel = ClaudeModel.HAIKU,
    current_user: User = Depends(get_current_user)
):
    """
    Test rapide de connectivité avec l'API Claude

    Utilise le modèle le plus économique (Haiku) pour un test minimal.
    """
    try:
        if not current_user.anthropic_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé API Anthropic configurée"
            )

        # Déchiffrer la clé API
        api_key = decrypt_api_key(current_user.anthropic_api_key)

        # Test de base avec le connector existant
        result = await anthropic_connector.test_connection(api_key)

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Connexion Claude réussie avec {model.value}",
                "model_tested": model.value,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Erreur de connexion Claude")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur test connexion Claude: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du test de connexion"
        )

@router.get("/supported-assets")
async def get_supported_assets():
    """
    Retourne la liste des actifs supportés pour l'analyse

    Basé sur les mappings CoinGecko disponibles dans le MarketDataService.
    """
    try:
        supported_assets = market_service.get_supported_assets()

        return {
            "assets": sorted(supported_assets),
            "total_count": len(supported_assets),
            "categories": {
                "major": ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL"],
                "defi": ["AAVE", "UNI", "SUSHI", "CRV", "COMP", "YFI", "MKR"],
                "layer2": ["MATIC", "AVAX", "FTM", "ONE"],
                "gaming": ["AXS", "MANA", "SAND", "ENJ", "CHZ"]
            },
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erreur récupération actifs supportés: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des actifs supportés"
        )

@router.get("/models")
async def get_available_models():
    """
    Retourne la liste des modèles Claude disponibles avec leurs caractéristiques
    """
    try:
        models_info = {
            ClaudeModel.HAIKU.value: {
                "name": "Claude 3 Haiku",
                "description": "Modèle rapide et économique, idéal pour des analyses concises",
                "max_tokens": 2048,
                "typical_speed": "Très rapide",
                "cost_level": "Faible",
                "best_for": ["Analyses rapides", "Résumés", "Signaux simples"]
            },
            ClaudeModel.SONNET.value: {
                "name": "Claude 3 Sonnet",
                "description": "Équilibre optimal entre performance et coût",
                "max_tokens": 3072,
                "typical_speed": "Rapide",
                "cost_level": "Modéré",
                "best_for": ["Analyses détaillées", "Stratégies", "Recommandations"]
            },
            ClaudeModel.SONNET_35.value: {
                "name": "Claude 3.5 Sonnet",
                "description": "Version améliorée avec capacités avancées",
                "max_tokens": 4096,
                "typical_speed": "Rapide",
                "cost_level": "Modéré",
                "best_for": ["Analyses complexes", "Corrélations", "Insights avancés"],
                "recommended": True
            },
            ClaudeModel.OPUS.value: {
                "name": "Claude 3 Opus",
                "description": "Modèle le plus sophistiqué pour analyses approfondies",
                "max_tokens": 4096,
                "typical_speed": "Plus lent",
                "cost_level": "Élevé",
                "best_for": ["Analyses institutionnelles", "Recherche", "Stratégies complexes"]
            }
        }

        return {
            "models": models_info,
            "default_model": ClaudeModel.SONNET_35.value,
            "total_count": len(models_info)
        }

    except Exception as e:
        logger.error(f"Erreur récupération modèles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des modèles"
        )

@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Retourne les statistiques du cache des données de marché

    Utile pour le debug et l'optimisation des performances.
    """
    try:
        cache_stats = market_service.get_cache_stats()

        return {
            "cache_stats": cache_stats,
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }

    except Exception as e:
        logger.error(f"Erreur récupération stats cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des statistiques"
        )

@router.post("/cache/clear")
async def clear_market_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Nettoie le cache des données de marché

    Force la récupération de nouvelles données lors du prochain appel.
    """
    try:
        market_service.clear_cache()

        logger.info(f"Cache nettoyé par utilisateur {current_user.id}")

        return {
            "status": "success",
            "message": "Cache des données de marché nettoyé",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Erreur nettoyage cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du nettoyage du cache"
        )