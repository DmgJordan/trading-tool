from typing import Dict, Any
from ..connectors.hyperliquid_connector import HyperliquidConnector
import logging

logger = logging.getLogger(__name__)

class DexValidator:
    """Service de validation pour les APIs DEX (Decentralized Exchange)"""

    def __init__(self):
        self.hyperliquid_mainnet = HyperliquidConnector(use_testnet=False)
        self.hyperliquid_testnet = HyperliquidConnector(use_testnet=True)

    async def validate_hyperliquid(self, private_key: str, use_testnet: bool = False) -> Dict[str, Any]:
        """
        Valide la connexion à Hyperliquid

        Args:
            private_key: Clé privée de l'utilisateur
            use_testnet: Utiliser le testnet (défaut: False)

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            connector = self.hyperliquid_testnet if use_testnet else self.hyperliquid_mainnet
            result = await connector.test_connection(private_key)

            # Enrichir le résultat avec des informations de validation
            if result["status"] == "success":
                result["validation"] = {
                    "network": "testnet" if use_testnet else "mainnet",
                    "connector_type": "hyperliquid",
                    "sdk_used": True
                }

            return result

        except Exception as e:
            logger.error(f"Erreur validation Hyperliquid: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }

    async def get_hyperliquid_user_info(self, private_key: str, use_testnet: bool = False) -> Dict[str, Any]:
        """
        Récupère les informations détaillées de l'utilisateur Hyperliquid

        Args:
            private_key: Clé privée de l'utilisateur
            use_testnet: Utiliser le testnet (défaut: False)

        Returns:
            Dict avec les informations utilisateur
        """
        try:
            connector = self.hyperliquid_testnet if use_testnet else self.hyperliquid_mainnet
            return await connector.get_user_info(private_key)

        except Exception as e:
            logger.error(f"Erreur récupération info utilisateur: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    def validate_dex_key_format(self, key: str, dex_type: str = "hyperliquid") -> Dict[str, Any]:
        """
        Valide le format d'une clé DEX sans tester la connexion

        Args:
            key: Clé à valider
            dex_type: Type de DEX (hyperliquid, etc.)

        Returns:
            Dict avec le résultat de la validation
        """
        try:
            if dex_type.lower() == "hyperliquid":
                if not key.startswith('0x'):
                    return {
                        "status": "error",
                        "message": "Clé Hyperliquid doit commencer par '0x'"
                    }

                if len(key) != 66:
                    return {
                        "status": "error",
                        "message": "Clé Hyperliquid doit faire 66 caractères (0x + 64 caractères hex)"
                    }

                # Vérifier que c'est du hexadécimal valide
                try:
                    int(key[2:], 16)
                except ValueError:
                    return {
                        "status": "error",
                        "message": "Clé Hyperliquid doit contenir uniquement des caractères hexadécimaux"
                    }

                return {
                    "status": "success",
                    "message": "Format de clé Hyperliquid valide"
                }

            else:
                return {
                    "status": "error",
                    "message": f"Type de DEX non supporté: {dex_type}"
                }

        except Exception as e:
            logger.error(f"Erreur validation format clé: {e}")
            return {
                "status": "error",
                "message": f"Erreur de validation: {str(e)}"
            }