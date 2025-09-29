import apiClient from './client';
import {
  ExecuteTradeRequest,
  TradeExecutionResult,
  PortfolioInfo,
} from '../types/trading';
import { HyperliquidUserInfoData } from '../types/hyperliquid';

export const hyperliquidTradingApi = {
  /**
   * Exécute un trade complet sur Hyperliquid avec gestion des risques
   */
  executeTrade: async (
    tradeRequest: ExecuteTradeRequest
  ): Promise<TradeExecutionResult> => {
    const response = await apiClient.post('/hyperliquid/execute-trade', tradeRequest);
    return response.data as TradeExecutionResult;
  },

  /**
   * Récupère les informations du portefeuille Hyperliquid
   * Endpoint de production
   */
  getPortfolioInfo: async (useTestnet = false): Promise<{
    status: string;
    data: HyperliquidUserInfoData;
  }> => {
    const response = await apiClient.get('/hyperliquid/portfolio-info', {
      params: { use_testnet: useTestnet }
    });
    return response.data;
  },
};