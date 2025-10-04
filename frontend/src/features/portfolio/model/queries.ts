import { useQuery } from '@tanstack/react-query';
import { hyperliquidTradingApi } from '@/features/trading/api/trading.api';
import type { HyperliquidPortfolioResponse } from '@/features/trading/api/trading.api';

const portfolioKey = (useTestnet: boolean) => ['portfolio', { useTestnet }];

export const usePortfolioQuery = (useTestnet: boolean = false) =>
  useQuery<HyperliquidPortfolioResponse>({
    queryKey: portfolioKey(useTestnet),
    queryFn: () => hyperliquidTradingApi.getPortfolioInfo(useTestnet),
    staleTime: 30_000,
  });
