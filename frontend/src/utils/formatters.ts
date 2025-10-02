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

  if (diffSec < 60) return 'À l\'instant';
  if (diffMin < 60) return `Il y a ${diffMin} min`;
  if (diffHour < 24) return `Il y a ${diffHour}h`;
  if (diffDay < 7) return `Il y a ${diffDay}j`;

  return formatDate(dateObj);
};
