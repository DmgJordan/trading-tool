// Barrel exports pour une API propre
export { default as apiClient } from './client';
export { authApi } from './auth';
export { preferencesApi } from './preferences';
export * from './ai_recommendations';
export { hyperliquidApi } from './hyperliquid';

// Types pour faciliter les imports
export type { AuthTokens, User, LoginRequest, RegisterRequest } from '../types/auth';
export type {
  TradingPreferences,
  TradingPreferencesUpdate,
  TradingPreferencesDefault
} from '../types/preferences';
