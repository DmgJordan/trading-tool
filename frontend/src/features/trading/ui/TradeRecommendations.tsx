'use client';

import { useState } from 'react';
import TradeCard from './TradeCard';
import ExecuteTradeModal from './ExecuteTradeModal';
import {
  TradeRecommendation,
  ExecuteTradeRequest,
  TradeExecutionResult,
} from '@/lib/types/trading';
import { hyperliquidTradingApi } from '@/features/trading/api/trading.api';
import { useNotifications } from '@/hooks/useNotifications';

interface TradeRecommendationsProps {
  recommendations: TradeRecommendation[];
  ticker: string;
  analysisTimestamp: Date;
  className?: string;
}

export default function TradeRecommendations({
  recommendations,
  ticker,
  analysisTimestamp,
  className = '',
}: TradeRecommendationsProps) {
  const [selectedRecommendation, setSelectedRecommendation] =
    useState<TradeRecommendation | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [executingTrades, setExecutingTrades] = useState<Set<number>>(
    new Set()
  );
  const [executionResults, setExecutionResults] = useState<
    Map<number, TradeExecutionResult>
  >(new Map());

  const { success, warning, error: notifyError } = useNotifications();

  const handleExecuteTrade = (recommendation: TradeRecommendation) => {
    setSelectedRecommendation(recommendation);
    setIsModalOpen(true);
  };

  const handleConfirmExecution = async (request: ExecuteTradeRequest) => {
    if (!selectedRecommendation) return;

    const recIndex = recommendations.indexOf(selectedRecommendation);

    // Marquer comme en cours d'exécution
    setExecutingTrades(prev => new Set(prev).add(recIndex));

    try {
      const result = await hyperliquidTradingApi.executeTrade(request);

      // Stocker le résultat
      setExecutionResults(prev => new Map(prev).set(recIndex, result));

      // Afficher une notification selon le résultat
      if (result.status === 'success') {
        success(
          `Trade exécuté avec succès ! Order ID: ${result.main_order_id || 'N/A'}`
        );
      } else if (result.status === 'partial') {
        warning(`Trade partiellement exécuté: ${result.message}`);
      } else {
        notifyError(`Échec du trade: ${result.message}`);
      }
    } catch (error) {
      notifyError(
        `Erreur lors de l'exécution du trade: ${error instanceof Error ? error.message : 'Erreur inconnue'}`
      );
    } finally {
      // Retirer de la liste des trades en cours
      setExecutingTrades(prev => {
        const newSet = new Set(prev);
        newSet.delete(recIndex);
        return newSet;
      });
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedRecommendation(null);
  };

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('fr-FR', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const getResultSummary = () => {
    const executed = Array.from(executionResults.values());
    const successCount = executed.filter(r => r.status === 'success').length;
    const partialCount = executed.filter(r => r.status === 'partial').length;
    const errorCount = executed.filter(r => r.status === 'error').length;

    return {
      successCount,
      partialCount,
      errorCount,
      totalExecuted: executed.length,
    };
  };

  if (recommendations.length === 0) {
    return (
      <div
        className={`bg-gray-50 border border-gray-200 rounded-xl p-8 text-center ${className}`}
      >
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Aucune opportunité de trading détectée
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Claude n&apos;a identifié aucun signal de trading suffisamment fiable
          selon les critères techniques actuels. Cela peut indiquer un marché en
          consolidation ou l&apos;absence de confluence d&apos;indicateurs.
        </p>
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            💡 <strong>Conseil :</strong> Attendez de meilleurs setups ou
            analysez d&apos;autres actifs.
          </p>
        </div>
      </div>
    );
  }

  const resultSummary = getResultSummary();

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black">
            🎯 Opportunités de Trading
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            {recommendations.length} recommandation
            {recommendations.length > 1 ? 's' : ''} générée
            {recommendations.length > 1 ? 's' : ''} •{' '}
            {formatTimestamp(analysisTimestamp)}
          </p>
        </div>

        {/* Résumé des exécutions */}
        {resultSummary.totalExecuted > 0 && (
          <div className="text-right">
            <div className="text-sm text-gray-600">Trades exécutés</div>
            <div className="flex items-center space-x-3 text-sm">
              {resultSummary.successCount > 0 && (
                <span className="text-green-600 font-semibold">
                  ✅ {resultSummary.successCount}
                </span>
              )}
              {resultSummary.partialCount > 0 && (
                <span className="text-yellow-600 font-semibold">
                  ⚠️ {resultSummary.partialCount}
                </span>
              )}
              {resultSummary.errorCount > 0 && (
                <span className="text-red-600 font-semibold">
                  ❌ {resultSummary.errorCount}
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Informations générales */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <span className="text-blue-600 text-lg">💡</span>
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">À propos des recommandations</p>
            <p>
              Ces recommandations sont basées sur l&apos;analyse technique
              multi-timeframes de Claude. Chaque trade inclut une gestion
              automatique des risques avec stop-loss et take-profits échelonnés.
              Les ordres seront placés automatiquement sur Hyperliquid.
            </p>
          </div>
        </div>
      </div>

      {/* Grille des recommandations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {recommendations.map((recommendation, index) => {
          const isExecuting = executingTrades.has(index);
          const executionResult = executionResults.get(index);

          return (
            <div key={index} className="relative">
              <TradeCard
                recommendation={recommendation}
                ticker={ticker}
                onExecuteTrade={handleExecuteTrade}
                isExecuting={isExecuting}
              />

              {/* Overlay de résultat d'exécution */}
              {executionResult && (
                <div className="absolute top-4 right-4">
                  {executionResult.status === 'success' && (
                    <div className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                      <span>✅</span>
                      <span>Exécuté</span>
                    </div>
                  )}
                  {executionResult.status === 'partial' && (
                    <div className="bg-yellow-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                      <span>⚠️</span>
                      <span>Partiel</span>
                    </div>
                  )}
                  {executionResult.status === 'error' && (
                    <div className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1">
                      <span>❌</span>
                      <span>Échec</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Résultats détaillés des exécutions */}
      {executionResults.size > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-black mb-4">
            📊 Historique des exécutions
          </h3>
          <div className="space-y-3">
            {Array.from(executionResults.entries()).map(([index, result]) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      result.status === 'success'
                        ? 'bg-green-500'
                        : result.status === 'partial'
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                    }`}
                  ></div>
                  <div>
                    <div className="font-medium text-sm">
                      {recommendations[index].direction.toUpperCase()} {ticker}
                    </div>
                    <div className="text-xs text-gray-600">
                      {result.message}
                    </div>
                  </div>
                </div>
                <div className="text-right text-xs text-gray-600">
                  {result.executed_size && (
                    <div>Taille : {result.executed_size.toFixed(4)}</div>
                  )}
                  {result.main_order_id && (
                    <div>ID : {result.main_order_id.slice(0, 8)}...</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal de confirmation */}
      <ExecuteTradeModal
        isOpen={isModalOpen}
        recommendation={selectedRecommendation}
        ticker={ticker}
        onClose={handleCloseModal}
        onExecute={handleConfirmExecution}
      />
    </div>
  );
}
