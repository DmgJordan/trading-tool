import ccxt
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .technical_indicators.technical_indicators_service import TechnicalIndicatorsService

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

    # Anciennes méthodes get_current_price et get_ohlcv_data supprimées - remplacées par get_multi_timeframe_analysis

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

    async def get_multi_timeframe_analysis(
        self,
        exchange_name: str,
        symbol: str,
        profile: str
    ) -> Dict[str, Any]:
        """
        Récupère et analyse les données sur plusieurs timeframes selon le profil

        Args:
            exchange_name: Nom de l'exchange
            symbol: Symbole du trading pair
            profile: Profil de trading ("short", "medium", "long")

        Returns:
            Dict contenant l'analyse multi-timeframes
        """
        try:
            # Vérifier le profil
            if profile not in self.profile_configs:
                return {
                    "status": "error",
                    "message": f"Profil '{profile}' non supporté. Profils disponibles: {list(self.profile_configs.keys())}"
                }

            # Récupérer la configuration du profil
            config = self.profile_configs[profile]
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

            # Récupérer 600 bougies pour chaque timeframe
            main_data = await self._fetch_ohlcv_async(exchange, normalized_symbol, main_tf, 600)
            higher_data = await self._fetch_ohlcv_async(exchange, normalized_symbol, higher_tf, 600)
            lower_data = await self._fetch_ohlcv_async(exchange, normalized_symbol, lower_tf, 600)

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

            # Calculer les indicateurs pour chaque timeframe
            main_indicators = self._calculate_indicators(main_data)
            higher_indicators = self._calculate_indicators(higher_data)
            lower_indicators = self._calculate_indicators(lower_data)

            # Formater la réponse selon le format souhaité
            response = {
                "profile": profile,
                "symbol": normalized_symbol,
                "tf": main_tf,
                "current_price": current_price_info,
                "features": {
                    "ma": {
                        "ma20": main_indicators["ma20"],
                        "ma50": main_indicators["ma50"],
                        "ma200": main_indicators["ma200"]
                    },
                    "rsi14": main_indicators["rsi14"],
                    "atr14": main_indicators["atr14"],
                    "volume": {
                        "current": int(main_data[-1][5]) if main_data else 0,
                        "avg20": int(main_indicators["volume_avg20"]),
                        "spike_ratio": main_indicators["volume_spike_ratio"]
                    },
                    "last_20_candles": [[
                        candle[0],  # timestamp
                        candle[1],  # open
                        candle[2],  # high
                        candle[3],  # low
                        candle[4],  # close
                        candle[5]   # volume
                    ] for candle in main_data[-20:]] if main_data else []
                },
                "higher_tf": {
                    "tf": higher_tf,
                    "ma": {
                        "ma20": higher_indicators["ma20"],
                        "ma50": higher_indicators["ma50"],
                        "ma200": higher_indicators["ma200"]
                    },
                    "rsi14": higher_indicators["rsi14"],
                    "atr14": higher_indicators["atr14"],
                    "structure": higher_indicators["market_structure"],
                    "nearest_resistance": higher_indicators["nearest_resistance"]
                },
                "lower_tf": {
                    "tf": lower_tf,
                    "rsi14": lower_indicators["rsi14"],
                    "volume": {
                        "current": int(lower_data[-1][5]) if lower_data else 0,
                        "avg20": int(lower_indicators["volume_avg20"]),
                        "spike_ratio": lower_indicators["volume_spike_ratio"]
                    },
                    "last_20_candles": [[
                        candle[0],  # timestamp
                        candle[1],  # open
                        candle[2],  # high
                        candle[3],  # low
                        candle[4],  # close
                        candle[5]   # volume
                    ] for candle in lower_data[-20:]] if lower_data else []
                }
            }

            return response

        except Exception as e:
            logger.error(f"Erreur analyse multi-timeframes pour {symbol} sur {exchange_name}: {e}")
            return {
                "status": "error",
                "message": f"Erreur analyse multi-timeframes: {str(e)}"
            }

    def _calculate_indicators(self, ohlcv_data: List[List[float]]) -> Dict[str, float]:
        """
        Calcule les indicateurs techniques à partir des données OHLCV

        Args:
            ohlcv_data: Liste des données OHLCV [timestamp, open, high, low, close, volume]

        Returns:
            Dict contenant tous les indicateurs calculés
        """
        if not ohlcv_data or len(ohlcv_data) < 200:
            return self._get_default_indicators()

        # Extraire les prix et volumes
        closes = [candle[4] for candle in ohlcv_data]
        highs = [candle[2] for candle in ohlcv_data]
        lows = [candle[3] for candle in ohlcv_data]
        volumes = [candle[5] for candle in ohlcv_data]

        # Calculer les moyennes mobiles
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else closes[-1]
        ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else closes[-1]
        ma200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else closes[-1]

        # Calculer RSI 14
        rsi14 = self._calculate_rsi(closes, 14)

        # Calculer ATR 14
        atr14 = self._calculate_atr(highs, lows, closes, 14)

        # Calculer indicateurs de volume
        volume_avg20 = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else volumes[-1]
        volume_spike_ratio = volumes[-1] / volume_avg20 if volume_avg20 > 0 else 1.0

        # Analyser la structure du marché (simplifié)
        market_structure = self._analyze_market_structure(highs, lows)

        # Trouver la résistance la plus proche (simplifié)
        nearest_resistance = max(highs[-50:]) if len(highs) >= 50 else highs[-1]

        return {
            "ma20": round(ma20, 2),
            "ma50": round(ma50, 2),
            "ma200": round(ma200, 2),
            "rsi14": round(rsi14, 1),
            "atr14": round(atr14, 4),
            "volume_avg20": volume_avg20,
            "volume_spike_ratio": round(volume_spike_ratio, 2),
            "market_structure": market_structure,
            "nearest_resistance": round(nearest_resistance, 2)
        }

    def _get_default_indicators(self) -> Dict[str, float]:
        """Retourne des indicateurs par défaut en cas de données insuffisantes"""
        return {
            "ma20": 0.0,
            "ma50": 0.0,
            "ma200": 0.0,
            "rsi14": 50.0,
            "atr14": 0.0,
            "volume_avg20": 0.0,
            "volume_spike_ratio": 1.0,
            "market_structure": "UNDEFINED",
            "nearest_resistance": 0.0
        }

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calcule le RSI sur une période donnée"""
        if len(closes) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        if len(gains) < period:
            return 50.0

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calcule l'ATR (Average True Range)"""
        if len(highs) < period + 1:
            return 0.0

        true_ranges = []
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_ranges.append(max(tr1, tr2, tr3))

        if len(true_ranges) < period:
            return 0.0

        return sum(true_ranges[-period:]) / period

    def _analyze_market_structure(self, highs: List[float], lows: List[float]) -> str:
        """Analyse simplifiée de la structure du marché"""
        if len(highs) < 50 or len(lows) < 50:
            return "UNDEFINED"

        recent_highs = highs[-20:]
        recent_lows = lows[-20:]
        previous_highs = highs[-40:-20]
        previous_lows = lows[-40:-20]

        max_recent_high = max(recent_highs)
        max_previous_high = max(previous_highs)
        min_recent_low = min(recent_lows)
        min_previous_low = min(previous_lows)

        # Structure haussière : HH (Higher Highs) et HL (Higher Lows)
        if max_recent_high > max_previous_high and min_recent_low > min_previous_low:
            return "HH_HL"
        # Structure baissière : LH (Lower Highs) et LL (Lower Lows)
        elif max_recent_high < max_previous_high and min_recent_low < min_previous_low:
            return "LH_LL"
        # Structure mixte
        elif max_recent_high > max_previous_high and min_recent_low < min_previous_low:
            return "HH_LL"
        elif max_recent_high < max_previous_high and min_recent_low > min_previous_low:
            return "LH_HL"
        else:
            return "SIDEWAYS"

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