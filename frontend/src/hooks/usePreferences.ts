import { useEffect } from 'react';
import { usePreferencesStore } from '../store/preferencesStore';
import type { TradingPreferences, TradingPreferencesUpdate } from '../lib/types/preferences';

/**
 * Hook pour initialiser et charger les préférences utilisateur
 * Gère le chargement initial des préférences, defaults et validation info
 */
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

/**
 * Hook pour les actions de préférences avec gestion d'erreurs
 */
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
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { detail?: string } } }).response?.data
          ?.detail || 'Erreur lors de la sauvegarde';
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
      } catch (error: unknown) {
        const errorMessage =
          (error as { response?: { data?: { detail?: string } } }).response
            ?.data?.detail || 'Erreur lors de la réinitialisation';
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

/**
 * Hook pour l'auto-save avec debounce
 */
export const useAutoSavePreferences = (delayMs: number = 2000) => {
  const { updatePreferences } = usePreferencesStore();

  const debouncedUpdate = (preferences: TradingPreferencesUpdate) => {
    const timeoutId = setTimeout(async () => {
      try {
        await updatePreferences(preferences);
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, delayMs);

    // Cleanup
    return () => clearTimeout(timeoutId);
  };

  return { debouncedUpdate };
};
