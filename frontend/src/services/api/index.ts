export { authApi } from './auth.api';
export { preferencesApi } from './preferences.api';
export { claudeApi } from './claude.api';
export { hyperliquidTradingApi } from './hyperliquid.api';
export { ohlcvApi, fetchOHLCV } from './ohlcv.api';

export type { HyperliquidPortfolioResponse } from './hyperliquid.api';
export type { Candle, OHLCVResponse } from './ohlcv.api';

export type {
  AuthTokens,
  User,
  LoginRequest,
  RegisterRequest,
} from '@/lib/types/auth';
export type {
  TradingPreferences,
  TradingPreferencesUpdate,
  TradingPreferencesDefault,
  PreferencesValidationInfo,
} from '@/lib/types/preferences';
export type {
  ExchangeListResponse,
  ExchangeSymbolsRequest,
  ExchangeSymbolsResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
} from '@/lib/types/api/ohlcv';
export type {
  SingleAssetAnalysisRequest,
  SingleAssetAnalysisResponse,
  TradeRecommendation,
} from './schemas/claude.schemas';
export type {
  ExecuteTradeRequest,
  TradeExecutionResult,
} from '@/lib/types/trading';
