import { z } from 'zod';
import http from '@/services/http/client';
import type {
  TradingPreferences,
  TradingPreferencesUpdate,
  TradingPreferencesDefault,
  PreferencesValidationInfo,
} from '@/lib/types/preferences';

const riskToleranceSchema = z.enum(['LOW', 'MEDIUM', 'HIGH']);
const investmentHorizonSchema = z.enum([
  'SHORT_TERM',
  'MEDIUM_TERM',
  'LONG_TERM',
]);
const tradingStyleSchema = z.enum(['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE']);

const stringArraySchema = z
  .union([z.array(z.string()), z.string(), z.null(), z.undefined()])
  .transform(value => {
    if (Array.isArray(value)) {
      return value.map(item => String(item));
    }
    if (typeof value === 'string') {
      return value
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    }
    return [] as string[];
  });

const tradingPreferencesSchema: z.ZodType<TradingPreferences> = z
  .object({
    id: z.number().optional(),
    user_id: z.number().optional(),
    risk_tolerance: riskToleranceSchema,
    investment_horizon: investmentHorizonSchema,
    trading_style: tradingStyleSchema,
    max_position_size: z.number(),
    stop_loss_percentage: z.number(),
    take_profit_ratio: z.number(),
    preferred_assets: stringArraySchema,
    technical_indicators: stringArraySchema,
    created_at: z.string().optional(),
    updated_at: z.string().optional(),
  })
  .passthrough();

const tradingPreferencesDefaultSchema: z.ZodType<TradingPreferencesDefault> = z
  .object({
    risk_tolerance: riskToleranceSchema,
    investment_horizon: investmentHorizonSchema,
    trading_style: tradingStyleSchema,
    max_position_size: z.number(),
    stop_loss_percentage: z.number(),
    take_profit_ratio: z.number(),
    preferred_assets: stringArraySchema,
    technical_indicators: stringArraySchema,
  })
  .passthrough();

const constraintsSchema = z.object({
  max_position_size: z.object({
    min: z.number(),
    max: z.number(),
    unit: z.string(),
  }),
  stop_loss_percentage: z.object({
    min: z.number(),
    max: z.number(),
    unit: z.string(),
  }),
  take_profit_ratio: z.object({
    min: z.number(),
    max: z.number(),
    unit: z.string(),
  }),
  preferred_assets: z.object({ max_items: z.number() }),
  technical_indicators: z.object({ max_items: z.number() }),
});

const preferencesValidationInfoSchema: z.ZodType<PreferencesValidationInfo> = z
  .object({
    risk_tolerance_options: z.array(riskToleranceSchema),
    investment_horizon_options: z.array(investmentHorizonSchema),
    trading_style_options: z.array(tradingStyleSchema),
    constraints: constraintsSchema,
    supported_technical_indicators: z.array(z.string()),
  })
  .passthrough();

const resetResponseSchema = z.object({
  status: z.string(),
  message: z.string(),
  preferences: tradingPreferencesSchema,
});

export const preferencesApi = {
  getPreferences: async (): Promise<TradingPreferences> => {
    const response = await http.get<unknown>('/users/me/preferences/', {
      auth: true,
    });
    return tradingPreferencesSchema.parse(response);
  },
  updatePreferences: async (
    preferences: TradingPreferencesUpdate
  ): Promise<TradingPreferences> => {
    const response = await http.put<unknown>(
      '/users/me/preferences/',
      preferences,
      { auth: true }
    );
    return tradingPreferencesSchema.parse(response);
  },
  createPreferences: async (
    preferences: Omit<
      TradingPreferences,
      'id' | 'user_id' | 'created_at' | 'updated_at'
    >
  ): Promise<TradingPreferences> => {
    const response = await http.post<unknown>(
      '/users/me/preferences/',
      preferences,
      { auth: true }
    );
    return tradingPreferencesSchema.parse(response);
  },
  resetToDefaults: async () => {
    const response = await http.del<unknown>(
      '/users/me/preferences/',
      undefined,
      { auth: true }
    );
    return resetResponseSchema.parse(response);
  },
  getDefaults: async (): Promise<TradingPreferencesDefault> => {
    const response = await http.get<unknown>('/users/me/preferences/default', {
      auth: true,
    });
    return tradingPreferencesDefaultSchema.parse(response);
  },
  getValidationInfo: async (): Promise<PreferencesValidationInfo> => {
    const response = await http.get<unknown>(
      '/users/me/preferences/validation-info',
      { auth: true }
    );
    return preferencesValidationInfoSchema.parse(response);
  },
  validatePreferences: async (
    preferences: TradingPreferencesUpdate
  ): Promise<{ isValid: boolean; errors?: Record<string, string[]> }> => {
    try {
      await http.post('/users/me/preferences/validate', preferences, {
        auth: true,
      });
      return { isValid: true, errors: {} };
    } catch (error) {
      const detail =
        (
          error as {
            response?: { data?: { detail?: Record<string, string[]> } };
          }
        )?.response?.data?.detail || {};
      return { isValid: false, errors: detail };
    }
  },
};

export default preferencesApi;
