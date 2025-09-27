import {
  TradingPreferences,
  TradingPreferencesUpdate,
  TradingPreferencesDefault,
  PreferencesValidationInfo,
} from '../types/preferences';
import apiClient from './client';

export const preferencesApi = {
  /**
   * Récupère les préférences de trading de l'utilisateur actuel
   */
  getPreferences: async (): Promise<TradingPreferences> => {
    const response = await apiClient.get('/users/me/preferences/');
    return response.data as TradingPreferences;
  },

  /**
   * Met à jour les préférences de trading (PATCH/PUT selon les champs fournis)
   */
  updatePreferences: async (
    preferences: TradingPreferencesUpdate
  ): Promise<TradingPreferences> => {
    const response = await apiClient.put('/users/me/preferences/', preferences);
    return response.data as TradingPreferences;
  },

  /**
   * Crée ou remplace complètement les préférences de trading
   */
  createPreferences: async (
    preferences: Omit<
      TradingPreferences,
      'id' | 'user_id' | 'created_at' | 'updated_at'
    >
  ): Promise<TradingPreferences> => {
    const response = await apiClient.post(
      '/users/me/preferences/',
      preferences
    );
    return response.data as TradingPreferences;
  },

  /**
   * Remet les préférences aux valeurs par défaut
   */
  resetToDefaults: async (): Promise<{
    status: string;
    message: string;
    preferences: TradingPreferences;
  }> => {
    const response = await apiClient.delete('/users/me/preferences/');
    return response.data as {
      status: string;
      message: string;
      preferences: TradingPreferences;
    };
  },

  /**
   * Récupère les valeurs par défaut des préférences
   */
  getDefaults: async (): Promise<TradingPreferencesDefault> => {
    const response = await apiClient.get('/users/me/preferences/default');
    return response.data as TradingPreferencesDefault;
  },

  /**
   * Récupère les informations de validation (contraintes, options disponibles)
   */
  getValidationInfo: async (): Promise<PreferencesValidationInfo> => {
    const response = await apiClient.get(
      '/users/me/preferences/validation-info'
    );
    return response.data as PreferencesValidationInfo;
  },

  /**
   * Valide des préférences sans les sauvegarder (optionnel pour validation côté serveur)
   */
  validatePreferences: async (
    preferences: TradingPreferencesUpdate
  ): Promise<{ isValid: boolean; errors?: Record<string, string[]> }> => {
    try {
      // Cette route n'existe peut-être pas encore côté backend, mais utile pour l'avenir
      await apiClient.post('/users/me/preferences/validate', preferences);
      return { isValid: true, errors: {} };
    } catch (error: unknown) {
      if (
        (error as { response?: { status?: number } }).response?.status === 422
      ) {
        // Erreurs de validation
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
      throw error;
    }
  },
};

// Types spécifiques pour les réponses API avec gestion d'erreurs
export interface PreferencesApiError {
  detail: string | Record<string, string[]>;
  status_code: number;
}

export interface PreferencesApiResponse<T> {
  data?: T;
  error?: PreferencesApiError;
  isLoading: boolean;
}

// Wrapper pour les appels API avec gestion d'erreurs standardisée
export const withErrorHandling = async <T>(
  apiCall: () => Promise<T>
): Promise<PreferencesApiResponse<T>> => {
  try {
    const data = await apiCall();
    return { data, isLoading: false };
  } catch (error: unknown) {
    const apiError: PreferencesApiError = {
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
        throw error;
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
export const preferencesApiWithRetry = {
  getPreferences: () => withRetry(() => preferencesApi.getPreferences()),
  updatePreferences: (preferences: TradingPreferencesUpdate) =>
    withRetry(() => preferencesApi.updatePreferences(preferences)),
  getDefaults: () => withRetry(() => preferencesApi.getDefaults()),
  getValidationInfo: () => withRetry(() => preferencesApi.getValidationInfo()),
};

export default preferencesApi;
