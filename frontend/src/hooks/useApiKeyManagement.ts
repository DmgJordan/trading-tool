import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '@/features/auth/model/store';
import { authApi } from '@/services/api/auth.api';
import http from '@/services/http/client';
import { useNotifications } from './useNotifications';

// Types
type ApiService = 'hyperliquid' | 'anthropic' | 'coingecko';
type TestResult = {
  status: 'success' | 'error' | 'testing' | null;
  message: string;
};

// Schéma de validation
const apiKeysSchema = z.object({
  hyperliquid_api_key: z.string().optional(),
  hyperliquid_public_address: z.string().optional(),
  anthropic_api_key: z.string().optional(),
  coingecko_api_key: z.string().optional(),
});

type ApiKeysFormData = z.infer<typeof apiKeysSchema>;

const API_NAMES: Record<ApiService, string> = {
  hyperliquid: 'Hyperliquid',
  anthropic: 'Anthropic',
  coingecko: 'CoinGecko',
};

/**
 * Hook personnalisé pour gérer les clés API
 * Centralise toute la logique de gestion des clés API
 */
export const useApiKeyManagement = () => {
  const { user, setUser } = useAuthStore();
  const { success, error: notifyError } = useNotifications();

  // États pour les tests
  const [testResults, setTestResults] = useState<
    Record<ApiService, TestResult>
  >({
    hyperliquid: { status: null, message: '' },
    anthropic: { status: null, message: '' },
    coingecko: { status: null, message: '' },
  });

  // États pour la sauvegarde
  const [isSaving, setIsSaving] = useState<Record<ApiService, boolean>>({
    hyperliquid: false,
    anthropic: false,
    coingecko: false,
  });

  // État pour la visibilité des clés
  const [showKeys, setShowKeys] = useState<Record<ApiService, boolean>>({
    hyperliquid: false,
    anthropic: false,
    coingecko: false,
  });

  // Formulaire
  const { register, getValues, setValue, watch } = useForm<ApiKeysFormData>({
    resolver: zodResolver(apiKeysSchema),
  });

  // Tester une clé stockée (utilise la clé chiffrée en DB)
  const testStoredApiKey = useCallback(
    async (apiType: ApiService) => {
      const statusKey = `${apiType}_api_key_status` as const;
      const isConfigured = user?.[statusKey] === 'configured';

      if (!isConfigured) {
        setTestResults(prev => ({
          ...prev,
          [apiType]: {
            status: 'error',
            message: `Aucune clé ${API_NAMES[apiType]} configurée`,
          },
        }));
        return;
      }

      setIsSaving(prev => ({ ...prev, [apiType]: true }));
      setTestResults(prev => ({
        ...prev,
        [apiType]: { status: 'testing', message: 'Test en cours...' },
      }));

      try {
        const response = await http.post<{ status: string; message?: string }>(
          `/users/me/api-keys/test-stored/${apiType}`,
          {},
          { auth: true }
        );

        setTestResults(prev => ({
          ...prev,
          [apiType]: {
            status: response.status === 'success' ? 'success' : 'error',
            message: response.message || 'Connexion réussie !',
          },
        }));

        if (response.status === 'success') {
          success(`Test ${API_NAMES[apiType]} réussi !`);
        }
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'Erreur de connexion';

        setTestResults(prev => ({
          ...prev,
          [apiType]: { status: 'error', message },
        }));

        notifyError(`Test ${API_NAMES[apiType]} échoué: ${message}`);
      } finally {
        setIsSaving(prev => ({ ...prev, [apiType]: false }));
      }
    },
    [user, success, notifyError]
  );

  // Toggle visibilité d'une clé
  const toggleKeyVisibility = useCallback((service: ApiService) => {
    setShowKeys(prev => ({ ...prev, [service]: !prev[service] }));
  }, []);

  // Sauvegarder une clé API
  const saveApiKey = useCallback(
    async (apiType: ApiService) => {
      const values = getValues();
      setIsSaving(prev => ({ ...prev, [apiType]: true }));

      try {
        let payload: Record<string, string | undefined> = {};

        if (apiType === 'hyperliquid') {
          if (values.hyperliquid_api_key?.trim()) {
            payload.hyperliquid_api_key = values.hyperliquid_api_key.trim();
          }
          if (values.hyperliquid_public_address?.trim()) {
            payload.hyperliquid_public_address =
              values.hyperliquid_public_address.trim();
          }

          if (Object.keys(payload).length === 0) {
            notifyError(
              "Veuillez renseigner la clé API ou l'adresse publique Hyperliquid"
            );
            return;
          }
        } else {
          const apiKey =
            apiType === 'anthropic'
              ? values.anthropic_api_key
              : values.coingecko_api_key;

          if (!apiKey?.trim()) {
            notifyError('Veuillez renseigner une clé API');
            return;
          }

          payload = { [`${apiType}_api_key`]: apiKey.trim() };
        }

        await http.put('/users/me/api-keys', payload, { auth: true });

        const successMessage =
          apiType === 'hyperliquid'
            ? 'Configuration Hyperliquid sauvegardée !'
            : `Clé API ${API_NAMES[apiType]} sauvegardée !`;

        success(successMessage);

        // Recharger les données utilisateur
        const updatedUser = await authApi.getMe();
        setUser(updatedUser);
      } catch (error) {
        notifyError(
          `Erreur lors de la sauvegarde: ${error instanceof Error ? error.message : 'Erreur inconnue'}`
        );
      } finally {
        setIsSaving(prev => ({ ...prev, [apiType]: false }));
      }
    },
    [getValues, setUser, success, notifyError]
  );

  // Tester une nouvelle clé API (non sauvegardée)
  const testApiConnection = useCallback(
    async (apiType: ApiService) => {
      const values = getValues();
      const apiKey =
        apiType === 'hyperliquid'
          ? values.hyperliquid_api_key
          : apiType === 'anthropic'
            ? values.anthropic_api_key
            : values.coingecko_api_key;

      if (!apiKey?.trim()) {
        setTestResults(prev => ({
          ...prev,
          [apiType]: {
            status: 'error',
            message: 'Veuillez renseigner une clé API',
          },
        }));
        return;
      }

      setIsSaving(prev => ({ ...prev, [apiType]: true }));
      setTestResults(prev => ({
        ...prev,
        [apiType]: { status: 'testing', message: 'Test en cours...' },
      }));

      try {
        const response = await http.post<{ status: string; message?: string }>(
          `/users/me/api-keys/test`,
          { api_key: apiKey, api_type: apiType },
          { auth: true }
        );

        setTestResults(prev => ({
          ...prev,
          [apiType]: {
            status: response.status === 'success' ? 'success' : 'error',
            message: response.message || 'Connexion réussie !',
          },
        }));

        if (response.status === 'success') {
          success(`Test ${API_NAMES[apiType]} réussi !`);
        }
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'Erreur de connexion';

        setTestResults(prev => ({
          ...prev,
          [apiType]: { status: 'error', message },
        }));

        notifyError(`Test ${API_NAMES[apiType]} échoué: ${message}`);
      } finally {
        setIsSaving(prev => ({ ...prev, [apiType]: false }));
      }
    },
    [getValues, success, notifyError]
  );

  return {
    // État
    user,
    testResults,
    isSaving,
    showKeys,

    // Formulaire
    register,
    getValues,
    setValue,
    watch,

    // Actions
    toggleKeyVisibility,
    saveApiKey,
    testApiConnection,
    testStoredApiKey,
  };
};
