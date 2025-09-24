from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import logging
import json
from datetime import datetime

from ..database import get_db
from ..models.user import User
from ..auth import get_current_user, decrypt_api_key
from ..schemas.claude import (
    ClaudeModel,
    SingleAssetAnalysisRequest,
    SingleAssetAnalysisResponse,
    TechnicalDataLight
)
from ..services.connectors.anthropic_connector import AnthropicConnector
from ..services.ccxt_service import CCXTService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claude", tags=["claude"])

# Initialisation des services
anthropic_connector = AnthropicConnector()
ccxt_service = CCXTService()


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


@router.post("/analyze-single-asset", response_model=SingleAssetAnalysisResponse)
async def analyze_single_asset_with_technical(
    request: SingleAssetAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyse complète d'un seul actif avec données techniques multi-timeframes

    Processus:
    1. Récupère 600 bougies sur 3 timeframes via CCXT
    2. Calcule indicateurs techniques complets
    3. Envoie données complètes (avec bougies) au LLM Claude
    4. Retourne analyse Claude + données techniques allégées au frontend
    """
    try:
        request_id = str(uuid.uuid4())
        start_time = datetime.now()

        logger.info(f"Analyse single-asset {request_id}: {request.ticker} - {request.profile}")

        # 1. Vérifier la clé API Anthropic
        if not current_user.anthropic_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé API Anthropic configurée. Configurez-la dans vos paramètres."
            )

        api_key = decrypt_api_key(current_user.anthropic_api_key)

        # 2. Récupérer données techniques multi-timeframes (600 bougies par TF)
        try:
            technical_data = await ccxt_service.get_multi_timeframe_analysis(
                exchange_name=request.exchange,
                symbol=request.ticker,
                profile=request.profile
            )

            if "status" in technical_data and technical_data["status"] == "error":
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur récupération données techniques: {technical_data['message']}"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur service CCXT: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la récupération des données techniques"
            )

        # 3. Préparer les prompts système et utilisateur
        system_prompt = """Tu es un expert en analyse technique de trading cryptocurrency avec une expertise en analyse multi-timeframes. Tu dois analyser des données techniques complètes et fournir des recommandations de trading précises basées sur les indicateurs, patterns, et structure de marché."""

        user_prompt = f"""
ANALYSE TECHNIQUE DÉTAILLÉE - {request.ticker}

Profil de trading: {request.profile}
Exchange: {request.exchange}

=== DONNÉES TECHNIQUES COMPLÈTES ===
{json.dumps(technical_data, indent=2, ensure_ascii=False)}

=== INSTRUCTIONS D'ANALYSE ===
Analysez ces données techniques multi-timeframes et fournissez:

1. **SITUATION ACTUELLE**
   - Prix actuel et contexte de marché
   - Analyse de la structure multi-timeframes
   - Confluence des indicateurs

2. **ANALYSE PAR TIMEFRAME**
   - Timeframe principal ({technical_data.get('tf', 'N/A')}): Tendance, signaux d'entrée/sortie
   - Contexte supérieur: Biais directionnel et niveaux clés
   - Contexte inférieur: Points d'entrée précis et timing

3. **SIGNAUX DE TRADING**
   - Points d'entrée potentiels avec justifications
   - Niveaux de stop-loss basés sur la structure
   - Objectifs de take-profit réalistes
   - Gestion de position recommandée

4. **ÉVALUATION DES RISQUES**
   - Analyse de la volatilité (ATR)
   - Identification des zones dangereuses
   - Scénarios alternatifs

5. **RECOMMANDATION FINALE**
   - Action recommandée (ACHAT/VENTE/ATTENTE)
   - Niveau de confiance et horizon temporel
   - Conditions de révision de l'analyse

Utilisez les données de bougies pour identifier les patterns, cassures, et niveaux de prix précis.
Basez vos recommandations sur les 600 bougies analysées pour chaque timeframe.
"""

        # 4. Ajouter instructions personnalisées si fournies
        if request.custom_prompt:
            user_prompt += f"\n\n=== INSTRUCTIONS ADDITIONNELLES ===\n{request.custom_prompt}"

        # 5. Appeler Claude avec toutes les données
        try:
            claude_response = await anthropic_connector.generate_analysis(
                api_key=api_key,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=request.model
            )

            if claude_response["status"] != "success":
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur analyse Claude: {claude_response.get('message', 'Erreur inconnue')}"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur appel Claude: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de l'appel à l'API Claude"
            )

        # 6. Préparer données techniques allégées (sans bougies pour frontend)
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
                # Pas de last_20_candles ici
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
                # Pas de last_20_candles ici non plus
            }
        )

        # 7. Calculer métriques de performance
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        tokens_used = claude_response.get("tokens_used", 0)

        # 8. Construire réponse finale
        response = SingleAssetAnalysisResponse(
            request_id=request_id,
            timestamp=start_time,
            model_used=request.model,
            ticker=request.ticker,
            exchange=request.exchange,
            profile=request.profile,
            technical_data=technical_light,
            claude_analysis=claude_response.get("content", ""),
            tokens_used=tokens_used,
            processing_time_ms=int(processing_time),
            warnings=[]
        )

        logger.info(
            f"Analyse {request_id} terminée - "
            f"Tokens: {tokens_used}, Temps: {int(processing_time)}ms"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue analyze_single_asset: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'analyse"
        )