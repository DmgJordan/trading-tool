from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging

from ..database import get_db
from ..models.user import User
from ..schemas.ai_recommendations import (
    AIRecommendationRequest,
    AIRecommendationsListResponse,
    AIRecommendationResponse,
    AIAnalysisError
)
from ..services.ai_trading_service import AITradingService
from ..auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai-recommendations"])

# Instance du service IA (singleton)
ai_service = AITradingService()

@router.post("/generate-recommendations", response_model=AIRecommendationsListResponse)
async def generate_ai_recommendations(
    request: AIRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère des recommandations de trading personnalisées avec l'IA.

    Cette endpoint combine:
    - Les préférences de trading de l'utilisateur
    - Les données de marché récentes
    - L'analyse avancée de Claude (Anthropic)

    Pour obtenir des recommandations personnalisées et actionnables.
    """
    try:
        logger.info(f"Génération recommandations IA pour utilisateur {current_user.id}")

        # Générer les recommandations via le service IA
        recommendations = await ai_service.generate_recommendations(
            user=current_user,
            request=request,
            db=db
        )

        logger.info(
            f"Recommandations générées avec succès pour utilisateur {current_user.id}: "
            f"{len(recommendations.recommendations)} recommandations"
        )

        return recommendations

    except ValueError as ve:
        # Erreurs métier (clé API manquante, quota dépassé, etc.)
        logger.warning(f"Erreur métier génération IA utilisateur {current_user.id}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_type": "validation_error",
                "message": str(ve),
                "user_id": current_user.id
            }
        )

    except Exception as e:
        # Erreurs techniques inattendues
        logger.error(f"Erreur technique génération IA utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_error",
                "message": "Erreur interne lors de la génération des recommandations",
                "user_id": current_user.id
            }
        )

@router.get("/recommendations/history", response_model=List[AIRecommendationResponse])
async def get_recommendations_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100, description="Nombre de recommandations à récupérer"),
    symbol: Optional[str] = Query(default=None, description="Filtrer par symbole (ex: BTC)")
):
    """
    Récupère l'historique des recommandations IA de l'utilisateur.

    Permet de consulter les recommandations passées pour:
    - Analyser les performances
    - Comparer les prédictions avec les résultats réels
    - Affiner la stratégie de trading
    """
    try:
        logger.info(f"Récupération historique recommandations utilisateur {current_user.id}")

        recommendations = await ai_service.get_user_recommendation_history(
            user=current_user,
            db=db,
            limit=limit,
            symbol=symbol
        )

        logger.info(
            f"Historique récupéré pour utilisateur {current_user.id}: "
            f"{len(recommendations)} recommandations"
        )

        return recommendations

    except Exception as e:
        logger.error(f"Erreur récupération historique utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_error",
                "message": "Erreur lors de la récupération de l'historique",
                "user_id": current_user.id
            }
        )

@router.get("/recommendations/latest", response_model=List[AIRecommendationResponse])
async def get_latest_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=5, ge=1, le=20, description="Nombre de recommandations récentes"),
    hours: int = Query(default=24, ge=1, le=168, description="Récupérer les recommandations des X dernières heures")
):
    """
    Récupère les recommandations IA les plus récentes de l'utilisateur.

    Utile pour:
    - Afficher un résumé des dernières recommandations
    - Vérifier l'état actuel des positions suggérées
    - Interface rapide sans générer de nouvelles recommandations
    """
    try:
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import desc
        from ..models.ai_recommendations import AIRecommendation

        logger.info(f"Récupération recommandations récentes utilisateur {current_user.id}")

        # Calculer la date limite
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Requête pour les recommandations récentes
        recent_recommendations = db.query(AIRecommendation).filter(
            AIRecommendation.user_id == current_user.id,
            AIRecommendation.created_at >= cutoff_time
        ).order_by(desc(AIRecommendation.created_at)).limit(limit).all()

        # Convertir en schémas de réponse
        recommendations = [
            AIRecommendationResponse.from_orm(rec) for rec in recent_recommendations
        ]

        logger.info(
            f"Recommandations récentes récupérées pour utilisateur {current_user.id}: "
            f"{len(recommendations)} recommandations des {hours} dernières heures"
        )

        return recommendations

    except Exception as e:
        logger.error(f"Erreur récupération recommandations récentes utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_error",
                "message": "Erreur lors de la récupération des recommandations récentes",
                "user_id": current_user.id
            }
        )

@router.get("/status")
async def get_ai_service_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vérifie le statut du service IA pour l'utilisateur actuel.

    Retourne:
    - Statut de la clé API Anthropic
    - Nombre de recommandations générées aujourd'hui
    - Informations sur les préférences configurées
    """
    try:
        from datetime import datetime, timezone, timedelta
        from ..models.ai_recommendations import AIRecommendation
        from ..models.user_preferences import UserTradingPreferences
        from ..auth import decrypt_api_key

        logger.info(f"Vérification statut service IA utilisateur {current_user.id}")

        # Vérifier la clé API Anthropic
        anthropic_status = "not_configured"
        if current_user.anthropic_api_key:
            try:
                api_key = decrypt_api_key(current_user.anthropic_api_key)
                if api_key and api_key.startswith("sk-ant-"):
                    anthropic_status = "configured"
                else:
                    anthropic_status = "invalid_format"
            except:
                anthropic_status = "decryption_error"

        # Compter les recommandations générées aujourd'hui
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(AIRecommendation).filter(
            AIRecommendation.user_id == current_user.id,
            AIRecommendation.created_at >= today_start
        ).count()

        # Vérifier les préférences de trading
        preferences = db.query(UserTradingPreferences).filter(
            UserTradingPreferences.user_id == current_user.id
        ).first()

        preferences_status = "configured" if preferences else "not_configured"

        # Dernière recommandation
        last_recommendation = db.query(AIRecommendation).filter(
            AIRecommendation.user_id == current_user.id
        ).order_by(desc(AIRecommendation.created_at)).first()

        last_generation_time = None
        if last_recommendation:
            last_generation_time = last_recommendation.created_at

        status_response = {
            "user_id": current_user.id,
            "anthropic_api_status": anthropic_status,
            "trading_preferences_status": preferences_status,
            "recommendations_generated_today": today_count,
            "last_generation_time": last_generation_time,
            "service_available": anthropic_status == "configured" and preferences_status == "configured",
            "checks": {
                "anthropic_key": anthropic_status == "configured",
                "trading_preferences": preferences_status == "configured",
                "can_generate": anthropic_status == "configured"
            }
        }

        return status_response

    except Exception as e:
        logger.error(f"Erreur vérification statut service IA utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "internal_error",
                "message": "Erreur lors de la vérification du statut",
                "user_id": current_user.id
            }
        )

@router.get("/models")
async def get_available_models():
    """
    Retourne les informations sur les modèles IA disponibles.

    Informatif pour l'interface utilisateur.
    """
    return {
        "current_model": ai_service.model,
        "model_info": {
            "name": "Claude 3.5 Sonnet",
            "version": "20241022",
            "capabilities": [
                "Analyse technique avancée",
                "Analyse fondamentale",
                "Gestion du risque",
                "Recommandations personnalisées"
            ],
            "max_tokens": ai_service.max_tokens,
            "timeout_seconds": ai_service.timeout
        },
        "supported_features": [
            "Recommandations buy/sell/hold",
            "Calcul de niveaux de prix",
            "Analyse multi-symboles",
            "Personnalisation selon profil de risque",
            "Gestion de position optimisée"
        ]
    }