// Barrel exports pour une API propre
export { default as apiClient } from './client';
export { authApi } from './auth';
export { preferencesApi } from './preferences';
export { claudeApi } from './claude';
export { hyperliquidTradingApi } from './hyperliquid-trading';
export { ohlcvApi } from './ohlcv';

// Types pour faciliter les imports
export type {
  AuthTokens,
  User,
  LoginRequest,
  RegisterRequest,
} from '../types/auth';
export type {
  TradingPreferences,
  TradingPreferencesUpdate,
  TradingPreferencesDefault,
} from '../types/preferences';
export type {
  ExchangeListResponse,
  ExchangeSymbolsRequest,
  ExchangeSymbolsResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
  MAIndicators,
  VolumeIndicators,
  CurrentPriceInfo,
  MainTFFeatures,
  HigherTFFeatures,
  LowerTFFeatures,
} from '../types/api/ohlcv';
export type {
  SingleAssetAnalysisRequest,
  SingleAssetAnalysisResponse,
  TechnicalDataLight,
  TradeRecommendation,
} from '../types/api/claude';
