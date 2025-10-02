import apiClient from './client';

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
// Interfaces basées sur les schémas Pydantic du backend

export interface MAIndicators {
  ma20: number;
  ma50: number;
  ma200: number;
}

export interface VolumeIndicators {
  current: number;
  avg20: number;
  spike_ratio: number;
}

export interface CurrentPriceInfo {
  current_price: number;
  change_24h_percent?: number;
  volume_24h?: number;
}

export interface MainTFFeatures {
  ma: MAIndicators;
  rsi14: number;
  atr14: number;
  volume: VolumeIndicators;
  last_20_candles: number[][];
}

export interface HigherTFFeatures {
  tf: string;
  ma: MAIndicators;
  rsi14: number;
  atr14: number;
  structure: string;
  nearest_resistance: number;
}

export interface LowerTFFeatures {
  tf: string;
  rsi14: number;
  volume: VolumeIndicators;
  last_20_candles: number[][];
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

export interface SingleAssetAnalysisResponse {
  request_id: string;
  timestamp: string;
  model_used: string;
  ticker: string;
  exchange: string;
  profile: string;
  technical_data: TechnicalDataLight;
  claude_analysis: string;
  trade_recommendations?: Array<{
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
  }>;
  tokens_used?: number;
  processing_time_ms?: number;
  warnings: string[];
}

export const claudeApi = {
  /**
   * Tester la connectivité avec l'API Claude
   */
  testConnection: async (): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post('/connectors/test-anthropic-stored');
    return response.data as { success: boolean; message: string };
  },

  /**
   * Analyser un seul actif avec données techniques
   */
  analyzeSingleAsset: async (
    request: SingleAssetAnalysisRequest
  ): Promise<SingleAssetAnalysisResponse> => {
    const response = await apiClient.post('/claude/analyze-single-asset', {
      ticker: request.ticker,
      exchange: request.exchange || 'binance',
      profile: request.profile,
      model: request.model || 'claude-sonnet-4-5-20250929',
      custom_prompt: request.custom_prompt,
    });
    return response.data as SingleAssetAnalysisResponse;
  },
};
