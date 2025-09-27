// Barrel exports pour une API propre
export { default as apiClient } from './client';
export { authApi } from './auth';
export { preferencesApi } from './preferences';
export { claudeApi } from './claude';
export * from './ai_recommendations';
export { hyperliquidApi } from './hyperliquid';
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
  CurrentPriceInfo,
  MAIndicators,
  VolumeIndicators,
  MainTFFeatures,
  HigherTFFeatures,
  LowerTFFeatures,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
} from './ohlcv';
