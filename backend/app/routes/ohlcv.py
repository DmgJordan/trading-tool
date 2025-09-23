from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models.user import User
from ..schemas.ohlcv import (
    CCXTTestRequest,
    CCXTTestResponse,
    ExchangeListResponse,
    ExchangeSymbolsRequest,
    ExchangeSymbolsResponse
)
from ..auth import get_current_user
from ..services.ccxt_service import CCXTService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ohlcv", tags=["ohlcv"])

# Initialisation du service CCXT
ccxt_service = CCXTService()

@router.post("/test", response_model=CCXTTestResponse)
async def test_ccxt_ohlcv(
    request: CCXTTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test de récupération de données OHLCV via CCXT

    - **exchange**: Nom de l'exchange (ex: binance, coinbase, kraken)
    - **symbol**: Symbole du trading pair (ex: BTC/USDT, ETH/USDT)
    - **timeframe**: Période (ex: 1m, 5m, 1h, 1d)
    - **limit**: Nombre de bougies à récupérer (max 500)
    """
    try:
        logger.info(f"Test CCXT OHLCV pour utilisateur {current_user.id}: {request.exchange} {request.symbol} {request.timeframe}")

        # Appeler le service CCXT
        result = await ccxt_service.get_ohlcv_data(
            exchange_name=request.exchange,
            symbol=request.symbol,
            timeframe=request.timeframe,
            limit=request.limit
        )

        # Retourner la réponse formatée
        return CCXTTestResponse(**result)

    except Exception as e:
        logger.error(f"Erreur test CCXT OHLCV: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

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