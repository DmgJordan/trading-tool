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

export interface CCXTTestResponse {
  status: string;
  message: string;
  exchange?: string;
  symbol?: string;
  timeframe?: string;
  count?: number;
  data?: OHLCVCandle[];
  current_price_info?: CurrentPriceInfo;
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