'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuthStore } from '../store/authStore';
import { authApi } from '../lib/api/auth';
import apiClient from '../lib/api/client';

const apiKeysSchema = z.object({
  hyperliquid_api_key: z.string().optional(),
  hyperliquid_public_address: z.string().optional(),
  anthropic_api_key: z.string().optional(),
  coingecko_api_key: z.string().optional(),
});

type ApiKeysFormData = z.infer<typeof apiKeysSchema>;

interface ApiTestResult {
  status: 'success' | 'error' | 'testing' | null;
  message: string;
}

export default function ApiKeysConfiguration() {
  const [hyperliquidResult, setHyperliquidResult] = useState<ApiTestResult>({ status: null, message: '' });
  const [anthropicResult, setAnthropicResult] = useState<ApiTestResult>({ status: null, message: '' });
  const [coingeckoResult, setCoingeckoResult] = useState<ApiTestResult>({ status: null, message: '' });
  const [isHelpModalOpen, setIsHelpModalOpen] = useState<string | null>(null);
  const [showKeys, setShowKeys] = useState({ hyperliquid: false, anthropic: false, coingecko: false });
  const [isSaving, setIsSaving] = useState({ hyperliquid: false, anthropic: false, coingecko: false });
  const { user, setUser } = useAuthStore();

  const {
    register,
    getValues,
    setValue,
  } = useForm<ApiKeysFormData>({
    resolver: zodResolver(apiKeysSchema),
  });

  // Charger les clés masquées quand l'utilisateur est chargé
  useEffect(() => {
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

  const saveApiKey = async (apiType: 'hyperliquid' | 'anthropic' | 'coingecko') => {
    const values = getValues();

    setIsSaving(prev => ({ ...prev, [apiType]: true }));

    try {
      let payload: Record<string, string | undefined> = {};

      if (apiType === 'hyperliquid') {
        if (values.hyperliquid_api_key?.trim()) {
          payload.hyperliquid_api_key = values.hyperliquid_api_key.trim();
        }

        if (values.hyperliquid_public_address !== undefined) {
          payload.hyperliquid_public_address = values.hyperliquid_public_address.trim();
        }

        if (Object.keys(payload).length === 0) {
          alert('Veuillez renseigner la clé API ou l\'adresse publique Hyperliquid avant de sauvegarder.');
          return;
        }
      } else {
        const apiKey = apiType === 'anthropic' ? values.anthropic_api_key : values.coingecko_api_key;
        if (!apiKey?.trim()) {
          alert('Veuillez renseigner une clé API avant de sauvegarder.');
          return;
        }
        payload = { [`${apiType}_api_key`]: apiKey.trim() };
      }

      await apiClient.put('/users/me/api-keys', payload);

      const apiNames = {
        hyperliquid: 'Hyperliquid',
        anthropic: 'Anthropic',
        coingecko: 'CoinGecko'
      } as const;

      const successMessage = apiType === 'hyperliquid'
        ? 'Configuration Hyperliquid sauvegardée avec succès !'
        : `Clé API ${apiNames[apiType]} sauvegardée avec succès !`;

      alert(successMessage);

      // Recharger les informations utilisateur pour obtenir les clés masquées
      try {
        const updatedUser = await authApi.getMe();
        setUser(updatedUser);
      } catch (error) {
        console.error('Erreur lors du rechargement des données utilisateur:', error);
      }
    } catch (error) {
      alert(`Erreur lors de la sauvegarde: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
    } finally {
      setIsSaving(prev => ({ ...prev, [apiType]: false }));
    }
  };

  const testApiConnection = async (apiType: 'hyperliquid' | 'anthropic' | 'coingecko') => {
    const values = getValues();
    const apiKey = apiType === 'hyperliquid' ? values.hyperliquid_api_key :
                   apiType === 'anthropic' ? values.anthropic_api_key : values.coingecko_api_key;

    const isStoredKey = apiType === 'hyperliquid'
      ? user?.hyperliquid_api_key_status === 'configured' && apiKey?.includes('••••••••')
      : apiType === 'anthropic'
      ? user?.anthropic_api_key_status === 'configured' && apiKey?.includes('••••••••')
      : user?.coingecko_api_key_status === 'configured' && apiKey?.includes('••••••••');

    // Si pas de clé saisie et pas de clé enregistrée
    if (!apiKey?.trim() && !isStoredKey) {
      const setter = apiType === 'hyperliquid' ? setHyperliquidResult :
                     apiType === 'anthropic' ? setAnthropicResult : setCoingeckoResult;
      setter({ status: 'error', message: 'Veuillez saisir une clé API avant de tester.' });
      return;
    }

    const setter = apiType === 'hyperliquid' ? setHyperliquidResult :
                   apiType === 'anthropic' ? setAnthropicResult : setCoingeckoResult;
    setter({ status: 'testing', message: 'Test de connexion en cours...' });

    try {
      let endpoint;
      let requestBody;

      if (isStoredKey) {
        // Utiliser les endpoints pour les clés stockées
        endpoint = apiType === 'hyperliquid' ? 'test-hyperliquid-stored' :
                   apiType === 'anthropic' ? 'test-anthropic-stored' : 'test-coingecko-stored';
        requestBody = apiType === 'hyperliquid'
          ? { private_key: '', use_testnet: false }  // private_key sera ignoré car on utilise la clé stockée
          : {};
      } else {
        // Utiliser les endpoints classiques avec la nouvelle clé
        endpoint = apiType === 'hyperliquid' ? 'test-hyperliquid' :
                   apiType === 'anthropic' ? 'test-anthropic' : 'test-coingecko';
        requestBody = apiType === 'hyperliquid'
          ? { private_key: apiKey, use_testnet: false }
          : { api_key: apiKey };
      }

      const response = await apiClient.post(`/connectors/${endpoint}`, requestBody);
      setter({ status: 'success', message: response.data.message || 'Connexion réussie !' });
    } catch (error) {
      setter({ status: 'error', message: `Erreur de connexion: ${error instanceof Error ? error.message : 'Connexion échouée'}` });
    }
  };

  const getStatusIcon = (status: 'success' | 'error' | 'testing' | null) => {
    switch (status) {
      case 'success':
        return <span className="text-green-600 text-xl font-bold">✓</span>;
      case 'error':
        return <span className="text-red-600 text-xl font-bold">✗</span>;
      case 'testing':
        return <span className="text-blue-600 text-xl animate-spin">⟳</span>;
      default:
        return null;
    }
  };

  const HelpModal = ({ apiType, isOpen, onClose }: { apiType: string; isOpen: boolean; onClose: () => void }) => {
    if (!isOpen) return null;

    const content = {
      hyperliquid: {
        title: 'Configuration Hyperliquid API',
        steps: [
          '1. Connectez-vous à Hyperliquid, ouvrez la section « API Keys » et créez une clé Blaze.',
          '2. Copiez la clé privée générée (agent wallet) et collez-la dans le champ « Clé privée API ». Elle sert à signer les ordres.',
          '3. Cliquez sur « Copy API Wallet Address » pour récupérer l’adresse publique affichée en haut de la section et collez-la dans « Adresse publique Hyperliquid ».',
          '4. Assurez-vous de transférer des fonds vers votre API wallet depuis Hyperliquid si nécessaire.',
          '5. Sauvegardez les informations ci-dessous puis testez la connexion.'
        ]
      },
      anthropic: {
        title: 'Configuration Anthropic API',
        steps: [
          '1. Connectez-vous à votre console Anthropic',
          '2. Allez dans la section "API Keys"',
          '3. Créez une nouvelle clé API',
          '4. Copiez la clé et collez-la dans le champ ci-dessous',
          '5. Assurez-vous d\'avoir des crédits suffisants'
        ]
      },
      coingecko: {
        title: 'Configuration CoinGecko API',
        steps: [
          '1. Connectez-vous à votre compte CoinGecko Pro',
          '2. Allez dans la section "Developer Dashboard"',
          '3. Naviguez vers "API Keys"',
          '4. Créez une nouvelle clé API ou utilisez celle existante',
          '5. Copiez la clé (format CG-xxxxx) et collez-la ci-dessous'
        ]
      }
    };

    const info = content[apiType as keyof typeof content];

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl max-w-md w-full p-6 border-2 border-black">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-black">{info?.title}</h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-black text-2xl font-bold"
            >
              ×
            </button>
          </div>
          <div className="space-y-2">
            {info?.steps.map((step, index) => (
              <p key={index} className="text-gray-700">{step}</p>
            ))}
          </div>
          <div className="mt-6">
            <button
              onClick={onClose}
              className="w-full px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-black mb-2">
          Configuration des Clés API
        </h2>
        <p className="text-gray-600">
          Configurez vos clés API pour activer les fonctionnalités de trading.
        </p>
      </div>

      <form className="space-y-8">
        {/* Hyperliquid API */}
        <div className="p-6 rounded-xl border-2 border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <h3 className="text-lg font-semibold text-black">Hyperliquid API</h3>
              {user?.hyperliquid_api_key_status === 'configured' && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Configurée
                </span>
              )}
              <button
                type="button"
                onClick={() => setIsHelpModalOpen('hyperliquid')}
                className="text-gray-500 hover:text-black text-sm font-medium underline"
              >
                Aide
              </button>
            </div>
            {getStatusIcon(hyperliquidResult.status)}
          </div>

          <div className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-black">
                Clé privée API Hyperliquid (agent wallet)
              </label>
              <div className="relative">
                <input
                  {...register('hyperliquid_api_key')}
                  type={showKeys.hyperliquid ? 'text' : 'password'}
                  placeholder={user?.hyperliquid_api_key_status === 'configured' ? "Clé configurée (masquée pour la sécurité)" : "Collez la clé privée reçue lors de la création de la clé Blaze"}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(prev => ({ ...prev, hyperliquid: !prev.hyperliquid }))}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-black"
                >
                  {showKeys.hyperliquid ? '👁️' : '🙈'}
                </button>
              </div>
              <p className="text-xs text-gray-500">
                Cette clé permet de signer les ordres depuis le Trading Tool. Elle n&apos;autorise pas les retraits.
              </p>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-semibold text-black">
                Adresse publique Hyperliquid (wallet principal)
              </label>
              <input
                {...register('hyperliquid_public_address')}
                type="text"
                placeholder="Ex. 0x1234..."
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none"
              />
              <p className="text-xs text-gray-500">
                Utilisée pour récupérer votre portefeuille et vos positions. Elle correspond à l&apos;adresse affichée dans Hyperliquid, section API.
              </p>
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => saveApiKey('hyperliquid')}
                disabled={isSaving.hyperliquid}
                className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {isSaving.hyperliquid ? 'Sauvegarde...' : 'Sauvegarder'}
              </button>
              <button
                type="button"
                onClick={() => testApiConnection('hyperliquid')}
                disabled={hyperliquidResult.status === 'testing'}
                className="px-4 py-2 border-2 border-black text-black rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {hyperliquidResult.status === 'testing' ? 'Test...' : 'Tester'}
              </button>
            </div>

            {hyperliquidResult.message && (
              <div className={`p-3 rounded-lg border-2 ${
                hyperliquidResult.status === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
                hyperliquidResult.status === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
                'bg-blue-50 border-blue-200 text-blue-800'
              }`}>
                <p className="text-sm font-medium">{hyperliquidResult.message}</p>
              </div>
            )}
          </div>
        </div>

        {/* Anthropic API */}
        <div className="p-6 rounded-xl border-2 border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <h3 className="text-lg font-semibold text-black">Anthropic API</h3>
              {user?.anthropic_api_key_status === 'configured' && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Configurée
                </span>
              )}
              <button
                type="button"
                onClick={() => setIsHelpModalOpen('anthropic')}
                className="text-gray-500 hover:text-black text-sm font-medium underline"
              >
                Aide
              </button>
            </div>
            {getStatusIcon(anthropicResult.status)}
          </div>

          <div className="space-y-4">
            <div className="relative">
              <input
                {...register('anthropic_api_key')}
                type={showKeys.anthropic ? 'text' : 'password'}
                placeholder={user?.anthropic_api_key_status === 'configured' ? "Clé configurée (masquée pour la sécurité)" : "Entrez votre clé API Anthropic"}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowKeys(prev => ({ ...prev, anthropic: !prev.anthropic }))}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-black"
              >
                {showKeys.anthropic ? '👁️' : '🙈'}
              </button>
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => saveApiKey('anthropic')}
                disabled={isSaving.anthropic}
                className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {isSaving.anthropic ? 'Sauvegarde...' : 'Sauvegarder'}
              </button>
              <button
                type="button"
                onClick={() => testApiConnection('anthropic')}
                disabled={anthropicResult.status === 'testing'}
                className="px-4 py-2 border-2 border-black text-black rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {anthropicResult.status === 'testing' ? 'Test...' : 'Tester'}
              </button>
            </div>

            {anthropicResult.message && (
              <div className={`p-3 rounded-lg border-2 ${
                anthropicResult.status === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
                anthropicResult.status === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
                'bg-blue-50 border-blue-200 text-blue-800'
              }`}>
                <p className="text-sm font-medium">{anthropicResult.message}</p>
              </div>
            )}
          </div>
        </div>

        {/* CoinGecko API */}
        <div className="p-6 rounded-xl border-2 border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <h3 className="text-lg font-semibold text-black">CoinGecko API</h3>
              {user?.coingecko_api_key_status === 'configured' && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                  Configurée
                </span>
              )}
              <button
                type="button"
                onClick={() => setIsHelpModalOpen('coingecko')}
                className="text-gray-500 hover:text-black text-sm font-medium underline"
              >
                Aide
              </button>
            </div>
            {getStatusIcon(coingeckoResult.status)}
          </div>

          <div className="space-y-4">
            <div className="relative">
              <input
                {...register('coingecko_api_key')}
                type={showKeys.coingecko ? 'text' : 'password'}
                placeholder={user?.coingecko_api_key_status === 'configured' ? "Clé configurée (masquée pour la sécurité)" : "Entrez votre clé API CoinGecko"}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-black focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowKeys(prev => ({ ...prev, coingecko: !prev.coingecko }))}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-black"
              >
                {showKeys.coingecko ? '👁️' : '🙈'}
              </button>
            </div>

            <div className="flex space-x-3">
              <button
                type="button"
                onClick={() => saveApiKey('coingecko')}
                disabled={isSaving.coingecko}
                className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {isSaving.coingecko ? 'Sauvegarde...' : 'Sauvegarder'}
              </button>
              <button
                type="button"
                onClick={() => testApiConnection('coingecko')}
                disabled={coingeckoResult.status === 'testing'}
                className="px-4 py-2 border-2 border-black text-black rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {coingeckoResult.status === 'testing' ? 'Test...' : 'Tester'}
              </button>
            </div>

            {coingeckoResult.message && (
              <div className={`p-3 rounded-lg border-2 ${
                coingeckoResult.status === 'success' ? 'bg-green-50 border-green-200 text-green-800' :
                coingeckoResult.status === 'error' ? 'bg-red-50 border-red-200 text-red-800' :
                'bg-blue-50 border-blue-200 text-blue-800'
              }`}>
                <p className="text-sm font-medium">{coingeckoResult.message}</p>
              </div>
            )}
          </div>
        </div>
      </form>

      {/* Modales d'aide */}
      <HelpModal
        apiType="hyperliquid"
        isOpen={isHelpModalOpen === 'hyperliquid'}
        onClose={() => setIsHelpModalOpen(null)}
      />
      <HelpModal
        apiType="anthropic"
        isOpen={isHelpModalOpen === 'anthropic'}
        onClose={() => setIsHelpModalOpen(null)}
      />
      <HelpModal
        apiType="coingecko"
        isOpen={isHelpModalOpen === 'coingecko'}
        onClose={() => setIsHelpModalOpen(null)}
      />
    </div>
  );
}
