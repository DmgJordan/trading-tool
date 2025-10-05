from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..core import get_db, get_current_user, decrypt_api_key
from ..schemas.connectors import (
    StandardApiKeyTest,
    ConnectorTestResponse,
    KeyFormatValidation,
    UserInfoRequest
)
from ..services.validators.api_validator import ApiValidator
from ..domains.auth.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connectors", tags=["connectors"])

# Initialisation des validators
api_validator = ApiValidator()

@router.post("/test-anthropic", response_model=ConnectorTestResponse)
async def test_anthropic_connection(
    api_test: StandardApiKeyTest,
    current_user: User = Depends(get_current_user)
):
    """Test la connexion à l'API Anthropic"""
    try:
        result = await api_validator.validate_anthropic(api_test.api_key)

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"],
            data=result.get("data"),
            validation=result.get("validation")
        )

    except Exception as e:
        logger.error(f"Erreur test Anthropic: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/test-coingecko", response_model=ConnectorTestResponse)
async def test_coingecko_connection(
    api_test: StandardApiKeyTest,
    current_user: User = Depends(get_current_user)
):
    """Test la connexion à l'API CoinGecko"""
    try:
        result = await api_validator.validate_coingecko(api_test.api_key)

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"],
            data=result.get("data"),
            validation=result.get("validation")
        )

    except Exception as e:
        logger.error(f"Erreur test CoinGecko: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/test-anthropic-stored", response_model=ConnectorTestResponse)
async def test_anthropic_stored_connection(
    current_user: User = Depends(get_current_user)
):
    """Test la connexion à l'API Anthropic avec la clé stockée de l'utilisateur"""
    try:
        if not current_user.anthropic_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé Anthropic configurée. Veuillez d'abord enregistrer votre clé API."
            )

        # Déchiffrer la clé stockée
        api_key = decrypt_api_key(current_user.anthropic_api_key)
        result = await api_validator.validate_anthropic(api_key)

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"],
            data=result.get("data"),
            validation=result.get("validation")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur test Anthropic stocké: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/test-coingecko-stored", response_model=ConnectorTestResponse)
async def test_coingecko_stored_connection(
    current_user: User = Depends(get_current_user)
):
    """Test la connexion à l'API CoinGecko avec la clé stockée de l'utilisateur"""
    try:
        if not current_user.coingecko_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé CoinGecko configurée. Veuillez d'abord enregistrer votre clé API."
            )

        # Déchiffrer la clé stockée
        api_key = decrypt_api_key(current_user.coingecko_api_key)
        result = await api_validator.validate_coingecko(api_key)

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"],
            data=result.get("data"),
            validation=result.get("validation")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur test CoinGecko stocké: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/validate-key-format", response_model=ConnectorTestResponse)
async def validate_key_format(
    validation_request: KeyFormatValidation,
    current_user: User = Depends(get_current_user)
):
    """Valide le format d'une clé sans tester la connexion"""
    try:
        if validation_request.key_type == "api_key":
            result = api_validator.validate_api_key_format(
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
                    "message": f"Type de DEX non supporté: {validation_request.service_type}"
                }
        else:
            raise HTTPException(status_code=400, detail="Type de clé non supporté")

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"]
        )

    except Exception as e:
        logger.error(f"Erreur validation format: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.post("/user-info", response_model=ConnectorTestResponse)
async def get_user_info(
    info_request: UserInfoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les informations utilisateur pour un service donné (test uniquement)"""
    try:
        # Hyperliquid utilise maintenant l'endpoint de production /trading/portfolio
        if info_request.service_type in ["hyperliquid", "hyperliquid_legacy"]:
            raise HTTPException(
                status_code=400,
                detail="Utilisez l'endpoint de production /trading/portfolio pour Hyperliquid"
            )

        if info_request.service_type == "anthropic":
            if not current_user.anthropic_api_key:
                raise HTTPException(
                    status_code=400,
                    detail="Aucune clé Anthropic configurée pour cet utilisateur"
                )

            result = await api_validator.get_anthropic_models(
                current_user.anthropic_api_key
            )

        elif info_request.service_type == "coingecko":
            if not current_user.coingecko_api_key:
                raise HTTPException(
                    status_code=400,
                    detail="Aucune clé CoinGecko configurée pour cet utilisateur"
                )

            api_key = decrypt_api_key(current_user.coingecko_api_key)
            result = await api_validator.get_coingecko_info(api_key)

        else:
            raise HTTPException(status_code=400, detail="Type de service non supporté")

        return ConnectorTestResponse(
            status=result["status"],
            message=result.get("message", "Informations récupérées"),
            data=result.get("data")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération info utilisateur: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/supported-services")
async def get_supported_services():
    """Retourne la liste des services supportés"""
    return {
        "api_services": {
            "anthropic": {
                "type": "standard_api",
                "key_format": "sk-ant-*",
                "description": "API Anthropic Claude"
            },
            "coingecko": {
                "type": "standard_api",
                "key_format": "CG-*",
                "description": "API CoinGecko Pro"
            }
        },
        "dex_services": {
            "hyperliquid": {
                "type": "dex",
                "key_format": "0x* (66 chars)",
                "description": "Hyperliquid DEX",
                "supports_testnet": True
            }
        }
    }
