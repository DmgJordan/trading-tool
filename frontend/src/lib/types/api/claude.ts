/**
 * Types pour l'API Claude et l'analyse technique
 * Réutilise les types communs depuis ohlcv.ts
 */

import type {
  MAIndicators,
  VolumeIndicators,
  CurrentPriceInfo,
  MainTFFeatures,
  HigherTFFeatures,
  LowerTFFeatures,
} from './ohlcv';

export interface SingleAssetAnalysisRequest {
  ticker: string;
  exchange?: string;
  profile: 'short' | 'medium' | 'long';
  model?:
    | 'claude-3-5-haiku-20241022'
    | 'claude-sonnet-4-5-20250929'
    | 'claude-opus-4-1-20250805';
  custom_prompt?: string;
}

export interface TechnicalDataLight {
  symbol: string;
  profile: string;
  tf: string;
  current_price: CurrentPriceInfo;
  features: MainTFFeatures;
  higher_tf: HigherTFFeatures;
  lower_tf: LowerTFFeatures;
}

export interface TradeRecommendation {
  entry_price: number;
  direction: 'long' | 'short';
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  take_profit_3: number;
  confidence_level: number;
  risk_reward_ratio: number;
  portfolio_percentage: number;
  timeframe: string;
  reasoning: string;
}

export interface SingleAssetAnalysisResponse {
  request_id: string;
  timestamp: string;
  model_used: string;
  ticker: string;
  exchange: string;
  profile: string;
  technical_data: TechnicalDataLight;
  claude_analysis: string;
  trade_recommendations?: TradeRecommendation[];
  tokens_used?: number;
  processing_time_ms?: number;
  warnings: string[];
}

// Ré-exporter les types communs pour faciliter l'import
export type {
  MAIndicators,
  VolumeIndicators,
  CurrentPriceInfo,
  MainTFFeatures,
  HigherTFFeatures,
  LowerTFFeatures,
};
