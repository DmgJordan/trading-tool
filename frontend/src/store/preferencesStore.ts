import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  TradingPreferences,
  TradingPreferencesUpdate,
  PreferencesState,
  PreferencesActions,
} from '../lib/types/preferences';
import { preferencesApi } from '../lib/api/preferences';

interface PreferencesStore extends PreferencesState, PreferencesActions {}

export const usePreferencesStore = create<PreferencesStore>()(
  persist(
    (set, get) => ({
      // État initial
      preferences: null,
      defaults: null,
      validationInfo: null,
      isLoading: false,
      isSaving: false,
      error: null,
      lastSaved: null,

      // Actions
      loadPreferences: async () => {
        try {
          set({ isLoading: true, error: null });

          const preferences = await preferencesApi.getPreferences();

          set({
            preferences,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            'Erreur lors du chargement des préférences';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      loadDefaults: async () => {
        try {
          const defaults = await preferencesApi.getDefaults();
          set({ defaults, error: null });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            'Erreur lors du chargement des valeurs par défaut';
          set({ error: errorMessage });
          throw error;
        }
      },

      loadValidationInfo: async () => {
        try {
          const validationInfo = await preferencesApi.getValidationInfo();
          set({ validationInfo, error: null });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            'Erreur lors du chargement des informations de validation';
          set({ error: errorMessage });
          throw error;
        }
      },

      updatePreferences: async (
        preferencesUpdate: TradingPreferencesUpdate
      ) => {
        try {
          set({ isSaving: true, error: null });

          // Optimistic update
          const currentPreferences = get().preferences;
          if (currentPreferences) {
            set({
              preferences: { ...currentPreferences, ...preferencesUpdate },
            });
          }

          const updatedPreferences =
            await preferencesApi.updatePreferences(preferencesUpdate);

          set({
            preferences: updatedPreferences,
            isSaving: false,
            error: null,
            lastSaved: new Date().toISOString(),
          });
        } catch (error: any) {
          // Revert optimistic update en cas d'erreur
          const { preferences: currentPreferences } = get();
          if (currentPreferences) {
            // Recalculer l'état précédent en retirant les modifications optimistes
            const revertedPreferences = { ...currentPreferences };
            Object.keys(preferencesUpdate).forEach(key => {
              delete (revertedPreferences as any)[key];
            });
            set({ preferences: revertedPreferences });
          }

          const errorMessage =
            error.response?.data?.detail ||
            'Erreur lors de la sauvegarde des préférences';
          set({
            isSaving: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      resetToDefaults: async () => {
        try {
          set({ isSaving: true, error: null });

          const response = await preferencesApi.resetToDefaults();

          set({
            preferences: response.preferences,
            isSaving: false,
            error: null,
            lastSaved: new Date().toISOString(),
          });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail ||
            'Erreur lors de la réinitialisation';
          set({
            isSaving: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'preferences-store',
      storage: createJSONStorage(() => localStorage),
      // Persister seulement les données essentielles, pas les états de chargement
      partialize: state => ({
        preferences: state.preferences,
        defaults: state.defaults,
        validationInfo: state.validationInfo,
        lastSaved: state.lastSaved,
      }),
    }
  )
);

// Hook personnalisé pour l'auto-save avec debounce
export const useAutoSavePreferences = (delayMs: number = 2000) => {
  const { updatePreferences } = usePreferencesStore();
  let timeoutId: NodeJS.Timeout;

  const debouncedUpdate = (preferences: TradingPreferencesUpdate) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(async () => {
      try {
        await updatePreferences(preferences);
      } catch (error) {
        console.error('Auto-save failed:', error);
        // L'erreur sera gérée par le store et affichée dans l'UI
      }
    }, delayMs);
  };

  return { debouncedUpdate };
};

// Hook pour charger toutes les données nécessaires à l'initialisation
export const useInitializePreferences = () => {
  const {
    loadPreferences,
    loadDefaults,
    loadValidationInfo,
    preferences,
    defaults,
    validationInfo,
    isLoading,
    error,
  } = usePreferencesStore();

  const initialize = async () => {
    try {
      // Charger en parallèle pour optimiser les performances
      await Promise.all([
        loadPreferences(),
        loadDefaults(),
        loadValidationInfo(),
      ]);
    } catch (error) {
      console.error("Erreur lors de l'initialisation des préférences:", error);
      // L'erreur sera gérée par le store et affichée dans l'UI
    }
  };

  const isInitialized =
    preferences !== null && defaults !== null && validationInfo !== null;

  return {
    initialize,
    isInitialized,
    isLoading,
    error,
    preferences,
    defaults,
    validationInfo,
  };
};

// Hook pour les actions de préférences avec gestion d'erreurs intégrée
export const usePreferencesActions = () => {
  const {
    updatePreferences,
    resetToDefaults,
    clearError,
    isSaving,
    error,
    lastSaved,
  } = usePreferencesStore();

  const updateWithNotification = async (
    preferences: TradingPreferencesUpdate,
    onSuccess?: (preferences: TradingPreferences) => void,
    onError?: (error: string) => void
  ) => {
    try {
      await updatePreferences(preferences);
      onSuccess?.(usePreferencesStore.getState().preferences!);
    } catch (error: any) {
      const errorMessage =
        error.response?.data?.detail || 'Erreur lors de la sauvegarde';
      onError?.(errorMessage);
    }
  };

  const resetWithConfirmation = async (
    onSuccess?: () => void,
    onError?: (error: string) => void
  ) => {
    if (
      window.confirm(
        'Êtes-vous sûr de vouloir réinitialiser toutes vos préférences aux valeurs par défaut ?'
      )
    ) {
      try {
        await resetToDefaults();
        onSuccess?.();
      } catch (error: any) {
        const errorMessage =
          error.response?.data?.detail || 'Erreur lors de la réinitialisation';
        onError?.(errorMessage);
      }
    }
  };

  return {
    updateWithNotification,
    resetWithConfirmation,
    clearError,
    isSaving,
    error,
    lastSaved,
  };
};

export default usePreferencesStore;
