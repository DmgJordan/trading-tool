import { z } from 'zod';

// Schémas pour les enums
export const riskToleranceSchema = z.enum(['LOW', 'MEDIUM', 'HIGH'], {
  errorMap: () => ({ message: 'Tolérance au risque invalide' }),
});

export const investmentHorizonSchema = z.enum(
  ['SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM'],
  {
    errorMap: () => ({ message: "Horizon d'investissement invalide" }),
  }
);

export const tradingStyleSchema = z.enum(
  ['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE'],
  {
    errorMap: () => ({ message: 'Style de trading invalide' }),
  }
);

// Validation pour les actifs préférés
export const preferredAssetsSchema = z
  .array(z.string().min(1, 'Le symbole ne peut pas être vide'))
  .max(20, 'Maximum 20 actifs autorisés')
  .default(['BTC', 'ETH'])
  .refine(
    assets => {
      const uniqueAssets = new Set(assets.map(a => a.toUpperCase()));
      return uniqueAssets.size === assets.length;
    },
    {
      message: 'Les actifs doivent être uniques',
    }
  )
  .transform(assets => assets.map(a => a.toUpperCase()));

// Validation pour les indicateurs techniques
export const technicalIndicatorsSchema = z
  .array(z.string().min(1, "L'indicateur ne peut pas être vide"))
  .max(15, 'Maximum 15 indicateurs autorisés')
  .default(['RSI', 'MACD', 'SMA'])
  .refine(
    indicators => {
      const supportedIndicators = [
        'RSI',
        'MACD',
        'SMA',
        'EMA',
        'BB',
        'STOCH',
        'ADX',
        'CCI',
        'ROC',
        'WILLIAMS',
        'ATR',
        'VWAP',
        'OBV',
        'TRIX',
        'CHAIKIN',
      ];
      return indicators.every(indicator =>
        supportedIndicators.includes(indicator.toUpperCase())
      );
    },
    {
      message: 'Un ou plusieurs indicateurs ne sont pas supportés',
    }
  )
  .refine(
    indicators => {
      const uniqueIndicators = new Set(indicators.map(i => i.toUpperCase()));
      return uniqueIndicators.size === indicators.length;
    },
    {
      message: 'Les indicateurs doivent être uniques',
    }
  )
  .transform(indicators => indicators.map(i => i.toUpperCase()));

// Schéma principal des préférences de trading
export const tradingPreferencesSchema = z.object({
  risk_tolerance: riskToleranceSchema,

  investment_horizon: investmentHorizonSchema,

  trading_style: tradingStyleSchema,

  max_position_size: z
    .number({
      required_error: 'La taille maximale de position est requise',
      invalid_type_error: 'La taille doit être un nombre',
    })
    .min(0.1, 'La taille minimale est de 0.1%')
    .max(100, 'La taille maximale est de 100%')
    .refine(val => Number(val.toFixed(1)) === val, {
      message: 'Maximum 1 décimale autorisée',
    }),

  stop_loss_percentage: z
    .number({
      required_error: 'Le pourcentage de stop-loss est requis',
      invalid_type_error: 'Le stop-loss doit être un nombre',
    })
    .min(0.1, 'Le stop-loss minimal est de 0.1%')
    .max(50, 'Le stop-loss maximal est de 50%')
    .refine(val => Number(val.toFixed(1)) === val, {
      message: 'Maximum 1 décimale autorisée',
    }),

  take_profit_ratio: z
    .number({
      required_error: 'Le ratio take-profit est requis',
      invalid_type_error: 'Le ratio doit être un nombre',
    })
    .min(0.1, 'Le ratio minimal est de 0.1x')
    .max(10, 'Le ratio maximal est de 10x')
    .refine(val => Number(val.toFixed(1)) === val, {
      message: 'Maximum 1 décimale autorisée',
    }),

  preferred_assets: preferredAssetsSchema,

  technical_indicators: technicalIndicatorsSchema,
});

// Schéma pour la mise à jour partielle
export const tradingPreferencesUpdateSchema =
  tradingPreferencesSchema.partial();

// Schéma de validation pour le formulaire UI avec transformations
export const tradingPreferencesFormSchema = z
  .object({
    // Profil de trading
    risk_tolerance: riskToleranceSchema,
    investment_horizon: investmentHorizonSchema,
    trading_style: tradingStyleSchema,

    // Gestion des risques - avec validation croisée
    max_position_size: z
      .union([z.string(), z.number()])
      .transform(val => (typeof val === 'string' ? parseFloat(val) : val))
      .pipe(tradingPreferencesSchema.shape.max_position_size),

    stop_loss_percentage: z
      .union([z.string(), z.number()])
      .transform(val => (typeof val === 'string' ? parseFloat(val) : val))
      .pipe(tradingPreferencesSchema.shape.stop_loss_percentage),

    take_profit_ratio: z
      .union([z.string(), z.number()])
      .transform(val => (typeof val === 'string' ? parseFloat(val) : val))
      .pipe(tradingPreferencesSchema.shape.take_profit_ratio),

    // Actifs préférés avec validation personnalisée
    preferred_assets: z
      .union([
        z.string().transform(str =>
          str
            .split(',')
            .map(s => s.trim())
            .filter(Boolean)
        ),
        z.array(z.string()),
      ])
      .pipe(preferredAssetsSchema),

    // Indicateurs techniques
    technical_indicators: z.array(z.string()).pipe(technicalIndicatorsSchema),
  })
  .refine(
    data => {
      // Validation croisée : cohérence entre style de trading et paramètres de risque
      if (data.trading_style === 'CONSERVATIVE') {
        return data.max_position_size <= 20 && data.stop_loss_percentage <= 10;
      }
      if (data.trading_style === 'AGGRESSIVE') {
        return data.max_position_size >= 5 && data.take_profit_ratio >= 1.5;
      }
      return true;
    },
    {
      message:
        'Les paramètres de risque ne correspondent pas au style de trading choisi',
      path: ['trading_style'],
    }
  );

// Types inférés des schémas
export type TradingPreferencesFormData = z.infer<
  typeof tradingPreferencesFormSchema
>;
export type TradingPreferencesData = z.infer<typeof tradingPreferencesSchema>;
export type TradingPreferencesUpdateData = z.infer<
  typeof tradingPreferencesUpdateSchema
>;

// Validation d'un actif individuel pour les inputs en temps réel
export const assetSymbolSchema = z
  .string()
  .min(1, 'Le symbole est requis')
  .max(10, 'Maximum 10 caractères')
  .regex(
    /^[A-Z0-9]+$/,
    'Seules les lettres majuscules et chiffres sont autorisés'
  )
  .transform(val => val.toUpperCase());

// Validation d'un indicateur technique individuel
export const technicalIndicatorSchema = z
  .string()
  .min(1, "L'indicateur est requis")
  .toUpperCase()
  .refine(
    val => {
      const supportedIndicators = [
        'RSI',
        'MACD',
        'SMA',
        'EMA',
        'BB',
        'STOCH',
        'ADX',
        'CCI',
        'ROC',
        'WILLIAMS',
        'ATR',
        'VWAP',
        'OBV',
        'TRIX',
        'CHAIKIN',
      ];
      return supportedIndicators.includes(val);
    },
    {
      message: 'Indicateur technique non supporté',
    }
  );

// Utilitaires de validation
export const validateAssetSymbol = (
  symbol: string
): { isValid: boolean; error?: string } => {
  try {
    assetSymbolSchema.parse(symbol);
    return { isValid: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { isValid: false, error: error.errors[0]?.message };
    }
    return { isValid: false, error: 'Erreur de validation' };
  }
};

export const validateTechnicalIndicator = (
  indicator: string
): { isValid: boolean; error?: string } => {
  try {
    technicalIndicatorSchema.parse(indicator);
    return { isValid: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { isValid: false, error: error.errors[0]?.message };
    }
    return { isValid: false, error: 'Erreur de validation' };
  }
};

// Valeurs par défaut pour le formulaire
export const defaultPreferencesValues: TradingPreferencesFormData = {
  risk_tolerance: 'MEDIUM',
  investment_horizon: 'MEDIUM_TERM',
  trading_style: 'BALANCED',
  max_position_size: 10.0,
  stop_loss_percentage: 5.0,
  take_profit_ratio: 2.0,
  preferred_assets: ['BTC', 'ETH'],
  technical_indicators: ['RSI', 'MACD', 'SMA'],
};
