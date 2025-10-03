/**
 * Utilitaires UI pour couleurs, styles et labels
 * Centralise toutes les fonctions de formatage visuel
 */

// Types pour les statuts
export type Status = 'success' | 'error' | 'warning' | 'info' | 'testing' | 'idle' | null;
export type TradeDirection = 'long' | 'short';
export type TradingProfile = 'short' | 'medium' | 'long';

/**
 * Retourne les classes Tailwind pour une couleur de statut
 */
export const getStatusColor = (status: Status): string => {
  switch (status) {
    case 'success':
      return 'border-black bg-gray-100 text-black';
    case 'error':
      return 'border-red-500 bg-red-50 text-red-700';
    case 'warning':
      return 'border-yellow-500 bg-yellow-50 text-yellow-700';
    case 'testing':
      return 'border-black bg-gray-50 text-gray-700';
    case 'info':
      return 'border-blue-500 bg-blue-50 text-blue-700';
    case 'idle':
    default:
      return 'border-gray-300 bg-white text-gray-600';
  }
};

/**
 * Retourne l'icône pour un statut donné
 */
export const getStatusIcon = (status: Status): string => {
  switch (status) {
    case 'success':
      return '✓';
    case 'error':
      return '✗';
    case 'warning':
      return '⚠';
    case 'testing':
      return '⟳';
    case 'info':
      return 'ℹ';
    default:
      return '○';
  }
};

/**
 * Retourne la classe de couleur pour un RSI
 */
export const getRSIColor = (rsi: number): string => {
  if (rsi >= 70) return 'text-red-600';
  if (rsi <= 30) return 'text-green-600';
  if (rsi >= 50) return 'text-blue-600';
  return 'text-yellow-600';
};

/**
 * Retourne le label descriptif pour un RSI
 */
export const getRSILabel = (rsi: number): string => {
  if (rsi >= 70) return 'Surachat';
  if (rsi <= 30) return 'Survente';
  if (rsi >= 50) return 'Haussier';
  return 'Baissier';
};

/**
 * Configuration des couleurs pour les directions de trade
 */
export const getDirectionColors = (direction: TradeDirection) => {
  const config = {
    long: {
      bg: 'bg-green-50',
      border: 'border-green-500',
      text: 'text-green-700',
      badge: 'bg-green-100 text-green-800',
      hover: 'hover:bg-green-100',
      gradient: 'from-green-50 to-emerald-50',
    },
    short: {
      bg: 'bg-red-50',
      border: 'border-red-500',
      text: 'text-red-700',
      badge: 'bg-red-100 text-red-800',
      hover: 'hover:bg-red-100',
      gradient: 'from-red-50 to-rose-50',
    },
  };

  return config[direction];
};

/**
 * Retourne la couleur selon le niveau de confiance (0-100)
 */
export const getConfidenceColor = (level: number): string => {
  if (level >= 80) return 'text-green-600';
  if (level >= 60) return 'text-blue-600';
  if (level >= 40) return 'text-yellow-600';
  return 'text-red-600';
};

/**
 * Retourne le label pour un niveau de confiance
 */
export const getConfidenceLabel = (level: number): string => {
  if (level >= 80) return 'Très élevée';
  if (level >= 60) return 'Élevée';
  if (level >= 40) return 'Moyenne';
  return 'Faible';
};

/**
 * Retourne le label d'un profil de trading
 */
export const getProfileLabel = (profile: TradingProfile): string => {
  const labels = {
    short: 'Court terme (15m/1h/5m)',
    medium: 'Moyen terme (1h/1D/15m)',
    long: 'Long terme (1D/1W/4h)',
  };

  return labels[profile];
};

/**
 * Retourne la description complète d'un profil de trading
 */
export const getProfileDescription = (profile: TradingProfile): string => {
  const descriptions = {
    short: 'Court terme (15m/1h/5m) - Scalping et day trading',
    medium: 'Moyen terme (1h/1D/15m) - Swing trading',
    long: 'Long terme (1D/1W/4h) - Position trading',
  };

  return descriptions[profile];
};

/**
 * Retourne la couleur pour un changement de prix (positif/négatif)
 */
export const getPriceChangeColor = (change: number): string => {
  return change >= 0 ? 'text-green-600' : 'text-red-600';
};

/**
 * Retourne la couleur pour un PnL
 */
export const getPnLColor = (pnl: number): string => {
  return pnl >= 0 ? 'text-green-600' : 'text-red-600';
};

/**
 * Retourne les classes pour un bouton de direction
 */
export const getDirectionButtonClasses = (
  direction: TradeDirection,
  isSelected: boolean
): string => {
  const colors = getDirectionColors(direction);
  const base = `px-4 py-2 rounded-lg font-medium transition-all border-2`;

  if (isSelected) {
    return `${base} ${colors.bg} ${colors.border} ${colors.text}`;
  }

  return `${base} border-gray-300 text-gray-700 hover:${colors.bg}`;
};

/**
 * Retourne les classes pour un badge de réseau (mainnet/testnet)
 */
export const getNetworkBadgeClasses = (isTestnet: boolean): string => {
  if (isTestnet) {
    return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  }
  return 'bg-green-100 text-green-800 border-green-300';
};

/**
 * Retourne le label pour un réseau
 */
export const getNetworkLabel = (isTestnet: boolean): string => {
  return isTestnet ? 'Testnet' : 'Mainnet';
};

/**
 * Retourne la couleur d'un volume spike
 */
export const getVolumeSpikeColor = (spikeRatio: number): string => {
  if (spikeRatio >= 2.0) return 'text-red-600';
  if (spikeRatio >= 1.5) return 'text-orange-600';
  return 'text-green-600';
};

/**
 * Retourne le label d'un volume spike
 */
export const getVolumeSpikeLabel = (spikeRatio: number): string => {
  if (spikeRatio >= 2.0) return 'Très élevé';
  if (spikeRatio >= 1.5) return 'Élevé';
  if (spikeRatio >= 1.2) return 'Modéré';
  return 'Normal';
};

/**
 * Classes communes pour les cartes d'indicateurs
 */
export const INDICATOR_CARD_CLASSES = {
  rsi: 'bg-gradient-to-br from-purple-50 to-indigo-50',
  ma: 'bg-gradient-to-br from-blue-50 to-cyan-50',
  volume: 'bg-gradient-to-br from-green-50 to-emerald-50',
  atr: 'bg-gradient-to-br from-orange-50 to-red-50',
  price: 'bg-gradient-to-r from-blue-50 to-indigo-50',
  structure: 'bg-gradient-to-br from-yellow-50 to-orange-50',
};
