"""Service de trading avec logique métier centralisée"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from .adapters.hyperliquid import HyperliquidAdapter
from .schemas import (
    ExecuteTradeRequest,
    TradeExecutionResult,
    PortfolioInfo,
    PositionInfo,
    OrderInfo,
)
from ..auth.models import User
from ...core.security import decrypt_api_key

logger = logging.getLogger(__name__)


class TradingService:
    """
    Service de trading avec TOUTE la logique métier centralisée

    Responsabilités :
    - Validation complète des trades (cohérence prix, pourcentages, etc.)
    - Risk management (calcul position size, stratégie TP)
    - Orchestration des appels à l'adapter
    - Intégration avec market/ (prix) et users/ (préférences)

    PAS de code dans le router (sauf validation Pydantic + auth)
    """

    # Configuration des limites
    MIN_ORDER_VALUE_USD = 10.0  # Minimum Hyperliquid par ordre
    MAX_POSITION_PERCENTAGE = 50.0  # Maximum autorisé par trade
    SMALL_POSITION_THRESHOLD = 30.0  # Seuil pour TP unique vs multiple
    TP_SPLIT_PERCENTAGES = [0.4, 0.35, 0.25]  # Répartition 40/35/25%
    SAFETY_MARGIN = 0.95  # Garder 5% de marge sur balance disponible

    # Lot sizes par symbole (taille minimale d'ordre en nombre de décimales)
    LOT_SIZES = {
        "BTC": 0.00001,  # 5 décimales
        "ETH": 0.0001,   # 4 décimales
        "SOL": 0.01,     # 2 décimales
        "AVAX": 0.1,     # 1 décimale
        "MATIC": 1.0,    # 0 décimales
    }

    def __init__(self):
        self.hyperliquid_adapter = HyperliquidAdapter()

    # =========================================================================
    # WORKFLOW PRINCIPAL - Exécution de trade
    # =========================================================================

    async def execute_trade(
        self,
        user: User,
        request: ExecuteTradeRequest,
        db: Session
    ) -> TradeExecutionResult:
        """
        Exécute un trade complet avec gestion automatique des risques

        Workflow:
        1. Récupérer et déchiffrer la clé privée Hyperliquid
        2. Valider le trade (cohérence prix, pourcentages, etc.)
        3. Récupérer les informations du portefeuille
        4. Calculer et valider la taille de position
        5. Placer l'ordre d'entrée principal
        6. Placer les ordres Stop-Loss et Take-Profits (TPSL natifs)

        Args:
            user: Utilisateur authentifié
            request: Paramètres du trade
            db: Session de base de données

        Returns:
            TradeExecutionResult avec statut et détails des ordres placés
        """
        try:
            logger.info(
                f"execute_trade: utilisateur {user.id}, "
                f"{request.symbol} {request.direction.upper()} {request.portfolio_percentage}%"
            )

            # 1. Récupérer et déchiffrer la clé privée
            private_key = await self._get_user_private_key(user)

            # 2. Injecter l'adresse publique pour trading délégué si configurée
            if user.hyperliquid_public_address and not request.account_address:
                request.account_address = user.hyperliquid_public_address
                logger.info(f"Mode délégué activé: {user.hyperliquid_public_address[:10]}...")

            # 3. Valider le trade (TOUTE la validation centralisée ici)
            validation_error = self.validate_trade_request(request)
            if validation_error:
                return TradeExecutionResult(status="error", message=validation_error)

            # 4. Récupérer les informations du portefeuille
            portfolio_result = await self.hyperliquid_adapter.get_portfolio_summary(
                private_key,
                request.account_address,
                request.use_testnet
            )

            if portfolio_result["status"] != "success":
                return TradeExecutionResult(
                    status="error",
                    message=f"Erreur récupération portfolio: {portfolio_result.get('message')}"
                )

            portfolio_data = portfolio_result["data"]
            portfolio_info = PortfolioInfo(
                account_value=portfolio_data["account_value"],
                available_balance=portfolio_data["available_balance"],
                symbol_position=self._get_current_position_size(
                    portfolio_data["positions"], request.symbol
                ),
                max_leverage=1.0
            )

            logger.info(f"Portefeuille: ${portfolio_info.account_value:.2f}")

            # 5. Calculer et valider la taille de position
            position_size = await self._calculate_position_size(
                portfolio_info,
                request.entry_price,
                request.portfolio_percentage
            )

            # Arrondir au lot size et valider le minimum $10
            lot_size = self.LOT_SIZES.get(request.symbol, 0.01)
            position_size = round(position_size / lot_size) * lot_size

            validation_error = self._validate_order_size(
                position_size,
                request.entry_price,
                portfolio_info.account_value
            )
            if validation_error:
                return TradeExecutionResult(status="error", message=validation_error)

            logger.info(
                f"Position: {position_size:.6f} {request.symbol} "
                f"(${position_size * request.entry_price:.2f})"
            )

            # 6. Placer l'ordre principal d'entrée
            main_order_result = await self._place_entry_order(
                private_key,
                request.symbol,
                request.direction,
                position_size,
                request.entry_price,
                request.use_testnet,
                request.account_address
            )

            if not main_order_result["success"]:
                return TradeExecutionResult(
                    status="error",
                    message=f"Échec ordre principal: {main_order_result['error']}"
                )

            logger.info(f"Ordre principal placé - ID: {main_order_result['order_id']}")

            # 7. Placer les ordres de gestion des risques (SL + TPs)
            stop_loss_id, take_profit_ids, errors = await self._place_risk_management_orders(
                private_key,
                request,
                position_size
            )

            # 8. Déterminer le statut final
            status = self._determine_final_status(stop_loss_id, take_profit_ids, errors)
            message = f"Trade exécuté: {position_size:.4f} {request.symbol}"
            if errors:
                message += f" ({len(errors)} erreurs)"
                logger.warning(f"Erreurs: {errors}")

            return TradeExecutionResult(
                status=status,
                message=message,
                main_order_id=main_order_result["order_id"],
                executed_size=position_size,
                executed_price=request.entry_price,
                stop_loss_order_id=stop_loss_id,
                take_profit_orders=take_profit_ids,
                execution_timestamp=datetime.now(),
                errors=errors
            )

        except Exception as e:
            logger.error(f"Erreur exécution trade pour utilisateur {user.id}: {e}")
            return TradeExecutionResult(
                status="error",
                message=f"Erreur: {str(e)}"
            )

    # =========================================================================
    # VALIDATION CENTRALISÉE
    # =========================================================================

    def validate_trade_request(self, request: ExecuteTradeRequest) -> Optional[str]:
        """
        Valide TOUTE la cohérence du trade
        Centralise TOUTE la validation métier (pas dans le router)

        Returns:
            Message d'erreur si invalide, None si valide
        """
        # 1. Validation du pourcentage (max 50%)
        if request.portfolio_percentage > self.MAX_POSITION_PERCENTAGE:
            return f"Pourcentage du portefeuille limité à {self.MAX_POSITION_PERCENTAGE}% maximum pour la sécurité"

        # 2. Validation cohérence SL/TP selon direction
        if request.direction == "long":
            # LONG : SL < entry < TP1 < TP2 < TP3
            if request.stop_loss >= request.entry_price:
                return "Pour un long, le stop-loss doit être inférieur au prix d'entrée"

            if request.take_profit_1 <= request.entry_price:
                return "Pour un long, les take-profits doivent être supérieurs au prix d'entrée"

            if not (request.take_profit_1 < request.take_profit_2 < request.take_profit_3):
                return "Pour un long, les take-profits doivent être croissants (TP1 < TP2 < TP3)"

        else:  # short
            # SHORT : SL > entry > TP1 > TP2 > TP3
            if request.stop_loss <= request.entry_price:
                return "Pour un short, le stop-loss doit être supérieur au prix d'entrée"

            if request.take_profit_1 >= request.entry_price:
                return "Pour un short, les take-profits doivent être inférieurs au prix d'entrée"

            if not (request.take_profit_1 > request.take_profit_2 > request.take_profit_3):
                return "Pour un short, les take-profits doivent être décroissants (TP1 > TP2 > TP3)"

        # 3. Validation symbole
        if not request.symbol or len(request.symbol) < 2:
            return "Symbole invalide"

        return None  # Tout est valide

    # =========================================================================
    # RISK MANAGEMENT
    # =========================================================================

    async def _calculate_position_size(
        self,
        portfolio: PortfolioInfo,
        entry_price: float,
        percentage: float
    ) -> float:
        """Calcule la taille de position en fonction du pourcentage du portefeuille"""

        investment_amount = portfolio.account_value * (percentage / 100.0)

        # Utiliser available_balance si > 0, sinon account_value (cas perpétuels)
        max_investable = portfolio.available_balance if portfolio.available_balance > 0 else portfolio.account_value

        if investment_amount > max_investable:
            investment_amount = max_investable * self.SAFETY_MARGIN

        return investment_amount / entry_price

    def _validate_order_size(
        self,
        position_size: float,
        entry_price: float,
        account_value: float
    ) -> Optional[str]:
        """Valide que l'ordre respecte le minimum de $10 USD"""

        order_value_usd = position_size * entry_price

        if order_value_usd >= self.MIN_ORDER_VALUE_USD:
            return None  # Valide

        min_percentage_needed = (self.MIN_ORDER_VALUE_USD / account_value) * 100

        if account_value == 0:
            return "Portefeuille vide. Déposez des fonds ou utilisez le testnet."
        elif min_percentage_needed > self.MAX_POSITION_PERCENTAGE:
            return (
                f"Fonds insuffisants. Minimum: ${self.MIN_ORDER_VALUE_USD:.2f} "
                f"({min_percentage_needed:.1f}% du portefeuille) mais maximum: {self.MAX_POSITION_PERCENTAGE}%."
            )
        else:
            return (
                f"Ordre trop petit (${order_value_usd:.2f}). "
                f"Minimum Hyperliquid: ${self.MIN_ORDER_VALUE_USD:.2f}. "
                f"Augmentez le pourcentage à minimum {min_percentage_needed:.1f}%."
            )

    def _calculate_adaptive_tp_strategy(
        self,
        trade_request: ExecuteTradeRequest,
        position_size: float
    ) -> tuple[List[float], List[Optional[float]]]:
        """
        Calcule une stratégie de Take-Profits adaptative selon la taille de position

        - Position < $30 → 1 seul TP (100% sur TP3, le meilleur prix)
        - Position ≥ $30 → 3 TPs (40/35/25%) si chaque ≥ $10, sinon filtrés

        Returns:
            (tp_prices, tp_sizes) où tp_sizes[i] peut être None si trop petit
        """
        lot_size = self.LOT_SIZES.get(trade_request.symbol, 0.01)
        position_value = position_size * trade_request.entry_price

        # Stratégie pour petite position
        if position_value < self.SMALL_POSITION_THRESHOLD:
            logger.info(f"Petite position (${position_value:.2f}) → TP unique sur meilleur prix")
            return [trade_request.take_profit_3], [position_size]

        # Stratégie standard : 3 TPs avec répartition 40/35/25%
        tp_prices = [
            trade_request.take_profit_1,
            trade_request.take_profit_2,
            trade_request.take_profit_3
        ]

        tp_sizes = []
        for pct in self.TP_SPLIT_PERCENTAGES:
            size = position_size * pct
            size_rounded = round(size / lot_size) * lot_size

            # Valider que chaque TP vaut au moins $10
            if size_rounded * trade_request.entry_price >= self.MIN_ORDER_VALUE_USD:
                tp_sizes.append(size_rounded)
            else:
                logger.warning(f"TP ignoré (${size_rounded * trade_request.entry_price:.2f} < $10)")
                tp_sizes.append(None)

        return tp_prices, tp_sizes

    # =========================================================================
    # PLACEMENT D'ORDRES (via adapter)
    # =========================================================================

    async def _place_entry_order(
        self,
        private_key: str,
        symbol: str,
        direction: str,
        size: float,
        price: float,
        use_testnet: bool,
        account_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Place l'ordre d'entrée principal (limit order)"""

        is_buy = direction == "long"
        order_type = {"limit": {"tif": "Gtc"}}

        return await self.hyperliquid_adapter.place_order(
            private_key=private_key,
            symbol=symbol,
            is_buy=is_buy,
            size=size,
            price=price,
            order_type=order_type,
            reduce_only=False,
            use_testnet=use_testnet,
            account_address=account_address
        )

    async def _place_stop_loss_order(
        self,
        private_key: str,
        symbol: str,
        direction: str,
        size: float,
        stop_price: float,
        use_testnet: bool,
        account_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Place un ordre Stop-Loss (TPSL natif trigger-based)"""

        is_buy = direction == "short"  # Ordre inverse
        order_type = {
            "trigger": {
                "triggerPx": float(stop_price),
                "isMarket": True,
                "tpsl": "sl"
            }
        }

        return await self.hyperliquid_adapter.place_order(
            private_key=private_key,
            symbol=symbol,
            is_buy=is_buy,
            size=size,
            price=stop_price,
            order_type=order_type,
            reduce_only=True,
            use_testnet=use_testnet,
            account_address=account_address
        )

    async def _place_take_profit_order(
        self,
        private_key: str,
        symbol: str,
        direction: str,
        size: float,
        tp_price: float,
        use_testnet: bool,
        account_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Place un ordre Take-Profit (TPSL natif trigger-based)"""

        is_buy = direction == "short"  # Ordre inverse
        order_type = {
            "trigger": {
                "triggerPx": float(tp_price),
                "isMarket": True,
                "tpsl": "tp"
            }
        }

        return await self.hyperliquid_adapter.place_order(
            private_key=private_key,
            symbol=symbol,
            is_buy=is_buy,
            size=size,
            price=tp_price,
            order_type=order_type,
            reduce_only=True,
            use_testnet=use_testnet,
            account_address=account_address
        )

    async def _place_risk_management_orders(
        self,
        private_key: str,
        trade_request: ExecuteTradeRequest,
        position_size: float
    ) -> tuple[Optional[str], List[str], List[str]]:
        """Place les ordres Stop-Loss et Take-Profits avec stratégie adaptative"""

        stop_loss_id = None
        take_profit_ids = []
        errors = []

        # 1. Stop-Loss
        try:
            sl_result = await self._place_stop_loss_order(
                private_key,
                trade_request.symbol,
                trade_request.direction,
                position_size,
                trade_request.stop_loss,
                trade_request.use_testnet,
                trade_request.account_address
            )
            if sl_result["success"]:
                stop_loss_id = sl_result["order_id"]
                logger.info(f"Stop-Loss placé - ID: {stop_loss_id}")
            else:
                errors.append(f"Stop-Loss: {sl_result['error']}")
        except Exception as e:
            errors.append(f"Erreur Stop-Loss: {str(e)}")

        # 2. Take-Profits avec stratégie adaptative
        tp_prices, tp_sizes = self._calculate_adaptive_tp_strategy(
            trade_request,
            position_size
        )

        for i, (tp_price, tp_size) in enumerate(zip(tp_prices, tp_sizes)):
            if tp_size is None:
                continue

            try:
                tp_result = await self._place_take_profit_order(
                    private_key,
                    trade_request.symbol,
                    trade_request.direction,
                    tp_size,
                    tp_price,
                    trade_request.use_testnet,
                    trade_request.account_address
                )
                if tp_result["success"]:
                    tp_id = tp_result["order_id"] or f"TP{i+1}_pending"
                    take_profit_ids.append(tp_id)
                    logger.info(f"TP{i+1} placé @ {tp_price} - ID: {tp_id}")
                else:
                    errors.append(f"TP{i+1}: {tp_result['error']}")
            except Exception as e:
                errors.append(f"Erreur TP{i+1}: {str(e)}")

        return stop_loss_id, take_profit_ids, errors

    # =========================================================================
    # QUERIES - Portfolio et Positions
    # =========================================================================

    async def get_portfolio_info(
        self,
        user: User,
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère les informations du portefeuille Hyperliquid de l'utilisateur

        Returns:
            Dict avec status et data du portfolio
        """
        try:
            private_key = await self._get_user_private_key(user)

            return await self.hyperliquid_adapter.get_user_info(
                private_key,
                user.hyperliquid_public_address,
                use_testnet
            )

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Erreur get_portfolio_info pour utilisateur {user.id}: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    async def get_user_positions(
        self,
        user: User,
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère les positions ouvertes de l'utilisateur

        Returns:
            Dict avec status et liste des positions
        """
        try:
            private_key = await self._get_user_private_key(user)

            result = await self.hyperliquid_adapter.get_positions(
                private_key,
                user.hyperliquid_public_address,
                use_testnet
            )

            # Convertir en schémas Pydantic si succès
            if result["status"] == "success":
                positions = [PositionInfo(**pos) for pos in result["data"]["positions"]]
                return {
                    "status": "success",
                    "data": {
                        "positions": [pos.dict() for pos in positions],
                        "count": len(positions)
                    }
                }

            return result

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Erreur get_user_positions pour utilisateur {user.id}: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    async def get_user_orders(
        self,
        user: User,
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère les ordres ouverts de l'utilisateur

        Returns:
            Dict avec status et liste des ordres
        """
        try:
            private_key = await self._get_user_private_key(user)

            return await self.hyperliquid_adapter.get_open_orders(
                private_key,
                user.hyperliquid_public_address,
                use_testnet
            )

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Erreur get_user_orders pour utilisateur {user.id}: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    async def cancel_order(
        self,
        user: User,
        symbol: str,
        order_id: int,
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Annule un ordre

        Returns:
            Dict avec success et message
        """
        try:
            private_key = await self._get_user_private_key(user)

            return await self.hyperliquid_adapter.cancel_order(
                private_key,
                symbol,
                order_id,
                use_testnet,
                user.hyperliquid_public_address
            )

        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Erreur cancel_order pour utilisateur {user.id}: {e}")
            return {
                "success": False,
                "error": f"Erreur interne: {str(e)}"
            }

    async def test_connection(
        self,
        user: User,
        use_testnet: bool = False
    ) -> Dict[str, Any]:
        """
        Test la connexion Hyperliquid de l'utilisateur

        Returns:
            Dict avec status et message
        """
        try:
            private_key = await self._get_user_private_key(user)

            return await self.hyperliquid_adapter.test_connection(
                private_key,
                use_testnet
            )

        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Erreur test_connection pour utilisateur {user.id}: {e}")
            return {
                "status": "error",
                "message": f"Erreur interne: {str(e)}"
            }

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _get_user_private_key(self, user: User) -> str:
        """
        Récupère et déchiffre la clé privée Hyperliquid de l'utilisateur

        Raises:
            ValueError: Si la clé n'est pas configurée ou invalide
        """
        if not user.hyperliquid_api_key:
            raise ValueError("Aucune clé privée Hyperliquid configurée. Configurez-la dans vos paramètres.")

        try:
            private_key = decrypt_api_key(user.hyperliquid_api_key)

            if not private_key:
                raise ValueError("Clé privée Hyperliquid vide. Veuillez reconfigurer votre clé privée dans les paramètres.")

            return private_key

        except Exception as e:
            logger.error(f"Erreur déchiffrement clé Hyperliquid utilisateur {user.id}: {e}")
            raise ValueError("Erreur lors du déchiffrement de la clé privée Hyperliquid")

    def _get_current_position_size(self, positions: List[Dict], symbol: str) -> float:
        """Extrait la taille de la position actuelle pour un symbole donné"""
        for position in positions:
            if position.get("symbol") == symbol:
                return position.get("size", 0.0)
        return 0.0

    def _determine_final_status(
        self,
        stop_loss_id: Optional[str],
        take_profit_ids: List[str],
        errors: List[str]
    ) -> str:
        """Détermine le statut final du trade"""

        if not errors:
            return "success"
        elif stop_loss_id or take_profit_ids:
            return "partial"
        else:
            return "error"
