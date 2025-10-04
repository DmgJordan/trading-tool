import { useQuery } from '@tanstack/react-query';
import { ohlcvApi } from '@/services/api';
import type { OHLCVResponse } from './types';

const ohlcvKey = (symbol: string, timeframe: string) => [
  'trading',
  'ohlcv',
  symbol?.toUpperCase() ?? '',
  timeframe,
];

export const OHLCV_STALE_TIME = 30_000;

export function useOHLCV(symbol: string, timeframe: string) {
  return useQuery<OHLCVResponse>({
    queryKey: ohlcvKey(symbol, timeframe),
    queryFn: () => ohlcvApi.fetchOHLCV(symbol, timeframe),
    enabled: Boolean(symbol && timeframe),
    staleTime: OHLCV_STALE_TIME,
    meta: {
      feature: 'trading',
      description: 'Fetch OHLCV data for Trading Assistant and dashboards',
    },
  });
}
