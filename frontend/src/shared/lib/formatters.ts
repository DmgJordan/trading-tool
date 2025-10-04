/**
 * Formate un nombre en devise avec séparateurs de milliers
 */
export const formatCurrency = (
  value: number | null | undefined,
  currency: string = 'USD',
  decimals: number = 2
): string => {
  if (value === null || value === undefined) return '-';

  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Formate un nombre avec séparateurs de milliers
 */
export const formatNumber = (
  value: number | null | undefined,
  decimals: number = 2
): string => {
  if (value === null || value === undefined) return '-';

  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Formate un pourcentage
 */
export const formatPercentage = (
  value: number | null | undefined,
  decimals: number = 2,
  includeSign: boolean = false
): string => {
  if (value === null || value === undefined) return '-';

  const sign = includeSign && value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
};

/**
 * Formate une date en français
 */
export const formatDate = (
  date: string | Date | null | undefined,
  format: 'short' | 'long' | 'time' = 'short'
): string => {
  if (!date) return '-';

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString('fr-FR');
    case 'long':
      return dateObj.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    case 'time':
      return dateObj.toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit',
      });
    default:
      return dateObj.toLocaleDateString('fr-FR');
  }
};

/**
 * Formate une date et heure complète
 */
export const formatDateTime = (
  date: string | Date | null | undefined
): string => {
  if (!date) return '-';

  const dateObj = typeof date === 'string' ? new Date(date) : date;

  return dateObj.toLocaleString('fr-FR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Formate un ratio (ex: 2.5x)
 */
export const formatRatio = (
  value: number | null | undefined,
  decimals: number = 1
): string => {
  if (value === null || value === undefined) return '-';

  return `${value.toFixed(decimals)}x`;
};

/**
 * Formate une adresse wallet (raccourcie)
 */
export const formatWalletAddress = (
  address: string | null | undefined,
  startChars: number = 6,
  endChars: number = 4
): string => {
  if (!address) return '-';

  if (address.length <= startChars + endChars) return address;

  return `${address.slice(0, startChars)}...${address.slice(-endChars)}`;
};

/**
 * Formate une clé API (masquée)
 */
export const formatApiKey = (
  key: string | null | undefined,
  visibleChars: number = 4
): string => {
  if (!key) return '-';

  const masked = '*'.repeat(Math.max(0, key.length - visibleChars));
  const visible = key.slice(-visibleChars);

  return `${masked}${visible}`;
};

/**
 * Formate un montant de cryptomonnaie
 */
export const formatCryptoAmount = (
  amount: number | null | undefined,
  symbol: string,
  decimals: number = 8
): string => {
  if (amount === null || amount === undefined) return '-';

  // Ajuster les décimales selon la taille du montant
  const adjustedDecimals = amount < 1 ? decimals : decimals > 4 ? 4 : decimals;

  return `${formatNumber(amount, adjustedDecimals)} ${symbol}`;
};

/**
 * Formate un timestamp relatif (il y a X minutes/heures)
 */
export const formatRelativeTime = (
  date: string | Date | null | undefined
): string => {
  if (!date) return '-';

  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "À l'instant";
  if (diffMin < 60) return `Il y a ${diffMin} min`;
  if (diffHour < 24) return `Il y a ${diffHour}h`;
  if (diffDay < 7) return `Il y a ${diffDay}j`;

  return formatDate(dateObj);
};

/**
 * Formate un changement de pourcentage avec signe
 */
export const formatPercentageChange = (
  value: number | null | undefined,
  decimals: number = 2
): string => {
  if (value === null || value === undefined) return '-';

  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
};

/**
 * Formate un volume avec suffixes K/M/B
 */
export const formatVolume = (
  volume: number | null | undefined,
  decimals: number = 2
): string => {
  if (volume === null || volume === undefined) return '-';

  if (volume >= 1_000_000_000) {
    return `${(volume / 1_000_000_000).toFixed(decimals)}B`;
  }
  if (volume >= 1_000_000) {
    return `${(volume / 1_000_000).toFixed(decimals)}M`;
  }
  if (volume >= 1_000) {
    return `${(volume / 1_000).toFixed(decimals)}K`;
  }

  return formatNumber(volume, decimals);
};

/**
 * Formate un symbole de trading (ajoute /USDT si manquant)
 */
export const formatTicker = (ticker: string): string => {
  if (!ticker) return '';

  const normalized = ticker.toUpperCase().trim();

  // Si déjà au format SYMBOL/QUOTE
  if (normalized.includes('/')) return normalized;

  // Ajouter /USDT par défaut
  return `${normalized}/USDT`;
};

/**
 * Formate un timeframe en label lisible
 */
export const formatTimeframe = (timeframe: string): string => {
  const labels: Record<string, string> = {
    '1m': '1 minute',
    '5m': '5 minutes',
    '15m': '15 minutes',
    '30m': '30 minutes',
    '1h': '1 heure',
    '4h': '4 heures',
    '1D': '1 jour',
    '1d': '1 jour',
    '1W': '1 semaine',
    '1w': '1 semaine',
    '1M': '1 mois',
    '1mo': '1 mois',
  };

  return labels[timeframe] || timeframe;
};

/**
 * Formate une quantité de trade
 */
export const formatQuantity = (
  quantity: number | string | null | undefined,
  decimals: number = 8
): string => {
  if (quantity === null || quantity === undefined) return '-';

  const num = typeof quantity === 'string' ? parseFloat(quantity) : quantity;

  if (isNaN(num)) return '-';

  // Ajuster les décimales selon la taille
  const adjustedDecimals = num < 0.001 ? decimals : Math.min(decimals, 4);

  return formatNumber(num, adjustedDecimals);
};

/**
 * Formate un prix avec nombre de décimales adaptatif
 */
export const formatPrice = (
  price: number | string | null | undefined,
  minDecimals: number = 2
): string => {
  if (price === null || price === undefined) return '-';

  const num = typeof price === 'string' ? parseFloat(price) : price;

  if (isNaN(num)) return '-';

  // Déterminer le nombre de décimales selon le prix
  let decimals = minDecimals;
  if (num < 0.0001) decimals = 8;
  else if (num < 0.01) decimals = 6;
  else if (num < 1) decimals = 4;

  return formatNumber(num, decimals);
};

/**
 * Formate un montant avec sa devise
 */
export const formatAmountWithCurrency = (
  amount: number | null | undefined,
  currency: string = 'USD',
  decimals: number = 2
): string => {
  if (amount === null || amount === undefined) return '-';

  if (currency === 'USD' || currency === 'USDT') {
    return formatCurrency(amount, 'USD', decimals);
  }

  return `${formatNumber(amount, decimals)} ${currency}`;
};

/**
 * Formate un risk/reward ratio
 */
export const formatRiskRewardRatio = (
  ratio: number | null | undefined
): string => {
  if (ratio === null || ratio === undefined) return '-';

  return `1:${ratio.toFixed(2)}`;
};
