"""Service d'exécution de trades sur Hyperliquid avec gestion automatique des risques"""

from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from eth_account import Account
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..schemas.hyperliquid_trading import (
    ExecuteTradeRequest,
    TradeExecutionResult,
    PortfolioInfo,
)

logger = logging.getLogger(__name__)


class HyperliquidTradingService:
    """
    Service d'exécution de trades sur Hyperliquid avec gestion des risques

    Features:
    - Support mainnet/testnet
    - Trading délégué (API key trade pour un wallet principal)
    - Ordres TPSL natifs (trigger-based)
    - Stratégie adaptative de take-profits selon taille de position
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
    }

    async def execute_trade(
        self,
        private_key: str,
        trade_request: ExecuteTradeRequest
    ) -> TradeExecutionResult:
        """
        Exécute un trade complet avec gestion automatique des risques

        Workflow:
        1. Connexion à Hyperliquid (testnet/mainnet)
        2. Validation du portefeuille et calcul de la position
        3. Placement de l'ordre d'entrée principal
        4. Placement des ordres Stop-Loss et Take-Profits (TPSL natifs)

        Args:
            private_key: Clé privée du wallet API
            trade_request: Paramètres du trade (symbole, direction, prix, etc.)

        Returns:
            TradeExecutionResult avec statut et détails des ordres placés
        """
        try:
            logger.info(f"execute_trade: {trade_request.symbol} {trade_request.direction.upper()} {trade_request.portfolio_percentage}%")

            # 1. Initialiser la connexion et récupérer les infos du portefeuille
            exchange, info, query_address = await self._initialize_connection(
                private_key,
                trade_request.use_testnet,
                trade_request.account_address
            )

            portfolio_info = await self._get_portfolio_info(info, query_address, trade_request.symbol)
            logger.info(f"Portefeuille: ${portfolio_info.account_value:.2f}")

            # 2. Calculer et valider la taille de position
            position_size = await self._calculate_position_size(
                portfolio_info,
                trade_request.entry_price,
                trade_request.portfolio_percentage
            )

            # Arrondir au lot size et valider le minimum $10
            lot_size = self.LOT_SIZES.get(trade_request.symbol, 0.01)
            position_size = round(position_size / lot_size) * lot_size

            validation_error = self._validate_order_size(
                position_size,
                trade_request.entry_price,
                portfolio_info.account_value
            )
            if validation_error:
                return TradeExecutionResult(status="error", message=validation_error)

            logger.info(f"Position: {position_size:.6f} {trade_request.symbol} (${position_size * trade_request.entry_price:.2f})")

            # 3. Placer l'ordre principal d'entrée
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

            logger.info(f"Ordre principal placé - ID: {main_order_result['order_id']}")

            # 4. Placer les ordres de gestion des risques (SL + TPs)
            stop_loss_id, take_profit_ids, errors = await self._place_risk_management_orders(
                exchange,
                trade_request,
                position_size
            )

            # 5. Déterminer le statut final
            status = self._determine_final_status(stop_loss_id, take_profit_ids, errors)
            message = f"Trade exécuté: {position_size:.4f} {trade_request.symbol}"
            if errors:
                message += f" ({len(errors)} erreurs)"
                logger.warning(f"Erreurs: {errors}")

            return TradeExecutionResult(
                status=status,
                message=message,
                main_order_id=main_order_result["order_id"],
                executed_size=position_size,
                executed_price=trade_request.entry_price,
                stop_loss_order_id=stop_loss_id,
                take_profit_orders=take_profit_ids,
                execution_timestamp=datetime.now(),
                errors=errors
            )

        except Exception as e:
            logger.error(f"Erreur exécution trade: {type(e).__name__}: {e}")
            return TradeExecutionResult(
                status="error",
                message=f"Erreur: {self._safe_encode_error(e)}"
            )

    async def _initialize_connection(
        self,
        private_key: str,
        use_testnet: bool,
        account_address: Optional[str] = None
    ) -> tuple[Exchange, Info, str]:
        """Initialise la connexion Hyperliquid et crée le wallet"""

        # Sélectionner l'URL API
        base_url = constants.TESTNET_API_URL if use_testnet else constants.MAINNET_API_URL
        logger.info(f"Mode: {'testnet' if use_testnet else 'mainnet'}")

        # Créer le wallet avec gestion des formats 0x
        wallet = self._create_wallet(private_key)
        logger.info(f"Wallet créé: {wallet.address}")

        # Initialiser Exchange et Info
        if account_address:
            logger.info(f"Mode délégué: API {wallet.address[:10]}... → {account_address[:10]}...")
            exchange = Exchange(wallet, base_url=base_url, account_address=account_address)
            query_address = account_address
        else:
            exchange = Exchange(wallet, base_url=base_url)
            query_address = wallet.address

        info = Info(base_url=base_url, skip_ws=True)

        return exchange, info, query_address

    def _create_wallet(self, private_key: str) -> Account:
        """Crée un wallet Ethereum à partir d'une clé privée (avec/sans 0x)"""
        try:
            return Account.from_key(private_key)
        except Exception:
            # Fallback: essayer avec/sans préfixe 0x
            try:
                if private_key.startswith('0x') and len(private_key) == 66:
                    return Account.from_key(private_key[2:])
                elif not private_key.startswith('0x') and len(private_key) == 64:
                    return Account.from_key('0x' + private_key)
            except Exception as e:
                raise ValueError(f"Format clé invalide (attendu: 64 chars hex avec/sans 0x): {e}")
            raise ValueError("Format clé privée invalide")

    async def _get_portfolio_info(
        self,
        info: Info,
        wallet_address: str,
        symbol: str
    ) -> PortfolioInfo:
        """Récupère les informations du portefeuille depuis Hyperliquid"""

        try:
            loop = asyncio.get_event_loop()
            user_state = await loop.run_in_executor(None, info.user_state, wallet_address)
        except Exception as e:
            raise ValueError(f"Erreur récupération portefeuille: {self._safe_encode_error(e)}")

        if not user_state:
            raise ValueError("État du portefeuille inaccessible")

        # Extraire account_value
        margin_summary = user_state.get("marginSummary", {})
        account_value = float(margin_summary.get("accountValue", 0))

        # Extraire available_balance (peut être à différents endroits)
        withdrawables = user_state.get("withdrawable", None)
        if isinstance(withdrawables, str):
            available_balance = float(withdrawables)
        elif isinstance(withdrawables, dict):
            available_balance = float(withdrawables.get("withdrawable", 0))
        else:
            available_balance = float(user_state.get("withdrawable", 0))

        # Récupérer position existante sur le symbole
        current_position = 0.0
        for position in user_state.get("assetPositions", []):
            if position.get("position", {}).get("coin") == symbol:
                current_position = float(position.get("position", {}).get("szi", 0))
                break

        return PortfolioInfo(
            account_value=account_value,
            available_balance=available_balance,
            symbol_position=current_position,
            max_leverage=1.0
        )

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

    async def _place_risk_management_orders(
        self,
        exchange: Exchange,
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
                exchange,
                trade_request.symbol,
                trade_request.direction,
                position_size,
                trade_request.stop_loss
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
                    exchange,
                    trade_request.symbol,
                    trade_request.direction,
                    tp_size,
                    tp_price
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

    async def _place_entry_order(
        self,
        exchange: Exchange,
        symbol: str,
        direction: str,
        size: float,
        price: float
    ) -> Dict[str, Any]:
        """Place l'ordre d'entrée principal (limit order)"""

        is_buy = direction == "long"
        order_type = {"limit": {"tif": "Gtc"}}

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                exchange.order,
                symbol,
                is_buy,
                float(size),
                float(price),
                order_type,
                False  # reduce_only
            )

            return self._parse_order_result(result, "ordre principal")

        except Exception as e:
            logger.error(f"Exception ordre principal: {type(e).__name__}: {e}")
            return {"success": False, "error": self._safe_encode_error(e)}

    async def _place_stop_loss_order(
        self,
        exchange: Exchange,
        symbol: str,
        direction: str,
        size: float,
        stop_price: float
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

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                exchange.order,
                symbol,
                is_buy,
                float(size),
                float(stop_price),
                order_type,
                True  # reduce_only
            )

            return self._parse_order_result(result, "stop-loss")

        except Exception as e:
            logger.error(f"Exception stop-loss: {type(e).__name__}: {e}")
            return {"success": False, "error": self._safe_encode_error(e)}

    async def _place_take_profit_order(
        self,
        exchange: Exchange,
        symbol: str,
        direction: str,
        size: float,
        tp_price: float
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

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                exchange.order,
                symbol,
                is_buy,
                float(size),
                float(tp_price),
                order_type,
                True  # reduce_only
            )

            return self._parse_order_result(result, "take-profit")

        except Exception as e:
            logger.error(f"Exception take-profit: {type(e).__name__}: {e}")
            return {"success": False, "error": self._safe_encode_error(e)}

    def _parse_order_result(self, result: Dict, order_label: str) -> Dict[str, Any]:
        """Parse la réponse de l'API Hyperliquid et extrait l'order ID"""

        if not result or result.get("status") != "ok":
            error = result.get("response", {}).get("error", "Erreur inconnue") if result else "Pas de réponse"
            logger.error(f"Échec {order_label}: {error}")
            return {"success": False, "error": error}

        statuses = result.get("response", {}).get("data", {}).get("statuses", [])

        if not statuses:
            return {"success": False, "error": "Aucun statut retourné"}

        first_status = statuses[0]

        # Vérifier si rejeté
        if "error" in first_status:
            error_msg = first_status["error"]
            logger.error(f"Ordre {order_label} rejeté: {error_msg}")
            return {"success": False, "error": error_msg}

        # Extraire order ID
        order_id = first_status.get("resting", {}).get("oid")
        order_id_str = str(order_id) if order_id is not None else None

        return {"success": True, "order_id": order_id_str}

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

    def _safe_encode_error(self, error: Exception) -> str:
        """Encode un message d'erreur en ASCII pour éviter les problèmes d'encodage"""
        try:
            return str(error).encode('ascii', errors='replace').decode('ascii')
        except:
            return f"Erreur {type(error).__name__} (message non décodable)"