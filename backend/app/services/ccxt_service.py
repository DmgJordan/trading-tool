import ccxt
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CCXTService:
    """Service pour récupérer les données OHLCV via CCXT"""

    def __init__(self):
        self.available_exchanges = [
            'binance',
            'coinbase',
            'kraken',
            'bitfinex',
            'huobi',
            'okx',
            'bybit',
            'kucoin'
        ]

        self.timeframes = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w'
        }

    async def get_current_price(
        self,
        exchange_name: str,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Récupère le prix actuel d'un symbole via fetch_ticker

        Args:
            exchange_name: Nom de l'exchange (ex: 'binance')
            symbol: Symbole du trading pair (ex: 'BTC/USDT')

        Returns:
            Dict contenant le prix actuel et les informations du ticker
        """
        try:
            # Vérifier que l'exchange est supporté
            if exchange_name.lower() not in self.available_exchanges:
                return {
                    "status": "error",
                    "message": f"Exchange '{exchange_name}' non supporté"
                }

            # Créer l'instance de l'exchange
            exchange_class = getattr(ccxt, exchange_name.lower())
            exchange = exchange_class({
                'sandbox': False,
                'enableRateLimit': True,
            })

            # Vérifier que l'exchange supporte fetchTicker
            if not exchange.has['fetchTicker']:
                return {
                    "status": "error",
                    "message": f"L'exchange {exchange_name} ne supporte pas la récupération de ticker"
                }

            # Charger les marchés de l'exchange
            await self._load_markets_async(exchange)

            # Vérifier que le symbole existe
            if symbol not in exchange.markets:
                return {
                    "status": "error",
                    "message": f"Symbole '{symbol}' non trouvé sur {exchange_name}"
                }

            # Récupérer le ticker
            ticker = await self._fetch_ticker_async(exchange, symbol)

            # Fermer la connexion de l'exchange si disponible
            if hasattr(exchange, 'close'):
                await exchange.close()

            return {
                "status": "success",
                "exchange": exchange_name,
                "symbol": symbol,
                "current_price": ticker['last'],
                "bid": ticker.get('bid'),
                "ask": ticker.get('ask'),
                "high_24h": ticker.get('high'),
                "low_24h": ticker.get('low'),
                "volume_24h": ticker.get('baseVolume'),
                "change_24h": ticker.get('change'),
                "change_24h_percent": ticker.get('percentage'),
                "timestamp": ticker.get('timestamp'),
                "datetime": ticker.get('datetime')
            }

        except Exception as e:
            logger.error(f"Erreur récupération prix actuel pour {symbol} sur {exchange_name}: {e}")
            return {
                "status": "error",
                "message": f"Erreur récupération prix: {str(e)}"
            }

    async def get_ohlcv_data(
        self,
        exchange_name: str,
        symbol: str,
        timeframe: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Récupère les données OHLCV pour un symbole donné

        Args:
            exchange_name: Nom de l'exchange (ex: 'binance')
            symbol: Symbole du trading pair (ex: 'BTC/USDT')
            timeframe: Période (ex: '1h', '1d')
            limit: Nombre de bougies à récupérer

        Returns:
            Dict contenant le statut et les données OHLCV
        """
        try:
            # Vérifier que l'exchange est supporté
            if exchange_name.lower() not in self.available_exchanges:
                return {
                    "status": "error",
                    "message": f"Exchange '{exchange_name}' non supporté. Exchanges disponibles: {', '.join(self.available_exchanges)}"
                }

            # Vérifier que la timeframe est supportée
            if timeframe not in self.timeframes:
                return {
                    "status": "error",
                    "message": f"Timeframe '{timeframe}' non supportée. Timeframes disponibles: {', '.join(self.timeframes.keys())}"
                }

            # Créer l'instance de l'exchange
            exchange_class = getattr(ccxt, exchange_name.lower())
            exchange = exchange_class({
                'sandbox': False,
                'enableRateLimit': True,
            })

            # Vérifier que l'exchange supporte fetchOHLCV
            if not exchange.has['fetchOHLCV']:
                return {
                    "status": "error",
                    "message": f"L'exchange {exchange_name} ne supporte pas la récupération de données OHLCV"
                }

            # Charger les marchés de l'exchange
            await self._load_markets_async(exchange)

            # Vérifier que le symbole existe
            if symbol not in exchange.markets:
                return {
                    "status": "error",
                    "message": f"Symbole '{symbol}' non trouvé sur {exchange_name}. Vérifiez le format (ex: 'BTC/USDT')"
                }

            # Récupérer les données OHLCV
            ohlcv_data = await self._fetch_ohlcv_async(
                exchange, symbol, timeframe, limit
            )

            # Récupérer le prix actuel via ticker
            current_price_data = None
            try:
                if exchange.has['fetchTicker']:
                    ticker = await self._fetch_ticker_async(exchange, symbol)
                    current_price_data = {
                        "current_price": ticker['last'],
                        "bid": ticker.get('bid'),
                        "ask": ticker.get('ask'),
                        "change_24h_percent": ticker.get('percentage'),
                        "volume_24h": ticker.get('baseVolume'),
                        "timestamp": ticker.get('timestamp'),
                        "datetime": ticker.get('datetime')
                    }
            except Exception as e:
                logger.warning(f"Impossible de récupérer le prix actuel: {e}")

            # Fermer la connexion de l'exchange si disponible
            if hasattr(exchange, 'close'):
                await exchange.close()

            # Formater les données
            formatted_data = []
            for candle in ohlcv_data:
                formatted_data.append({
                    "timestamp": candle[0],
                    "datetime": datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5]
                })

            result = {
                "status": "success",
                "message": f"Données OHLCV récupérées avec succès",
                "exchange": exchange_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "count": len(formatted_data),
                "data": formatted_data
            }

            # Ajouter le prix actuel si disponible
            if current_price_data:
                result["current_price_info"] = current_price_data

            return result

        except ccxt.NetworkError as e:
            logger.error(f"Erreur réseau CCXT pour {exchange_name}: {e}")
            return {
                "status": "error",
                "message": f"Erreur de connexion à {exchange_name}: {str(e)}"
            }
        except ccxt.ExchangeError as e:
            logger.error(f"Erreur exchange CCXT pour {exchange_name}: {e}")
            return {
                "status": "error",
                "message": f"Erreur de l'exchange {exchange_name}: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erreur inattendue CCXT: {e}")
            return {
                "status": "error",
                "message": f"Erreur inattendue: {str(e)}"
            }

    async def _load_markets_async(self, exchange) -> None:
        """Charge les marchés de l'exchange de manière asynchrone"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, exchange.load_markets)

    async def _fetch_ohlcv_async(self, exchange, symbol: str, timeframe: str, limit: int) -> List:
        """Récupère les données OHLCV de manière asynchrone"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            exchange.fetch_ohlcv,
            symbol,
            timeframe,
            None,
            limit
        )

    async def _fetch_ticker_async(self, exchange, symbol: str) -> Dict:
        """Récupère le ticker de manière asynchrone"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            exchange.fetch_ticker,
            symbol
        )

    def get_available_exchanges(self) -> List[str]:
        """Retourne la liste des exchanges disponibles"""
        return self.available_exchanges.copy()

    def get_available_timeframes(self) -> List[str]:
        """Retourne la liste des timeframes disponibles"""
        return list(self.timeframes.keys())

    async def get_exchange_symbols(self, exchange_name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Récupère les symboles populaires d'un exchange

        Args:
            exchange_name: Nom de l'exchange
            limit: Nombre de symboles à retourner

        Returns:
            Dict contenant les symboles disponibles
        """
        try:
            if exchange_name.lower() not in self.available_exchanges:
                return {
                    "status": "error",
                    "message": f"Exchange '{exchange_name}' non supporté"
                }

            # Créer l'instance de l'exchange
            exchange_class = getattr(ccxt, exchange_name.lower())
            exchange = exchange_class({
                'sandbox': False,
                'enableRateLimit': True,
            })

            # Charger les marchés
            await self._load_markets_async(exchange)

            # Obtenir les symboles, en priorité ceux avec USDT
            all_symbols = list(exchange.markets.keys())
            usdt_symbols = [s for s in all_symbols if '/USDT' in s]
            usdc_symbols = [s for s in all_symbols if '/USDC' in s]
            busd_symbols = [s for s in all_symbols if '/BUSD' in s]

            # Prendre les plus populaires
            popular_symbols = usdt_symbols[:limit//2] + usdc_symbols[:limit//4] + busd_symbols[:limit//4]
            popular_symbols = popular_symbols[:limit]

            if hasattr(exchange, 'close'):
                await exchange.close()

            return {
                "status": "success",
                "exchange": exchange_name,
                "symbols": popular_symbols,
                "total_available": len(all_symbols)
            }

        except Exception as e:
            logger.error(f"Erreur récupération symboles pour {exchange_name}: {e}")
            return {
                "status": "error",
                "message": f"Erreur récupération symboles: {str(e)}"
            }