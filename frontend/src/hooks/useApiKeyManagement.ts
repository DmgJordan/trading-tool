import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '@/store/authStore';
import { authApi } from '@/lib/api/auth';
import apiClient from '@/lib/api/client';
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
  const [testResults, setTestResults] = useState<Record<ApiService, TestResult>>({
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

  // Charger les clés masquées
  const loadMaskedKeys = useCallback(() => {
    if (user?.hyperliquid_api_key_status === 'configured') {
      setValue('hyperliquid_api_key', user.hyperliquid_api_key || '');
    }
    if (user?.hyperliquid_public_address) {
      setValue('hyperliquid_public_address', user.hyperliquid_public_address);
    }
    if (user?.anthropic_api_key_status === 'configured') {
      setValue('anthropic_api_key', user.anthropic_api_key || '');
    }
    if (user?.coingecko_api_key_status === 'configured') {
      setValue('coingecko_api_key', user.coingecko_api_key || '');
    }
  }, [user, setValue]);

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
            payload.hyperliquid_public_address = values.hyperliquid_public_address.trim();
          }

          if (Object.keys(payload).length === 0) {
            notifyError("Veuillez renseigner la clé API ou l'adresse publique Hyperliquid");
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

        await apiClient.put('/users/me/api-keys', payload);

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

  // Tester une connexion API
  const testApiConnection = useCallback(
    async (apiType: ApiService) => {
      const values = getValues();
      const apiKey =
        apiType === 'hyperliquid'
          ? values.hyperliquid_api_key
          : apiType === 'anthropic'
            ? values.anthropic_api_key
            : values.coingecko_api_key;

      const isStoredKey =
        apiType === 'hyperliquid'
          ? user?.hyperliquid_api_key_status === 'configured' && apiKey?.includes('••••')
          : apiType === 'anthropic'
            ? user?.anthropic_api_key_status === 'configured' && apiKey?.includes('••••')
            : user?.coingecko_api_key_status === 'configured' && apiKey?.includes('••••');

      if (!apiKey?.trim() && !isStoredKey) {
        setTestResults(prev => ({
          ...prev,
          [apiType]: {
            status: 'error',
            message: 'Veuillez renseigner une clé API',
          },
        }));
        return;
      }

      setTestResults(prev => ({
        ...prev,
        [apiType]: { status: 'testing', message: 'Test en cours...' },
      }));

      try {
        const endpoint = isStoredKey
          ? `/connectors/test-${apiType}-stored`
          : `/connectors/test-${apiType}`;

        const requestData = isStoredKey
          ? {}
          : apiType === 'hyperliquid'
            ? { api_key: values.hyperliquid_api_key }
            : { api_key: apiKey };

        const response = await apiClient.post<{ status: string; message?: string }>(endpoint, requestData);

        setTestResults(prev => ({
          ...prev,
          [apiType]: {
            status: response.data.status === 'success' ? 'success' : 'error',
            message: response.data.message || 'Connexion réussie !',
          },
        }));

        if (response.data.status === 'success') {
          success(`Connexion ${API_NAMES[apiType]} réussie !`);
        }
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'Erreur de connexion';

        setTestResults(prev => ({
          ...prev,
          [apiType]: { status: 'error', message },
        }));

        notifyError(`Test ${API_NAMES[apiType]} échoué: ${message}`);
      }
    },
    [getValues, user, success, notifyError]
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
    loadMaskedKeys,
    toggleKeyVisibility,
    saveApiKey,
    testApiConnection,
  };
};
