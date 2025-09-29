from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.connectors import (
    StandardApiKeyTest,
    DexKeyTest,
    ConnectorTestResponse,
    KeyFormatValidation,
    UserInfoRequest
)
from ..services.validators.api_validator import ApiValidator
from ..services.validators.dex_validator import DexValidator
from ..models.user import User
from ..auth import get_current_user, decrypt_api_key
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connectors", tags=["connectors"])

# Initialisation des validators
api_validator = ApiValidator()
dex_validator = DexValidator()

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

@router.post("/test-hyperliquid", response_model=ConnectorTestResponse)
async def test_hyperliquid_connection(
    dex_test: DexKeyTest,
    current_user: User = Depends(get_current_user)
):
    """Test la connexion à Hyperliquid DEX"""
    try:
        result = await dex_validator.validate_hyperliquid(
            dex_test.private_key,
            dex_test.use_testnet
        )

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"],
            data=result.get("data"),
            validation=result.get("validation")
        )

    except Exception as e:
        logger.error(f"Erreur test Hyperliquid: {e}")
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

@router.post("/test-hyperliquid-stored", response_model=ConnectorTestResponse)
async def test_hyperliquid_stored_connection(
    dex_test: DexKeyTest,  # Réutiliser DexKeyTest qui contient use_testnet
    current_user: User = Depends(get_current_user)
):
    """Test la connexion à Hyperliquid DEX avec la clé stockée de l'utilisateur"""
    try:
        if not current_user.hyperliquid_api_key:
            raise HTTPException(
                status_code=400,
                detail="Aucune clé Hyperliquid configurée. Veuillez d'abord enregistrer votre clé API."
            )

        # Déchiffrer la clé stockée
        private_key = decrypt_api_key(current_user.hyperliquid_api_key)
        result = await dex_validator.validate_hyperliquid(
            private_key,
            dex_test.use_testnet
        )

        return ConnectorTestResponse(
            status=result["status"],
            message=result["message"],
            data=result.get("data"),
            validation=result.get("validation")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur test Hyperliquid stocké: {e}")
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
            result = dex_validator.validate_dex_key_format(
                validation_request.key,
                validation_request.service_type
            )
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
        # Hyperliquid utilise maintenant un endpoint de production dédié
        if info_request.service_type == "hyperliquid":
            raise HTTPException(
                status_code=400,
                detail="Utilisez l'endpoint de production /hyperliquid/portfolio-info pour Hyperliquid"
            )

        if info_request.service_type == "hyperliquid_legacy":
            if not current_user.hyperliquid_api_key:
                raise HTTPException(
                    status_code=400,
                    detail="Aucune clé Hyperliquid configurée pour cet utilisateur"
                )

            if not current_user.hyperliquid_public_address:
                raise HTTPException(
                    status_code=400,
                    detail="Aucune adresse publique Hyperliquid configurée pour cet utilisateur"
                )

            private_key = decrypt_api_key(current_user.hyperliquid_api_key).strip()
            result = await dex_validator.get_hyperliquid_user_info(
                private_key,
                current_user.hyperliquid_public_address,
                info_request.use_testnet
            )

        elif info_request.service_type == "anthropic":
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
