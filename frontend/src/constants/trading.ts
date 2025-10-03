/**
 * Constantes pour le trading
 * Symboles, exchanges, profils et configurations
 */

import type { TradingProfile } from '../utils/ui';

// Symboles de trading disponibles
export const TRADING_SYMBOLS = [
  'BTC/USDT',
  'ETH/USDT',
  'SOL/USDT',
  'ADA/USDT',
  'DOT/USDT',
  'AVAX/USDT',
  'MATIC/USDT',
  'LINK/USDT',
  'UNI/USDT',
  'AAVE/USDT',
  'ATOM/USDT',
  'FTM/USDT',
  'NEAR/USDT',
  'ALGO/USDT',
  'XRP/USDT',
] as const;

// Exchanges disponibles
export const EXCHANGES = [
  'binance',
  'coinbase',
  'kraken',
  'bybit',
  'okx',
  'huobi',
] as const;

// Configuration des profils de trading
export interface TradingProfileConfig {
  value: TradingProfile;
  label: string;
  description: string;
  timeframes: {
    main: string;
    higher: string;
    lower: string;
  };
  characteristics: string[];
}

export const TRADING_PROFILES: TradingProfileConfig[] = [
  {
    value: 'short',
    label: 'Court terme',
    description: 'Scalping et day trading',
    timeframes: {
      main: '15m',
      higher: '1h',
      lower: '5m',
    },
    characteristics: [
      'Réactivité élevée',
      'Multiples trades/jour',
      'Stop-loss serrés',
    ],
  },
  {
    value: 'medium',
    label: 'Moyen terme',
    description: 'Swing trading',
    timeframes: {
      main: '1h',
      higher: '1D',
      lower: '15m',
    },
    characteristics: [
      'Équilibre risque/reward',
      'Quelques trades/semaine',
      'Gestion flexible',
    ],
  },
  {
    value: 'long',
    label: 'Long terme',
    description: 'Position trading',
    timeframes: {
      main: '1D',
      higher: '1W',
      lower: '4h',
    },
    characteristics: [
      'Vision macro',
      'Trades mensuels',
      'Stop-loss larges',
    ],
  },
];

// Modèles Claude disponibles
export const CLAUDE_MODELS = [
  {
    id: 'claude-sonnet-4-5-20250929',
    name: 'Claude Sonnet 4.5',
    description: 'Modèle équilibré (recommandé)',
    recommended: true,
  },
  {
    id: 'claude-3-7-sonnet-20250219',
    name: 'Claude 3.7 Sonnet',
    description: 'Ancien modèle stable',
    recommended: false,
  },
  {
    id: 'claude-opus-4-20250514',
    name: 'Claude Opus 4',
    description: 'Analyse approfondie',
    recommended: false,
  },
] as const;

// Niveaux de confiance
export const CONFIDENCE_LEVELS = {
  VERY_HIGH: { min: 80, max: 100, label: 'Très élevée', color: 'green' },
  HIGH: { min: 60, max: 79, label: 'Élevée', color: 'blue' },
  MEDIUM: { min: 40, max: 59, label: 'Moyenne', color: 'yellow' },
  LOW: { min: 0, max: 39, label: 'Faible', color: 'red' },
} as const;

// Niveaux RSI
export const RSI_LEVELS = {
  OVERBOUGHT: { min: 70, max: 100, label: 'Surachat', color: 'red' },
  BULLISH: { min: 50, max: 69, label: 'Haussier', color: 'blue' },
  BEARISH: { min: 31, max: 49, label: 'Baissier', color: 'yellow' },
  OVERSOLD: { min: 0, max: 30, label: 'Survente', color: 'green' },
} as const;

// Configuration des timeframes
export const TIMEFRAMES = {
  '1m': { label: '1 minute', seconds: 60 },
  '5m': { label: '5 minutes', seconds: 300 },
  '15m': { label: '15 minutes', seconds: 900 },
  '30m': { label: '30 minutes', seconds: 1800 },
  '1h': { label: '1 heure', seconds: 3600 },
  '4h': { label: '4 heures', seconds: 14400 },
  '1D': { label: '1 jour', seconds: 86400 },
  '1W': { label: '1 semaine', seconds: 604800 },
} as const;

// Statuts API Keys
export const API_KEY_STATUS = {
  CONFIGURED: 'configured',
  NOT_CONFIGURED: 'not_configured',
  INVALID: 'invalid',
  EXPIRED: 'expired',
} as const;

// Services API supportés
export const API_SERVICES = {
  ANTHROPIC: {
    name: 'Anthropic',
    description: 'API Claude pour analyse IA',
    keyFormat: /^sk-ant-/,
    required: true,
  },
  HYPERLIQUID: {
    name: 'Hyperliquid',
    description: 'DEX pour trading on-chain',
    keyFormat: /^0x[a-fA-F0-9]{64}$/,
    required: true,
  },
  COINGECKO: {
    name: 'CoinGecko',
    description: 'Données de marché (optionnel)',
    keyFormat: /^CG-/,
    required: false,
  },
} as const;

// Types dérivés
export type TradingSymbol = typeof TRADING_SYMBOLS[number];
export type Exchange = typeof EXCHANGES[number];
export type ClaudeModel = typeof CLAUDE_MODELS[number]['id'];
export type ApiKeyStatus = typeof API_KEY_STATUS[keyof typeof API_KEY_STATUS];
