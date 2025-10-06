import { z } from 'zod';
import http from '@/services/http/client';
import type {
  ExecuteTradeRequest,
  TradeExecutionResult,
} from '@/lib/types/trading';

const tradeExecutionResultSchema: z.ZodType<TradeExecutionResult> = z.object({
  status: z.enum(['success', 'error', 'partial']),
  message: z.string(),
  main_order_id: z.string().optional(),
  executed_size: z.number().optional(),
  executed_price: z.number().optional(),
  stop_loss_order_id: z.string().optional(),
  take_profit_orders: z.array(z.string()),
  execution_timestamp: z.string(),
  total_fees: z.number().optional(),
  errors: z.array(z.string()),
});

// Schéma pour les données de séries temporelles du portfolio
const portfolioTimeSeriesDataSchema = z.object({
  accountValueHistory: z.array(z.tuple([z.number(), z.string()])),
  pnlHistory: z.array(z.tuple([z.number(), z.string()])),
  vlm: z.string(),
});

// Schéma pour une entrée de portfolio [period, data]
const portfolioEntrySchema = z.tuple([
  z.enum(['day', 'week', 'month', 'allTime', 'perpDay', 'perpWeek', 'perpMonth', 'perpAllTime']),
  portfolioTimeSeriesDataSchema,
]);

const hyperliquidUserInfoSchema = z
  .object({
    wallet_address: z.string(),
    network: z.enum(['mainnet', 'testnet']),
    retrieved_at: z.string(),
    portfolio_summary: z.object({}).passthrough(),
    user_state: z.object({}).passthrough().nullable(),
    spot_user_state: z.object({}).passthrough().nullable(),
    portfolio: z.array(portfolioEntrySchema).nullable(),
    fills: z.array(z.object({}).passthrough()),
    open_orders: z.array(z.object({}).passthrough()),
    frontend_open_orders: z
      .record(z.string(), z.unknown())
      .nullable()
      .optional(),
  })
  .passthrough();

const hyperliquidPortfolioResponseSchema = z.object({
  status: z.string(),
  message: z.string().optional(),
  data: hyperliquidUserInfoSchema,
});

/**
 * Type inféré depuis le schéma Zod
 * TODO: Migrer vers types TypeScript manuels qui correspondent mieux au backend
 */
export type HyperliquidPortfolioResponse = z.infer<
  typeof hyperliquidPortfolioResponseSchema
>;

export const hyperliquidTradingApi = {
  executeTrade: async (
    tradeRequest: ExecuteTradeRequest
  ): Promise<TradeExecutionResult> => {
    const response = await http.post<unknown>(
      '/trading/orders',
      tradeRequest,
      { auth: true }
    );
    return tradeExecutionResultSchema.parse(response);
  },
  getPortfolioInfo: async (
    useTestnet: boolean = false
  ): Promise<HyperliquidPortfolioResponse> => {
    const response = await http.get<unknown>(
      `/trading/portfolio?use_testnet=${useTestnet}`,
      { auth: true }
    );
    return hyperliquidPortfolioResponseSchema.parse(response);
  },
};

export default hyperliquidTradingApi;
