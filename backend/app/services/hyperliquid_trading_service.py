from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from eth_account import Account
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
import json

from ..schemas.hyperliquid_trading import (
    ExecuteTradeRequest,
    TradeExecutionResult,
    HyperliquidTradeRequest,
    PortfolioInfo,
    HyperliquidOrderSide,
    HyperliquidOrderType
)

logger = logging.getLogger(__name__)

class HyperliquidTradingService:
    """Service pour l'exécution de trades sur Hyperliquid"""

    def __init__(self):
        self.min_order_size = 0.01  # Taille minimale d'ordre
        self.max_position_percentage = 10.0  # Maximum 10% du portefeuille par trade

    async def execute_trade(
        self,
        private_key: str,
        trade_request: ExecuteTradeRequest
    ) -> TradeExecutionResult:
        """
        Exécute un trade complet avec gestion des risques

        Args:
            private_key: Clé privée de l'utilisateur
            trade_request: Paramètres du trade

        Returns:
            Résultat de l'exécution avec détails des ordres
        """
        try:
            # 1. Initialiser la connexion
            wallet = Account.from_key(private_key)
            exchange = Exchange(wallet, base_url=None, testnet=trade_request.use_testnet)
            info = Info(skip_ws=True, testnet=trade_request.use_testnet)

            # 2. Récupérer les informations du portefeuille
            portfolio_info = await self._get_portfolio_info(info, wallet.address, trade_request.symbol)

            # 3. Calculer la taille de position
            position_size = await self._calculate_position_size(
                portfolio_info,
                trade_request.entry_price,
                trade_request.portfolio_percentage
            )

            if position_size < self.min_order_size:
                return TradeExecutionResult(
                    status="error",
                    message=f"Taille de position calculée ({position_size:.4f}) inférieure au minimum ({self.min_order_size})"
                )

            # 4. Placer l'ordre principal d'entrée
            main_order_result = await self._place_entry_order(
                exchange,
                trade_request.symbol,
                trade_request.direction,
                position_size,
                trade_request.entry_price
            )

            if not main_order_result["success"]:
                return TradeExecutionResult(
                    status="error",
                    message=f"Échec ordre principal: {main_order_result['error']}"
                )

            # 5. Placer les ordres de gestion des risques
            stop_loss_id = None
            take_profit_ids = []
            errors = []

            # Stop-loss
            try:
                stop_loss_result = await self._place_stop_loss_order(
                    exchange,
                    trade_request.symbol,
                    trade_request.direction,
                    position_size,
                    trade_request.stop_loss
                )
                if stop_loss_result["success"]:
                    stop_loss_id = stop_loss_result.get("order_id")
                else:
                    errors.append(f"Stop-loss: {stop_loss_result['error']}")
            except Exception as e:
                errors.append(f"Erreur stop-loss: {str(e)}")

            # Take-profits (ordres échelonnés)
            tp_prices = [
                trade_request.take_profit_1,
                trade_request.take_profit_2,
                trade_request.take_profit_3
            ]
            tp_sizes = [position_size * 0.4, position_size * 0.35, position_size * 0.25]  # Répartition 40/35/25%

            for i, (tp_price, tp_size) in enumerate(zip(tp_prices, tp_sizes)):
                try:
                    tp_result = await self._place_take_profit_order(
                        exchange,
                        trade_request.symbol,
                        trade_request.direction,
                        tp_size,
                        tp_price
                    )
                    if tp_result["success"]:
                        take_profit_ids.append(tp_result.get("order_id"))
                    else:
                        errors.append(f"TP{i+1}: {tp_result['error']}")
                except Exception as e:
                    errors.append(f"Erreur TP{i+1}: {str(e)}")

            # 6. Déterminer le statut final
            status = "success"
            if errors:
                status = "partial" if (stop_loss_id or take_profit_ids) else "error"

            message = f"Trade exécuté: {position_size:.4f} {trade_request.symbol}"
            if errors:
                message += f" (avec erreurs: {len(errors)})"

            return TradeExecutionResult(
                status=status,
                message=message,
                main_order_id=main_order_result.get("order_id"),
                executed_size=position_size,
                executed_price=trade_request.entry_price,
                stop_loss_order_id=stop_loss_id,
                take_profit_orders=take_profit_ids,
                execution_timestamp=datetime.now(),
                errors=errors
            )

        except Exception as e:
            logger.error(f"Erreur exécution trade: {e}")
            return TradeExecutionResult(
                status="error",
                message=f"Erreur exécution: {str(e)}"
            )

    async def _get_portfolio_info(
        self,
        info: Info,
        wallet_address: str,
        symbol: str
    ) -> PortfolioInfo:
        """Récupère les informations du portefeuille"""

        loop = asyncio.get_event_loop()

        # Récupérer l'état utilisateur
        user_state = await loop.run_in_executor(None, info.user_state, wallet_address)

        if not user_state:
            raise ValueError("Impossible de récupérer l'état du portefeuille")

        # Extraire les informations financières
        margin_summary = user_state.get("marginSummary", {})
        withdrawables = user_state.get("withdrawables", {})

        account_value = float(margin_summary.get("accountValue", 0))
        available_balance = float(withdrawables.get("withdrawable", 0))

        # Vérifier position existante sur le symbole
        perp_positions = user_state.get("assetPositions", [])
        current_position = 0.0

        for position in perp_positions:
            if position.get("position", {}).get("coin") == symbol:
                current_position = float(position.get("position", {}).get("szi", 0))
                break

        return PortfolioInfo(
            account_value=account_value,
            available_balance=available_balance,
            symbol_position=current_position,
            max_leverage=1.0  # Trading spot par défaut
        )

    async def _calculate_position_size(
        self,
        portfolio: PortfolioInfo,
        entry_price: float,
        percentage: float
    ) -> float:
        """Calcule la taille de position en fonction du pourcentage du portefeuille"""

        # Montant à investir
        investment_amount = portfolio.account_value * (percentage / 100.0)

        # Vérifier la balance disponible
        if investment_amount > portfolio.available_balance:
            investment_amount = portfolio.available_balance * 0.95  # Garder 5% de marge

        # Calculer la taille en tokens
        position_size = investment_amount / entry_price

        return position_size

    async def _place_entry_order(
        self,
        exchange: Exchange,
        symbol: str,
        direction: str,
        size: float,
        price: float
    ) -> Dict[str, Any]:
        """Place l'ordre d'entrée principal"""

        try:
            is_buy = direction == "long"

            order_request = {
                "coin": symbol,
                "is_buy": is_buy,
                "sz": size,
                "limit_px": price,
                "order_type": {"limit": {"tif": "Gtc"}},  # Good Till Cancel
                "reduce_only": False
            }

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, exchange.order, order_request)

            if result and result.get("status") == "ok":
                return {
                    "success": True,
                    "order_id": result.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", "Erreur inconnue")
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _place_stop_loss_order(
        self,
        exchange: Exchange,
        symbol: str,
        direction: str,
        size: float,
        stop_price: float
    ) -> Dict[str, Any]:
        """Place un ordre stop-loss"""

        try:
            # Stop-loss = ordre inverse de la position
            is_buy = direction == "short"  # Si long, stop en vente et vice versa

            order_request = {
                "coin": symbol,
                "is_buy": is_buy,
                "sz": size,
                "limit_px": stop_price,
                "order_type": {"trigger": {"trigger_px": stop_price, "is_market": True, "tpsl": "sl"}},
                "reduce_only": True
            }

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, exchange.order, order_request)

            if result and result.get("status") == "ok":
                return {
                    "success": True,
                    "order_id": result.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", "Erreur stop-loss")
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _place_take_profit_order(
        self,
        exchange: Exchange,
        symbol: str,
        direction: str,
        size: float,
        tp_price: float
    ) -> Dict[str, Any]:
        """Place un ordre take-profit"""

        try:
            # Take-profit = ordre inverse de la position
            is_buy = direction == "short"  # Si long, TP en vente et vice versa

            order_request = {
                "coin": symbol,
                "is_buy": is_buy,
                "sz": size,
                "limit_px": tp_price,
                "order_type": {"limit": {"tif": "Gtc"}},
                "reduce_only": True
            }

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, exchange.order, order_request)

            if result and result.get("status") == "ok":
                return {
                    "success": True,
                    "order_id": result.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", "Erreur take-profit")
                }

        except Exception as e:
            return {"success": False, "error": str(e)}