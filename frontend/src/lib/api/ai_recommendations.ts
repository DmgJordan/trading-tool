import axios from 'axios';
import type { AuthTokens } from '../types/auth';
import {
  AIRecommendation,
  AIRecommendationRequest,
  AIRecommendationResponse,
  RecommendationAction_Update,
  DashboardStats,
} from '../types/ai_recommendations';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Réutiliser la même instance axios que pour les préférences (avec intercepteurs JWT)
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'accès aux requêtes
api.interceptors.request.use(config => {
  const tokens = localStorage.getItem('auth_tokens');
  if (tokens) {
    const { access_token } = JSON.parse(tokens);
    if (config.headers) {
      config.headers.Authorization = `Bearer ${access_token}`;
    }
  }
  return config;
});

// Intercepteur pour gérer l'expiration des tokens
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expiré, essayer de le rafraîchir
      const tokens = localStorage.getItem('auth_tokens');
      if (tokens) {
        try {
          const { refresh_token } = JSON.parse(tokens);

          // Appel pour rafraîchir le token
          const refreshResponse = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            {
              refresh_token,
            }
          );

          const newTokens = refreshResponse.data as AuthTokens;

          // Mettre à jour les tokens stockés
          localStorage.setItem('auth_tokens', JSON.stringify(newTokens));

          // Relancer la requête originale avec le nouveau token
          if (error.config && error.config.headers) {
            error.config.headers.Authorization = `Bearer ${newTokens.access_token}`;
            return api.request(error.config);
          }
        } catch {
          // Impossible de rafraîchir, déconnecter l'utilisateur
          localStorage.removeItem('auth_tokens');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export interface GenerateRecommendationsResponse {
  recommendations: AIRecommendationResponse[];
  generated_at: string;
  total_count: number;
  message: string;
}

export interface RecommendationHistoryResponse {
  recommendations: AIRecommendation[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export const aiRecommendationsApi = {
  /**
   * Génère de nouvelles recommandations IA
   */
  generateRecommendations: async (
    request?: AIRecommendationRequest
  ): Promise<GenerateRecommendationsResponse> => {
    try {
      const response = await api.post(
        '/ai-recommendations/generate-recommendations',
        request || {}
      );
      return response.data as GenerateRecommendationsResponse;
    } catch (error: unknown) {
      // Si l'endpoint n'existe pas encore, simuler une réponse
      if ((error as any).response?.status === 404) {
        console.warn(
          'Endpoint /ai-recommendations/generate-recommendations not found, simulating response'
        );
        return {
          recommendations: [],
          generated_at: new Date().toISOString(),
          total_count: 0,
          message:
            'Service de recommandations IA non disponible pour le moment',
        };
      }
      throw error as Error;
    }
  },

  /**
   * Récupère les recommandations actives de l'utilisateur
   */
  getRecommendations: async (): Promise<AIRecommendation[]> => {
    try {
      const response = await api.get('/ai-recommendations/');
      return response.data as AIRecommendation[];
    } catch (error: unknown) {
      // Si l'endpoint n'existe pas encore, retourner un tableau vide
      if ((error as any).response?.status === 404) {
        console.warn(
          'Endpoint /ai-recommendations/ not found, returning empty array'
        );
        return [];
      }
      throw error as Error;
    }
  },

  /**
   * Récupère une recommandation spécifique par ID
   */
  getRecommendation: async (id: number): Promise<AIRecommendation> => {
    const response = await api.get(`/ai-recommendations/${id}`);
    return response.data as AIRecommendation;
  },

  /**
   * Accepte une recommandation
   */
  acceptRecommendation: async (
    id: number,
    note?: string
  ): Promise<AIRecommendation> => {
    const update: RecommendationAction_Update = {
      status: 'ACCEPTED',
      user_note: note,
    };
    const response = await api.put(`/ai-recommendations/${id}/accept`, update);
    return response.data as AIRecommendation;
  },

  /**
   * Rejette une recommandation
   */
  rejectRecommendation: async (
    id: number,
    note?: string
  ): Promise<AIRecommendation> => {
    const update: RecommendationAction_Update = {
      status: 'REJECTED',
      user_note: note,
    };
    const response = await api.put(`/ai-recommendations/${id}/reject`, update);
    return response.data as AIRecommendation;
  },

  /**
   * Récupère l'historique des recommandations avec pagination
   */
  getRecommendationHistory: async (
    page: number = 1,
    perPage: number = 20,
    status?: string,
    action?: string
  ): Promise<RecommendationHistoryResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (status) params.append('status', status);
    if (action) params.append('action', action);

    const response = await api.get(
      `/ai-recommendations/history?${params.toString()}`
    );
    return response.data as RecommendationHistoryResponse;
  },

  /**
   * Récupère les statistiques du dashboard
   */
  getDashboardStats: async (): Promise<DashboardStats> => {
    try {
      const response = await api.get('/ai-recommendations/stats');
      return response.data as DashboardStats;
    } catch (error: unknown) {
      // Si l'endpoint n'existe pas encore, retourner des stats par défaut
      if ((error as any).response?.status === 404) {
        console.warn(
          'Endpoint /ai-recommendations/stats not found, returning default stats'
        );
        return {
          total_recommendations: 0,
          pending_recommendations: 0,
          accepted_recommendations: 0,
          rejected_recommendations: 0,
          total_estimated_pnl: 0,
          total_estimated_pnl_percentage: 0,
          last_generated_at: null,
        };
      }
      throw error as Error;
    }
  },

  /**
   * Supprime les recommandations expirées
   */
  cleanupExpiredRecommendations: async (): Promise<{
    deleted_count: number;
    message: string;
  }> => {
    const response = await api.delete('/ai-recommendations/cleanup-expired');
    return response.data as { deleted_count: number; message: string };
  },

  /**
   * Valide les paramètres de génération de recommandations
   */
  validateGenerationRequest: async (
    request: AIRecommendationRequest
  ): Promise<{ isValid: boolean; errors?: Record<string, string[]> }> => {
    try {
      await api.post('/ai-recommendations/validate-request', request);
      return { isValid: true };
    } catch (error: unknown) {
      if (
        (error as { response?: { status?: number } }).response?.status === 422
      ) {
        return {
          isValid: false,
          errors:
            (
              error as {
                response?: { data?: { detail?: Record<string, string[]> } };
              }
            ).response?.data?.detail || {},
        };
      }
      throw error as Error;
    }
  },
};

// Types spécifiques pour les réponses API avec gestion d'erreurs
export interface RecommendationsApiError {
  detail: string | Record<string, string[]>;
  status_code: number;
}

export interface RecommendationsApiResponse<T> {
  data?: T;
  error?: RecommendationsApiError;
  isLoading: boolean;
}

// Wrapper pour les appels API avec gestion d'erreurs standardisée
export const withErrorHandling = async <T>(
  apiCall: () => Promise<T>
): Promise<RecommendationsApiResponse<T>> => {
  try {
    const data = await apiCall();
    return { data, isLoading: false };
  } catch (error: unknown) {
    const apiError: RecommendationsApiError = {
      detail:
        (
          error as {
            response?: { data?: { detail?: string } };
            message?: string;
          }
        ).response?.data?.detail ||
        (error as Error).message ||
        'Erreur inconnue',
      status_code:
        (error as { response?: { status?: number } }).response?.status || 500,
    };
    return { error: apiError, isLoading: false };
  }
};

// Utilitaires pour les appels API avec retry automatique
export const withRetry = async <T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error: unknown) {
      lastError = error;

      // Ne pas retry sur les erreurs 4xx (erreurs client)
      if (
        (error as any).response?.status >= 400 &&
        (error as any).response?.status < 500
      ) {
        throw error as Error;
      }

      // Attendre avant le retry, avec backoff exponentiel
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }
  }

  throw lastError;
};

// Client API avec retry automatique pour les opérations critiques
export const aiRecommendationsApiWithRetry = {
  generateRecommendations: (request?: AIRecommendationRequest) =>
    withRetry(() => aiRecommendationsApi.generateRecommendations(request)),
  getRecommendations: () =>
    withRetry(() => aiRecommendationsApi.getRecommendations()),
  getDashboardStats: () =>
    withRetry(() => aiRecommendationsApi.getDashboardStats()),
  acceptRecommendation: (id: number, note?: string) =>
    withRetry(() => aiRecommendationsApi.acceptRecommendation(id, note)),
  rejectRecommendation: (id: number, note?: string) =>
    withRetry(() => aiRecommendationsApi.rejectRecommendation(id, note)),
};

// Utilitaires pour la gestion du cache local
export const recommendationsCache = {
  setRecommendations: (recommendations: AIRecommendation[]) => {
    localStorage.setItem(
      'recommendations_cache',
      JSON.stringify({
        data: recommendations,
        timestamp: Date.now(),
        ttl: 5 * 60 * 1000, // 5 minutes
      })
    );
  },

  getRecommendations: (): AIRecommendation[] | null => {
    const cached = localStorage.getItem('recommendations_cache');
    if (!cached) return null;

    try {
      const { data, timestamp, ttl } = JSON.parse(cached);
      if (Date.now() - timestamp > ttl) {
        localStorage.removeItem('recommendations_cache');
        return null;
      }
      return data as AIRecommendation[];
    } catch {
      localStorage.removeItem('recommendations_cache');
      return null;
    }
  },

  clearCache: () => {
    localStorage.removeItem('recommendations_cache');
  },
};

export default aiRecommendationsApi;
