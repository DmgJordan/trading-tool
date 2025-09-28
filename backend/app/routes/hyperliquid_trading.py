from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models.user import User
from ..auth import get_current_user, decrypt_api_key
from ..schemas.hyperliquid_trading import (
    ExecuteTradeRequest,
    TradeExecutionResult
)
from ..services.hyperliquid_trading_service import HyperliquidTradingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hyperliquid", tags=["hyperliquid-trading"])

# Initialisation du service
trading_service = HyperliquidTradingService()

@router.post("/execute-trade", response_model=TradeExecutionResult)
async def execute_trade(
    trade_request: ExecuteTradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exécute un trade complet sur Hyperliquid avec gestion des risques

    Processus:
    1. Valide la clé privée Hyperliquid de l'utilisateur
    2. Récupère les informations du portefeuille
    3. Calcule la taille de position selon le pourcentage demandé
    4. Place l'ordre d'entrée principal
    5. Place les ordres stop-loss et take-profit
    6. Retourne le statut d'exécution complet
    """
    try:
        # 1. Vérifier la clé privée Hyperliquid
        if not current_user.hyperliquid_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé privée Hyperliquid configurée. Configurez-la dans vos paramètres."
            )

        # 2. Déchiffrer la clé privée
        try:
            private_key = decrypt_api_key(current_user.hyperliquid_api_key)
        except Exception as e:
            logger.error(f"Erreur déchiffrement clé Hyperliquid: {e}")
            raise HTTPException(
                status_code=400,
                detail="Erreur lors du déchiffrement de la clé privée Hyperliquid"
            )

        # 3. Validation de sécurité du trade
        if trade_request.portfolio_percentage > 5.0:
            logger.warning(f"Utilisateur {current_user.id} tente un trade > 5% du portefeuille")
            raise HTTPException(
                status_code=400,
                detail="Pourcentage du portefeuille limité à 5% maximum pour la sécurité"
            )

        # 4. Vérifier la cohérence des prix
        if trade_request.direction == "long":
            if trade_request.stop_loss >= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un long, le stop-loss doit être inférieur au prix d'entrée"
                )
            if trade_request.take_profit_1 <= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un long, les take-profits doivent être supérieurs au prix d'entrée"
                )
        else:  # short
            if trade_request.stop_loss <= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un short, le stop-loss doit être supérieur au prix d'entrée"
                )
            if trade_request.take_profit_1 >= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un short, les take-profits doivent être inférieurs au prix d'entrée"
                )

        # 5. Exécuter le trade
        logger.info(
            f"Exécution trade pour utilisateur {current_user.id}: "
            f"{trade_request.symbol} {trade_request.direction} "
            f"{trade_request.portfolio_percentage}% @ {trade_request.entry_price}"
        )

        result = await trading_service.execute_trade(private_key, trade_request)

        # 6. Logger le résultat
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue execute_trade pour utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'exécution du trade"
        )

# Note: Pour récupérer les informations du portefeuille,
# utiliser l'endpoint existant /connectors/user-info avec service_type="hyperliquid"