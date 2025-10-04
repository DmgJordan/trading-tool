import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  TradingPreferences,
  TradingPreferencesUpdate,
  PreferencesState,
  PreferencesActions,
} from './types';
import { preferencesApi } from '@/services/api/preferences.api';

interface PreferencesStore extends PreferencesState, PreferencesActions {}

export const usePreferencesStore = create<PreferencesStore>()(
  persist(
    (set, get) => ({
      preferences: null,
      defaults: null,
      validationInfo: null,
      isLoading: false,
      isSaving: false,
      error: null,
      lastSaved: null,

      async loadPreferences() {
        try {
          set({ isLoading: true, error: null });
          const preferences = await preferencesApi.getPreferences();
          set({ preferences, isLoading: false });
        } catch (error) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors du chargement des préférences';
          set({ isLoading: false, error: errorMessage });
          throw error;
        }
      },

      async loadDefaults() {
        try {
          const defaults = await preferencesApi.getDefaults();
          set({ defaults, error: null });
        } catch (error) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail ||
            'Erreur lors du chargement des valeurs par défaut';
          set({ error: errorMessage });
          throw error;
        }
      },

      async loadValidationInfo() {
        try {
          const validationInfo = await preferencesApi.getValidationInfo();
          set({ validationInfo, error: null });
        } catch (error) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail ||
            'Erreur lors du chargement des informations de validation';
          set({ error: errorMessage });
          throw error;
        }
      },

      async updatePreferences(preferencesUpdate: TradingPreferencesUpdate) {
        try {
          set({ isSaving: true, error: null });

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
        } catch (error) {
          const currentPreferences = get().preferences;
          if (currentPreferences) {
            const revertedPreferences = { ...currentPreferences } as Record<
              string,
              unknown
            >;
            Object.keys(preferencesUpdate).forEach(key => {
              delete revertedPreferences[key];
            });
            set({
              preferences: revertedPreferences as unknown as TradingPreferences,
            });
          }

          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors de la sauvegarde des préférences';
          set({ isSaving: false, error: errorMessage });
          throw error;
        }
      },

      async resetToDefaults() {
        try {
          set({ isSaving: true, error: null });

          const response = await preferencesApi.resetToDefaults();

          set({
            preferences: response.preferences,
            isSaving: false,
            error: null,
            lastSaved: new Date().toISOString(),
          });
        } catch (error) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors de la réinitialisation';
          set({ isSaving: false, error: errorMessage });
          throw error;
        }
      },

      clearError() {
        set({ error: null });
      },
    }),
    {
      name: 'preferences-store',
      storage: createJSONStorage(() => localStorage),
      partialize: state => ({
        preferences: state.preferences,
        defaults: state.defaults,
        validationInfo: state.validationInfo,
        lastSaved: state.lastSaved,
      }),
    }
  )
);
