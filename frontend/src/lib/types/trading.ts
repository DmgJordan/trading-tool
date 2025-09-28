// Types pour les recommandations de trading structurées

export type TradeDirection = 'long' | 'short';

export interface TradeRecommendation {
  entry_price: number;
  direction: TradeDirection;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  take_profit_3: number;
  confidence_level: number; // 0-100
  risk_reward_ratio: number;
  portfolio_percentage: number; // 0.1-10%
  timeframe: string;
  reasoning: string;
}

export interface StructuredAnalysisResponse {
  request_id: string;
  timestamp: string;
  model_used: string;
  ticker: string;
  exchange: string;
  profile: string;
  technical_data: any; // Utilise le type existant
  claude_analysis: string;
  trade_recommendations: TradeRecommendation[];
  tokens_used?: number;
  processing_time_ms?: number;
  warnings: string[];
}

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