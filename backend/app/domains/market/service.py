import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import logging

from .adapters import CCXTAdapter, CoinGeckoAdapter
from .models import MarketData
from ...domains.auth.models import User
from ...core import decrypt_api_key
from ...services.connectors.hyperliquid_connector import HyperliquidConnector
from ...schemas.claude import ClaudeMarketData
from ...shared import (
    calculate_rsi,
    calculate_atr,
    calculate_multiple_sma,
    analyze_volume
)

logger = logging.getLogger(__name__)

class MarketService:
    """Service unifié pour les données de marché et l'analyse technique"""

    def __init__(self):
        # Adapters pour I/O
        self.ccxt_adapter = CCXTAdapter()
        self.coingecko_adapter = CoinGeckoAdapter()
        self.hyperliquid_mainnet = HyperliquidConnector(use_testnet=False)
        self.hyperliquid_testnet = HyperliquidConnector(use_testnet=True)

        # Cache simple en mémoire pour CoinGecko
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_duration = timedelta(minutes=5)

        # Mapping des symboles vers les IDs CoinGecko
        self.symbol_to_id_mapping = self._get_symbol_mapping()

    def _get_symbol_mapping(self) -> Dict[str, str]:
        """Retourne le mapping symboles -> CoinGecko IDs"""
        return {
            # Principales cryptos
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "SOL": "solana",
            "TRX": "tron",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LINK": "chainlink",
            "UNI": "uniswap",
            "ATOM": "cosmos",
            "XLM": "stellar",
            "ALGO": "algorand",
            "VET": "vechain",
            "FIL": "filecoin",
            "THETA": "theta-token",
            "MANA": "decentraland",
            "SAND": "the-sandbox",
            "CRO": "crypto-com-chain",
            "NEAR": "near",
            "FLOW": "flow",
            "EGLD": "elrond-erd-2",
            "HBAR": "hedera-hashgraph",
            "ICP": "internet-computer",
            "AAVE": "aave",
            "GRT": "the-graph",
            "MKR": "maker",
            "SNX": "havven",
            "COMP": "compound-governance-token",
            "YFI": "yearn-finance",
            "SUSHI": "sushi",
            "CRV": "curve-dao-token",
            "BAL": "balancer",
            "REN": "republic-protocol",
            "ZRX": "0x",
            "OMG": "omisego",
            "LRC": "loopring",
            "BAT": "basic-attention-token",
            "ZIL": "zilliqa",
            "ICX": "icon",
            "QTUM": "qtum",
            "ONT": "ontology",
            "KAVA": "kava",
            "BAND": "band-protocol",
            "RVN": "ravencoin",
            "WAVES": "waves",
            "ZEC": "zcash",
            "DASH": "dash",
            "DCR": "decred",
            "XTZ": "tezos",
            "NEO": "neo",
            "EOS": "eos",
            "IOTA": "iota",
            "XMR": "monero",
            "LTC": "litecoin",
            "BCH": "bitcoin-cash",
            "ETC": "ethereum-classic",
            # DeFi tokens
            "1INCH": "1inch",
            "ALPHA": "alpha-finance-lab",
            "BADGER": "badger-dao",
            "CAKE": "pancakeswap-token",
            "RUNE": "thorchain",
            # Layer 2 & Scaling
            "AVAX": "avalanche-2",
            "FTM": "fantom",
            "LUNA": "terra-luna",
            "ONE": "harmony",
            # Meme coins
            "SHIB": "shiba-inu",
            # Gaming & NFT
            "AXS": "axie-infinity",
            "ENJ": "enjincoin",
            "CHZ": "chiliz",
            # Infrastructure
            "FTT": "ftx-token",
            "LEO": "leo-token",
            "HT": "huobi-token",
            "OKB": "okb",
            # Stablecoins
            "USDT": "tether",
            "USDC": "usd-coin"
        }

    # ==========================================================================
    # OHLCV ET ANALYSE TECHNIQUE
    # ==========================================================================

    async def get_multi_timeframe_analysis(
        self,
        exchange_name: str,
        symbol: str,
        profile: str
    ) -> Dict[str, Any]:
        """
        Récupère et analyse les données OHLCV multi-timeframes

        Args:
            exchange_name: Nom de l'exchange
            symbol: Symbole du trading pair
            profile: Profil de trading ("short", "medium", "long")

        Returns:
            Dict contenant l'analyse multi-timeframes complète
        """
        try:
            # 1. Récupérer les données OHLCV via CCXTAdapter
            ohlcv_result = await self.ccxt_adapter.fetch_multi_timeframe_ohlcv(
                exchange_name=exchange_name,
                symbol=symbol,
                profile=profile,
                limit=600
            )

            if ohlcv_result.get("status") == "error":
                return ohlcv_result

            # 2. Extraire les données
            ohlcv_data = ohlcv_result["ohlcv_data"]
            main_data = ohlcv_data["main"]
            higher_data = ohlcv_data["higher"]
            lower_data = ohlcv_data["lower"]
            timeframes = ohlcv_result["timeframes"]

            # 3. Calculer les indicateurs pour chaque timeframe (utilise shared/indicators)
            main_indicators = self._calculate_indicators(main_data)
            higher_indicators = self._calculate_indicators(higher_data)
            lower_indicators = self._calculate_indicators(lower_data)

            # 4. Formater la réponse
            return {
                "profile": profile,
                "symbol": ohlcv_result["symbol"],
                "tf": timeframes["main"],
                "current_price": ohlcv_result["current_price"],
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
                    "last_20_candles": [
                        [c[0], c[1], c[2], c[3], c[4], c[5]]
                        for c in main_data[-20:]
                    ] if main_data else []
                },
                "higher_tf": {
                    "tf": timeframes["higher"],
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
                    "tf": timeframes["lower"],
                    "rsi14": lower_indicators["rsi14"],
                    "volume": {
                        "current": int(lower_data[-1][5]) if lower_data else 0,
                        "avg20": int(lower_indicators["volume_avg20"]),
                        "spike_ratio": lower_indicators["volume_spike_ratio"]
                    },
                    "last_20_candles": [
                        [c[0], c[1], c[2], c[3], c[4], c[5]]
                        for c in lower_data[-20:]
                    ] if lower_data else []
                }
            }

        except Exception as e:
            logger.error(f"Erreur analyse multi-timeframes pour {symbol}: {e}")
            return {
                "status": "error",
                "message": f"Erreur analyse: {str(e)}"
            }

    def _calculate_indicators(self, ohlcv_data: List[List[float]]) -> Dict[str, float]:
        """
        Calcule les indicateurs techniques (délègue à shared/indicators)

        Args:
            ohlcv_data: Données OHLCV [timestamp, open, high, low, close, volume]

        Returns:
            Dict contenant tous les indicateurs
        """
        if not ohlcv_data or len(ohlcv_data) < 200:
            return self._get_default_indicators()

        # Extraire les prix et volumes
        closes = [candle[4] for candle in ohlcv_data]
        highs = [candle[2] for candle in ohlcv_data]
        lows = [candle[3] for candle in ohlcv_data]
        volumes = [candle[5] for candle in ohlcv_data]

        # Calculer les moyennes mobiles via shared/indicators
        mas = calculate_multiple_sma(closes, [20, 50, 200])

        # Calculer RSI et ATR via shared/indicators
        rsi14 = calculate_rsi(closes, 14)
        atr14 = calculate_atr(highs, lows, closes, 14)

        # Analyser le volume via shared/indicators
        volume_analysis = analyze_volume(volumes)

        # Analyser la structure du marché
        market_structure = self._analyze_market_structure(highs, lows)

        # Trouver la résistance la plus proche
        nearest_resistance = max(highs[-50:]) if len(highs) >= 50 else highs[-1]

        return {
            "ma20": round(mas["ma20"], 2),
            "ma50": round(mas["ma50"], 2),
            "ma200": round(mas["ma200"], 2),
            "rsi14": round(rsi14, 1) if rsi14 is not None else 50.0,
            "atr14": round(atr14, 4) if atr14 is not None else 0.0,
            "volume_avg20": volume_analysis["avg20"],
            "volume_spike_ratio": round(volume_analysis["spike_ratio"], 2),
            "market_structure": market_structure,
            "nearest_resistance": round(nearest_resistance, 2)
        }

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

    # ==========================================================================
    # PRIX ET MARKET DATA
    # ==========================================================================

    async def get_symbol_price(
        self,
        symbol: str,
        source: str = "auto",
        user: Optional[User] = None,
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère le prix d'un symbole depuis la source spécifiée

        Args:
            symbol: Symbole à rechercher (ex: "BTC", "ETH")
            source: Source des données ("coingecko", "hyperliquid", "auto")
            user: Utilisateur pour accéder aux clés API
            use_testnet: Utiliser le testnet pour Hyperliquid

        Returns:
            Dict avec les données de prix
        """
        try:
            if source == "auto":
                # Essayer CoinGecko en premier, puis Hyperliquid
                result = await self._try_coingecko_price(symbol, user)
                if result["status"] == "success":
                    return result

                result = await self._try_hyperliquid_price(symbol, user, use_testnet)
                if result["status"] == "success":
                    return result

                return {
                    "status": "error",
                    "message": f"Impossible de récupérer le prix pour {symbol} depuis toutes les sources"
                }

            elif source == "coingecko":
                return await self._try_coingecko_price(symbol, user)

            elif source == "hyperliquid":
                return await self._try_hyperliquid_price(symbol, user, use_testnet)

            else:
                return {
                    "status": "error",
                    "message": f"Source non supportée: {source}"
                }

        except Exception as e:
            logger.error(f"Erreur récupération prix pour {symbol}: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    async def _try_coingecko_price(self, symbol: str, user: Optional[User]) -> Dict[str, Any]:
        """Essaie de récupérer le prix depuis CoinGecko"""
        try:
            if not user or not user.coingecko_api_key:
                return {
                    "status": "error",
                    "message": "Clé API CoinGecko non configurée"
                }

            api_key = decrypt_api_key(user.coingecko_api_key)

            # Convertir le symbole en ID CoinGecko
            coin_id = self.symbol_to_id_mapping.get(symbol.upper(), symbol.lower())

            result = await self.coingecko_adapter.get_simple_price(
                api_key=api_key,
                ids=coin_id,
                vs_currencies="usd"
            )

            if result["status"] == "success" and result["data"]:
                coin_data = result["data"].get(coin_id, {})
                if coin_data:
                    return {
                        "status": "success",
                        "data": {
                            "symbol": symbol.upper(),
                            "name": coin_id.replace("-", " ").title(),
                            "price_usd": coin_data.get("usd", 0),
                            "price_change_24h": coin_data.get("usd_24h_change"),
                            "volume_24h_usd": coin_data.get("usd_24h_vol"),
                            "market_cap_usd": coin_data.get("usd_market_cap"),
                            "source": "coingecko",
                            "source_id": coin_id,
                            "data_timestamp": datetime.utcnow(),
                            "raw_data": json.dumps(coin_data)
                        }
                    }

            return {
                "status": "error",
                "message": f"Données non trouvées pour {symbol} sur CoinGecko"
            }

        except Exception as e:
            logger.error(f"Erreur CoinGecko pour {symbol}: {e}")
            return {
                "status": "error",
                "message": f"Erreur CoinGecko: {str(e)}"
            }

    async def _try_hyperliquid_price(
        self,
        symbol: str,
        user: Optional[User],
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """Essaie de récupérer le prix depuis Hyperliquid"""
        try:
            if not user or not user.hyperliquid_api_key:
                return {
                    "status": "error",
                    "message": "Clé API Hyperliquid non configurée"
                }

            # Note: Hyperliquid n'a pas d'endpoint simple pour les prix
            # Il faudrait implémenter get_market_data dans HyperliquidConnector
            return {
                "status": "error",
                "message": "Prix Hyperliquid non encore implémenté"
            }

        except Exception as e:
            logger.error(f"Erreur Hyperliquid pour {symbol}: {e}")
            return {
                "status": "error",
                "message": f"Erreur Hyperliquid: {str(e)}"
            }

    # ==========================================================================
    # STOCKAGE ET HISTORIQUE DB
    # ==========================================================================

    async def store_market_data(
        self,
        db: Session,
        market_data: Dict[str, Any]
    ) -> Optional[MarketData]:
        """Stocke les données de marché en base"""
        try:
            db_market_data = MarketData(
                symbol=market_data["symbol"],
                name=market_data.get("name"),
                price_usd=market_data["price_usd"],
                price_change_24h=market_data.get("price_change_24h"),
                price_change_24h_abs=market_data.get("price_change_24h_abs"),
                volume_24h_usd=market_data.get("volume_24h_usd"),
                market_cap_usd=market_data.get("market_cap_usd"),
                source=market_data["source"],
                source_id=market_data.get("source_id"),
                raw_data=market_data.get("raw_data"),
                data_timestamp=market_data["data_timestamp"]
            )

            db.add(db_market_data)
            db.commit()
            db.refresh(db_market_data)

            logger.info(f"Données stockées pour {market_data['symbol']} depuis {market_data['source']}")
            return db_market_data

        except Exception as e:
            logger.error(f"Erreur stockage données de marché: {e}")
            db.rollback()
            return None

    async def refresh_and_store_price(
        self,
        db: Session,
        symbol: str,
        user: User,
        source: str = "auto",
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """Récupère et stocke le prix d'un symbole"""
        try:
            # Récupérer le prix
            price_result = await self.get_symbol_price(symbol, source, user, use_testnet)

            if price_result["status"] != "success":
                return price_result

            # Stocker en base
            stored_data = await self.store_market_data(db, price_result["data"])

            if stored_data:
                return {
                    "status": "success",
                    "message": f"Prix récupéré et stocké pour {symbol}",
                    "data": price_result["data"],
                    "stored_id": stored_data.id
                }
            else:
                return {
                    "status": "partial",
                    "message": f"Prix récupéré pour {symbol} mais erreur de stockage",
                    "data": price_result["data"]
                }

        except Exception as e:
            logger.error(f"Erreur refresh prix pour {symbol}: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    async def get_historical_data(
        self,
        db: Session,
        symbol: str,
        hours_back: int = 24,
        source: Optional[str] = None
    ) -> List[MarketData]:
        """Récupère les données historiques pour un symbole"""
        try:
            query = db.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol.upper(),
                    MarketData.data_timestamp >= datetime.utcnow() - timedelta(hours=hours_back)
                )
            )

            if source:
                query = query.filter(MarketData.source == source)

            return query.order_by(desc(MarketData.data_timestamp)).limit(1000).all()

        except Exception as e:
            logger.error(f"Erreur récupération historique pour {symbol}: {e}")
            return []

    async def get_latest_price(
        self,
        db: Session,
        symbol: str,
        source: Optional[str] = None
    ) -> Optional[MarketData]:
        """Récupère le dernier prix stocké pour un symbole"""
        try:
            query = db.query(MarketData).filter(MarketData.symbol == symbol.upper())

            if source:
                query = query.filter(MarketData.source == source)

            return query.order_by(desc(MarketData.data_timestamp)).first()

        except Exception as e:
            logger.error(f"Erreur récupération dernier prix pour {symbol}: {e}")
            return None

    # ==========================================================================
    # MARKET DATA POUR CLAUDE IA
    # ==========================================================================

    async def get_market_data_for_assets(
        self,
        api_key: str,
        assets: List[str]
    ) -> Dict[str, ClaudeMarketData]:
        """
        Récupère les données de marché pour une liste d'actifs (pour Claude IA)

        Args:
            api_key: Clé API CoinGecko
            assets: Liste des symboles d'actifs

        Returns:
            Dictionnaire des données de marché par symbole
        """
        try:
            # Convertir les symboles en IDs CoinGecko
            coingecko_ids = []
            symbol_to_id = {}

            for symbol in assets:
                symbol_upper = symbol.upper()
                coingecko_id = self.symbol_to_id_mapping.get(symbol_upper)

                if coingecko_id:
                    coingecko_ids.append(coingecko_id)
                    symbol_to_id[coingecko_id] = symbol_upper
                else:
                    logger.warning(f"ID CoinGecko non trouvé pour {symbol_upper}")

            if not coingecko_ids:
                logger.error("Aucun ID CoinGecko valide trouvé")
                return {}

            # Vérifier le cache
            cached_data = self._get_cached_data(coingecko_ids)
            ids_to_fetch = [id for id in coingecko_ids if id not in cached_data]

            # Récupérer les données manquantes
            fresh_data = {}
            if ids_to_fetch:
                fresh_data = await self._fetch_fresh_data(api_key, ids_to_fetch)

                # Mettre à jour le cache
                for id, data in fresh_data.items():
                    self._cache[id] = {
                        "data": data,
                        "timestamp": datetime.now()
                    }

            # Combiner cache et nouvelles données
            all_data = {**cached_data, **fresh_data}

            # Convertir en format ClaudeMarketData
            result = {}
            for coingecko_id, raw_data in all_data.items():
                symbol = symbol_to_id.get(coingecko_id)
                if symbol and raw_data:
                    try:
                        market_data = self._convert_to_claude_format(symbol, coingecko_id, raw_data)
                        result[symbol] = market_data
                    except Exception as e:
                        logger.error(f"Erreur conversion données pour {symbol}: {e}")

            return result

        except Exception as e:
            logger.error(f"Erreur récupération données marché: {e}")
            return {}

    def _get_cached_data(self, coingecko_ids: List[str]) -> Dict[str, Any]:
        """Récupère les données en cache encore valides"""
        cached = {}
        now = datetime.now()

        for id in coingecko_ids:
            if id in self._cache:
                cache_entry = self._cache[id]
                cache_time = cache_entry["timestamp"]

                if now - cache_time < self._cache_duration:
                    cached[id] = cache_entry["data"]
                else:
                    # Nettoyer le cache expiré
                    del self._cache[id]

        return cached

    async def _fetch_fresh_data(self, api_key: str, coingecko_ids: List[str]) -> Dict[str, Any]:
        """Récupère de nouvelles données depuis CoinGecko"""
        try:
            # Joindre les IDs pour l'appel API
            ids_string = ",".join(coingecko_ids)

            # Appel à l'API CoinGecko
            result = await self.coingecko_adapter.get_simple_price(
                api_key=api_key,
                ids=ids_string,
                vs_currencies="usd"
            )

            if result["status"] != "success":
                logger.error(f"Erreur API CoinGecko: {result.get('message', 'Erreur inconnue')}")
                return {}

            return result["data"]

        except Exception as e:
            logger.error(f"Erreur appel API CoinGecko: {e}")
            return {}

    def _convert_to_claude_format(
        self,
        symbol: str,
        coingecko_id: str,
        raw_data: Dict[str, Any]
    ) -> ClaudeMarketData:
        """Convertit les données CoinGecko au format ClaudeMarketData"""
        try:
            # Extraire les données principales
            current_price = raw_data.get("usd", 0.0)
            price_change_24h = raw_data.get("usd_24h_change")
            volume_24h = raw_data.get("usd_24h_vol")
            market_cap = raw_data.get("usd_market_cap")

            # Données additionnelles si disponibles
            high_24h = raw_data.get("usd_24h_high")
            low_24h = raw_data.get("usd_24h_low")
            price_change_7d = raw_data.get("usd_7d_change")
            price_change_30d = raw_data.get("usd_30d_change")

            # Nom de l'actif
            name = coingecko_id.replace("-", " ").title()

            return ClaudeMarketData(
                symbol=symbol,
                name=name,
                current_price=float(current_price) if current_price else 0.0,
                price_change_24h=float(price_change_24h) if price_change_24h is not None else None,
                volume_24h=float(volume_24h) if volume_24h else None,
                market_cap=float(market_cap) if market_cap else None,
                high_24h=float(high_24h) if high_24h else None,
                low_24h=float(low_24h) if low_24h else None,
                price_change_7d=float(price_change_7d) if price_change_7d is not None else None,
                price_change_30d=float(price_change_30d) if price_change_30d is not None else None,
                last_updated=datetime.now()
            )

        except Exception as e:
            logger.error(f"Erreur conversion données {symbol}: {e}")

            # Fallback minimal
            return ClaudeMarketData(
                symbol=symbol,
                name=symbol,
                current_price=0.0,
                last_updated=datetime.now()
            )

    # ==========================================================================
    # SYMBOLES ET EXCHANGES
    # ==========================================================================

    async def get_supported_symbols(self) -> Dict[str, Any]:
        """Récupère la liste des symboles supportés"""
        try:
            coingecko_symbols = list(self.symbol_to_id_mapping.keys())

            hyperliquid_symbols = [
                "BTC", "ETH", "SOL", "AVAX", "MATIC", "LINK", "UNI", "ATOM"
            ]

            return {
                "status": "success",
                "message": "Symboles supportés récupérés",
                "coingecko_symbols": coingecko_symbols,
                "hyperliquid_symbols": hyperliquid_symbols,
                "total_symbols": len(set(coingecko_symbols + hyperliquid_symbols))
            }

        except Exception as e:
            logger.error(f"Erreur récupération symboles supportés: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    def clear_cache(self):
        """Nettoie le cache en mémoire"""
        self._cache.clear()
        logger.info("Cache des données de marché nettoyé")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le cache"""
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0

        for entry in self._cache.values():
            if now - entry["timestamp"] < self._cache_duration:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_duration_minutes": self._cache_duration.total_seconds() / 60
        }
