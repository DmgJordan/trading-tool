import apiClient from './client';

export interface ClaudeAnalysisRequest {
  assets: string[];
  analysis_type?: 'quick' | 'detailed';
  custom_prompt?: string;
  model?: 'claude-3-haiku-20240307' | 'claude-3-sonnet-20240229' | 'claude-3-opus-20240229' | 'claude-3-5-sonnet-20241022';
  include_market_data?: boolean;
  use_user_preferences?: boolean;
}

export interface ClaudeAnalysisResponse {
  request_id: string;
  timestamp: string;
  model_used: string;
  assets_analyzed: string[];
  full_analysis: string;
  recommendations: any[];
  market_summary: string;
  risk_assessment: string;
  market_data: Record<string, any>;
  user_preferences_summary?: Record<string, any>;
  tokens_used?: number;
  processing_time_ms?: number;
  warnings: string[];
  limitations: string[];
}

export const claudeApi = {
  /**
   * Envoyer une demande d'analyse trading à Claude
   */
  analyzeAssets: async (request: ClaudeAnalysisRequest): Promise<ClaudeAnalysisResponse> => {
    const response = await apiClient.post('/claude/analyze-trading', request);
    return response.data;
  },

  /**
   * Obtenir l'historique des analyses Claude
   */
  getAnalysisHistory: async (): Promise<ClaudeAnalysisResponse[]> => {
    const response = await apiClient.get('/claude/analysis-history');
    return response.data;
  },

  /**
   * Tester la connectivité avec l'API Claude
   */
  testConnection: async (): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post('/connectors/test-anthropic-stored');
    return response.data;
  },
};