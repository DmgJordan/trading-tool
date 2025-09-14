from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HyperliquidConnector:
    """Connector pour l'API Hyperliquid utilisant le SDK officiel"""

    def __init__(self, use_testnet: bool = False):
        self.api_url = constants.TESTNET_API_URL if use_testnet else constants.MAINNET_API_URL
        self.use_testnet = use_testnet

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

            # Test de connexion avec le SDK
            info = Info(self.api_url, skip_ws=True)

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
                exchange = Exchange(info, private_key)

                # Test simple - récupérer l'état de l'utilisateur
                user_state = await asyncio.get_event_loop().run_in_executor(
                    None, info.user_state, exchange.wallet.address
                )

                network = "Testnet" if self.use_testnet else "Mainnet"
                return {
                    "status": "success",
                    "message": f"Connexion Hyperliquid {network} réussie !",
                    "data": {
                        "wallet_address": exchange.wallet.address,
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

    async def get_user_info(self, private_key: str, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère les informations de l'utilisateur

        Args:
            private_key: Clé privée de l'utilisateur
            wallet_address: Adresse du wallet (optionnel, déduite de la clé privée si non fournie)

        Returns:
            Dict avec les informations utilisateur
        """
        try:
            info = Info(self.api_url, skip_ws=True)

            if not wallet_address:
                exchange = Exchange(info, private_key)
                wallet_address = exchange.wallet.address

            user_state = await asyncio.get_event_loop().run_in_executor(
                None, info.user_state, wallet_address
            )

            return {
                "status": "success",
                "data": user_state
            }

        except Exception as e:
            logger.error(f"Erreur récupération info utilisateur: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }