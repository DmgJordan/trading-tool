import axios from 'axios';

type AxiosError<T = unknown> = {
  response?: {
    data?: T;
    status: number;
  };
  request?: unknown;
  message?: string;
};

/**
 * Type pour les erreurs API standardisées
 */
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: Record<string, unknown>;
}

/**
 * Transforme une erreur Axios en ApiError standardisée
 */
export const handleApiError = (error: unknown): ApiError => {
  const axiosError = error as AxiosError<{
    detail?: string;
    message?: string;
    code?: string;
  }>;

  if (axiosError.response) {
    return {
      message:
        axiosError.response.data?.detail ||
        axiosError.response.data?.message ||
        'Erreur serveur',
      status: axiosError.response.status,
      code: axiosError.response.data?.code,
      details: axiosError.response.data as Record<string, unknown>,
    };
  }

  if (axiosError.request) {
    return {
      message: 'Impossible de contacter le serveur',
      code: 'NETWORK_ERROR',
    };
  }

  return {
    message:
      axiosError.message || 'Une erreur inattendue est survenue',
    code: 'UNKNOWN_ERROR',
  };
};

/**
 * Retry une requête API avec backoff exponentiel
 */
export const retryRequest = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> => {
  let lastError: unknown;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delayMs * Math.pow(2, i)));
      }
    }
  }

  throw lastError;
};

/**
 * Vérifie si une erreur est une erreur d'authentification
 */
export const isAuthError = (error: unknown): boolean => {
  const apiError = error as AxiosError;
  return apiError.response?.status === 401;
};

/**
 * Vérifie si une erreur est une erreur de validation
 */
export const isValidationError = (error: unknown): boolean => {
  const apiError = error as AxiosError;
  return apiError.response?.status === 422;
};

/**
 * Extrait les erreurs de validation d'une réponse API
 */
export const extractValidationErrors = (
  error: unknown
): Record<string, string> => {
  const apiError = error as AxiosError<{
    detail?: Array<{ loc: string[]; msg: string }>;
  }>;

  if (!apiError.response?.data?.detail || !Array.isArray(apiError.response.data.detail)) {
    return {};
  }

  return apiError.response.data.detail.reduce(
    (acc: Record<string, string>, err: { loc: string[]; msg: string }) => {
      const field = err.loc[err.loc.length - 1];
      acc[field] = err.msg;
      return acc;
    },
    {} as Record<string, string>
  );
};

/**
 * Crée un timeout pour une promesse
 */
export const withTimeout = <T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage: string = 'Request timeout'
): Promise<T> => {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error(errorMessage)), timeoutMs)
    ),
  ]);
};

/**
 * Crée un AbortController avec timeout
 */
export const createTimeoutController = (timeoutMs: number): AbortController => {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeoutMs);
  return controller;
};

/**
 * Cache simple pour les requêtes API
 */
class ApiCache {
  private cache = new Map<string, { data: unknown; timestamp: number }>();
  private ttl: number;

  constructor(ttlMs: number = 5 * 60 * 1000) {
    this.ttl = ttlMs;
  }

  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const isExpired = Date.now() - cached.timestamp > this.ttl;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return cached.data as T;
  }

  set<T>(key: string, data: T): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  clear(): void {
    this.cache.clear();
  }

  delete(key: string): void {
    this.cache.delete(key);
  }
}

export const apiCache = new ApiCache();
