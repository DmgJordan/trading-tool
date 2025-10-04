import { z } from 'zod';
import {
  currentPriceInfoSchema,
  maIndicatorsSchema,
  volumeIndicatorsSchema,
  higherTFFeaturesSchema,
} from './ohlcv.schemas';

/**
 * Schémas Zod pour l'API Claude
 * Basés sur les schémas Pydantic du backend (backend/app/schemas/claude.py)
 * Source de vérité unique - les types TypeScript sont inférés via z.infer
 */

// MainTFFeaturesLight (sans bougies)
export const mainTFFeaturesLightSchema = z.object({
  ma: maIndicatorsSchema,
  rsi14: z.number(),
  atr14: z.number(),
  volume: volumeIndicatorsSchema,
});

// LowerTFFeaturesLight (sans bougies)
export const lowerTFFeaturesLightSchema = z.object({
  tf: z.string(),
  rsi14: z.number(),
  volume: volumeIndicatorsSchema,
});

// TechnicalDataLight
export const technicalDataLightSchema = z.object({
  symbol: z.string(),
  profile: z.string(),
  tf: z.string(),
  current_price: currentPriceInfoSchema,
  features: mainTFFeaturesLightSchema,
  higher_tf: higherTFFeaturesSchema,
  lower_tf: lowerTFFeaturesLightSchema,
});

// TradeRecommendation
export const tradeRecommendationSchema = z.object({
  entry_price: z.number(),
  direction: z.enum(['long', 'short']),
  stop_loss: z.number(),
  take_profit_1: z.number(),
  take_profit_2: z.number(),
  take_profit_3: z.number(),
  confidence_level: z.number().min(0).max(100),
  risk_reward_ratio: z.number().positive(),
  portfolio_percentage: z.number().min(0.1).max(50.0),
  timeframe: z.string(),
  reasoning: z.string(),
});

// SingleAssetAnalysisRequest
export const singleAssetAnalysisRequestSchema = z.object({
  ticker: z.string(),
  exchange: z.string().default('binance'),
  profile: z.enum(['short', 'medium', 'long']),
  model: z
    .enum([
      'claude-3-5-haiku-20241022',
      'claude-sonnet-4-5-20250929',
      'claude-opus-4-1-20250805',
    ])
    .default('claude-sonnet-4-5-20250929'),
  custom_prompt: z.string().optional(),
});

// SingleAssetAnalysisResponse
export const singleAssetAnalysisResponseSchema = z.object({
  request_id: z.string(),
  timestamp: z.string(),
  model_used: z.string(),
  ticker: z.string(),
  exchange: z.string(),
  profile: z.string(),
  technical_data: technicalDataLightSchema,
  claude_analysis: z.string(),
  trade_recommendations: z.array(tradeRecommendationSchema).optional(),
  tokens_used: z.number().optional(),
  processing_time_ms: z.number().optional(),
  warnings: z.array(z.string()),
});

// Types inférés depuis les schémas Zod (source de vérité unique)
export type MainTFFeaturesLight = z.infer<typeof mainTFFeaturesLightSchema>;
export type LowerTFFeaturesLight = z.infer<typeof lowerTFFeaturesLightSchema>;
export type TechnicalDataLight = z.infer<typeof technicalDataLightSchema>;
export type TradeRecommendation = z.infer<typeof tradeRecommendationSchema>;
export type SingleAssetAnalysisRequest = z.infer<
  typeof singleAssetAnalysisRequestSchema
>;
export type SingleAssetAnalysisResponse = z.infer<
  typeof singleAssetAnalysisResponseSchema
>;
