"""
Router pour les endpoints IA

Migré depuis:
- app/routes/claude.py
- app/routes/ai_recommendations.py (endpoints génération)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ...core import get_db, get_current_user
from ...domains.auth.models import User

from .schemas import (
    SingleAssetAnalysisRequest,
    StructuredAnalysisResponse,
    AIProviderType,
    AITestRequest,
    AITestResponse,
    ClaudeModel,
)
from .service import AIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

# Instance du service IA (singleton)
ai_service = AIService()


# ═══════════════════════════════════════════════════════════════
# ANALYSE SINGLE-ASSET
# ═══════════════════════════════════════════════════════════════

@router.post("/analyze", response_model=StructuredAnalysisResponse)
async def analyze_single_asset(
    request: SingleAssetAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyse complète d'un seul actif avec données techniques multi-timeframes

    Migré depuis POST /claude/analyze-single-asset

    Processus:
    1. Récupère 600 bougies sur 3 timeframes via CCXT
    2. Calcule indicateurs techniques complets
    3. Envoie données complètes (avec bougies) au LLM
    4. Retourne analyse + données techniques allégées au frontend
    """
    try:
        logger.info(f"Analyse single-asset pour utilisateur {current_user.id}: {request.ticker}")

        result = await ai_service.analyze_single_asset(
            request=request,
            user=current_user,
            db=db
        )

        return result

    except ValueError as ve:
        logger.warning(f"Erreur métier analyse single-asset utilisateur {current_user.id}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as e:
        logger.error(f"Erreur technique analyse single-asset utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'analyse"
        )


# ═══════════════════════════════════════════════════════════════
# TESTS ET VALIDATION
# ═══════════════════════════════════════════════════════════════

@router.post("/test-provider", response_model=AITestResponse)
async def test_provider_connection(
    provider: AIProviderType = AIProviderType.ANTHROPIC,
    current_user: User = Depends(get_current_user)
):
    """
    Test rapide de connectivité avec un provider IA

    Migré depuis POST /claude/test-connection

    Utilise la clé API stockée de l'utilisateur pour tester la connexion.
    """
    try:
        logger.info(f"Test connexion {provider.value} pour utilisateur {current_user.id}")

        # Récupérer la clé API de l'utilisateur
        api_key = await ai_service._get_user_api_key(current_user, provider)

        # Tester la connexion
        result = await ai_service.test_provider_connection(api_key, provider)

        status_value = "success" if result["status"] == "success" else "error"

        return AITestResponse(
            provider=provider,
            status=status_value,
            message=result.get("message", "Test terminé"),
            timestamp=datetime.now()
        )

    except ValueError as ve:
        logger.warning(f"Erreur test connexion {provider.value} utilisateur {current_user.id}: {ve}")
        return AITestResponse(
            provider=provider,
            status="error",
            message=str(ve),
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Erreur test connexion {provider.value} utilisateur {current_user.id}: {e}")
        return AITestResponse(
            provider=provider,
            status="error",
            message=f"Erreur lors du test: {str(e)}",
            timestamp=datetime.now()
        )


# ═══════════════════════════════════════════════════════════════
# INFORMATIONS PROVIDERS ET MODÈLES
# ═══════════════════════════════════════════════════════════════

@router.get("/providers")
async def get_available_providers():
    """
    Retourne la liste des providers IA disponibles

    Nouveau endpoint pour architecture multi-providers
    """
    try:
        providers = ai_service.get_available_providers()
        return {
            "providers": providers,
            "count": len(providers)
        }

    except Exception as e:
        logger.error(f"Erreur récupération providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des providers"
        )


@router.get("/models")
async def get_available_models():
    """
    Retourne les informations sur les modèles IA disponibles

    Migré depuis GET /ai/models

    Informatif pour l'interface utilisateur.
    """
    return {
        "default_model": ai_service.default_model,
        "supported_models": {
            "claude": [
                {
                    "id": ClaudeModel.HAIKU_35.value,
                    "name": "Claude 3.5 Haiku",
                    "description": "Analyse rapide et concise",
                    "use_case": "Analyses rapides, réponses courtes"
                },
                {
                    "id": ClaudeModel.SONNET_45.value,
                    "name": "Claude Sonnet 4.5",
                    "description": "Analyse équilibrée et détaillée (recommandé)",
                    "use_case": "Analyses complètes, qualité institutionnelle"
                },
                {
                    "id": ClaudeModel.OPUS_41.value,
                    "name": "Claude Opus 4.1",
                    "description": "Analyse institutionnelle sophistiquée",
                    "use_case": "Analyses exhaustives, recherche quantitative"
                }
            ]
        },
        "capabilities": [
            "Analyse technique avancée",
            "Analyse multi-timeframes",
            "Gestion du risque",
            "Recommandations personnalisées",
            "Calcul de niveaux de prix"
        ],
        "max_tokens": ai_service.max_tokens,
        "timeout_seconds": ai_service.timeout
    }
