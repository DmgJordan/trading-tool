"""Router pour les endpoints de trading"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ...core import get_db, get_current_user
from ..auth.models import User
from .schemas import (
    ExecuteTradeRequest,
    TradeExecutionResult,
    CancelOrderRequest,
    CancelOrderResponse,
)
from .service import TradingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trading", tags=["trading"])

# Initialisation du service
trading_service = TradingService()


@router.post("/orders", response_model=TradeExecutionResult)
async def execute_trade(
    trade_request: ExecuteTradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exécute un trade complet sur Hyperliquid avec gestion des risques

    Processus:
    1. Valide la clé privée Hyperliquid de l'utilisateur
    2. Valide la cohérence du trade (prix SL/TP, pourcentage, etc.)
    3. Récupère les informations du portefeuille
    4. Calcule la taille de position selon le pourcentage demandé
    5. Place l'ordre d'entrée principal
    6. Place les ordres stop-loss et take-profit
    7. Retourne le statut d'exécution complet

    Notes:
    - Validation Pydantic automatique via ExecuteTradeRequest
    - Toute la logique métier est dans TradingService
    - Ce router ne fait que de l'authentification et de l'appel au service
    """
    try:
        result = await trading_service.execute_trade(current_user, trade_request, db)

        # Logger le résultat
        if result.status == "success":
            logger.info(
                f"Trade exécuté avec succès pour utilisateur {current_user.id}: "
                f"Ordre principal {result.main_order_id}, "
                f"SL: {result.stop_loss_order_id}, "
                f"TPs: {len(result.take_profit_orders)}"
            )
        elif result.status == "partial":
            logger.warning(
                f"Trade partiellement exécuté pour utilisateur {current_user.id}: "
                f"{len(result.errors)} erreurs"
            )
        else:
            logger.error(
                f"Échec trade pour utilisateur {current_user.id}: {result.message}"
            )

        return result

    except Exception as e:
        logger.error(f"Erreur inattendue execute_trade pour utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'exécution du trade"
        )


@router.get("/portfolio")
async def get_portfolio_info(
    use_testnet: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les informations du portefeuille Hyperliquid de l'utilisateur

    Retourne:
    - Valeur du compte
    - Balance disponible
    - Positions ouvertes
    - Ordres ouverts
    - Historique des trades récents
    - Portfolio performance (séries temporelles)
    """
    try:
        result = await trading_service.get_portfolio_info(current_user, use_testnet)

        if result["status"] != "success":
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Erreur récupération portfolio")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue get_portfolio_info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération du portfolio"
        )


@router.get("/positions")
async def get_positions(
    use_testnet: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les positions ouvertes de l'utilisateur

    Retourne la liste des positions avec:
    - Symbole
    - Taille (positif = long, négatif = short)
    - Prix d'entrée moyen
    - PnL non réalisé
    - Levier
    """
    try:
        result = await trading_service.get_user_positions(current_user, use_testnet)

        if result["status"] != "success":
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Erreur récupération positions")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue get_positions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération des positions"
        )


@router.get("/orders")
async def get_open_orders(
    use_testnet: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les ordres ouverts de l'utilisateur

    Retourne la liste des ordres avec:
    - ID de l'ordre
    - Symbole
    - Side (buy/sell)
    - Taille
    - Prix limite
    - Type d'ordre
    """
    try:
        result = await trading_service.get_user_orders(current_user, use_testnet)

        if result["status"] != "success":
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Erreur récupération ordres")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue get_open_orders: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la récupération des ordres"
        )


@router.delete("/orders/{order_id}", response_model=CancelOrderResponse)
async def cancel_order(
    order_id: int,
    cancel_request: CancelOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Annule un ordre ouvert

    Args:
        order_id: ID de l'ordre à annuler (dans l'URL)
        cancel_request: Informations de l'ordre (symbole, testnet)
    """
    try:
        result = await trading_service.cancel_order(
            current_user,
            cancel_request.symbol,
            order_id,
            cancel_request.use_testnet
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Erreur annulation ordre")
            )

        return CancelOrderResponse(
            status="success",
            message=result.get("message", f"Ordre {order_id} annulé avec succès"),
            order_id=order_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue cancel_order: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'annulation de l'ordre"
        )


@router.post("/test")
async def test_hyperliquid_connection(
    use_testnet: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test la connexion Hyperliquid de l'utilisateur

    Vérifie:
    - Format de la clé privée
    - Connexion à l'API Hyperliquid
    - Accès au portefeuille

    Utilise les clés stockées en base de données (chiffrées)
    """
    try:
        result = await trading_service.test_connection(current_user, use_testnet)

        if result["status"] != "success":
            # Retourner l'erreur sans lever d'exception (pour le frontend)
            return result

        return result

    except Exception as e:
        logger.error(f"Erreur inattendue test_hyperliquid_connection: {e}")
        return {
            "status": "error",
            "message": f"Erreur interne: {str(e)}"
        }
