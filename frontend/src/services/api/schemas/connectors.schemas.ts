import { z } from 'zod';

/**
 * Schémas Zod pour l'API Connectors
 * Basés sur les schémas Pydantic du backend (backend/app/schemas/connectors.py)
 * Source de vérité unique - les types TypeScript sont inférés via z.infer
 */

// HyperliquidUserInfo
export const hyperliquidUserInfoSchema = z.object({
  wallet_address: z.string(),
  network: z.enum(['mainnet', 'testnet']),
  user_state_available: z.boolean(),
  account_value: z.number().optional(),
  open_positions: z.number().optional(),
});

// AnthropicApiInfo
export const anthropicApiInfoSchema = z.object({
  api_version: z.string(),
  model_used: z.string(),
  available_models: z.array(z.string()).optional(),
});

// CoinGeckoApiInfo
export const coinGeckoApiInfoSchema = z.object({
  plan_type: z.string(),
  rate_limit: z.number().optional(),
  monthly_calls_used: z.number().optional(),
  monthly_calls_limit: z.number().optional(),
});

// ApiValidationInfo
export const apiValidationInfoSchema = z.object({
  api_type: z.enum(['anthropic', 'coingecko']),
  connector_type: z.literal('standard_api'),
  authentication_method: z.literal('api_key'),
});

// DexValidationInfo
export const dexValidationInfoSchema = z.object({
  network: z.enum(['mainnet', 'testnet']),
  connector_type: z.literal('hyperliquid'),
  sdk_used: z.boolean(),
});

// ConnectorTestResponse
export const connectorTestResponseSchema = z.object({
  status: z.enum(['success', 'error']),
  message: z.string(),
  data: z
    .union([
      hyperliquidUserInfoSchema,
      anthropicApiInfoSchema,
      coinGeckoApiInfoSchema,
    ])
    .optional(),
  validation: z
    .union([apiValidationInfoSchema, dexValidationInfoSchema])
    .optional(),
  timestamp: z.string(),
});

// StandardApiKeyTest
export const standardApiKeyTestSchema = z.object({
  api_key: z.string(),
  api_type: z.enum(['anthropic', 'openai', 'coingecko']).default('anthropic'),
});

// DexKeyTest
export const dexKeyTestSchema = z.object({
  private_key: z.string(),
  dex_type: z.enum(['hyperliquid']).default('hyperliquid'),
  use_testnet: z.boolean().default(false),
});

// KeyFormatValidation
export const keyFormatValidationSchema = z.object({
  key: z.string(),
  key_type: z.enum(['api_key', 'private_key']),
  service_type: z.string(),
});

// UserInfoRequest
export const userInfoRequestSchema = z.object({
  service_type: z.enum(['hyperliquid', 'anthropic', 'coingecko']),
  use_testnet: z.boolean().default(false),
});

// Types inférés depuis les schémas Zod (source de vérité unique)
export type HyperliquidUserInfo = z.infer<typeof hyperliquidUserInfoSchema>;
export type AnthropicApiInfo = z.infer<typeof anthropicApiInfoSchema>;
export type CoinGeckoApiInfo = z.infer<typeof coinGeckoApiInfoSchema>;
export type ApiValidationInfo = z.infer<typeof apiValidationInfoSchema>;
export type DexValidationInfo = z.infer<typeof dexValidationInfoSchema>;
export type ConnectorTestResponse = z.infer<typeof connectorTestResponseSchema>;
export type StandardApiKeyTest = z.infer<typeof standardApiKeyTestSchema>;
export type DexKeyTest = z.infer<typeof dexKeyTestSchema>;
export type KeyFormatValidation = z.infer<typeof keyFormatValidationSchema>;
export type UserInfoRequest = z.infer<typeof userInfoRequestSchema>;
