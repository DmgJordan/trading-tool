'use client';

import { useState } from 'react';
import { TradeRecommendation } from '@/lib/types/trading';

interface TradeCardProps {
  recommendation: TradeRecommendation;
  ticker: string;
  onExecuteTrade: (recommendation: TradeRecommendation) => void;
  isExecuting?: boolean;
  className?: string;
}

export default function TradeCard({
  recommendation,
  ticker,
  onExecuteTrade,
  isExecuting = false,
  className = '',
}: TradeCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculer les métriques
  const riskAmount = Math.abs(
    recommendation.entry_price - recommendation.stop_loss
  );

  // Couleurs selon la direction
  const directionColors = {
    long: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-900',
      accent: 'text-green-700',
      button: 'bg-green-600 hover:bg-green-700',
      icon: '📈',
    },
    short: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-900',
      accent: 'text-red-700',
      button: 'bg-red-600 hover:bg-red-700',
      icon: '📉',
    },
  };

  const colors = directionColors[recommendation.direction];

  const formatPrice = (price: number) => {
    return price.toLocaleString('fr-FR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    });
  };

  const getConfidenceColor = (level: number) => {
    if (level >= 90) return 'bg-green-500';
    if (level >= 80) return 'bg-yellow-500';
    if (level >= 70) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div
      className={`${colors.bg} ${colors.border} border-2 rounded-xl p-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{colors.icon}</span>
          <div>
            <h3 className={`text-lg font-bold ${colors.text}`}>
              {recommendation.direction.toUpperCase()} {ticker}
            </h3>
            <p className={`text-sm ${colors.accent}`}>
              {recommendation.timeframe} • {recommendation.portfolio_percentage}
              % portefeuille
            </p>
          </div>
        </div>

        {/* Niveau de confiance */}
        <div className="text-center">
          <div className={`text-xs font-medium ${colors.text} mb-1`}>
            Confiance
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getConfidenceColor(recommendation.confidence_level)}`}
                style={{ width: `${recommendation.confidence_level}%` }}
              ></div>
            </div>
            <span className={`text-sm font-bold ${colors.text}`}>
              {recommendation.confidence_level}%
            </span>
          </div>
        </div>
      </div>

      {/* Prix clés */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        {/* Prix d'entrée */}
        <div className="text-center">
          <div className={`text-xs font-medium ${colors.accent} mb-1`}>
            Entrée
          </div>
          <div className={`text-lg font-bold ${colors.text}`}>
            ${formatPrice(recommendation.entry_price)}
          </div>
        </div>

        {/* Stop Loss */}
        <div className="text-center">
          <div className="text-xs font-medium text-red-600 mb-1">Stop Loss</div>
          <div className="text-lg font-bold text-red-700">
            ${formatPrice(recommendation.stop_loss)}
          </div>
        </div>

        {/* Take Profit principal */}
        <div className="text-center">
          <div className="text-xs font-medium text-green-600 mb-1">
            TP Principal
          </div>
          <div className="text-lg font-bold text-green-700">
            ${formatPrice(recommendation.take_profit_2)}
          </div>
        </div>

        {/* Ratio R/R */}
        <div className="text-center">
          <div className={`text-xs font-medium ${colors.accent} mb-1`}>
            Ratio R/R
          </div>
          <div className={`text-lg font-bold ${colors.text}`}>
            {recommendation.risk_reward_ratio.toFixed(1)}:1
          </div>
        </div>
      </div>

      {/* Take Profits détaillés */}
      <div className="bg-white bg-opacity-50 rounded-lg p-3 mb-4">
        <div className="text-xs font-medium text-gray-600 mb-2">
          Take Profits Échelonnés
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <div className="text-xs text-gray-500">TP1 (40%)</div>
            <div className="text-sm font-semibold text-green-700">
              ${formatPrice(recommendation.take_profit_1)}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">TP2 (35%)</div>
            <div className="text-sm font-semibold text-green-700">
              ${formatPrice(recommendation.take_profit_2)}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500">TP3 (25%)</div>
            <div className="text-sm font-semibold text-green-700">
              ${formatPrice(recommendation.take_profit_3)}
            </div>
          </div>
        </div>
      </div>

      {/* Justification */}
      <div className="mb-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`text-sm font-medium ${colors.accent} hover:${colors.text} transition-colors`}
        >
          {isExpanded ? '↑ Masquer' : '↓ Voir'} la justification technique
        </button>

        {isExpanded && (
          <div className="mt-2 p-3 bg-white bg-opacity-30 rounded-lg">
            <p className="text-sm text-gray-700 leading-relaxed">
              {recommendation.reasoning}
            </p>
          </div>
        )}
      </div>

      {/* Bouton d'action */}
      <button
        onClick={() => onExecuteTrade(recommendation)}
        disabled={isExecuting}
        className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-colors ${colors.button} disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2`}
      >
        {isExecuting ? (
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
            <span>Exécution en cours...</span>
          </>
        ) : (
          <>
            <span>🚀</span>
            <span>Lancer le Trade</span>
          </>
        )}
      </button>

      {/* Warning pour les risques */}
      <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start space-x-2">
          <span className="text-yellow-600 text-sm">⚠️</span>
          <p className="text-xs text-yellow-800">
            <strong>Attention :</strong> Le trading comporte des risques de
            perte. Cette recommandation n&apos;est pas un conseil financier.
            Risque :{' '}
            {((riskAmount / recommendation.entry_price) * 100).toFixed(1)}% par
            position.
          </p>
        </div>
      </div>
    </div>
  );
}
