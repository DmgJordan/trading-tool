from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models.user import User
from ..schemas.ohlcv import (
    ExchangeListResponse,
    ExchangeSymbolsRequest,
    ExchangeSymbolsResponse,
    MultiTimeframeRequest,
    MultiTimeframeResponse
)
from ..auth import get_current_user
from ..services.ccxt_service import CCXTService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ohlcv", tags=["ohlcv"])

# Initialisation du service CCXT
ccxt_service = CCXTService()

# Ancien endpoint /test supprimé - remplacé par /multi-timeframe-analysis

@router.get("/exchanges", response_model=ExchangeListResponse)
async def get_available_exchanges(
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des exchanges et timeframes disponibles
    """
    try:
        exchanges = ccxt_service.get_available_exchanges()
        timeframes = ccxt_service.get_available_timeframes()

        return ExchangeListResponse(
            status="success",
            exchanges=exchanges,
            timeframes=timeframes
        )

    except Exception as e:
        logger.error(f"Erreur récupération exchanges: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/symbols", response_model=ExchangeSymbolsResponse)
async def get_exchange_symbols(
    request: ExchangeSymbolsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les symboles populaires d'un exchange spécifique

    - **exchange**: Nom de l'exchange
    - **limit**: Nombre de symboles à retourner (max 100)
    """
    try:
        logger.info(f"Récupération symboles pour {request.exchange}")

        result = await ccxt_service.get_exchange_symbols(
            exchange_name=request.exchange,
            limit=request.limit
        )

        return ExchangeSymbolsResponse(**result)

    except Exception as e:
        logger.error(f"Erreur récupération symboles: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/multi-timeframe-analysis", response_model=MultiTimeframeResponse)
async def get_multi_timeframe_analysis(
    request: MultiTimeframeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyse multi-timeframes pour un symbole donné selon le profil de trading

    - **exchange**: Nom de l'exchange (ex: binance, coinbase, kraken)
    - **symbol**: Symbole du trading pair (ex: BTC/USDT, ETH/USDT)
    - **profile**: Profil de trading (short, medium, long)

    Le profil détermine les timeframes utilisés :
    - **short**: Principal 15m, Supérieur 1h, Inférieur 5m
    - **medium**: Principal 1h, Supérieur 1d, Inférieur 15m
    - **long**: Principal 1d, Supérieur 1w, Inférieur 4h

    Récupère 600 bougies par timeframe pour calculs précis des indicateurs
    """
    try:
        logger.info(f"Analyse multi-timeframes pour utilisateur {current_user.id}: {request.exchange} {request.symbol} profil {request.profile}")

        # Appeler le service CCXT pour l'analyse multi-timeframes
        result = await ccxt_service.get_multi_timeframe_analysis(
            exchange_name=request.exchange,
            symbol=request.symbol,
            profile=request.profile
        )

        # Vérifier le statut de la réponse
        if "status" in result and result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        # Retourner la réponse formatée
        return MultiTimeframeResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse multi-timeframes: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")