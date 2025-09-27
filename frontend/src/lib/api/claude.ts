import apiClient from './client';

export interface SingleAssetAnalysisRequest {
  ticker: string;
  exchange?: string;
  profile: 'short' | 'medium' | 'long';
  model?:
    | 'claude-3-haiku-20240307'
    | 'claude-3-sonnet-20240229'
    | 'claude-3-opus-20240229'
    | 'claude-3-5-sonnet-20241022';
  custom_prompt?: string;
}
export interface SingleAssetAnalysisResponse {
  request_id: string;
  timestamp: string;
  model_used: string;
  ticker: string;
  exchange: string;
  profile: string;
  technical_data: {
    symbol: string;
    profile: string;
    tf: string;
    current_price: any;
    features: any;
    higher_tf: any;
    lower_tf: any;
  };
  claude_analysis: string;
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
    return response.data;
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
      model: request.model || 'claude-3-5-sonnet-20241022',
      custom_prompt: request.custom_prompt,
    });
    return response.data;
  },
};
