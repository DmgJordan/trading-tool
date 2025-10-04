import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import logging

from ..connectors.coingecko_connector import CoinGeckoConnector
from ..connectors.hyperliquid_connector import HyperliquidConnector
from ...models.market_data import MarketData
from ...models.user import User
from ...core import decrypt_api_key

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service principal pour la gestion des données de marché"""

    def __init__(self):
        self.coingecko_connector = CoinGeckoConnector()
        self.hyperliquid_mainnet = HyperliquidConnector(use_testnet=False)
        self.hyperliquid_testnet = HyperliquidConnector(use_testnet=True)

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

            # Convertir le symbole en ID CoinGecko (simplifié)
            coin_id = self._symbol_to_coingecko_id(symbol)

            result = await self.coingecko_connector.get_simple_price(
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

            private_key = decrypt_api_key(user.hyperliquid_api_key)
            connector = self.hyperliquid_testnet if use_testnet else self.hyperliquid_mainnet

            # Note: Hyperliquid n'a pas d'endpoint simple pour les prix
            # Il faudrait implémenter get_market_data dans HyperliquidConnector
            # Pour l'instant, on retourne une erreur
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

    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """
        Convertit un symbole en ID CoinGecko

        Note: C'est une version simplifiée. En production, il faudrait
        utiliser l'endpoint /coins/list de CoinGecko pour un mapping complet
        """
        symbol_mapping = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "USDT": "tether",
            "USDC": "usd-coin",
            "BNB": "binancecoin",
            "SOL": "solana",
            "ADA": "cardano",
            "AVAX": "avalanche-2",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LINK": "chainlink",
            "UNI": "uniswap",
            "LTC": "litecoin",
            "ATOM": "cosmos",
            "XRP": "ripple",
            "DOGE": "dogecoin"
        }

        return symbol_mapping.get(symbol.upper(), symbol.lower())

    async def store_market_data(
        self,
        db: Session,
        market_data: Dict[str, Any]
    ) -> Optional[MarketData]:
        """
        Stocke les données de marché en base

        Args:
            db: Session SQLAlchemy
            market_data: Données à stocker

        Returns:
            Instance MarketData créée ou None en cas d'erreur
        """
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

    async def get_historical_data(
        self,
        db: Session,
        symbol: str,
        hours_back: int = 24,
        source: Optional[str] = None
    ) -> List[MarketData]:
        """
        Récupère les données historiques pour un symbole

        Args:
            db: Session SQLAlchemy
            symbol: Symbole à rechercher
            hours_back: Nombre d'heures d'historique
            source: Filtrer par source (optionnel)

        Returns:
            Liste des données historiques
        """
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
        """
        Récupère le dernier prix stocké pour un symbole

        Args:
            db: Session SQLAlchemy
            symbol: Symbole à rechercher
            source: Filtrer par source (optionnel)

        Returns:
            Dernière donnée de marché ou None
        """
        try:
            query = db.query(MarketData).filter(MarketData.symbol == symbol.upper())

            if source:
                query = query.filter(MarketData.source == source)

            return query.order_by(desc(MarketData.data_timestamp)).first()

        except Exception as e:
            logger.error(f"Erreur récupération dernier prix pour {symbol}: {e}")
            return None

    async def refresh_and_store_price(
        self,
        db: Session,
        symbol: str,
        user: User,
        source: str = "auto",
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère et stocke le prix d'un symbole

        Args:
            db: Session SQLAlchemy
            symbol: Symbole à rechercher
            user: Utilisateur
            source: Source des données
            use_testnet: Utiliser le testnet

        Returns:
            Dict avec le résultat et les données stockées
        """
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

    async def get_supported_symbols(self) -> Dict[str, Any]:
        """
        Récupère la liste des symboles supportés

        Returns:
            Dict avec les symboles supportés par source
        """
        try:
            # Liste simplifiée des symboles supportés
            coingecko_symbols = [
                "BTC", "ETH", "USDT", "USDC", "BNB", "SOL", "ADA", "AVAX",
                "DOT", "MATIC", "LINK", "UNI", "LTC", "ATOM", "XRP", "DOGE"
            ]

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