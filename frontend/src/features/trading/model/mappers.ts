import type { HyperliquidUserInfoData } from './types';

export interface PortfolioSummary {
  accountValue?: number;
  withdrawableBalance?: number;
  totalMarginUsed?: number;
}

export const mapPortfolioSummary = (
  data: HyperliquidUserInfoData | null | undefined
): PortfolioSummary => {
  if (!data?.portfolio_summary) {
    return {};
  }

  const summary = data.portfolio_summary as unknown as Record<string, unknown>;

  return {
    accountValue:
      typeof summary.accountValue === 'number'
        ? summary.accountValue
        : undefined,
    withdrawableBalance:
      typeof summary.withdrawableBalance === 'number'
        ? summary.withdrawableBalance
        : undefined,
    totalMarginUsed:
      typeof summary.totalMarginUsed === 'number'
        ? summary.totalMarginUsed
        : undefined,
  };
};

// TODO: enrichir les mappers avec la structure exacte lorsque l'API Hyperliquid sera figée
