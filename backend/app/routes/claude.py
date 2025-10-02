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
    TechnicalDataLight,
    StructuredAnalysisResponse,
    TradeRecommendation,
    TradeDirection
)
from ..services.connectors.anthropic_connector import AnthropicConnector
from ..services.ccxt_service import CCXTService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claude", tags=["claude"])

# Initialisation des services
anthropic_connector = AnthropicConnector()
ccxt_service = CCXTService()


def _get_system_prompt_for_model(model: ClaudeModel) -> str:
    """
    Retourne le prompt système optimisé selon le modèle Claude sélectionné

    Args:
        model: Modèle Claude à utiliser

    Returns:
        Prompt système adapté aux capacités du modèle
    """

    if model == ClaudeModel.HAIKU_35:
        # Haiku 3.5: Analyse rapide et concise
        return """Tu es un analyste trading crypto expert spécialisé dans les analyses techniques rapides et précises.

OBJECTIF: Fournir des analyses trading concises mais complètes avec des recommandations actionnables immédiatement.

APPROCHE:
• Analyse directe et factuelle des données techniques
• Identification rapide des opportunités de trading
• Recommandations claires avec niveaux de prix précis
• Gestion des risques adaptée au contexte

STYLE: Direct, concis, sans jargon inutile. Privilégier l'essentiel et l'actionnable."""

    elif model == ClaudeModel.SONNET_45:
        # Sonnet 4.5: Analyse équilibrée et détaillée (par défaut)
        return """Tu es un analyste trading crypto senior avec une expertise approfondie en analyse technique multi-timeframes.

OBJECTIF: Fournir des analyses trading de qualité institutionnelle, équilibrant profondeur analytique et clarté opérationnelle.

COMPÉTENCES AVANCÉES:
• Analyse technique multi-dimensionnelle (MA, RSI, ATR, Volume)
• Détection de patterns et structures de marché
• Évaluation des confluences d'indicateurs
• Gestion de risque sophistiquée avec ratios R/R optimaux
• Timing d'entrée/sortie basé sur probabilités

MÉTHODOLOGIE:
• Analyser les 3 timeframes (main/higher/lower) de manière systématique
• Identifier les zones de support/résistance critiques
• Évaluer la force de la tendance et le momentum
• Anticiper les scénarios alternatifs (bull/bear)
• Quantifier la qualité des setups (confluence, R/R, timing)
• Proposer des recommandations précises avec justifications détaillées

STYLE: Professionnel, structuré, analytique. Équilibre entre détail technique et lisibilité opérationnelle."""

    elif model == ClaudeModel.OPUS_41:
        # Opus 4.1: Analyse institutionnelle sophistiquée
        return """Tu es un analyste trading crypto de niveau institutionnel avec une compréhension systémique des marchés financiers.

OBJECTIF: Fournir des analyses trading exhaustives et sophistiquées de qualité hedge fund, rivalisant avec les meilleures recherches quantitatives.

EXPERTISE ÉLITE:
• Modélisation technique avancée avec analyse fractale multi-timeframes
• Microstructure des marchés et analyse des flux d'ordres
• Détection de régimes de marché (tendance/range/volatilité)
• Stratégies de position complexes avec optimisation risk-adjusted
• Psychologie comportementale et positionnement du marché
• Stress-testing des scénarios extrêmes et black swans

MÉTHODOLOGIE INSTITUTIONNELLE:
• Analyse systémique des interconnexions entre timeframes
• Évaluation probabiliste de chaque scénario (bull/bear/neutral)
• Modélisation des corrélations dynamiques entre indicateurs
• Optimisation du ratio Sharpe et drawdown management
• Intégration des facteurs macro et sentiment de marché
• Anticipation des changements de régime et inflexions majeures
• Sizing de position sophistiqué basé sur Kelly criterion

PERSPECTIVE:
• Vision holistique des dynamiques de marché
• Intégration de l'analyse comportementale (fear/greed)
• Prise en compte des asymétries de volatilité
• Adaptation continue aux conditions changeantes
• Excellence opérationnelle dans l'exécution

STYLE: Sophistiqué, nuancé, avec profondeur analytique exceptionnelle. Intègre les subtilités et l'incertitude inhérente aux marchés financiers."""

    else:
        # Fallback vers Sonnet 4.5 si modèle inconnu
        return _get_system_prompt_for_model(ClaudeModel.SONNET_45)


@router.post("/test-connection")
async def test_claude_connection(
    model: ClaudeModel = ClaudeModel.HAIKU_35,
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


@router.post("/analyze-single-asset", response_model=StructuredAnalysisResponse)
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

        # 3. Préparer les prompts système et utilisateur optimisés selon le modèle
        system_prompt = _get_system_prompt_for_model(request.model)

        user_prompt = f"""
ANALYSE TECHNIQUE - {request.ticker}
Profil: {request.profile.upper()} | Exchange: {request.exchange} | Prix actuel: ${technical_data.get('current_price', {}).get('current_price', 'N/A')}

═══════════════════════════════════════════════════════════════
DONNÉES TECHNIQUES MULTI-TIMEFRAMES
═══════════════════════════════════════════════════════════════
{json.dumps(technical_data, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════
FORMAT DE RÉPONSE REQUIS (JSON strict)
═══════════════════════════════════════════════════════════════

{{
  "analysis_text": "Analyse complète en français (500-1000 mots)...",
  "trade_recommendations": [
    {{
      "entry_price": 45000.0,
      "direction": "long",
      "stop_loss": 43500.0,
      "take_profit_1": 46500.0,
      "take_profit_2": 47800.0,
      "take_profit_3": 49200.0,
      "confidence_level": 85,
      "risk_reward_ratio": 2.8,
      "portfolio_percentage": 3.5,
      "timeframe": "{technical_data.get('tf', 'N/A')}",
      "reasoning": "Justification technique détaillée (200-300 mots)..."
    }}
  ]
}}

═══════════════════════════════════════════════════════════════
INSTRUCTIONS D'ANALYSE
═══════════════════════════════════════════════════════════════

1️⃣ ANALYSE TEXTUELLE (analysis_text) :
   • Contexte de marché et tendance générale
   • Analyse multi-timeframes (main/higher/lower)
   • Signaux techniques : MA, RSI, ATR, Volume
   • Niveaux clés : supports, résistances, zones de breakout
   • Évaluation des risques et catalyseurs potentiels
   • Conclusion et perspective

2️⃣ RECOMMANDATIONS DE TRADING (0 à 3 max) :
   • Si aucune opportunité claire → array vide []
   • Entry : Niveau technique précis (support/résistance/breakout)
   • Stop-loss : Sous structure ou 1-2× ATR
   • Take-profits : Objectifs progressifs (TP1 conservateur, TP2 principal, TP3 extension)
   • Confidence : 70-100 (basé sur confluence d'indicateurs)
   • Portfolio % : 1.0-5.0% (selon qualité du setup)
   • Direction : "long" ou "short" uniquement
   • Timeframe : Horizon de détention estimé
   • Reasoning : Justification technique précise

3️⃣ CRITÈRES DE QUALITÉ :
   ✓ Confluence de 3+ indicateurs
   ✓ Structure de marché claire (tendance ou range)
   ✓ Ratio R/R minimum : 1.5:1
   ✓ Cohérence multi-timeframes
   ✓ Volume et momentum favorables

⚠️ RÈGLES STRICTES :
   • Réponds UNIQUEMENT avec le JSON valide
   • Pas de texte avant/après le JSON
   • Calcul R/R : (TP_moyen - Entry) / (Entry - SL)
   • Prix réalistes basés sur données fournies"""

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

        # 8. Parser la réponse structurée de Claude
        try:
            claude_content = claude_response.get("content", "")

            # Nettoyer et extraire le JSON
            content_clean = claude_content.strip()
            start_idx = content_clean.find("{")
            end_idx = content_clean.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                # Fallback vers l'ancien format si pas de JSON
                structured_response = {
                    "analysis_text": claude_content,
                    "trade_recommendations": []
                }
            else:
                json_content = content_clean[start_idx:end_idx]
                structured_response = json.loads(json_content)

            # Valider et construire les recommandations de trading
            trade_recommendations = []
            for rec_data in structured_response.get("trade_recommendations", []):
                try:
                    trade_rec = TradeRecommendation(**rec_data)
                    trade_recommendations.append(trade_rec)
                except Exception as e:
                    logger.warning(f"Recommandation trade invalide ignorée: {e}")
                    continue

        except json.JSONDecodeError as e:
            logger.warning(f"Erreur parsing JSON Claude: {e}")
            # Fallback vers l'ancien format
            structured_response = {
                "analysis_text": claude_response.get("content", ""),
                "trade_recommendations": []
            }
            trade_recommendations = []
        except Exception as e:
            logger.error(f"Erreur inattendue parsing Claude: {e}")
            structured_response = {
                "analysis_text": claude_response.get("content", ""),
                "trade_recommendations": []
            }
            trade_recommendations = []

        # 9. Construire réponse finale avec nouveau format structuré
        response = StructuredAnalysisResponse(
            request_id=request_id,
            timestamp=start_time,
            model_used=request.model,
            ticker=request.ticker,
            exchange=request.exchange,
            profile=request.profile,
            technical_data=technical_light,
            claude_analysis=structured_response.get("analysis_text", claude_response.get("content", "")),
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue analyze_single_asset: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'analyse"
        )