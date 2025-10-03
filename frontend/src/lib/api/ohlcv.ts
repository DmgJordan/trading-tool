import apiClient from './client';
import type {
  ExchangeListResponse,
  ExchangeSymbolsRequest,
  ExchangeSymbolsResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
} from '../types/api/ohlcv';

export const ohlcvApi = {
  /**
   * Récupère la liste des exchanges et timeframes disponibles
   */
  getAvailableExchanges: async (): Promise<ExchangeListResponse> => {
    const response = await apiClient.get('/ohlcv/exchanges');
    return response.data as ExchangeListResponse;
  },

  /**
   * Récupère les symboles populaires d'un exchange
   */
  getExchangeSymbols: async (
    request: ExchangeSymbolsRequest
  ): Promise<ExchangeSymbolsResponse> => {
    const response = await apiClient.post('/ohlcv/symbols', request);
    return response.data as ExchangeSymbolsResponse;
  },

  /**
   * Analyse multi-timeframes pour un symbole selon le profil de trading
   */
  getMultiTimeframeAnalysis: async (
    request: MultiTimeframeRequest
  ): Promise<MultiTimeframeResponse> => {
    const response = await apiClient.post(
      '/ohlcv/multi-timeframe-analysis',
      request
    );
    return response.data as MultiTimeframeResponse;
  },
};
