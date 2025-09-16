from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from ..models.user_preferences import RiskTolerance, InvestmentHorizon, TradingStyle
import json

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
        max_items=20,
        description="Liste des actifs préférés (max 20)"
    )

    technical_indicators: List[str] = Field(
        default=["RSI", "MACD", "SMA"],
        max_items=15,
        description="Liste des indicateurs techniques préférés (max 15)"
    )

    @validator('preferred_assets')
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

    @validator('technical_indicators')
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
    preferred_assets: Optional[List[str]] = Field(None, max_items=20)
    technical_indicators: Optional[List[str]] = Field(None, max_items=15)

    @validator('preferred_assets')
    def validate_preferred_assets_update(cls, v):
        """Valide la liste des actifs préférés lors d'une mise à jour"""
        if v is None:
            return v
        return UserTradingPreferencesBase.__validators__['validate_preferred_assets'](v)

    @validator('technical_indicators')
    def validate_technical_indicators_update(cls, v):
        """Valide la liste des indicateurs techniques lors d'une mise à jour"""
        if v is None:
            return v
        return UserTradingPreferencesBase.__validators__['validate_technical_indicators'](v)

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