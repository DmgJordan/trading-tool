import apiClient from './client';
import {
  ExecuteTradeRequest,
  TradeExecutionResult,
  PortfolioInfo,
} from '../types/trading';

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
   * Utilise l'endpoint existant /connectors/user-info
   */
  getPortfolioInfo: async (useTestnet = false): Promise<{
    status: string;
    data: any;
  }> => {
    const response = await apiClient.post('/connectors/user-info', {
      service_type: 'hyperliquid',
      use_testnet: useTestnet,
    });
    return response.data as { status: string; data: any };
  },
};