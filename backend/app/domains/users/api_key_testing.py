"""
Service de test de clés API pour le domaine users

Migré depuis app/routes/connectors.py
Responsabilité : Tester la validité des clés API sans les sauvegarder
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from ...core import decrypt_api_key
from ...services.validators.api_validator import ApiValidator
from ...domains.auth.models import User
from ...domains.users.models import UserProfile

from .schemas import (
    StandardApiKeyTest,
    DexKeyTest,
    ConnectorTestResponse,
    KeyFormatValidation,
    UserInfoRequest
)

logger = logging.getLogger(__name__)


class ApiKeyTestingService:
    """Service pour tester les clés API"""

    def __init__(self):
        self.api_validator = ApiValidator()

    async def test_standard_api(self, test_data: StandardApiKeyTest) -> ConnectorTestResponse:
        """
        Teste une nouvelle clé API standard (Anthropic, CoinGecko)

        Args:
            test_data: Données de test avec la clé API

        Returns:
            Résultat du test de connexion
        """
        try:
            if test_data.api_type == "anthropic":
                result = await self.api_validator.validate_anthropic(test_data.api_key)
            elif test_data.api_type == "coingecko":
                result = await self.api_validator.validate_coingecko(test_data.api_key)
            else:
                raise ValueError(f"Type d'API non supporté: {test_data.api_type}")

            return ConnectorTestResponse(
                status=result["status"],
                message=result["message"],
                data=result.get("data"),
                validation=result.get("validation")
            )

        except Exception as e:
            logger.error(f"Erreur test {test_data.api_type}: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    async def test_stored_api_key(
        self,
        api_type: str,
        current_user: User,
        db: Session
    ) -> ConnectorTestResponse:
        """
        Teste une clé API stockée de l'utilisateur

        Args:
            api_type: Type d'API à tester (anthropic, coingecko)
            current_user: Utilisateur authentifié
            db: Session de base de données

        Returns:
            Résultat du test de connexion
        """
        try:
            # Récupérer le profil utilisateur
            profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

            if not profile:
                raise HTTPException(
                    status_code=404,
                    detail="Profil utilisateur introuvable"
                )

            # Vérifier la clé selon le type
            if api_type == "anthropic":
                if not profile.anthropic_api_key:
                    raise HTTPException(
                        status_code=400,
                        detail="Aucune clé Anthropic configurée. Veuillez d'abord enregistrer votre clé API."
                    )
                api_key = decrypt_api_key(profile.anthropic_api_key)
                result = await self.api_validator.validate_anthropic(api_key)

            elif api_type == "coingecko":
                if not profile.coingecko_api_key:
                    raise HTTPException(
                        status_code=400,
                        detail="Aucune clé CoinGecko configurée. Veuillez d'abord enregistrer votre clé API."
                    )
                api_key = decrypt_api_key(profile.coingecko_api_key)
                result = await self.api_validator.validate_coingecko(api_key)

            else:
                raise ValueError(f"Type d'API non supporté: {api_type}")

            return ConnectorTestResponse(
                status=result["status"],
                message=result["message"],
                data=result.get("data"),
                validation=result.get("validation")
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur test {api_type} stocké: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    def validate_key_format(self, validation_request: KeyFormatValidation) -> ConnectorTestResponse:
        """
        Valide le format d'une clé sans tester la connexion

        Args:
            validation_request: Requête de validation

        Returns:
            Résultat de la validation de format
        """
        try:
            if validation_request.key_type == "api_key":
                result = self.api_validator.validate_api_key_format(
                    validation_request.key,
                    validation_request.service_type
                )
            elif validation_request.key_type == "private_key":
                # Validation format clé privée Hyperliquid
                if validation_request.service_type.lower() == "hyperliquid":
                    if not validation_request.key.startswith('0x'):
                        result = {
                            "status": "error",
                            "message": "Clé Hyperliquid doit commencer par '0x'"
                        }
                    elif len(validation_request.key) != 66:
                        result = {
                            "status": "error",
                            "message": "Clé Hyperliquid doit faire 66 caractères (0x + 64 caractères hex)"
                        }
                    else:
                        try:
                            int(validation_request.key[2:], 16)
                            result = {
                                "status": "success",
                                "message": "Format de clé Hyperliquid valide"
                            }
                        except ValueError:
                            result = {
                                "status": "error",
                                "message": "Clé Hyperliquid doit contenir uniquement des caractères hexadécimaux"
                            }
                else:
                    result = {
                        "status": "error",
                        "message": f"Service non supporté pour private_key: {validation_request.service_type}"
                    }
            else:
                result = {
                    "status": "error",
                    "message": f"Type de clé non supporté: {validation_request.key_type}"
                }

            return ConnectorTestResponse(
                status=result["status"],
                message=result["message"]
            )

        except Exception as e:
            logger.error(f"Erreur validation format clé: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

    def get_supported_services(self) -> Dict[str, Any]:
        """
        Retourne la liste des services d'API supportés

        Returns:
            Dictionnaire des services supportés
        """
        return {
            "status": "success",
            "services": {
                "standard_api": [
                    {
                        "type": "anthropic",
                        "name": "Anthropic Claude",
                        "auth_method": "api_key",
                        "key_prefix": "sk-ant-",
                        "description": "API Claude pour l'analyse IA"
                    },
                    {
                        "type": "coingecko",
                        "name": "CoinGecko",
                        "auth_method": "api_key",
                        "key_prefix": "CG-",
                        "description": "API CoinGecko pour les données de marché"
                    }
                ],
                "dex": [
                    {
                        "type": "hyperliquid",
                        "name": "Hyperliquid DEX",
                        "auth_method": "private_key",
                        "key_prefix": "0x",
                        "description": "DEX Hyperliquid pour le trading",
                        "testnet_available": True
                    }
                ]
            }
        }
