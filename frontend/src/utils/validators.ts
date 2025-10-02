import { z } from 'zod';

/**
 * Valide une adresse email
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Valide un symbole d'actif (crypto)
 */
export const isValidAssetSymbol = (symbol: string): boolean => {
  return /^[A-Z0-9]{1,10}$/.test(symbol);
};

/**
 * Valide une adresse Ethereum
 */
export const isValidEthAddress = (address: string): boolean => {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
};

/**
 * Valide un nombre dans une plage
 */
export const isInRange = (
  value: number,
  min: number,
  max: number
): boolean => {
  return value >= min && value <= max;
};

/**
 * Valide une clé API Anthropic
 */
export const isValidAnthropicKey = (key: string): boolean => {
  return key.startsWith('sk-ant-') && key.length > 20;
};

/**
 * Valide une clé API Hyperliquid
 */
export const isValidHyperliquidKey = (key: string): boolean => {
  return /^0x[a-fA-F0-9]{64}$/.test(key);
};

/**
 * Nettoie et normalise un symbole d'actif
 */
export const normalizeAssetSymbol = (symbol: string): string => {
  return symbol.trim().toUpperCase();
};

/**
 * Valide et parse un JSON
 */
export const isValidJson = (jsonString: string): boolean => {
  try {
    JSON.parse(jsonString);
    return true;
  } catch {
    return false;
  }
};

/**
 * Valide une URL
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Extrait le message d'erreur d'une erreur API
 */
export const extractErrorMessage = (error: unknown): string => {
  if (typeof error === 'string') return error;

  const apiError = error as {
    response?: { data?: { detail?: string; message?: string } };
    message?: string;
  };

  return (
    apiError.response?.data?.detail ||
    apiError.response?.data?.message ||
    apiError.message ||
    'Une erreur est survenue'
  );
};

/**
 * Valide les contraintes de préférences de trading
 */
export const validateTradingPreferences = {
  maxPositionSize: (value: number) => isInRange(value, 0.1, 100),
  stopLossPercentage: (value: number) => isInRange(value, 0.1, 50),
  takeProfitRatio: (value: number) => isInRange(value, 0.1, 10),
  preferredAssets: (assets: string[]) => assets.length >= 1 && assets.length <= 20,
  technicalIndicators: (indicators: string[]) => indicators.length >= 1 && indicators.length <= 15,
};

/**
 * Valide un mot de passe sécurisé
 */
export const isStrongPassword = (password: string): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Au moins 8 caractères');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Au moins une majuscule');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Au moins une minuscule');
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Au moins un chiffre');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * Sanitize une chaîne pour éviter les XSS
 */
export const sanitizeString = (str: string): string => {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};
