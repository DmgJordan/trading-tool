import aiohttp
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CoinGeckoConnector:
    """Connecteur pour l'API CoinGecko"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.pro_base_url = "https://pro-api.coingecko.com/api/v3"

    async def test_connection(self, api_key: str) -> Dict[str, Any]:
        """
        Teste la connexion à l'API CoinGecko

        Args:
            api_key: Clé API CoinGecko

        Returns:
            Dict avec le résultat du test
        """
        try:
            headers = {"x-cg-pro-api-key": api_key}

            # Tester d'abord l'API Pro
            async with aiohttp.ClientSession() as session:
                # Test avec un endpoint simple qui consomme peu de quota
                async with session.get(
                    f"{self.pro_base_url}/ping",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        plan_info = await self._get_plan_info(session, headers)

                        return {
                            "status": "success",
                            "message": "Connexion CoinGecko API Pro réussie",
                            "data": {
                                "api_type": "coingecko_pro",
                                "ping_response": data,
                                "plan_info": plan_info
                            }
                        }

                    elif response.status == 401:
                        return {
                            "status": "error",
                            "message": "Clé API CoinGecko invalide ou expirée"
                        }

                    elif response.status == 429:
                        return {
                            "status": "error",
                            "message": "Limite de taux API CoinGecko atteinte"
                        }

                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "message": f"Erreur API CoinGecko: {response.status} - {error_text}"
                        }

        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "Timeout lors de la connexion à l'API CoinGecko"
            }

        except Exception as e:
            logger.error(f"Erreur test connexion CoinGecko: {e}")
            return {
                "status": "error",
                "message": f"Erreur de connexion: {str(e)}"
            }

    async def _get_plan_info(self, session: aiohttp.ClientSession, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Récupère les informations du plan API

        Args:
            session: Session aiohttp
            headers: Headers avec la clé API

        Returns:
            Dict avec les informations du plan
        """
        try:
            # CoinGecko n'a pas d'endpoint spécifique pour les infos de plan
            # On utilise un endpoint simple pour tester et examiner les headers de réponse
            async with session.get(
                f"{self.pro_base_url}/simple/price?ids=bitcoin&vs_currencies=usd",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:

                plan_info = {
                    "plan_type": "pro",
                    "rate_limit": None,
                    "monthly_calls_used": None,
                    "monthly_calls_limit": None
                }

                # Examiner les headers pour les informations de limite
                if "x-ratelimit-limit" in response.headers:
                    plan_info["rate_limit"] = int(response.headers["x-ratelimit-limit"])

                if "x-ratelimit-remaining" in response.headers:
                    plan_info["rate_limit_remaining"] = int(response.headers["x-ratelimit-remaining"])

                return plan_info

        except Exception as e:
            logger.warning(f"Impossible de récupérer les infos de plan: {e}")
            return {
                "plan_type": "pro",
                "rate_limit": None,
                "monthly_calls_used": None,
                "monthly_calls_limit": None
            }

    async def get_simple_price(self, api_key: str, ids: str, vs_currencies: str = "usd") -> Dict[str, Any]:
        """
        Récupère le prix simple d'une crypto

        Args:
            api_key: Clé API CoinGecko
            ids: IDs des cryptos (ex: "bitcoin,ethereum")
            vs_currencies: Devises de référence (ex: "usd,eur")

        Returns:
            Dict avec les prix
        """
        try:
            headers = {"x-cg-pro-api-key": api_key}

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.pro_base_url}/simple/price",
                    headers=headers,
                    params={
                        "ids": ids,
                        "vs_currencies": vs_currencies,
                        "include_24hr_change": "true",
                        "include_24hr_vol": "true",
                        "include_market_cap": "true"
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": data
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "error",
                            "message": f"Erreur API: {response.status} - {error_text}"
                        }

        except Exception as e:
            logger.error(f"Erreur récupération prix: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }

    async def get_api_info(self, api_key: str) -> Dict[str, Any]:
        """
        Récupère les informations détaillées de l'API

        Args:
            api_key: Clé API CoinGecko

        Returns:
            Dict avec les informations de l'API
        """
        try:
            headers = {"x-cg-pro-api-key": api_key}

            async with aiohttp.ClientSession() as session:
                # Test avec ping et récupération des headers
                async with session.get(
                    f"{self.pro_base_url}/ping",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:

                    if response.status == 200:
                        plan_info = await self._get_plan_info(session, headers)

                        return {
                            "status": "success",
                            "message": "Informations API récupérées",
                            "data": {
                                "api_type": "coingecko_pro",
                                "plan_info": plan_info,
                                "endpoints_available": [
                                    "simple/price",
                                    "coins/markets",
                                    "coins/{id}/history",
                                    "ping"
                                ]
                            }
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Erreur API: {response.status}"
                        }

        except Exception as e:
            logger.error(f"Erreur récupération info API: {e}")
            return {
                "status": "error",
                "message": f"Erreur: {str(e)}"
            }