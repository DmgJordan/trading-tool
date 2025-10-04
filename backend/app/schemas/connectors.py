from pydantic import BaseModel, Field
from typing import Optional, Literal, Union
from datetime import datetime

class StandardApiKeyTest(BaseModel):
    """Schéma pour tester une clé API standard (Anthropic, OpenAI, CoinGecko, etc.)"""
    api_key: str = Field(..., description="Clé API à tester")
    api_type: Literal["anthropic", "openai", "coingecko"] = Field(default="anthropic", description="Type d'API")

class DexKeyTest(BaseModel):
    """Schéma pour tester une clé DEX (Hyperliquid, etc.)"""
    private_key: str = Field(..., description="Clé privée DEX à tester")
    dex_type: Literal["hyperliquid"] = Field(default="hyperliquid", description="Type de DEX")
    use_testnet: bool = Field(default=False, description="Utiliser le testnet")

class HyperliquidUserInfo(BaseModel):
    """Schéma spécialisé pour les informations utilisateur Hyperliquid"""
    wallet_address: str
    network: Literal["mainnet", "testnet"]
    user_state_available: bool
    account_value: Optional[float] = None
    open_positions: Optional[int] = None

class AnthropicApiInfo(BaseModel):
    """Schéma spécialisé pour les informations API Anthropic"""
    api_version: str
    model_used: str
    available_models: Optional[list] = None

class CoinGeckoApiInfo(BaseModel):
    """Schéma spécialisé pour les informations API CoinGecko"""
    plan_type: str  # demo, startup, pro, etc.
    rate_limit: Optional[int] = None
    monthly_calls_used: Optional[int] = None
    monthly_calls_limit: Optional[int] = None

# Types pour les champs data et validation de ConnectorTestResponse
class ApiValidationInfo(BaseModel):
    """Informations de validation pour les APIs standard"""
    api_type: Literal["anthropic", "coingecko"]
    connector_type: Literal["standard_api"]
    authentication_method: Literal["api_key"]

class DexValidationInfo(BaseModel):
    """Informations de validation pour les DEX"""
    network: Literal["mainnet", "testnet"]
    connector_type: Literal["hyperliquid"]
    sdk_used: bool

class ConnectorTestResponse(BaseModel):
    """Schéma de réponse pour les tests de connexion"""
    status: Literal["success", "error"]
    message: str
    data: Optional[Union[HyperliquidUserInfo, AnthropicApiInfo, CoinGeckoApiInfo]] = None
    validation: Optional[Union[ApiValidationInfo, DexValidationInfo]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class KeyFormatValidation(BaseModel):
    """Schéma pour la validation de format de clé"""
    key: str = Field(..., description="Clé à valider")
    key_type: Literal["api_key", "private_key"] = Field(..., description="Type de clé")
    service_type: str = Field(..., description="Type de service (anthropic, hyperliquid, coingecko, etc.)")

class UserInfoRequest(BaseModel):
    """Schéma pour récupérer les informations utilisateur"""
    service_type: Literal["hyperliquid", "anthropic", "coingecko"]
    use_testnet: bool = Field(default=False, description="Pour Hyperliquid uniquement")