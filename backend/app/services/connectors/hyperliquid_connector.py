from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account import Account
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HyperliquidConnector:
    """Connector pour l'API Hyperliquid utilisant le SDK officiel"""

    def __init__(self, use_testnet: bool = False):
        # Laisser le SDK gérer les URLs automatiquement
        # URL de production par défaut : https://api.hyperliquid.xyz
        self.use_testnet = use_testnet

    def _build_info_client(self) -> Info:
        """Instantiate the Info client with the right network."""
        try:
            return Info(skip_ws=True, testnet=self.use_testnet)
        except TypeError:
            # Older versions of the SDK might not support the testnet kwarg
            logger.debug("Hyperliquid Info client does not accept testnet flag, falling back to defaults")
            return Info(skip_ws=True)

    async def test_connection(self, private_key: str) -> Dict[str, Any]:
        """
        Test la connexion à Hyperliquid avec une clé privée

        Args:
            private_key: Clé privée de l'utilisateur (format 0x...)

        Returns:
            Dict avec status et message
        """
        try:
            # Validation basique du format de clé privée
            if not private_key.startswith('0x') or len(private_key) != 66:
                return {
                    "status": "error",
                    "message": "Format de clé privée invalide (doit commencer par 0x et faire 66 caractères)"
                }

            # Test de connexion avec le SDK - laissez l'instance choisir l'URL
            info = self._build_info_client()

            # Essai de récupérer les métadonnées (endpoint public pour tester la connexion)
            meta = await asyncio.get_event_loop().run_in_executor(
                None, info.meta
            )

            if not meta:
                return {
                    "status": "error",
                    "message": "Impossible de récupérer les métadonnées Hyperliquid"
                }

            # Test avec Exchange pour valider la clé privée
            try:
                # Créer un wallet à partir de la clé privée
                wallet = Account.from_key(private_key)
                exchange = Exchange(wallet, base_url=None)

                # Test simple - récupérer l'état de l'utilisateur
                user_state = await asyncio.get_event_loop().run_in_executor(
                    None, info.user_state, wallet.address
                )

                network = "Testnet" if self.use_testnet else "Mainnet"
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

    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _ensure_dict(value: Any) -> Dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _ensure_list(value: Any) -> List[Any]:
        return value if isinstance(value, list) else []

    async def get_user_info(self, private_key: Optional[str], wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère les informations de l'utilisateur

        Args:
            private_key: Clé privée de l'utilisateur
            wallet_address: Adresse du wallet (optionnel, déduite de la clé privée si non fournie)

        Returns:
            Dict avec les informations utilisateur
        """
        try:
            info = self._build_info_client()

            if not wallet_address:
                if not private_key:
                    raise ValueError("Either a private key or a wallet address must be provided for user info retrieval")
                wallet = Account.from_key(private_key)
                wallet_address = wallet.address
            else:
                wallet_address = wallet_address.lower()

            loop = asyncio.get_event_loop()

            user_state = await loop.run_in_executor(
                None, info.user_state, wallet_address
            )

            spot_state: Optional[Dict[str, Any]] = None
            try:
                spot_state = await loop.run_in_executor(None, info.spot_user_state, wallet_address)
            except Exception as spot_error:
                logger.warning(f"Impossible de récupérer l'état spot Hyperliquid: {spot_error}")

            portfolio_data: Optional[Dict[str, Any]] = None
            try:
                portfolio_data = await loop.run_in_executor(None, info.portfolio, wallet_address)
            except Exception as portfolio_error:
                logger.warning(f"Impossible de récupérer le portefeuille Hyperliquid: {portfolio_error}")

            fills: List[Dict[str, Any]] = []
            try:
                raw_fills = await loop.run_in_executor(None, info.user_fills, wallet_address)
                fills = raw_fills[:50] if isinstance(raw_fills, list) else []
            except Exception as fill_error:
                logger.warning(f"Impossible de récupérer l'historique des trades Hyperliquid: {fill_error}")

            open_orders: List[Dict[str, Any]] = []
            try:
                raw_orders = await loop.run_in_executor(None, info.open_orders, wallet_address)
                open_orders = raw_orders if isinstance(raw_orders, list) else []
            except Exception as order_error:
                logger.warning(f"Impossible de récupérer les ordres ouverts Hyperliquid: {order_error}")

            frontend_orders: Optional[Dict[str, Any]] = None
            try:
                raw_frontend_orders = await loop.run_in_executor(None, info.frontend_open_orders, wallet_address)
                frontend_orders = raw_frontend_orders if isinstance(raw_frontend_orders, dict) else None
            except Exception as frontend_error:
                logger.debug(f"Impossible de récupérer les ordres frontend Hyperliquid: {frontend_error}")

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
                    "network": "testnet" if self.use_testnet else "mainnet",
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
