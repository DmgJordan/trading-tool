"""Adapter pur I/O pour Hyperliquid API - AUCUNE logique métier"""

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account import Account
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HyperliquidAdapter:
    """
    Adapter pur I/O pour Hyperliquid API

    Responsabilités :
    - Communication avec l'API Hyperliquid
    - Parsing des réponses
    - Création wallet et connexion

    PAS de logique métier (validation, calculs, risk management)
    """

    def __init__(self, use_testnet: bool = False):
        self.use_testnet = use_testnet

    # =========================================================================
    # HELPERS - Création wallet et connexion
    # =========================================================================

    def _build_info_client(self, use_testnet: Optional[bool] = None) -> Info:
        """Crée un client Info avec le bon réseau"""
        if use_testnet is None:
            use_testnet = self.use_testnet

        try:
            return Info(skip_ws=True, testnet=use_testnet)
        except TypeError:
            # Anciennes versions du SDK ne supportent pas testnet kwarg
            logger.debug("Hyperliquid Info client does not accept testnet flag, falling back to defaults")
            return Info(skip_ws=True)

    def _create_wallet(self, private_key: str) -> Account:
        """
        Crée un wallet Ethereum à partir d'une clé privée
        Gère les formats avec/sans préfixe 0x
        """
        try:
            return Account.from_key(private_key)
        except Exception:
            # Fallback: essayer avec/sans préfixe 0x
            try:
                if private_key.startswith('0x') and len(private_key) == 66:
                    return Account.from_key(private_key[2:])
                elif not private_key.startswith('0x') and len(private_key) == 64:
                    return Account.from_key('0x' + private_key)
            except Exception as e:
                raise ValueError(f"Format clé invalide (attendu: 64 chars hex avec/sans 0x): {e}")
            raise ValueError("Format clé privée invalide")

    def _initialize_connection(
        self,
        private_key: str,
        use_testnet: bool,
        account_address: Optional[str] = None
    ) -> tuple[Exchange, Info, str]:
        """
        Initialise la connexion Hyperliquid et crée le wallet

        Returns:
            (exchange, info, query_address) où query_address est l'adresse à interroger
        """
        # Sélectionner l'URL API
        base_url = constants.TESTNET_API_URL if use_testnet else constants.MAINNET_API_URL
        logger.info(f"Mode: {'testnet' if use_testnet else 'mainnet'}")

        # Créer le wallet
        wallet = self._create_wallet(private_key)
        logger.info(f"Wallet créé: {wallet.address}")

        # Initialiser Exchange et Info
        if account_address:
            logger.info(f"Mode délégué: API {wallet.address[:10]}... → {account_address[:10]}...")
            exchange = Exchange(wallet, base_url=base_url, account_address=account_address)
            query_address = account_address
        else:
            exchange = Exchange(wallet, base_url=base_url)
            query_address = wallet.address

        info = Info(base_url=base_url, skip_ws=True)

        return exchange, info, query_address

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """Convertit une valeur en float de manière sécurisée"""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _ensure_dict(value: Any) -> Dict[str, Any]:
        """Assure qu'une valeur est un dict"""
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _ensure_list(value: Any) -> List[Any]:
        """Assure qu'une valeur est une list"""
        return value if isinstance(value, list) else []

    # =========================================================================
    # TESTS ET INFORMATIONS
    # =========================================================================

    async def test_connection(self, private_key: str, use_testnet: Optional[bool] = None) -> Dict[str, Any]:
        """
        Test la connexion à Hyperliquid avec une clé privée

        Args:
            private_key: Clé privée de l'utilisateur (format 0x...)
            use_testnet: Utiliser le testnet (défaut: self.use_testnet)

        Returns:
            Dict avec status et message
        """
        if use_testnet is None:
            use_testnet = self.use_testnet

        try:
            # Validation basique du format de clé privée
            if not private_key.startswith('0x') or len(private_key) != 66:
                return {
                    "status": "error",
                    "message": "Format de clé privée invalide (doit commencer par 0x et faire 66 caractères)"
                }

            # Test de connexion avec le SDK
            info = self._build_info_client(use_testnet)

            # Essai de récupérer les métadonnées (endpoint public)
            meta = await asyncio.get_event_loop().run_in_executor(None, info.meta)

            if not meta:
                return {
                    "status": "error",
                    "message": "Impossible de récupérer les métadonnées Hyperliquid"
                }

            # Test avec Exchange pour valider la clé privée
            try:
                wallet = self._create_wallet(private_key)
                exchange = Exchange(wallet, base_url=None)

                # Test simple - récupérer l'état de l'utilisateur
                user_state = await asyncio.get_event_loop().run_in_executor(
                    None, info.user_state, wallet.address
                )

                network = "Testnet" if use_testnet else "Mainnet"
                return {
                    "status": "success",
                    "message": f"Connexion Hyperliquid {network} réussie !",
                    "data": {
                        "wallet_address": wallet.address,
                        "network": network,
                        "user_state_available": user_state is not None
                    }
                }

            except Exception as auth_error:
                logger.error(f"Erreur d'authentification Hyperliquid: {auth_error}")
                return {
                    "status": "error",
                    "message": f"Clé privée invalide ou problème d'authentification: {str(auth_error)}"
                }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "Timeout lors de la connexion à Hyperliquid"
            }
        except Exception as e:
            logger.error(f"Erreur de connexion Hyperliquid: {e}")
            return {
                "status": "error",
                "message": f"Erreur de connexion: {str(e)}"
            }

    async def get_user_info(
        self,
        private_key: Optional[str],
        wallet_address: Optional[str] = None,
        use_testnet: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Récupère les informations complètes de l'utilisateur Hyperliquid

        Args:
            private_key: Clé privée de l'utilisateur
            wallet_address: Adresse du wallet (optionnel, déduite de la clé privée si non fournie)
            use_testnet: Utiliser le testnet (défaut: self.use_testnet)

        Returns:
            Dict avec status et data complète (portfolio, positions, ordres, etc.)
        """
        if use_testnet is None:
            use_testnet = self.use_testnet

        try:
            info = self._build_info_client(use_testnet)

            if not wallet_address:
                if not private_key:
                    raise ValueError("Either a private key or a wallet address must be provided")
                wallet = self._create_wallet(private_key)
                wallet_address = wallet.address
            else:
                wallet_address = wallet_address.lower()

            loop = asyncio.get_event_loop()

            # Récupérer user_state (perpétuels)
            user_state = await loop.run_in_executor(None, info.user_state, wallet_address)

            # Récupérer spot_state
            spot_state: Optional[Dict[str, Any]] = None
            try:
                spot_state = await loop.run_in_executor(None, info.spot_user_state, wallet_address)
            except Exception as spot_error:
                logger.warning(f"Impossible de récupérer l'état spot Hyperliquid: {spot_error}")

            # Récupérer portfolio (historique)
            portfolio_data: Optional[List[List[Union[str, Dict[str, Any]]]]] = None
            try:
                raw_portfolio = await loop.run_in_executor(None, info.portfolio, wallet_address)
                portfolio_data = self._ensure_list(raw_portfolio)
            except Exception as portfolio_error:
                logger.warning(f"Impossible de récupérer le portefeuille Hyperliquid: {portfolio_error}")

            # Récupérer fills (trades récents)
            fills: List[Dict[str, Any]] = []
            try:
                raw_fills = await loop.run_in_executor(None, info.user_fills, wallet_address)
                fills = raw_fills[:50] if isinstance(raw_fills, list) else []
            except Exception as fill_error:
                logger.warning(f"Impossible de récupérer l'historique des trades Hyperliquid: {fill_error}")

            # Récupérer ordres ouverts
            open_orders: List[Dict[str, Any]] = []
            try:
                raw_orders = await loop.run_in_executor(None, info.open_orders, wallet_address)
                open_orders = raw_orders if isinstance(raw_orders, list) else []
            except Exception as order_error:
                logger.warning(f"Impossible de récupérer les ordres ouverts Hyperliquid: {order_error}")

            # Récupérer frontend orders
            frontend_orders: Optional[Dict[str, Any]] = None
            try:
                raw_frontend_orders = await loop.run_in_executor(None, info.frontend_open_orders, wallet_address)
                frontend_orders = raw_frontend_orders if isinstance(raw_frontend_orders, dict) else None
            except Exception as frontend_error:
                logger.debug(f"Impossible de récupérer les ordres frontend Hyperliquid: {frontend_error}")

            # Parser les données
            margin_summary = self._ensure_dict(user_state.get('marginSummary')) if isinstance(user_state, dict) else {}

            perp_positions: List[Any] = []
            asset_positions: List[Any] = []
            if isinstance(user_state, dict):
                raw_perp_positions = user_state.get('perpPositions')
                if not isinstance(raw_perp_positions, list):
                    raw_perp_positions = user_state.get('assetPositions')
                perp_positions = self._ensure_list(raw_perp_positions)
                asset_positions = self._ensure_list(user_state.get('assetPositions'))

            spot_positions_count = 0
            if isinstance(spot_state, dict):
                raw_spot_positions = spot_state.get('assetPositions')
                if isinstance(raw_spot_positions, list):
                    spot_positions_count = len(raw_spot_positions)
                else:
                    balances = spot_state.get('balances') or spot_state.get('tokenBalances')
                    if isinstance(balances, dict):
                        spot_positions_count = len([
                            value for value in balances.values() if self._safe_float(value)
                        ])

            withdrawables = self._ensure_dict(user_state.get('withdrawables')) if isinstance(user_state, dict) else {}

            portfolio_summary = {
                'account_value': self._safe_float(
                    margin_summary.get('accountValue') or margin_summary.get('account_value')
                ),
                'total_margin_used': self._safe_float(
                    margin_summary.get('totalMargin') or margin_summary.get('total_margin')
                ),
                'total_unrealized_pnl': self._safe_float(
                    margin_summary.get('totalUnrealizedPnL') or margin_summary.get('totalUnrealizedPnl')
                ),
                'withdrawable_balance': self._safe_float(
                    withdrawables.get('withdrawable') or withdrawables.get('amount')
                ),
                'perp_position_count': len(perp_positions),
                'asset_position_count': spot_positions_count,
            }

            return {
                "status": "success",
                "data": {
                    "wallet_address": wallet_address,
                    "network": "testnet" if use_testnet else "mainnet",
                    "retrieved_at": datetime.utcnow().isoformat() + "Z",
                    "portfolio_summary": portfolio_summary,
                    "user_state": user_state,
                    "spot_user_state": spot_state,
                    "portfolio": portfolio_data,
                    "fills": fills,
                    "open_orders": open_orders,
                    "frontend_open_orders": frontend_orders,
                }
            }

        except Exception as e:
            logger.error(f"Erreur récupération info utilisateur: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    async def get_portfolio_summary(
        self,
        private_key: str,
        wallet_address: Optional[str] = None,
        use_testnet: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Récupère un résumé simplifié du portfolio (pour trading)

        Returns:
            Dict avec account_value, available_balance, positions
        """
        if use_testnet is None:
            use_testnet = self.use_testnet

        try:
            info = self._build_info_client(use_testnet)

            if not wallet_address:
                wallet = self._create_wallet(private_key)
                wallet_address = wallet.address

            loop = asyncio.get_event_loop()
            user_state = await loop.run_in_executor(None, info.user_state, wallet_address)

            if not user_state:
                raise ValueError("État du portefeuille inaccessible")

            # Extraire account_value
            margin_summary = user_state.get("marginSummary", {})
            account_value = float(margin_summary.get("accountValue", 0))

            # Extraire available_balance
            withdrawables = user_state.get("withdrawable", None)
            if isinstance(withdrawables, str):
                available_balance = float(withdrawables)
            elif isinstance(withdrawables, dict):
                available_balance = float(withdrawables.get("withdrawable", 0))
            else:
                available_balance = float(user_state.get("withdrawable", 0))

            # Extraire positions
            positions = []
            for position in user_state.get("assetPositions", []):
                pos_data = position.get("position", {})
                positions.append({
                    "symbol": pos_data.get("coin"),
                    "size": float(pos_data.get("szi", 0)),
                    "entry_price": float(pos_data.get("entryPx", 0)) if pos_data.get("entryPx") else None,
                    "unrealized_pnl": float(pos_data.get("unrealizedPnl", 0)) if pos_data.get("unrealizedPnl") else None,
                })

            return {
                "status": "success",
                "data": {
                    "account_value": account_value,
                    "available_balance": available_balance,
                    "positions": positions,
                    "network": "testnet" if use_testnet else "mainnet"
                }
            }

        except Exception as e:
            logger.error(f"Erreur récupération portfolio summary: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    # =========================================================================
    # TRADING - Placement d'ordres
    # =========================================================================

    async def place_order(
        self,
        private_key: str,
        symbol: str,
        is_buy: bool,
        size: float,
        price: float,
        order_type: Dict[str, Any],
        reduce_only: bool = False,
        use_testnet: bool = False,
        account_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place un ordre sur Hyperliquid

        Args:
            private_key: Clé privée du wallet API
            symbol: Symbole (ex: "BTC")
            is_buy: True pour achat, False pour vente
            size: Taille de l'ordre
            price: Prix limite
            order_type: Type d'ordre (ex: {"limit": {"tif": "Gtc"}})
            reduce_only: Réduire seulement (pour SL/TP)
            use_testnet: Utiliser le testnet
            account_address: Adresse du compte principal (trading délégué)

        Returns:
            Dict avec success (bool), order_id (str) ou error (str)
        """
        try:
            exchange, info, query_address = self._initialize_connection(
                private_key, use_testnet, account_address
            )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                exchange.order,
                symbol,
                is_buy,
                float(size),
                float(price),
                order_type,
                reduce_only
            )

            return self._parse_order_result(result)

        except Exception as e:
            logger.error(f"Exception placement ordre: {type(e).__name__}: {e}")
            return {"success": False, "error": self._safe_encode_error(e)}

    def _parse_order_result(self, result: Dict) -> Dict[str, Any]:
        """
        Parse la réponse de l'API Hyperliquid et extrait l'order ID

        Returns:
            {"success": bool, "order_id": str} ou {"success": bool, "error": str}
        """
        if not result or result.get("status") != "ok":
            error = result.get("response", {}).get("error", "Erreur inconnue") if result else "Pas de réponse"
            logger.error(f"Échec ordre: {error}")
            return {"success": False, "error": error}

        statuses = result.get("response", {}).get("data", {}).get("statuses", [])

        if not statuses:
            return {"success": False, "error": "Aucun statut retourné"}

        first_status = statuses[0]

        # Vérifier si rejeté
        if "error" in first_status:
            error_msg = first_status["error"]
            logger.error(f"Ordre rejeté: {error_msg}")
            return {"success": False, "error": error_msg}

        # Extraire order ID
        order_id = first_status.get("resting", {}).get("oid")
        order_id_str = str(order_id) if order_id is not None else None

        return {"success": True, "order_id": order_id_str}

    def _safe_encode_error(self, error: Exception) -> str:
        """Encode un message d'erreur en ASCII pour éviter les problèmes d'encodage"""
        try:
            return str(error).encode('ascii', errors='replace').decode('ascii')
        except:
            return f"Erreur {type(error).__name__} (message non décodable)"

    # =========================================================================
    # QUERIES - Positions et ordres
    # =========================================================================

    async def get_open_orders(
        self,
        private_key: str,
        wallet_address: Optional[str] = None,
        use_testnet: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Récupère les ordres ouverts

        Returns:
            Dict avec status et liste des ordres ouverts
        """
        if use_testnet is None:
            use_testnet = self.use_testnet

        try:
            info = self._build_info_client(use_testnet)

            if not wallet_address:
                wallet = self._create_wallet(private_key)
                wallet_address = wallet.address

            loop = asyncio.get_event_loop()
            raw_orders = await loop.run_in_executor(None, info.open_orders, wallet_address)
            orders = raw_orders if isinstance(raw_orders, list) else []

            return {
                "status": "success",
                "data": {
                    "orders": orders,
                    "count": len(orders)
                }
            }

        except Exception as e:
            logger.error(f"Erreur récupération ordres ouverts: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    async def get_positions(
        self,
        private_key: str,
        wallet_address: Optional[str] = None,
        use_testnet: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Récupère les positions ouvertes

        Returns:
            Dict avec status et liste des positions
        """
        if use_testnet is None:
            use_testnet = self.use_testnet

        try:
            info = self._build_info_client(use_testnet)

            if not wallet_address:
                wallet = self._create_wallet(private_key)
                wallet_address = wallet.address

            loop = asyncio.get_event_loop()
            user_state = await loop.run_in_executor(None, info.user_state, wallet_address)

            positions = []
            for position in user_state.get("assetPositions", []):
                pos_data = position.get("position", {})
                size = float(pos_data.get("szi", 0))

                # Filtrer les positions fermées (size == 0)
                if size != 0:
                    positions.append({
                        "symbol": pos_data.get("coin"),
                        "size": size,
                        "entry_price": float(pos_data.get("entryPx", 0)) if pos_data.get("entryPx") else None,
                        "unrealized_pnl": float(pos_data.get("unrealizedPnl", 0)) if pos_data.get("unrealizedPnl") else None,
                        "leverage": float(pos_data.get("leverage", {}).get("value", 1)) if pos_data.get("leverage") else None,
                    })

            return {
                "status": "success",
                "data": {
                    "positions": positions,
                    "count": len(positions)
                }
            }

        except Exception as e:
            logger.error(f"Erreur récupération positions: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    async def cancel_order(
        self,
        private_key: str,
        symbol: str,
        order_id: int,
        use_testnet: bool = False,
        account_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Annule un ordre

        Args:
            private_key: Clé privée du wallet API
            symbol: Symbole de l'ordre
            order_id: ID de l'ordre à annuler
            use_testnet: Utiliser le testnet
            account_address: Adresse du compte principal (trading délégué)

        Returns:
            Dict avec success et message
        """
        try:
            exchange, info, query_address = self._initialize_connection(
                private_key, use_testnet, account_address
            )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                exchange.cancel,
                symbol,
                order_id
            )

            if result and result.get("status") == "ok":
                return {
                    "success": True,
                    "message": f"Ordre {order_id} annulé avec succès"
                }
            else:
                error = result.get("response", {}).get("error", "Erreur inconnue") if result else "Pas de réponse"
                return {
                    "success": False,
                    "error": error
                }

        except Exception as e:
            logger.error(f"Erreur annulation ordre: {e}")
            return {
                "success": False,
                "error": str(e)
            }
