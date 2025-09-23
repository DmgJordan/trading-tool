import apiClient from './client';

export interface OHLCVCandle {
  timestamp: number;
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CCXTTestRequest {
  exchange: string;
  symbol: string;
  timeframe: string;
  limit?: number;
}

export interface CurrentPriceInfo {
  current_price: number;
  bid?: number;
  ask?: number;
  change_24h_percent?: number;
  volume_24h?: number;
  timestamp?: number;
  datetime?: string;
}

export interface RSIAnalysis {
  value: number | null;
  interpretation: string;
  signal: string;
}

export interface MovingAveragesAnalysis {
  ma20: number | null;
  ma50: number | null;
  ma200: number | null;
  current_price: number | null;
  short_trend: string;
  medium_trend: string;
  long_trend: string;
  overall_signal: string;
  crossover_20_50: string | null;
  crossover_50_200: string | null;
}

export interface VolumeAnalysis {
  current: number;
  avg20: number;
  spike_ratio: number;
  interpretation: string;
  signal: string;
  trend: string;
  trend_strength: number;
  price_change_percent: number;
}

export interface SupportResistanceAnalysis {
  support_levels: number[];
  resistance_levels: number[];
  confidence_scores: number[];
  nearest_support: number | null;
  nearest_resistance: number | null;
  total_levels: number;
}

export interface OverallAnalysis {
  overall_signal: string;
  signal_strength: number;
  active_signals: string[];
  score: number;
  recommendation: string;
}

export interface TechnicalAnalysis {
  rsi: RSIAnalysis;
  moving_averages: MovingAveragesAnalysis;
  volume_analysis: VolumeAnalysis;
  support_resistance: SupportResistanceAnalysis;
  overall_analysis: OverallAnalysis;
  analyzed_at: string;
  data_points: number;
}

export interface CCXTTestResponse {
  status: string;
  message: string;
  exchange?: string;
  symbol?: string;
  timeframe?: string;
  count?: number;
  data?: OHLCVCandle[];
  current_price_info?: CurrentPriceInfo;
  technical_analysis?: TechnicalAnalysis;
}

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

export const ohlcvApi = {
  /**
   * Test la récupération de données OHLCV via CCXT
   */
  testCCXT: async (request: CCXTTestRequest): Promise<CCXTTestResponse> => {
    const response = await apiClient.post('/ohlcv/test', request);
    return response.data;
  },

  /**
   * Récupère la liste des exchanges et timeframes disponibles
   */
  getAvailableExchanges: async (): Promise<ExchangeListResponse> => {
    const response = await apiClient.get('/ohlcv/exchanges');
    return response.data;
  },

  /**
   * Récupère les symboles populaires d'un exchange
   */
  getExchangeSymbols: async (request: ExchangeSymbolsRequest): Promise<ExchangeSymbolsResponse> => {
    const response = await apiClient.post('/ohlcv/symbols', request);
    return response.data;
  }
};