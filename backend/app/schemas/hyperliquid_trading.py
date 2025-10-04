from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, List, Tuple
from datetime import datetime
from enum import Enum

class HyperliquidOrderSide(str, Enum):
    BUY = "B"
    SELL = "A"

class HyperliquidOrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

class ExecuteTradeRequest(BaseModel):
    """Requête d'exécution de trade sur Hyperliquid"""

    symbol: str = Field(..., description="Symbole à trader (ex: BTC)")
    direction: Literal["long", "short"] = Field(..., description="Direction du trade")
    entry_price: float = Field(..., description="Prix d'entrée")
    stop_loss: float = Field(..., description="Prix de stop-loss")
    take_profit_1: float = Field(..., description="Premier take-profit")
    take_profit_2: float = Field(..., description="Deuxième take-profit")
    take_profit_3: float = Field(..., description="Troisième take-profit")
    portfolio_percentage: float = Field(..., ge=0.1, le=50.0, description="Pourcentage du portefeuille")
    use_testnet: bool = Field(default=False, description="Utiliser le testnet")
    account_address: Optional[str] = Field(None, description="Adresse du wallet principal (trading délégué)")

    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Valide et normalise le symbole"""
        return v.upper().strip()

    @field_validator('entry_price', 'stop_loss', 'take_profit_1', 'take_profit_2', 'take_profit_3')
    @classmethod
    def validate_prices(cls, v):
        """Valide que les prix sont positifs"""
        if v <= 0:
            raise ValueError("Les prix doivent être positifs")
        return v

class TradeExecutionResult(BaseModel):
    """Résultat d'exécution de trade"""

    status: Literal["success", "error", "partial"] = Field(..., description="Statut de l'exécution")
    message: str = Field(..., description="Message de statut")

    # Détails de l'ordre principal
    main_order_id: Optional[str] = Field(None, description="ID de l'ordre principal")
    executed_size: Optional[float] = Field(None, description="Taille exécutée")
    executed_price: Optional[float] = Field(None, description="Prix d'exécution moyen")

    # Ordres de gestion des risques
    stop_loss_order_id: Optional[str] = Field(None, description="ID de l'ordre stop-loss")
    take_profit_orders: list[str] = Field(default=[], description="IDs des ordres take-profit")

    # Métadonnées
    execution_timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp d'exécution")
    total_fees: Optional[float] = Field(None, description="Frais totaux")

    # Erreurs partielles
    errors: list[str] = Field(default=[], description="Erreurs rencontrées")

class HyperliquidTradeRequest(BaseModel):
    """Requête d'ordre Hyperliquid formatée"""

    coin: str = Field(..., description="Symbole de la crypto")
    is_buy: bool = Field(..., description="True pour achat, False pour vente")
    sz: float = Field(..., description="Taille de l'ordre")
    limit_px: float = Field(..., description="Prix limite")
    order_type: dict = Field(default={"limit": {"tif": "Gtc"}}, description="Type d'ordre")
    reduce_only: bool = Field(default=False, description="Réduire seulement")

class PortfolioInfo(BaseModel):
    """Informations du portefeuille pour calculs de position"""

    account_value: float = Field(..., description="Valeur totale du compte")
    available_balance: float = Field(..., description="Balance disponible")
    symbol_position: Optional[float] = Field(None, description="Position actuelle sur le symbole")
    max_leverage: float = Field(default=1.0, description="Levier maximum autorisé")

# Types pour les données portfolio de Hyperliquid
class PortfolioTimeSeriesData(BaseModel):
    """Données de séries temporelles pour le portfolio"""

    accountValueHistory: List[List] = Field(
        default_factory=list,
        description="Historique de valeur du compte [[timestamp, value], ...]"
    )
    pnlHistory: List[List] = Field(
        default_factory=list,
        description="Historique PnL [[timestamp, pnl], ...]"
    )
    vlm: str = Field(default="0.0", description="Volume total")

# Type alias pour la structure complète du portfolio
# Format: [["day", {...}], ["week", {...}], ...]
PortfolioDataEntry = Tuple[
    Literal["day", "week", "month", "allTime", "perpDay", "perpWeek", "perpMonth", "perpAllTime"],
    PortfolioTimeSeriesData
]
PortfolioData = List[PortfolioDataEntry]