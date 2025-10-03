import apiClient from './client';
import type {
  SingleAssetAnalysisRequest,
  SingleAssetAnalysisResponse,
} from '../types/api/claude';

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
