# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from ..core import get_db, get_current_user, decrypt_api_key
from ..models.user import User
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
                detail="Aucune cle privee Hyperliquid configuree. Configurez-la dans vos parametres."
            )

        # 2. Déchiffrer la clé privée
        try:
            private_key = decrypt_api_key(current_user.hyperliquid_api_key)

            if not private_key:
                raise HTTPException(
                    status_code=400,
                    detail="Cle privee Hyperliquid vide. Veuillez reconfigurer votre cle privee dans les parametres."
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur dechiffrement cle Hyperliquid: {e}")
            raise HTTPException(
                status_code=400,
                detail="Erreur lors du dechiffrement de la cle privee Hyperliquid"
            )

        # 3. Validation de sécurité du trade
        if trade_request.portfolio_percentage > 50.0:
            logger.warning(f"Utilisateur {current_user.id} tente un trade > 50% du portefeuille")
            raise HTTPException(
                status_code=400,
                detail="Pourcentage du portefeuille limite a 50% maximum pour la securite"
            )

        # 4. Vérifier la cohérence des prix
        if trade_request.direction == "long":
            if trade_request.stop_loss >= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un long, le stop-loss doit etre inferieur au prix d'entree"
                )
            if trade_request.take_profit_1 <= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un long, les take-profits doivent etre superieurs au prix d'entree"
                )
        else:  # short
            if trade_request.stop_loss <= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un short, le stop-loss doit etre superieur au prix d'entree"
                )
            if trade_request.take_profit_1 >= trade_request.entry_price:
                raise HTTPException(
                    status_code=400,
                    detail="Pour un short, les take-profits doivent etre inferieurs au prix d'entree"
                )

        # 5. Injecter l'adresse publique pour trading delegue si configuree
        if current_user.hyperliquid_public_address and not trade_request.account_address:
            trade_request.account_address = current_user.hyperliquid_public_address
            logger.info(f"Mode delegue active: API trade pour {current_user.hyperliquid_public_address[:10]}...")

        # 6. Executer le trade
        logger.info(
            f"Execution trade pour utilisateur {current_user.id}: "
            f"{trade_request.symbol} {trade_request.direction} "
            f"{trade_request.portfolio_percentage}% @ {trade_request.entry_price}"
        )

        result = await trading_service.execute_trade(private_key, trade_request)

        # 7. Logger le resultat
        if result.status == "success":
            logger.info(
                f"Trade execute avec succes pour utilisateur {current_user.id}: "
                f"Ordre principal {result.main_order_id}, "
                f"SL: {result.stop_loss_order_id}, "
                f"TPs: {len(result.take_profit_orders)}"
            )
        elif result.status == "partial":
            logger.warning(
                f"Trade partiellement execute pour utilisateur {current_user.id}: "
                f"{len(result.errors)} erreurs"
            )
        else:
            logger.error(
                f"Echec trade pour utilisateur {current_user.id}: {result.message}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue execute_trade pour utilisateur {current_user.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de l'execution du trade"
        )

@router.get("/portfolio-info")
async def get_portfolio_info(
    use_testnet: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les informations du portefeuille Hyperliquid de l'utilisateur
    Endpoint de production pour le trading actif
    """
    try:
        # Vérifier la clé privée Hyperliquid
        if not current_user.hyperliquid_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune cle privee Hyperliquid configuree"
            )

        if not current_user.hyperliquid_public_address:
            raise HTTPException(
                status_code=400,
                detail="Aucune adresse publique Hyperliquid configuree"
            )

        # Déchiffrer la clé privée
        try:
            private_key = decrypt_api_key(current_user.hyperliquid_api_key)
            if not private_key:
                raise HTTPException(
                    status_code=400,
                    detail="Cle privee Hyperliquid vide"
                )
        except Exception as e:
            logger.error(f"Erreur dechiffrement cle: {e}")
            raise HTTPException(
                status_code=400,
                detail="Erreur dechiffrement cle privee"
            )

        # Récupérer les infos via le service
        from ..services.validators.dex_validator import DexValidator
        dex_validator = DexValidator()

        result = await dex_validator.get_hyperliquid_user_info(
            private_key,
            current_user.hyperliquid_public_address,
            use_testnet
        )

        if result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Erreur recuperation portfolio")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue get_portfolio_info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la recuperation du portfolio"
        )