import ccxt
import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class CCXTAdapter:
    """Adapter pour récupérer les données OHLCV via CCXT (I/O pur - aucun calcul)"""

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

        # Configuration des profils multi-timeframes
        self.profile_configs = {
            "short": {
                "main": "15m",
                "higher": "1h",
                "lower": "5m"
            },
            "medium": {
                "main": "1h",
                "higher": "1d",
                "lower": "15m"
            },
            "long": {
                "main": "1d",
                "higher": "1w",
                "lower": "4h"
            }
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

    def get_profile_config(self, profile: str) -> Optional[Dict[str, str]]:
        """
        Retourne la configuration des timeframes pour un profil donné

        Args:
            profile: Profil de trading ("short", "medium", "long")

        Returns:
            Dict avec les timeframes (main, higher, lower) ou None si profil invalide
        """
        return self.profile_configs.get(profile)

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

    async def fetch_multi_timeframe_ohlcv(
        self,
        exchange_name: str,
        symbol: str,
        profile: str,
        limit: int = 600
    ) -> Dict[str, Any]:
        """
        Récupère les données OHLCV pour plusieurs timeframes selon le profil

        Args:
            exchange_name: Nom de l'exchange
            symbol: Symbole du trading pair
            profile: Profil de trading ("short", "medium", "long")
            limit: Nombre de bougies à récupérer par timeframe

        Returns:
            Dict contenant les données OHLCV brutes pour chaque timeframe
        """
        try:
            # Vérifier le profil
            config = self.get_profile_config(profile)
            if not config:
                return {
                    "status": "error",
                    "message": f"Profil '{profile}' non supporté. Profils disponibles: {list(self.profile_configs.keys())}"
                }

            main_tf = config["main"]
            higher_tf = config["higher"]
            lower_tf = config["lower"]

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

            # Vérifier la disponibilité des fonctionnalités
            if not exchange.has['fetchOHLCV']:
                return {
                    "status": "error",
                    "message": f"L'exchange {exchange_name} ne supporte pas la récupération OHLCV"
                }

            # Charger les marchés
            await self._load_markets_async(exchange)

            # Normaliser le symbole (convertir 'SOL' en 'SOL/USDT' par exemple)
            normalized_symbol = self._normalize_symbol(symbol, exchange)
            if not normalized_symbol:
                return {
                    "status": "error",
                    "message": f"Symbole '{symbol}' non trouvé sur {exchange_name}. Symboles disponibles limités aux paires avec USDT, USDC, BTC."
                }

            # Récupérer les données OHLCV pour les 3 timeframes
            main_data = await self._fetch_ohlcv_async(exchange, normalized_symbol, main_tf, limit)
            higher_data = await self._fetch_ohlcv_async(exchange, normalized_symbol, higher_tf, limit)
            lower_data = await self._fetch_ohlcv_async(exchange, normalized_symbol, lower_tf, limit)

            # Récupérer le prix actuel via ticker
            current_price_info = None
            try:
                if exchange.has['fetchTicker']:
                    ticker = await self._fetch_ticker_async(exchange, normalized_symbol)
                    current_price_info = {
                        "current_price": ticker['last'] if ticker['last'] else (main_data[-1][4] if main_data else 0),
                        "change_24h_percent": ticker.get('percentage'),
                        "volume_24h": ticker.get('baseVolume')
                    }
                else:
                    # Fallback au prix de fermeture de la dernière bougie
                    current_price_info = {
                        "current_price": main_data[-1][4] if main_data else 0,
                        "change_24h_percent": None,
                        "volume_24h": None
                    }
            except Exception as e:
                logger.warning(f"Impossible de récupérer le prix actuel: {e}")
                current_price_info = {
                    "current_price": main_data[-1][4] if main_data else 0,
                    "change_24h_percent": None,
                    "volume_24h": None
                }

            # Fermer la connexion
            if hasattr(exchange, 'close'):
                await exchange.close()

            # Retourner les données brutes (pas de calculs)
            return {
                "status": "success",
                "profile": profile,
                "symbol": normalized_symbol,
                "timeframes": {
                    "main": main_tf,
                    "higher": higher_tf,
                    "lower": lower_tf
                },
                "current_price": current_price_info,
                "ohlcv_data": {
                    "main": main_data,
                    "higher": higher_data,
                    "lower": lower_data
                }
            }

        except Exception as e:
            logger.error(f"Erreur récupération OHLCV multi-timeframes pour {symbol} sur {exchange_name}: {e}")
            return {
                "status": "error",
                "message": f"Erreur récupération OHLCV: {str(e)}"
            }

    def _normalize_symbol(self, symbol: str, exchange) -> Optional[str]:
        """
        Normalise un symbole en trouvant la paire de trading correspondante
        Exemple: 'SOL' -> 'SOL/USDT'

        Args:
            symbol: Symbole simple (ex: 'SOL', 'BTC', 'ETH')
            exchange: Instance de l'exchange CCXT

        Returns:
            Symbole normalisé ou None si non trouvé
        """
        # Si le symbole est déjà une paire (contient '/'), le vérifier directement
        if '/' in symbol:
            return symbol if symbol in exchange.markets else None

        # Sinon, essayer de créer une paire avec les bases communes
        bases_courantes = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'USD']

        symbol_upper = symbol.upper()

        for base in bases_courantes:
            pair = f"{symbol_upper}/{base}"
            if pair in exchange.markets:
                return pair

        # Aucune paire trouvée
        return None
