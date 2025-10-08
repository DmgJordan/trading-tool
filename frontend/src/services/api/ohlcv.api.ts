import { z } from 'zod';
import http from '@/services/http/client';
import type {
  ExchangeListResponse,
  ExchangeSymbolsRequest,
  ExchangeSymbolsResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
} from '@/lib/types/api/ohlcv';

export type Candle = [number, number, number, number, number, number];

const candleSchema: z.ZodType<Candle> = z.tuple([
  z.number(),
  z.number(),
  z.number(),
  z.number(),
  z.number(),
  z.number(),
]);

const ohlcvResponseSchema = z.object({
  symbol: z.string(),
  tf: z.string(),
  last_200: z.array(candleSchema),
});

export type OHLCVResponse = z.infer<typeof ohlcvResponseSchema>;

const exchangeListSchema = z.object({
  status: z.string(),
  exchanges: z.array(z.string()),
  timeframes: z.array(z.string()),
});

const exchangeSymbolsResponseSchema = z.object({
  status: z.string(),
  message: z.string().optional(),
  exchange: z.string().optional(),
  symbols: z.array(z.string()).optional(),
  total_available: z.number().optional(),
});

const maIndicatorsSchema = z.object({
  ma20: z.number(),
  ma50: z.number(),
  ma200: z.number(),
});

const volumeIndicatorsSchema = z.object({
  current: z.number(),
  avg20: z.number(),
  spike_ratio: z.number(),
});

const currentPriceInfoSchema = z.object({
  current_price: z.number(),
  change_24h_percent: z.number().optional(),
  volume_24h: z.number().optional(),
});

const mainTFFeaturesSchema = z.object({
  ma: maIndicatorsSchema,
  rsi14: z.number(),
  atr14: z.number(),
  volume: volumeIndicatorsSchema,
  last_20_candles: z.array(candleSchema),
});

const higherTFFeaturesSchema = z.object({
  tf: z.string(),
  ma: maIndicatorsSchema,
  rsi14: z.number(),
  atr14: z.number(),
  structure: z.string(),
  nearest_resistance: z.number(),
});

const lowerTFFeaturesSchema = z.object({
  tf: z.string(),
  rsi14: z.number(),
  volume: volumeIndicatorsSchema,
  last_20_candles: z.array(candleSchema),
});

const multiTimeframeResponseSchema = z.object({
  profile: z.string(),
  symbol: z.string(),
  tf: z.string(),
  current_price: currentPriceInfoSchema,
  features: mainTFFeaturesSchema,
  higher_tf: higherTFFeaturesSchema,
  lower_tf: lowerTFFeaturesSchema,
});

export const fetchOHLCV = async (
  symbol: string,
  timeframe: string
): Promise<OHLCVResponse> => {
  const response = await http.get<unknown>(
    // TODO: confirmer l'endpoint exact côté backend
    `/market/ohlcv/${encodeURIComponent(symbol)}/${encodeURIComponent(timeframe)}`,
    { auth: true }
  );

  return ohlcvResponseSchema.parse(response);
};

export const ohlcvApi = {
  fetchOHLCV,
  getAvailableExchanges: async (): Promise<ExchangeListResponse> => {
    const response = await http.get<unknown>('/market/ohlcv/exchanges', {
      auth: true,
    });
    return exchangeListSchema.parse(response);
  },
  getExchangeSymbols: async (
    request: ExchangeSymbolsRequest
  ): Promise<ExchangeSymbolsResponse> => {
    const response = await http.post<unknown>(
      '/market/ohlcv/symbols',
      request,
      {
        auth: true,
      }
    );
    return exchangeSymbolsResponseSchema.parse(response);
  },
  getMultiTimeframeAnalysis: async (
    request: MultiTimeframeRequest
  ): Promise<MultiTimeframeResponse> => {
    const response = await http.post<unknown>(
      '/market/ohlcv/multi-timeframe-analysis',
      request,
      { auth: true }
    );
    return multiTimeframeResponseSchema.parse(response);
  },
};

export default ohlcvApi;
