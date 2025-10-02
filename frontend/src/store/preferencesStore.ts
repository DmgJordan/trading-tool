import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  TradingPreferences,
  TradingPreferencesUpdate,
  PreferencesState,
  PreferencesActions,
} from '@/lib/types/preferences';
import { preferencesApi } from '@/lib/api/preferences';

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
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors du chargement des préférences';
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
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail ||
            'Erreur lors du chargement des valeurs par défaut';
          set({ error: errorMessage });
          throw error;
        }
      },

      loadValidationInfo: async () => {
        try {
          const validationInfo = await preferencesApi.getValidationInfo();
          set({ validationInfo, error: null });
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail ||
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
        } catch (error: unknown) {
          // Revert optimistic update en cas d'erreur
          const { preferences: currentPreferences } = get();
          if (currentPreferences) {
            // Recalculer l'état précédent en retirant les modifications optimistes
            const revertedPreferences = { ...currentPreferences };
            Object.keys(preferencesUpdate).forEach(key => {
              delete (revertedPreferences as Record<string, unknown>)[key];
            });
            set({ preferences: revertedPreferences });
          }

          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors de la sauvegarde des préférences';
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
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors de la réinitialisation';
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

// Note: Les hooks useAutoSavePreferences, useInitializePreferences et usePreferencesActions
// ont été déplacés vers src/hooks/usePreferences.ts pour une meilleure organisation

export default usePreferencesStore;
