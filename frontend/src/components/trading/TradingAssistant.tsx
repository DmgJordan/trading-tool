'use client';

import { useState } from 'react';
import AssetSelector from './AssetSelector';
import ModelSelector from './ModelSelector';
import ClaudeResponse from './ClaudeResponse';
import { claudeApi } from '../../lib/api';

interface TradingAssistantProps {
  className?: string;
}

export default function TradingAssistant({ className = '' }: TradingAssistantProps) {
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('claude-3-5-sonnet-20241022');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [claudeResponse, setClaudeResponse] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAssetSelectionChange = (assets: string[]) => {
    setSelectedAssets(assets);
    // Reset previous results when selection changes
    setClaudeResponse(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (selectedAssets.length === 0) {
      setError('Veuillez sélectionner au moins un actif à analyser');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setClaudeResponse(null);

    try {
      const analysisResult = await claudeApi.analyzeAssets({
        assets: selectedAssets,
        model: selectedModel as any,
        analysis_type: 'detailed',
        custom_prompt: `Analysez les actifs suivants pour le trading: ${selectedAssets.join(', ')}.
        Donnez des recommandations spécifiques incluant:
        - Analyse technique actuelle
        - Niveaux de support et résistance
        - Signaux d'entrée et de sortie
        - Gestion des risques
        - Perspective à court et moyen terme`,
        include_market_data: true,
        use_user_preferences: true
      });

      setClaudeResponse(analysisResult.full_analysis);
    } catch (err) {
      // Fallback to mock response in case of API error
      if (err instanceof Error && err.message.includes('404')) {
        console.warn('Claude API endpoint not implemented yet, using mock response');

        const mockResponse = `Analyse des actifs sélectionnés : ${selectedAssets.join(', ')}
Modèle utilisé : ${selectedModel}

📊 Résumé du marché:
Les actifs sélectionnés montrent des signaux mixtes dans le contexte actuel du marché.

🔍 Recommandations par actif:
${selectedAssets.map(asset => `
• ${asset}:
  - Tendance: Neutre à haussière
  - Signal: Attendre une cassure des résistances
  - Niveau d'entrée suggéré: À définir selon l'évolution
`).join('')}

⚠️ Avertissement:
Cette analyse est une simulation. L'endpoint /claude/analyze-trading n'existe pas encore.
Configurez votre clé API Claude dans les paramètres pour obtenir de vraies analyses.`;

        setClaudeResponse(mockResponse);
      } else {
        setError(err instanceof Error ? err.message : 'Erreur lors de l\'analyse');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-black mb-4">
          Assistant Trading IA
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Sélectionnez vos actifs préférés et obtenez une analyse personnalisée
          grâce à l'intelligence artificielle Claude.
        </p>
      </div>

      {/* Asset Selection */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold text-black mb-4">
          Sélection des actifs
        </h2>
        <AssetSelector
          onSelectionChange={handleAssetSelectionChange}
          selectedAssets={selectedAssets}
        />
      </div>

      {/* Model Selection */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <ModelSelector
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </div>

      {/* Analysis Controls */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-black">
              Lancer l'analyse
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {selectedAssets.length > 0
                ? `${selectedAssets.length} actif${selectedAssets.length > 1 ? 's' : ''} sélectionné${selectedAssets.length > 1 ? 's' : ''} • Modèle: ${selectedModel.replace('claude-3', 'Claude 3').replace('-20240307', '').replace('-20240229', '').replace('-20241022', '').replace('-', ' ')}`
                : 'Aucun actif sélectionné'
              }
            </p>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={selectedAssets.length === 0 || isAnalyzing}
            className="px-6 py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            {isAnalyzing ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                </svg>
                <span>Analyse en cours...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                </svg>
                <span>Analyser avec Claude</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-semibold text-red-900">Erreur</h4>
              <p className="text-red-800 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Claude Response */}
      {claudeResponse && (
        <ClaudeResponse
          response={claudeResponse}
          selectedAssets={selectedAssets}
        />
      )}
    </div>
  );
}