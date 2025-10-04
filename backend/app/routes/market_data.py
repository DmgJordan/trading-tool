from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from ..core import get_db, get_current_user
from ..domains.auth.models import User
from ..models.market_data import MarketData
from ..schemas.market_data import (
    MarketDataResponse,
    MarketDataRequest,
    HistoricalDataRequest,
    SupportedSymbolsResponse,
    MarketDataBatch,
    MarketDataBatchResponse
)
from ..services.market_data.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market-data", tags=["market-data"])

# Initialisation du service
market_data_service = MarketDataService()

@router.get("/{symbol}", response_model=MarketDataResponse)
async def get_market_data(
    symbol: str,
    source: Optional[str] = Query(default="auto", description="Source (coingecko, hyperliquid, auto)"),
    use_testnet: bool = Query(default=False, description="Utiliser testnet pour Hyperliquid"),
    refresh: bool = Query(default=True, description="Forcer rafraîchissement depuis l'API"),
    store: bool = Query(default=True, description="Stocker en base de données"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les données de marché pour un symbole donné

    - **symbol**: Symbole de la crypto (ex: BTC, ETH)
    - **source**: Source des données (auto, coingecko, hyperliquid)
    - **use_testnet**: Utiliser le testnet Hyperliquid
    - **refresh**: Forcer la récupération depuis l'API externe
    - **store**: Stocker les données en base
    """
    try:
        symbol = symbol.upper()

        if refresh:
            # Récupérer et optionnellement stocker les données
            if store:
                result = await market_data_service.refresh_and_store_price(
                    db=db,
                    symbol=symbol,
                    user=current_user,
                    source=source,
                    use_testnet=use_testnet
                )
            else:
                result = await market_data_service.get_symbol_price(
                    symbol=symbol,
                    source=source,
                    user=current_user,
                    use_testnet=use_testnet
                )

            if result["status"] == "success":
                # Convertir les données en format MarketData pour la réponse
                data = result["data"]
                market_data = MarketData(
                    id=result.get("stored_id", 0),
                    symbol=data["symbol"],
                    name=data.get("name"),
                    price_usd=data["price_usd"],
                    price_change_24h=data.get("price_change_24h"),
                    price_change_24h_abs=data.get("price_change_24h_abs"),
                    volume_24h_usd=data.get("volume_24h_usd"),
                    market_cap_usd=data.get("market_cap_usd"),
                    source=data["source"],
                    source_id=data.get("source_id"),
                    data_timestamp=data["data_timestamp"],
                    created_at=datetime.utcnow(),
                    updated_at=None
                )

                return MarketDataResponse(
                    status="success",
                    message=f"Données récupérées pour {symbol}",
                    symbol=symbol,
                    data=market_data
                )
            else:
                return MarketDataResponse(
                    status="error",
                    message=result["message"],
                    symbol=symbol
                )
        else:
            # Récupérer depuis la base de données
            latest_data = await market_data_service.get_latest_price(
                db=db,
                symbol=symbol,
                source=source if source != "auto" else None
            )

            if latest_data:
                return MarketDataResponse(
                    status="success",
                    message=f"Dernières données pour {symbol}",
                    symbol=symbol,
                    data=latest_data
                )
            else:
                return MarketDataResponse(
                    status="error",
                    message=f"Aucune donnée trouvée pour {symbol}",
                    symbol=symbol
                )

    except Exception as e:
        logger.error(f"Erreur récupération données de marché pour {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/{symbol}/history", response_model=MarketDataResponse)
async def get_historical_data(
    symbol: str,
    hours_back: int = Query(default=24, le=168, description="Heures d'historique (max 168h = 7 jours)"),
    source: Optional[str] = Query(default=None, description="Filtrer par source"),
    limit: int = Query(default=100, le=1000, description="Nombre max d'entrées"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des données de marché pour un symbole

    - **symbol**: Symbole de la crypto
    - **hours_back**: Nombre d'heures d'historique (max 168h)
    - **source**: Filtrer par source spécifique
    - **limit**: Nombre maximum d'entrées
    """
    try:
        symbol = symbol.upper()

        historical_data = await market_data_service.get_historical_data(
            db=db,
            symbol=symbol,
            hours_back=hours_back,
            source=source
        )

        # Limiter les résultats
        if len(historical_data) > limit:
            historical_data = historical_data[:limit]

        return MarketDataResponse(
            status="success",
            message=f"Historique récupéré pour {symbol} ({len(historical_data)} entrées)",
            symbol=symbol,
            historical_data=historical_data
        )

    except Exception as e:
        logger.error(f"Erreur récupération historique pour {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/batch", response_model=MarketDataBatchResponse)
async def get_batch_market_data(
    batch_request: MarketDataBatch,
    use_testnet: bool = Query(default=False),
    refresh: bool = Query(default=True),
    store: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les données de marché pour plusieurs symboles en lot

    - **symbols**: Liste des symboles (max 50)
    - **source**: Source des données (auto, coingecko, hyperliquid)
    - **refresh**: Forcer la récupération depuis l'API externe
    - **store**: Stocker les données en base
    """
    try:
        results = []
        errors = []
        successful_count = 0
        failed_count = 0

        for symbol in batch_request.symbols:
            try:
                symbol = symbol.upper()

                if refresh:
                    if store:
                        result = await market_data_service.refresh_and_store_price(
                            db=db,
                            symbol=symbol,
                            user=current_user,
                            source=batch_request.source,
                            use_testnet=use_testnet
                        )
                    else:
                        result = await market_data_service.get_symbol_price(
                            symbol=symbol,
                            source=batch_request.source,
                            user=current_user,
                            use_testnet=use_testnet
                        )

                    if result["status"] == "success":
                        data = result["data"]
                        market_data = MarketData(
                            id=result.get("stored_id", 0),
                            symbol=data["symbol"],
                            name=data.get("name"),
                            price_usd=data["price_usd"],
                            price_change_24h=data.get("price_change_24h"),
                            price_change_24h_abs=data.get("price_change_24h_abs"),
                            volume_24h_usd=data.get("volume_24h_usd"),
                            market_cap_usd=data.get("market_cap_usd"),
                            source=data["source"],
                            source_id=data.get("source_id"),
                            data_timestamp=data["data_timestamp"],
                            created_at=datetime.utcnow(),
                            updated_at=None
                        )
                        results.append(market_data)
                        successful_count += 1
                    else:
                        errors.append(f"{symbol}: {result['message']}")
                        failed_count += 1
                else:
                    # Récupérer depuis la base
                    latest_data = await market_data_service.get_latest_price(
                        db=db,
                        symbol=symbol,
                        source=batch_request.source if batch_request.source != "auto" else None
                    )

                    if latest_data:
                        results.append(latest_data)
                        successful_count += 1
                    else:
                        errors.append(f"{symbol}: Aucune donnée trouvée")
                        failed_count += 1

            except Exception as e:
                errors.append(f"{symbol}: {str(e)}")
                failed_count += 1

        # Déterminer le statut global
        if successful_count == len(batch_request.symbols):
            status = "success"
            message = f"Toutes les données récupérées ({successful_count} symboles)"
        elif successful_count > 0:
            status = "partial"
            message = f"Données partielles: {successful_count} réussies, {failed_count} échouées"
        else:
            status = "error"
            message = f"Échec pour tous les symboles ({failed_count} erreurs)"

        return MarketDataBatchResponse(
            status=status,
            message=message,
            successful_count=successful_count,
            failed_count=failed_count,
            data=results,
            errors=errors
        )

    except Exception as e:
        logger.error(f"Erreur traitement batch: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/", response_model=SupportedSymbolsResponse)
async def get_supported_symbols(
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste des symboles supportés par les différentes sources
    """
    try:
        result = await market_data_service.get_supported_symbols()

        return SupportedSymbolsResponse(
            status=result["status"],
            message=result["message"],
            coingecko_symbols=result.get("coingecko_symbols"),
            hyperliquid_symbols=result.get("hyperliquid_symbols"),
            total_symbols=result.get("total_symbols", 0)
        )

    except Exception as e:
        logger.error(f"Erreur récupération symboles supportés: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.delete("/{symbol}")
async def delete_market_data(
    symbol: str,
    older_than_hours: int = Query(default=24, description="Supprimer données plus anciennes que X heures"),
    source: Optional[str] = Query(default=None, description="Filtrer par source"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime les données de marché anciennes pour un symbole

    - **symbol**: Symbole de la crypto
    - **older_than_hours**: Supprimer données plus anciennes que X heures
    - **source**: Filtrer par source spécifique
    """
    try:
        symbol = symbol.upper()
        cutoff_date = datetime.utcnow() - timedelta(hours=older_than_hours)

        query = db.query(MarketData).filter(
            MarketData.symbol == symbol,
            MarketData.data_timestamp < cutoff_date
        )

        if source:
            query = query.filter(MarketData.source == source)

        deleted_count = query.count()
        query.delete()
        db.commit()

        return {
            "status": "success",
            "message": f"Supprimé {deleted_count} entrées pour {symbol}",
            "deleted_count": deleted_count
        }

    except Exception as e:
        logger.error(f"Erreur suppression données pour {symbol}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")