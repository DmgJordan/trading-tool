import { z } from 'zod';

/**
 * Schémas Zod pour l'API OHLCV
 * Basés sur les schémas Pydantic du backend (backend/app/schemas/ohlcv.py)
 * Source de vérité unique - les types TypeScript sont inférés via z.infer
 */

// Type pour une bougie OHLCV : [timestamp, open, high, low, close, volume]
export const candleSchema = z.tuple([
  z.number(), // timestamp
  z.number(), // open
  z.number(), // high
  z.number(), // low
  z.number(), // close
  z.number(), // volume
]);

export const maIndicatorsSchema = z.object({
  ma20: z.number(),
  ma50: z.number(),
  ma200: z.number(),
});

export const volumeIndicatorsSchema = z.object({
  current: z.number(),
  avg20: z.number(),
  spike_ratio: z.number(),
});

export const currentPriceInfoSchema = z.object({
  current_price: z.number(),
  change_24h_percent: z.number().optional(),
  volume_24h: z.number().optional(),
});

export const mainTFFeaturesSchema = z.object({
  ma: maIndicatorsSchema,
  rsi14: z.number(),
  atr14: z.number(),
  volume: volumeIndicatorsSchema,
  last_20_candles: z.array(candleSchema),
});

export const higherTFFeaturesSchema = z.object({
  tf: z.string(),
  ma: maIndicatorsSchema,
  rsi14: z.number(),
  atr14: z.number(),
  structure: z.string(),
  nearest_resistance: z.number(),
});

export const lowerTFFeaturesSchema = z.object({
  tf: z.string(),
  rsi14: z.number(),
  volume: volumeIndicatorsSchema,
  last_20_candles: z.array(candleSchema),
});

export const multiTimeframeResponseSchema = z.object({
  profile: z.string(),
  symbol: z.string(),
  tf: z.string(),
  current_price: currentPriceInfoSchema,
  features: mainTFFeaturesSchema,
  higher_tf: higherTFFeaturesSchema,
  lower_tf: lowerTFFeaturesSchema,
});

export const exchangeListResponseSchema = z.object({
  status: z.string(),
  exchanges: z.array(z.string()),
  timeframes: z.array(z.string()),
});

export const exchangeSymbolsRequestSchema = z.object({
  exchange: z.string(),
  limit: z.number().max(100).optional().default(20),
});

export const exchangeSymbolsResponseSchema = z.object({
  status: z.string(),
  message: z.string().optional(),
  exchange: z.string().optional(),
  symbols: z.array(z.string()).optional(),
  total_available: z.number().optional(),
});

export const multiTimeframeRequestSchema = z.object({
  exchange: z.string(),
  symbol: z.string(),
  profile: z.enum(['short', 'medium', 'long']),
});

// Types inférés depuis les schémas Zod (source de vérité unique)
export type Candle = z.infer<typeof candleSchema>;
export type MAIndicators = z.infer<typeof maIndicatorsSchema>;
export type VolumeIndicators = z.infer<typeof volumeIndicatorsSchema>;
export type CurrentPriceInfo = z.infer<typeof currentPriceInfoSchema>;
export type MainTFFeatures = z.infer<typeof mainTFFeaturesSchema>;
export type HigherTFFeatures = z.infer<typeof higherTFFeaturesSchema>;
export type LowerTFFeatures = z.infer<typeof lowerTFFeaturesSchema>;
export type MultiTimeframeResponse = z.infer<
  typeof multiTimeframeResponseSchema
>;
export type ExchangeListResponse = z.infer<typeof exchangeListResponseSchema>;
export type ExchangeSymbolsRequest = z.infer<
  typeof exchangeSymbolsRequestSchema
>;
export type ExchangeSymbolsResponse = z.infer<
  typeof exchangeSymbolsResponseSchema
>;
export type MultiTimeframeRequest = z.infer<typeof multiTimeframeRequestSchema>;
