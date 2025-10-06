"""
Schémas Pydantic pour le domaine users - Profils et préférences
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Literal, Union
from datetime import datetime
import json

from .models import RiskTolerance, InvestmentHorizon, TradingStyle


# ========== Helpers ==========

def mask_api_key(api_key: Optional[str], show_last_chars: int = 4) -> Optional[str]:
    """
    Masque une clé API pour affichage sécurisé

    ✅ OPTIMISATION : Fonction centrale pour masquage cohérent

    Args:
        api_key: Clé API à masquer
        show_last_chars: Nombre de caractères à montrer à la fin

    Returns:
        Clé masquée au format "sk-...abcd" ou None
    """
    if not api_key or len(api_key) <= show_last_chars:
        return None

    # Extraire le préfixe (ex: "sk-", "CG-", "0x")
    prefix_length = 3 if api_key.startswith(("sk-", "CG-")) else 2 if api_key.startswith("0x") else 0

    if prefix_length > 0:
        prefix = api_key[:prefix_length]
        suffix = api_key[-show_last_chars:]
        return f"{prefix}...{suffix}"
    else:
        suffix = api_key[-show_last_chars:]
        return f"***...{suffix}"


# ========== Schémas UserProfile ==========

class UserProfileUpdate(BaseModel):
    """Schéma pour mettre à jour le profil utilisateur"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None


class ApiKeyUpdate(BaseModel):
    """Schéma pour mettre à jour les clés API"""
    hyperliquid_api_key: Optional[str] = None
    hyperliquid_public_address: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None


class UserProfileResponse(BaseModel):
    """
    Schéma de réponse pour le profil utilisateur

    ✅ SÉCURITÉ : Toutes les clés API sont masquées
    Les clés complètes ne sont jamais retournées au client
    """
    id: int
    email: EmailStr
    username: str

    # Clés API masquées
    hyperliquid_api_key: Optional[str] = None
    hyperliquid_public_address: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None

    # Statuts de configuration
    hyperliquid_api_key_status: Optional[str] = None
    anthropic_api_key_status: Optional[str] = None
    coingecko_api_key_status: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_user_and_profile(cls, user, profile=None):
        """
        Construit le schéma à partir d'un User et son UserProfile

        Args:
            user: Instance du modèle User (auth/)
            profile: Instance du modèle UserProfile (users/) - optionnel

        Returns:
            UserProfileResponse avec clés masquées
        """
        # Clés masquées
        hyperliquid_key_masked = None
        anthropic_key_masked = None
        coingecko_key_masked = None

        # Statuts
        hyperliquid_status = None
        anthropic_status = None
        coingecko_status = None

        if profile:
            if profile.hyperliquid_api_key:
                hyperliquid_key_masked = mask_api_key(profile.hyperliquid_api_key)
                hyperliquid_status = "configured"

            if profile.anthropic_api_key:
                anthropic_key_masked = mask_api_key(profile.anthropic_api_key)
                anthropic_status = "configured"

            if profile.coingecko_api_key:
                coingecko_key_masked = mask_api_key(profile.coingecko_api_key)
                coingecko_status = "configured"

        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            hyperliquid_api_key=hyperliquid_key_masked,
            hyperliquid_public_address=profile.hyperliquid_public_address if profile else None,
            anthropic_api_key=anthropic_key_masked,
            coingecko_api_key=coingecko_key_masked,
            hyperliquid_api_key_status=hyperliquid_status,
            anthropic_api_key_status=anthropic_status,
            coingecko_api_key_status=coingecko_status,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


# ========== Schémas UserTradingPreferences (migration) ==========

class UserTradingPreferencesBase(BaseModel):
    """Schéma de base pour les préférences de trading"""
    risk_tolerance: RiskTolerance = Field(
        default=RiskTolerance.MEDIUM,
        description="Tolérance au risque de l'utilisateur"
    )

    investment_horizon: InvestmentHorizon = Field(
        default=InvestmentHorizon.MEDIUM_TERM,
        description="Horizon d'investissement préféré"
    )

    trading_style: TradingStyle = Field(
        default=TradingStyle.BALANCED,
        description="Style de trading de l'utilisateur"
    )

    max_position_size: float = Field(
        default=10.0,
        ge=0.1,
        le=100.0,
        description="Taille maximum d'une position en % du portefeuille (0.1-100%)"
    )

    stop_loss_percentage: float = Field(
        default=5.0,
        ge=0.1,
        le=50.0,
        description="Pourcentage de stop-loss par défaut (0.1-50%)"
    )

    take_profit_ratio: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        description="Ratio risk/reward pour take-profit (0.1-10)"
    )

    preferred_assets: List[str] = Field(
        default=["BTC", "ETH"],
        max_length=20,
        description="Liste des actifs préférés (max 20)"
    )

    technical_indicators: List[str] = Field(
        default=["RSI", "MACD", "SMA"],
        max_length=15,
        description="Liste des indicateurs techniques préférés (max 15)"
    )

    @field_validator('preferred_assets')
    @classmethod
    def validate_preferred_assets(cls, v):
        """Valide la liste des actifs préférés"""
        if not v:
            return ["BTC", "ETH"]

        # Normaliser en majuscules et supprimer les doublons
        normalized = list(set([asset.upper().strip() for asset in v if asset.strip()]))

        if len(normalized) > 20:
            raise ValueError("Maximum 20 actifs préférés autorisés")

        # Validation basique du format des symboles
        for asset in normalized:
            if not asset.isalnum() or len(asset) > 10:
                raise ValueError(f"Format d'actif invalide: {asset}")

        return normalized

    @field_validator('technical_indicators')
    @classmethod
    def validate_technical_indicators(cls, v):
        """Valide la liste des indicateurs techniques"""
        if not v:
            return ["RSI", "MACD", "SMA"]

        # Liste des indicateurs supportés
        supported_indicators = [
            "RSI", "MACD", "SMA", "EMA", "BB", "STOCH", "ADX", "CCI", "ROC",
            "WILLIAMS", "ATR", "VWAP", "OBV", "TRIX", "CHAIKIN"
        ]

        # Normaliser et valider
        normalized = []
        for indicator in v:
            indicator = indicator.upper().strip()
            if indicator in supported_indicators:
                normalized.append(indicator)

        # Supprimer les doublons
        normalized = list(set(normalized))

        if len(normalized) > 15:
            raise ValueError("Maximum 15 indicateurs techniques autorisés")

        return normalized


class UserTradingPreferencesCreate(UserTradingPreferencesBase):
    """Schéma pour créer des préférences de trading"""
    pass


class UserTradingPreferencesUpdate(BaseModel):
    """Schéma pour mettre à jour partiellement les préférences de trading"""
    risk_tolerance: Optional[RiskTolerance] = None
    investment_horizon: Optional[InvestmentHorizon] = None
    trading_style: Optional[TradingStyle] = None
    max_position_size: Optional[float] = Field(None, ge=0.1, le=100.0)
    stop_loss_percentage: Optional[float] = Field(None, ge=0.1, le=50.0)
    take_profit_ratio: Optional[float] = Field(None, ge=0.1, le=10.0)
    preferred_assets: Optional[List[str]] = Field(None, max_length=20)
    technical_indicators: Optional[List[str]] = Field(None, max_length=15)

    @field_validator('preferred_assets')
    @classmethod
    def validate_preferred_assets_update(cls, v):
        """Valide la liste des actifs préférés lors d'une mise à jour"""
        if v is None:
            return v
        return UserTradingPreferencesBase.validate_preferred_assets(v)

    @field_validator('technical_indicators')
    @classmethod
    def validate_technical_indicators_update(cls, v):
        """Valide la liste des indicateurs techniques lors d'une mise à jour"""
        if v is None:
            return v
        return UserTradingPreferencesBase.validate_technical_indicators(v)


class UserTradingPreferencesResponse(UserTradingPreferencesBase):
    """Schéma de réponse pour les préférences de trading"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_db_model(cls, db_preferences):
        """Convertit le modèle DB en schéma de réponse"""
        if not db_preferences:
            # Retourner les valeurs par défaut si pas de préférences
            return cls(
                id=0,
                user_id=0,
                risk_tolerance=RiskTolerance.MEDIUM,
                investment_horizon=InvestmentHorizon.MEDIUM_TERM,
                trading_style=TradingStyle.BALANCED,
                max_position_size=10.0,
                stop_loss_percentage=5.0,
                take_profit_ratio=2.0,
                preferred_assets=["BTC", "ETH"],
                technical_indicators=["RSI", "MACD", "SMA"],
                created_at=datetime.utcnow(),
                updated_at=None
            )

        # Convertir les JSON strings en listes
        preferred_assets = ["BTC", "ETH"]
        technical_indicators = ["RSI", "MACD", "SMA"]

        try:
            if db_preferences.preferred_assets:
                preferred_assets = json.loads(db_preferences.preferred_assets)
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            if db_preferences.technical_indicators:
                technical_indicators = json.loads(db_preferences.technical_indicators)
        except (json.JSONDecodeError, TypeError):
            pass

        return cls(
            id=db_preferences.id,
            user_id=db_preferences.user_id,
            risk_tolerance=db_preferences.risk_tolerance,
            investment_horizon=db_preferences.investment_horizon,
            trading_style=db_preferences.trading_style,
            max_position_size=db_preferences.max_position_size,
            stop_loss_percentage=db_preferences.stop_loss_percentage,
            take_profit_ratio=db_preferences.take_profit_ratio,
            preferred_assets=preferred_assets,
            technical_indicators=technical_indicators,
            created_at=db_preferences.created_at,
            updated_at=db_preferences.updated_at
        )


class UserTradingPreferencesDefault(BaseModel):
    """Schéma pour les valeurs par défaut des préférences"""
    risk_tolerance: RiskTolerance = RiskTolerance.MEDIUM
    investment_horizon: InvestmentHorizon = InvestmentHorizon.MEDIUM_TERM
    trading_style: TradingStyle = TradingStyle.BALANCED
    max_position_size: float = 10.0
    stop_loss_percentage: float = 5.0
    take_profit_ratio: float = 2.0
    preferred_assets: List[str] = ["BTC", "ETH"]
    technical_indicators: List[str] = ["RSI", "MACD", "SMA"]


class PreferencesValidationError(BaseModel):
    """Schéma pour les erreurs de validation des préférences"""
    field: str
    message: str
    received_value: Optional[str] = None


# ═══════════════════════════════════════════════════════════════
# SCHÉMAS POUR TESTS DE CLÉS API
# Migré depuis app/schemas/connectors.py
# ═══════════════════════════════════════════════════════════════

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
