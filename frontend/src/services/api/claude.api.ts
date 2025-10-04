import { z } from 'zod';
import http from '@/services/http/client';
import {
  singleAssetAnalysisResponseSchema,
  type SingleAssetAnalysisRequest,
  type SingleAssetAnalysisResponse,
} from './schemas/claude.schemas';

const testConnectionSchema = z.object({
  success: z.boolean(),
  message: z.string(),
});

export const claudeApi = {
  testConnection: async (): Promise<{ success: boolean; message: string }> => {
    const response = await http.post<unknown>(
      '/connectors/test-anthropic-stored',
      undefined,
      { auth: true }
    );
    return testConnectionSchema.parse(response);
  },
  analyzeSingleAsset: async (
    request: SingleAssetAnalysisRequest
  ): Promise<SingleAssetAnalysisResponse> => {
    const response = await http.post<unknown>(
      '/claude/analyze-single-asset',
      {
        ticker: request.ticker,
        exchange: request.exchange ?? 'binance',
        profile: request.profile,
        model: request.model ?? 'claude-sonnet-4-5-20250929',
        custom_prompt: request.custom_prompt,
      },
      { auth: true }
    );
    return singleAssetAnalysisResponseSchema.parse(response);
  },
};

export default claudeApi;
