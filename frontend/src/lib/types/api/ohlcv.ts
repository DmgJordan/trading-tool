/**
 * Types pour l'API OHLCV et l'analyse multi-timeframes
 */

export interface ExchangeListResponse {
  status: string;
  exchanges: string[];
  timeframes: string[];
}

export interface ExchangeSymbolsRequest {
  exchange: string;
  limit?: number;
}

export interface ExchangeSymbolsResponse {
  status: string;
  message?: string;
  exchange?: string;
  symbols?: string[];
  total_available?: number;
}

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
  last_20_candles: number[][]; // [timestamp, open, high, low, close, volume]
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
  last_20_candles: number[][]; // [timestamp, open, high, low, close, volume]
}

export interface MultiTimeframeRequest {
  exchange: string;
  symbol: string;
  profile: 'short' | 'medium' | 'long';
}

export interface MultiTimeframeResponse {
  profile: string;
  symbol: string;
  tf: string;
  current_price: CurrentPriceInfo;
  features: MainTFFeatures;
  higher_tf: HigherTFFeatures;
  lower_tf: LowerTFFeatures;
}
