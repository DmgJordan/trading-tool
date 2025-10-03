'use client';

import { useEffect } from 'react';
import { useApiKeyManagement } from '@/hooks';
import { API_SERVICES } from '@/constants/trading';
import { getStatusColor, getStatusIcon } from '@/utils/ui';

export default function ApiKeysConfiguration() {
  const {
    user,
    testResults,
    isSaving,
    showKeys,
    register,
    loadMaskedKeys,
    toggleKeyVisibility,
    saveApiKey,
    testApiConnection,
  } = useApiKeyManagement();

  useEffect(() => {
    loadMaskedKeys();
  }, [loadMaskedKeys]);

  const renderApiKeySection = (
    service: 'anthropic' | 'hyperliquid' | 'coingecko',
    label: string,
    description: string,
    required: boolean = false
  ) => {
    const fieldName = `${service}_api_key` as const;
    const testResult = testResults[service];
    const isTestingKey = isSaving[service];
    const showKey = showKeys[service];
    const statusKey = `${service}_api_key_status` as const;
    const isConfigured = user?.[statusKey] === 'configured';

    return (
      <div key={service} className="bg-white rounded-xl shadow-lg border-2 border-black p-6">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xl font-bold text-black">
              {label}
              {required && <span className="text-red-600 ml-1">*</span>}
            </h3>
            {isConfigured && (
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                ✓ Configurée
              </span>
            )}
          </div>
          <p className="text-gray-600 text-sm">{description}</p>
        </div>

        <div className="space-y-4">
          {/* Champ clé API */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Clé API
            </label>
            <div className="relative">
              <input
                {...register(fieldName)}
                type={showKey ? 'text' : 'password'}
                className="w-full p-3 pr-24 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
                placeholder={`sk-${service}-...`}
              />
              <button
                type="button"
                onClick={() => toggleKeyVisibility(service)}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 text-sm text-gray-600 hover:text-black"
              >
                {showKey ? '🙈 Masquer' : '👁️ Afficher'}
              </button>
            </div>
          </div>

          {/* Adresse publique pour Hyperliquid */}
          {service === 'hyperliquid' && (
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Adresse publique (optionnel)
              </label>
              <input
                {...register('hyperliquid_public_address')}
                type="text"
                className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
                placeholder="0x..."
              />
            </div>
          )}

          {/* Résultat du test */}
          {testResult.status && (
            <div className={`p-4 rounded-lg border-2 ${getStatusColor(testResult.status)}`}>
              <div className="flex items-center gap-2">
                <span className="text-xl">{getStatusIcon(testResult.status)}</span>
                <span className="font-medium">{testResult.message}</span>
              </div>
            </div>
          )}

          {/* Boutons d'action */}
          <div className="flex gap-3">
            <button
              onClick={() => testApiConnection(service)}
              disabled={isTestingKey}
              className="flex-1 px-4 py-3 border-2 border-black text-black rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
            >
              {isTestingKey ? 'Test...' : 'Tester'}
            </button>

            <button
              onClick={() => saveApiKey(service)}
              disabled={isTestingKey}
              className="flex-1 px-4 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
            >
              {isTestingKey ? 'Sauvegarde...' : 'Sauvegarder'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-black p-8 sm:p-10">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-black mb-3">
          Configuration des Clés API
        </h2>
        <p className="text-gray-600">
          Configurez vos clés API pour activer toutes les fonctionnalités du
          trading tool.
        </p>
      </div>

      <div className="space-y-6">
        {renderApiKeySection(
          'anthropic',
          API_SERVICES.ANTHROPIC.name,
          API_SERVICES.ANTHROPIC.description,
          API_SERVICES.ANTHROPIC.required
        )}

        {renderApiKeySection(
          'hyperliquid',
          API_SERVICES.HYPERLIQUID.name,
          API_SERVICES.HYPERLIQUID.description,
          API_SERVICES.HYPERLIQUID.required
        )}

        {renderApiKeySection(
          'coingecko',
          API_SERVICES.COINGECKO.name,
          API_SERVICES.COINGECKO.description,
          API_SERVICES.COINGECKO.required
        )}
      </div>

      {/* Aide */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
        <h4 className="font-bold text-blue-900 mb-2">💡 Aide</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• <strong>Anthropic</strong> : Nécessaire pour l'analyse IA</li>
          <li>• <strong>Hyperliquid</strong> : Nécessaire pour l'exécution des trades</li>
          <li>• <strong>CoinGecko</strong> : Optionnel, pour des données de marché enrichies</li>
        </ul>
      </div>
    </div>
  );
}
