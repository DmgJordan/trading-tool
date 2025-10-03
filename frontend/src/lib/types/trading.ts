// Types pour les recommandations de trading structurées
// Ré-export de TradeRecommendation depuis api/claude.ts pour compatibilité
export type { TradeRecommendation } from './api/claude';

export type TradeDirection = 'long' | 'short';

// Types pour l'exécution de trades Hyperliquid

export interface ExecuteTradeRequest {
  symbol: string;
  direction: TradeDirection;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  take_profit_3: number;
  portfolio_percentage: number;
  use_testnet?: boolean;
}

export interface TradeExecutionResult {
  status: 'success' | 'error' | 'partial';
  message: string;
  main_order_id?: string;
  executed_size?: number;
  executed_price?: number;
  stop_loss_order_id?: string;
  take_profit_orders: string[];
  execution_timestamp: string;
  total_fees?: number;
  errors: string[];
}

export interface PortfolioInfo {
  account_value: number;
  available_balance: number;
  symbol_position?: number;
  max_leverage: number;
}