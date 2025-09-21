from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
from ..services.connectors.coingecko_connector import CoinGeckoConnector
from ..schemas.claude import ClaudeMarketData

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service d'intégration des données de marché CoinGecko"""

    def __init__(self):
        self.coingecko = CoinGeckoConnector()

        # Cache simple en mémoire (pour éviter trop d'appels API)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_duration = timedelta(minutes=5)  # Cache 5 minutes

        # Mapping des symboles vers les IDs CoinGecko
        self.symbol_to_id_mapping = {
            # Cryptos principales
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
            "MATIC": "matic-network",
            "AVAX": "avalanche-2",
            "FTM": "fantom",
            "LUNA": "terra-luna",
            "ONE": "harmony",
            # Meme coins
            "SHIB": "shiba-inu",
            "DOGE": "dogecoin",
            # Gaming & NFT
            "AXS": "axie-infinity",
            "ENJ": "enjincoin",
            "CHZ": "chiliz",
            # Infrastructure
            "FTT": "ftx-token",
            "LEO": "leo-token",
            "HT": "huobi-token",
            "OKB": "okb"
        }

    async def get_market_data_for_assets(
        self,
        api_key: str,
        assets: List[str]
    ) -> Dict[str, ClaudeMarketData]:
        """
        Récupère les données de marché pour une liste d'actifs

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
            result = await self.coingecko.get_simple_price(
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
        """
        Convertit les données CoinGecko au format ClaudeMarketData

        Args:
            symbol: Symbole de l'actif (ex: BTC)
            coingecko_id: ID CoinGecko (ex: bitcoin)
            raw_data: Données brutes de CoinGecko

        Returns:
            Données formatées pour Claude
        """
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

            # Nom de l'actif (utiliser mapping ou fallback)
            name = self._get_asset_name(symbol, coingecko_id)

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

    def _get_asset_name(self, symbol: str, coingecko_id: str) -> str:
        """Retourne le nom complet d'un actif"""

        # Mapping des noms complets
        name_mapping = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "BNB": "BNB",
            "XRP": "XRP",
            "ADA": "Cardano",
            "DOGE": "Dogecoin",
            "SOL": "Solana",
            "TRX": "TRON",
            "DOT": "Polkadot",
            "MATIC": "Polygon",
            "LINK": "Chainlink",
            "UNI": "Uniswap",
            "ATOM": "Cosmos",
            "XLM": "Stellar",
            "ALGO": "Algorand",
            "VET": "VeChain",
            "FIL": "Filecoin",
            "THETA": "Theta Token",
            "MANA": "Decentraland",
            "SAND": "The Sandbox",
            "CRO": "Cronos",
            "NEAR": "NEAR Protocol",
            "FLOW": "Flow",
            "EGLD": "MultiversX",
            "HBAR": "Hedera",
            "ICP": "Internet Computer",
            "AAVE": "Aave",
            "GRT": "The Graph",
            "MKR": "Maker",
            "SNX": "Synthetix",
            "COMP": "Compound",
            "YFI": "yearn.finance",
            "SUSHI": "SushiSwap",
            "CRV": "Curve DAO Token",
            "BAL": "Balancer",
            "LTC": "Litecoin",
            "BCH": "Bitcoin Cash",
            "ETC": "Ethereum Classic",
            "XMR": "Monero",
            "ZEC": "Zcash",
            "DASH": "Dash",
            "XTZ": "Tezos",
            "AVAX": "Avalanche",
            "FTM": "Fantom",
            "LUNA": "Terra Luna Classic",
            "ONE": "Harmony",
            "SHIB": "Shiba Inu",
            "AXS": "Axie Infinity",
            "ENJ": "Enjin Coin",
            "CHZ": "Chiliz"
        }

        return name_mapping.get(symbol, symbol)

    async def get_asset_details(
        self,
        api_key: str,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère des détails approfondis pour un actif spécifique

        Args:
            api_key: Clé API CoinGecko
            symbol: Symbole de l'actif

        Returns:
            Détails de l'actif ou None
        """
        try:
            coingecko_id = self.symbol_to_id_mapping.get(symbol.upper())
            if not coingecko_id:
                return None

            # Pour l'instant, utiliser les données simple price
            # TODO: Implémenter appel à l'endpoint coins/{id} pour plus de détails
            result = await self.coingecko.get_simple_price(
                api_key=api_key,
                ids=coingecko_id,
                vs_currencies="usd"
            )

            if result["status"] == "success":
                return result["data"].get(coingecko_id)

            return None

        except Exception as e:
            logger.error(f"Erreur récupération détails {symbol}: {e}")
            return None

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

    def get_supported_assets(self) -> List[str]:
        """Retourne la liste des actifs supportés"""
        return list(self.symbol_to_id_mapping.keys())