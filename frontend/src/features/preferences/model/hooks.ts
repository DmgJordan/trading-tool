import { useCallback, useRef } from 'react';
import { usePreferencesStore } from './store';
import type { TradingPreferences, TradingPreferencesUpdate } from './types';

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

  const initialize = useCallback(async () => {
    try {
      await Promise.all([
        loadPreferences(),
        loadDefaults(),
        loadValidationInfo(),
      ]);
    } catch (err) {
      console.error("Erreur lors de l'initialisation des préférences:", err);
    }
  }, [loadPreferences, loadDefaults, loadValidationInfo]);

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

export const usePreferencesActions = () =>
  usePreferencesStore(state => ({
    updatePreferences: state.updatePreferences,
    resetToDefaults: state.resetToDefaults,
    clearError: state.clearError,
    isSaving: state.isSaving,
    error: state.error,
    lastSaved: state.lastSaved,
  }));

export const useAutoSavePreferences = (delay: number = 3000) => {
  const updatePreferences = usePreferencesStore(
    state => state.updatePreferences
  );
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const debouncedUpdate = useCallback(
    (data: TradingPreferences | TradingPreferencesUpdate) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        updatePreferences(data as TradingPreferencesUpdate).catch(error => {
          console.error('Erreur lors de la sauvegarde automatique:', error);
        });
      }, delay);
    },
    [delay, updatePreferences]
  );

  return { debouncedUpdate };
};
