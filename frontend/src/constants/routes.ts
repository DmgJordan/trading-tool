// Routes publiques (non protégées)
export const PUBLIC_ROUTES = ['/login'] as const;

// Routes protégées
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
  HYPERLIQUID: {
    EXECUTE_TRADE: '/hyperliquid/execute-trade',
    PORTFOLIO_INFO: '/hyperliquid/portfolio-info',
  },
  CONNECTORS: {
    TEST_ANTHROPIC: '/connectors/test-anthropic',
    TEST_HYPERLIQUID: '/connectors/test-hyperliquid',
    USER_INFO: '/connectors/user-info',
  },
  HEALTH: {
    API: '/health',
    DB: '/db-health',
  },
} as const;

// Helper pour vérifier si une route est publique
export const isPublicRoute = (pathname: string): boolean => {
  return PUBLIC_ROUTES.some(route => pathname.startsWith(route));
};

// Helper pour vérifier si une route est protégée
export const isProtectedRoute = (pathname: string): boolean => {
  return Object.values(PROTECTED_ROUTES).some(route => pathname.startsWith(route));
};
