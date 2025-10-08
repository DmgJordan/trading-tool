/**
 * Routes publiques (non protégées)
 *
 * Pattern Next.js : routes sous /(public)/* sont accessibles sans authentification
 */
export const PUBLIC_ROUTES = ['/login'] as const;

/**
 * Patterns regex pour détecter les routes publiques
 * Utilisés par le middleware SSR pour whitelisting
 */
export const PUBLIC_ROUTE_PATTERNS = [
  /^\/(public)\/.*/, // Toutes routes sous /(public)/*
  /^\/login$/, // Legacy /login (compatibilité)
] as const;

/**
 * Routes protégées (nécessitent authentification)
 *
 * Pattern Next.js : routes sous /(app)/* requièrent auth
 */
export const PROTECTED_ROUTES = {
  HOME: '/',
  ACCOUNT: '/account',
  PREFERENCES: '/preferences',
  TRADING: '/trading',
  DASHBOARD: '/dashboard',
} as const;

// Routes API
export const API_ROUTES = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
  },
  USERS: {
    ME: '/users/me',
    UPDATE: '/users/me',
    API_KEYS: '/users/me/api-keys',
  },
  PREFERENCES: {
    BASE: '/users/me/preferences',
    DEFAULT: '/users/me/preferences/default',
    VALIDATION: '/users/me/preferences/validation-info',
  },
  TRADING: {
    EXECUTE_TRADE: '/trading/orders',
    PORTFOLIO_INFO: '/trading/portfolio',
    POSITIONS: '/trading/positions',
    ORDERS: '/trading/orders',
    TEST_CONNECTION: '/trading/test',
  },
  MARKET: {
    OHLCV_EXCHANGES: '/market/ohlcv/exchanges',
    OHLCV_SYMBOLS: '/market/ohlcv/symbols',
    MULTI_TIMEFRAME_ANALYSIS: '/market/ohlcv/multi-timeframe-analysis',
    MARKET_DATA: (symbol: string) => `/market/data/${symbol}`,
  },
  AI: {
    ANALYZE: '/ai/analyze',
    TEST_PROVIDER: '/ai/test-provider',
    PROVIDERS: '/ai/providers',
    MODELS: '/ai/models',
  },
  API_KEYS: {
    // Migré depuis CONNECTORS vers users/me/api-keys
    TEST: '/users/me/api-keys/test',
    TEST_STORED: (apiType: string) => `/users/me/api-keys/test-stored/${apiType}`,
    VALIDATE_FORMAT: '/users/me/api-keys/validate-format',
    SUPPORTED_SERVICES: '/users/me/api-keys/supported-services',
  },
  HEALTH: {
    API: '/health',
    DB: '/db-health',
  },
} as const;

/**
 * Helper pour vérifier si une route est publique (legacy)
 * @deprecated Utiliser isPublicPath() à la place
 */
export const isPublicRoute = (pathname: string): boolean => {
  return PUBLIC_ROUTES.some(route => pathname.startsWith(route));
};

/**
 * Helper pour vérifier si un chemin est public (compatible route groups Next.js)
 * Utilisé par le middleware SSR
 */
export const isPublicPath = (pathname: string): boolean => {
  return PUBLIC_ROUTE_PATTERNS.some(pattern => pattern.test(pathname));
};

/**
 * Helper pour vérifier si une route est protégée
 *
 * CRITICAL: Traiter '/' comme cas spécial pour éviter que TOUTES
 * les routes soient considérées comme protégées (car '/login'.startsWith('/') === true)
 */
export const isProtectedRoute = (pathname: string): boolean => {
  // Cas spécial : '/' exact (page d'accueil)
  if (pathname === '/') {
    return true;
  }

  // Vérifier les autres routes protégées (en excluant '/')
  return Object.values(PROTECTED_ROUTES)
    .filter(route => route !== '/') // Exclure '/' pour éviter le bug startsWith
    .some(route => pathname.startsWith(route));
};
