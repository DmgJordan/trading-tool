/**
 * Barrel exports limités pour éviter les cycles de dépendances
 *
 * ⚠️ IMPORTANT : Privilégier les imports directs depuis les sous-dossiers
 * Exemples :
 * - import { User } from '@/lib/types/auth'
 * - import { MAIndicators } from '@/lib/types/api/ohlcv'
 *
 * Ce fichier existe uniquement pour compatibilité legacy.
 * À terme, il sera supprimé au profit d'imports directs.
 */

// Types core (compatibilité legacy)
export type { User, AuthTokens, LoginRequest, RegisterRequest } from './auth';
export type {
  TradingPreferences,
  TradingPreferencesUpdate,
} from './preferences';
export type { ExecuteTradeRequest, TradeExecutionResult } from './trading';
