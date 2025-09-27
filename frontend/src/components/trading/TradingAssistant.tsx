'use client';

import { useState, useEffect } from 'react';
import ModelSelector from './ModelSelector';
import ClaudeResponse from './ClaudeResponse';
import {
  claudeApi,
  SingleAssetAnalysisRequest,
  SingleAssetAnalysisResponse,
  type MainTFFeatures,
  type CurrentPriceInfo,
} from '../../lib/api';
import { usePreferencesStore } from '../../store/preferencesStore';

interface TradingAssistantProps {
  className?: string;
}

export default function TradingAssistant({
  className = '',
}: TradingAssistantProps) {
  const { preferences, isLoading, loadPreferences } = usePreferencesStore();

  const [selectedTicker, setSelectedTicker] = useState<string>('');
  const [selectedProfile, setSelectedProfile] = useState<
    'short' | 'medium' | 'long'
  >('medium');
  const [selectedModel, setSelectedModel] = useState<string>(
    'claude-3-5-sonnet-20241022'
  );
  const [availableTickers, setAvailableTickers] = useState<string[]>([]);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] =
    useState<SingleAssetAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Charger les préférences utilisateur au montage
  useEffect(() => {
    loadPreferences().catch(console.error);
  }, [loadPreferences]);

  // Extraire les tickers des préférences utilisateur
  useEffect(() => {
    if (preferences?.preferred_assets) {
      let assets: string[] = [];

      if (typeof preferences.preferred_assets === 'string') {
        assets = (preferences.preferred_assets as string)
          .split(',')
          .map((asset: string) => asset.trim().toUpperCase())
          .filter((asset: string) => asset.length > 0);
      } else if (Array.isArray(preferences.preferred_assets)) {
        assets = preferences.preferred_assets
          .map((asset: string) => String(asset).trim().toUpperCase())
          .filter((asset: string) => asset.length > 0);
      }

      setAvailableTickers(assets);

      // Sélectionner le premier ticker par défaut
      if (assets.length > 0 && !selectedTicker) {
        setSelectedTicker(assets[0]);
      }
    }
  }, [preferences?.preferred_assets, selectedTicker]);

  const getProfileDescription = (profile: string) => {
    switch (profile) {
      case 'short':
        return 'Court terme (15m/1h/5m) - Scalping et day trading';
      case 'medium':
        return 'Moyen terme (1h/1D/15m) - Swing trading';
      case 'long':
        return 'Long terme (1D/1W/4h) - Position trading';
      default:
        return '';
    }
  };

  const handleAnalyze = async () => {
    if (!selectedTicker) {
      setError('Veuillez sélectionner un ticker à analyser');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const request: SingleAssetAnalysisRequest = {
        ticker: selectedTicker,
        exchange: 'binance',
        profile: selectedProfile,
        model: selectedModel as
          | 'claude-3-haiku-20240307'
          | 'claude-3-sonnet-20240229'
          | 'claude-3-opus-20240229'
          | 'claude-3-5-sonnet-20241022',
        custom_prompt: undefined,
      };

      const result = await claudeApi.analyzeSingleAsset(request);
      setAnalysisResult(result);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Erreur lors de l'analyse");
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setError(null);
  };

  if (isLoading) {
    return (
      <div className={`space-y-8 ${className}`}>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mx-auto mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mx-auto mb-8"></div>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (availableTickers.length === 0) {
    return (
      <div className={`space-y-8 ${className}`}>
        <div className="text-center py-16">
          <div className="text-6xl mb-6">⚙️</div>
          <h2 className="text-2xl font-bold text-black mb-4">
            Aucun actif configuré
          </h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Vous devez d&apos;abord configurer vos actifs préférés dans les
            préférences pour utiliser l&apos;assistant trading.
          </p>
          <button
            onClick={() => (window.location.href = '/preferences')}
            className="px-6 py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
          >
            Configurer les préférences
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-black mb-4">
          Assistant Trading IA
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Sélectionnez un actif, choisissez votre profil de trading et obtenez
          une analyse technique détaillée powered by Claude AI.
        </p>
      </div>

      {/* Configuration */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold text-black mb-6">
          Configuration de l&apos;analyse
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sélection du Ticker */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Actif à analyser
            </label>
            <select
              value={selectedTicker}
              onChange={e => setSelectedTicker(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none bg-white"
            >
              <option value="">Sélectionner un actif</option>
              {availableTickers.map(ticker => (
                <option key={ticker} value={ticker}>
                  {ticker}
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-500 mt-1">
              {availableTickers.length} actif
              {availableTickers.length > 1 ? 's' : ''} disponible
              {availableTickers.length > 1 ? 's' : ''}
            </p>
          </div>

          {/* Sélection du Profil */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Profil de trading
            </label>
            <div className="space-y-2">
              {(['short', 'medium', 'long'] as const).map(profile => (
                <label key={profile} className="flex items-center">
                  <input
                    type="radio"
                    name="profile"
                    value={profile}
                    checked={selectedProfile === profile}
                    onChange={e =>
                      setSelectedProfile(
                        e.target.value as 'short' | 'medium' | 'long'
                      )
                    }
                    className="mr-3 text-black focus:ring-black"
                  />
                  <div>
                    <div className="font-medium text-black">
                      {profile === 'short'
                        ? 'Court terme'
                        : profile === 'medium'
                          ? 'Moyen terme'
                          : 'Long terme'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {getProfileDescription(profile).split(' - ')[0]}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Info du Profil Sélectionné */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Détails du profil
            </label>
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-sm">
                <div className="font-medium text-blue-900 mb-1">
                  {selectedProfile === 'short'
                    ? 'Court terme'
                    : selectedProfile === 'medium'
                      ? 'Moyen terme'
                      : 'Long terme'}
                </div>
                <div className="text-blue-800 text-xs">
                  {getProfileDescription(selectedProfile)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sélection du Modèle */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <ModelSelector
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </div>

      {/* Bouton d'analyse */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-black">
              Lancer l&apos;analyse
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {selectedTicker
                ? `${selectedTicker} • ${selectedProfile === 'short' ? 'Court' : selectedProfile === 'medium' ? 'Moyen' : 'Long'} terme • ${selectedModel.replace('claude-3', 'Claude 3').replace('-20240307', '').replace('-20240229', '').replace('-20241022', '').replace('-', ' ')}`
                : 'Sélectionnez un actif pour commencer'}
            </p>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={!selectedTicker || isAnalyzing}
            className="px-6 py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isAnalyzing ? (
              <>
                <svg
                  className="animate-spin w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Analyse en cours...</span>
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Analyser avec Claude</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start space-x-3">
            <svg
              className="w-5 h-5 text-red-600 mt-0.5"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h4 className="font-semibold text-red-900">Erreur</h4>
              <p className="text-red-800 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Résultats de l'analyse */}
      {analysisResult && (
        <>
          {/* Données techniques */}
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-black">
                📊 Données Techniques - {analysisResult.ticker}
              </h3>
              <button
                onClick={handleNewAnalysis}
                className="text-sm px-3 py-1.5 text-gray-600 hover:text-black border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Nouvelle analyse
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              {/* Prix actuel */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Prix Actuel</h4>
                <div className="text-2xl font-bold text-blue-800">
                  $
                  {analysisResult.technical_data.current_price?.current_price?.toFixed(
                    4
                  ) || 'N/A'}
                </div>
                {analysisResult.technical_data.current_price
                  ?.change_24h_percent && (
                  <div
                    className={`text-sm ${analysisResult.technical_data.current_price.change_24h_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}
                  >
                    {analysisResult.technical_data.current_price
                      .change_24h_percent >= 0
                      ? '+'
                      : ''}
                    {analysisResult.technical_data.current_price.change_24h_percent.toFixed(
                      2
                    )}
                    % (24h)
                  </div>
                )}
              </div>

              {/* RSI principal */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-medium text-purple-900 mb-2">
                  RSI ({analysisResult.technical_data.tf})
                </h4>
                <div className="text-2xl font-bold text-purple-800">
                  {analysisResult.technical_data.features?.rsi14?.toFixed(1) ||
                    'N/A'}
                </div>
                <div className="text-sm text-purple-600">
                  {analysisResult.technical_data.features?.rsi14 >= 70
                    ? 'Surachat'
                    : analysisResult.technical_data.features?.rsi14 <= 30
                      ? 'Survente'
                      : analysisResult.technical_data.features?.rsi14 >= 50
                        ? 'Haussier'
                        : 'Baissier'}
                </div>
              </div>

              {/* ATR */}
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-medium text-orange-900 mb-2">
                  Volatilité (ATR)
                </h4>
                <div className="text-2xl font-bold text-orange-800">
                  {analysisResult.technical_data.features?.atr14?.toFixed(4) ||
                    'N/A'}
                </div>
                <div className="text-sm text-orange-600">
                  {analysisResult.technical_data.tf}
                </div>
              </div>
            </div>

            {/* Résumé multi-timeframes */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">
                Analyse Multi-Timeframes
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium">
                    Principal ({analysisResult.technical_data.tf}):
                  </span>
                  <br />
                  RSI:{' '}
                  {analysisResult.technical_data.features?.rsi14?.toFixed(1) ||
                    'N/A'}
                </div>
                <div>
                  <span className="font-medium">
                    Supérieur ({analysisResult.technical_data.higher_tf?.tf}):
                  </span>
                  <br />
                  RSI:{' '}
                  {analysisResult.technical_data.higher_tf?.rsi14?.toFixed(1) ||
                    'N/A'}
                  <br />
                  Structure:{' '}
                  {analysisResult.technical_data.higher_tf?.structure || 'N/A'}
                </div>
                <div>
                  <span className="font-medium">
                    Inférieur ({analysisResult.technical_data.lower_tf?.tf}):
                  </span>
                  <br />
                  RSI:{' '}
                  {analysisResult.technical_data.lower_tf?.rsi14?.toFixed(1) ||
                    'N/A'}
                </div>
              </div>
            </div>
          </div>

          {/* Analyse Claude */}
          <ClaudeResponse
            response={analysisResult.claude_analysis}
            selectedAssets={[analysisResult.ticker]}
            timestamp={new Date(analysisResult.timestamp)}
          />
        </>
      )}
    </div>
  );
}
