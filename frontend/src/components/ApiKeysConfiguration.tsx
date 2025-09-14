'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const apiKeysSchema = z.object({
  hyperliquid_api_key: z.string().optional(),
  anthropic_api_key: z.string().optional(),
});

type ApiKeysFormData = z.infer<typeof apiKeysSchema>;

interface ApiTestResult {
  status: 'success' | 'error' | 'testing' | null;
  message: string;
}

export default function ApiKeysConfiguration() {
  const [hyperliquidResult, setHyperliquidResult] = useState<ApiTestResult>({ status: null, message: '' });
  const [anthropicResult, setAnthropicResult] = useState<ApiTestResult>({ status: null, message: '' });
  const [isHelpModalOpen, setIsHelpModalOpen] = useState<string | null>(null);
  const [showKeys, setShowKeys] = useState({ hyperliquid: false, anthropic: false });
  const [isSaving, setIsSaving] = useState({ hyperliquid: false, anthropic: false });

  const {
    register,
    getValues,
  } = useForm<ApiKeysFormData>({
    resolver: zodResolver(apiKeysSchema),
  });

  const saveApiKey = async (apiType: 'hyperliquid' | 'anthropic') => {
    const values = getValues();
    const apiKey = apiType === 'hyperliquid' ? values.hyperliquid_api_key : values.anthropic_api_key;

    if (!apiKey?.trim()) {
      return;
    }

    setIsSaving(prev => ({ ...prev, [apiType]: true }));

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users/me/api-keys`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${JSON.parse(localStorage.getItem('auth_tokens') || '{}').access_token}`,
        },
        body: JSON.stringify({
          [apiType + '_api_key']: apiKey
        }),
      });

      if (response.ok) {
        alert(`Clé API ${apiType === 'hyperliquid' ? 'Hyperliquid' : 'Anthropic'} sauvegardée avec succès !`);
      } else {
        throw new Error(`Erreur ${response.status}`);
      }
    } catch (error) {
      alert(`Erreur lors de la sauvegarde: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
    } finally {
      setIsSaving(prev => ({ ...prev, [apiType]: false }));
    }
  };

  const testApiConnection = async (apiType: 'hyperliquid' | 'anthropic') => {
    const values = getValues();
    const apiKey = apiType === 'hyperliquid' ? values.hyperliquid_api_key : values.anthropic_api_key;

    if (!apiKey?.trim()) {
      const setter = apiType === 'hyperliquid' ? setHyperliquidResult : setAnthropicResult;
      setter({ status: 'error', message: 'Veuillez saisir une clé API avant de tester.' });
      return;
    }

    const setter = apiType === 'hyperliquid' ? setHyperliquidResult : setAnthropicResult;
    setter({ status: 'testing', message: 'Test de connexion en cours...' });

    try {
      const endpoint = apiType === 'hyperliquid' ? 'test-hyperliquid' : 'test-anthropic';
      const requestBody = apiType === 'hyperliquid'
        ? { private_key: apiKey, use_testnet: false }
        : { api_key: apiKey };

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/connectors/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${JSON.parse(localStorage.getItem('auth_tokens') || '{}').access_token}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const data = await response.json();
        setter({ status: 'success', message: data.message || 'Connexion réussie !' });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Erreur ${response.status}`);
      }
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
          '1. Connectez-vous à votre compte Hyperliquid',
          '2. Allez dans les paramètres de votre compte',
          '3. Naviguez vers la section "API Keys"',
          '4. Créez une nouvelle clé API avec les permissions de lecture',
          '5. Copiez la clé et collez-la dans le champ ci-dessous'
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

          <div className="space-y-4">
            <div className="relative">
              <input
                {...register('hyperliquid_api_key')}
                type={showKeys.hyperliquid ? 'text' : 'password'}
                placeholder="Entrez votre clé API Hyperliquid"
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
                placeholder="Entrez votre clé API Anthropic"
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
    </div>
  );
}