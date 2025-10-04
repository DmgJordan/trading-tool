import type { MultiSelectOption } from '@/features/preferences/ui/MultiSelect';

// Options pour les cryptomonnaies populaires
export const CRYPTO_OPTIONS: MultiSelectOption[] = [
  {
    value: 'BTC',
    label: 'Bitcoin',
    description: 'La première cryptomonnaie',
    category: 'Major',
    isPopular: true,
  },
  {
    value: 'ETH',
    label: 'Ethereum',
    description: 'Plateforme de contrats intelligents',
    category: 'Major',
    isPopular: true,
  },
  {
    value: 'SOL',
    label: 'Solana',
    description: 'Blockchain haute performance',
    category: 'Layer 1',
    isPopular: true,
  },
  {
    value: 'ADA',
    label: 'Cardano',
    description: 'Blockchain proof-of-stake',
    category: 'Layer 1',
  },
  {
    value: 'DOT',
    label: 'Polkadot',
    description: 'Interopérabilité blockchain',
    category: 'Layer 1',
  },
  {
    value: 'AVAX',
    label: 'Avalanche',
    description: 'Plateforme DeFi rapide',
    category: 'Layer 1',
  },
  {
    value: 'MATIC',
    label: 'Polygon',
    description: "Solution de mise à l'échelle Ethereum",
    category: 'Layer 2',
  },
  {
    value: 'LINK',
    label: 'Chainlink',
    description: 'Oracle décentralisé',
    category: 'Infrastructure',
  },
  {
    value: 'UNI',
    label: 'Uniswap',
    description: 'Exchange décentralisé',
    category: 'DeFi',
  },
  {
    value: 'AAVE',
    label: 'Aave',
    description: 'Protocole de prêt DeFi',
    category: 'DeFi',
  },
];

// Options pour les indicateurs techniques
export const INDICATOR_OPTIONS: MultiSelectOption[] = [
  {
    value: 'RSI',
    label: 'RSI',
    description: 'Relative Strength Index',
    category: 'Momentum',
    isPopular: true,
  },
  {
    value: 'MACD',
    label: 'MACD',
    description: 'Moving Average Convergence Divergence',
    category: 'Momentum',
    isPopular: true,
  },
  {
    value: 'SMA',
    label: 'SMA',
    description: 'Simple Moving Average',
    category: 'Trend',
    isPopular: true,
  },
  {
    value: 'EMA',
    label: 'EMA',
    description: 'Exponential Moving Average',
    category: 'Trend',
  },
  {
    value: 'BB',
    label: 'Bollinger Bands',
    description: 'Bandes de Bollinger',
    category: 'Volatility',
  },
  {
    value: 'STOCH',
    label: 'Stochastic',
    description: 'Oscillateur stochastique',
    category: 'Momentum',
  },
  {
    value: 'ADX',
    label: 'ADX',
    description: 'Average Directional Index',
    category: 'Trend',
  },
  {
    value: 'CCI',
    label: 'CCI',
    description: 'Commodity Channel Index',
    category: 'Momentum',
  },
  {
    value: 'ATR',
    label: 'ATR',
    description: 'Average True Range',
    category: 'Volatility',
  },
  {
    value: 'VWAP',
    label: 'VWAP',
    description: 'Volume Weighted Average Price',
    category: 'Volume',
  },
  {
    value: 'OBV',
    label: 'OBV',
    description: 'On Balance Volume',
    category: 'Volume',
  },
];

// Valeurs par défaut des préférences
export const DEFAULT_PREFERENCES = {
  risk_tolerance: 'MEDIUM' as const,
  investment_horizon: 'MEDIUM_TERM' as const,
  trading_style: 'BALANCED' as const,
  max_position_size: 10.0,
  stop_loss_percentage: 5.0,
  take_profit_ratio: 2.0,
  preferred_assets: ['BTC', 'ETH'],
  technical_indicators: ['RSI', 'MACD', 'SMA'],
};
