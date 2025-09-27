export type RiskTolerance = 'LOW' | 'MEDIUM' | 'HIGH';
export type InvestmentHorizon = 'SHORT_TERM' | 'MEDIUM_TERM' | 'LONG_TERM';
export type TradingStyle = 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE';

export interface TradingPreferences {
  id?: number;
  user_id?: number;
  risk_tolerance: RiskTolerance;
  investment_horizon: InvestmentHorizon;
  trading_style: TradingStyle;
  max_position_size: number; // 0.1-100%
  stop_loss_percentage: number; // 0.1-50%
  take_profit_ratio: number; // 0.1-10
  preferred_assets: string[]; // Max 20 assets
  technical_indicators: string[]; // Max 15 indicators
  created_at?: string;
  updated_at?: string;
}

export interface TradingPreferencesUpdate {
  risk_tolerance?: RiskTolerance;
  investment_horizon?: InvestmentHorizon;
  trading_style?: TradingStyle;
  max_position_size?: number;
  stop_loss_percentage?: number;
  take_profit_ratio?: number;
  preferred_assets?: string[];
  technical_indicators?: string[];
}

export interface TradingPreferencesDefault {
  risk_tolerance: RiskTolerance;
  investment_horizon: InvestmentHorizon;
  trading_style: TradingStyle;
  max_position_size: number;
  stop_loss_percentage: number;
  take_profit_ratio: number;
  preferred_assets: string[];
  technical_indicators: string[];
}

export interface PreferencesValidationInfo {
  risk_tolerance_options: RiskTolerance[];
  investment_horizon_options: InvestmentHorizon[];
  trading_style_options: TradingStyle[];
  constraints: {
    max_position_size: { min: number; max: number; unit: string };
    stop_loss_percentage: { min: number; max: number; unit: string };
    take_profit_ratio: { min: number; max: number; unit: string };
    preferred_assets: { max_items: number };
    technical_indicators: { max_items: number };
  };
  supported_technical_indicators: string[];
}

// États pour l'interface utilisateur
export interface PreferencesState {
  preferences: TradingPreferences | null;
  defaults: TradingPreferencesDefault | null;
  validationInfo: PreferencesValidationInfo | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  lastSaved: string | null;
}

export interface PreferencesActions {
  loadPreferences: () => Promise<void>;
  loadDefaults: () => Promise<void>;
  loadValidationInfo: () => Promise<void>;
  updatePreferences: (preferences: TradingPreferencesUpdate) => Promise<void>;
  resetToDefaults: () => Promise<void>;
  clearError: () => void;
}

// Types pour les options d'interface
export interface SelectOption {
  value: string;
  label: string;
  description?: string;
}

export interface RiskToleranceOption extends SelectOption {
  value: RiskTolerance;
  color: string;
  icon: string;
}

export interface InvestmentHorizonOption extends SelectOption {
  value: InvestmentHorizon;
  duration: string;
}

export interface TradingStyleOption extends SelectOption {
  value: TradingStyle;
  characteristics: string[];
}

// Types pour les composants UI
export interface SliderConfig {
  min: number;
  max: number;
  step: number;
  unit: string;
  formatValue?: (value: number) => string;
}

export interface AssetOption {
  symbol: string;
  name: string;
  category: 'crypto' | 'forex' | 'stocks';
  isPopular: boolean;
}

export interface IndicatorOption {
  code: string;
  name: string;
  description: string;
  category: 'momentum' | 'trend' | 'volatility' | 'volume';
}

// Constantes utiles pour l'interface
export const RISK_TOLERANCE_OPTIONS = [
  {
    value: 'LOW',
    label: 'Prudent',
    description: 'Je préfère la sécurité et minimiser les pertes',
    color: 'text-green-600',
    icon: '🛡️',
  },
  {
    value: 'MEDIUM',
    label: 'Équilibré',
    description: "J'accepte un risque modéré pour un rendement décent",
    color: 'text-blue-600',
    icon: '⚖️',
  },
  {
    value: 'HIGH',
    label: 'Agressif',
    description: 'Je vise des rendements élevés malgré les risques',
    color: 'text-red-600',
    icon: '🚀',
  },
] as const;

export const INVESTMENT_HORIZON_OPTIONS = [
  {
    value: 'SHORT_TERM',
    label: 'Court terme',
    description: 'Quelques jours à quelques semaines',
    duration: '< 1 mois',
  },
  {
    value: 'MEDIUM_TERM',
    label: 'Moyen terme',
    description: 'Quelques mois à une année',
    duration: '1-12 mois',
  },
  {
    value: 'LONG_TERM',
    label: 'Long terme',
    description: "Plus d'une année",
    duration: '> 1 an',
  },
] as const;

export const TRADING_STYLE_OPTIONS = [
  {
    value: 'CONSERVATIVE',
    label: 'Conservateur',
    description: 'Stratégie défensive privilégiant la préservation du capital',
    characteristics: [
      'Positions petites',
      'Stop-loss stricts',
      'Diversification',
    ],
  },
  {
    value: 'BALANCED',
    label: 'Équilibré',
    description: 'Approche mixte entre croissance et sécurité',
    characteristics: [
      'Positions moyennes',
      'Gestion risque/reward',
      'Flexible',
    ],
  },
  {
    value: 'AGGRESSIVE',
    label: 'Agressif',
    description: 'Stratégie offensive visant des gains importants',
    characteristics: [
      'Positions importantes',
      'Leverage possible',
      'Haute volatilité',
    ],
  },
] as const;

export const SLIDER_CONFIGS: Record<string, SliderConfig> = {
  max_position_size: {
    min: 0.1,
    max: 100,
    step: 0.1,
    unit: '%',
    formatValue: (value: number) => `${value.toFixed(1)}%`,
  },
  stop_loss_percentage: {
    min: 0.1,
    max: 50,
    step: 0.1,
    unit: '%',
    formatValue: (value: number) => `${value.toFixed(1)}%`,
  },
  take_profit_ratio: {
    min: 0.1,
    max: 10,
    step: 0.1,
    unit: 'x',
    formatValue: (value: number) => `${value.toFixed(1)}x`,
  },
};
