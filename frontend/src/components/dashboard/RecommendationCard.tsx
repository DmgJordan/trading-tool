'use client';

import { useState } from 'react';
import {
  AIRecommendation,
  RECOMMENDATION_ACTIONS,
  RISK_LEVELS,
  formatPnL,
  formatConfidence,
  getConfidenceColor,
  formatTimeAgo,
  isRecommendationExpiringSoon,
  isRecommendationExpired
} from '../../lib/types/ai_recommendations';

interface RecommendationCardProps {
  recommendation: AIRecommendation;
  onAccept: (id: number) => void;
  onReject: (id: number) => void;
  onExpand?: (id: number) => void;
  isExpanded?: boolean;
  disabled?: boolean;
}

export default function RecommendationCard({
  recommendation,
  onAccept,
  onReject,
  onExpand,
  isExpanded = false,
  disabled = false
}: RecommendationCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const actionConfig = RECOMMENDATION_ACTIONS.find(a => a.value === recommendation.action);
  const riskConfig = RISK_LEVELS.find(r => r.value === recommendation.risk_level);

  const isPending = recommendation.status === 'PENDING';
  const isExpired = isRecommendationExpired(recommendation.expires_at);
  const isExpiringSoon = isRecommendationExpiringSoon(recommendation.expires_at);

  const isInteractable = isPending && !isExpired && !disabled;

  const handleAccept = () => {
    if (isInteractable) {
      onAccept(recommendation.id);
    }
  };

  const handleReject = () => {
    if (isInteractable) {
      onReject(recommendation.id);
    }
  };

  const handleExpand = () => {
    if (onExpand) {
      onExpand(recommendation.id);
    }
  };

  return (
    <div
      className={`bg-white rounded-xl border-2 transition-all duration-200 ${
        isPending && !isExpired
          ? 'border-gray-200 hover:border-gray-400 hover:shadow-lg'
          : 'border-gray-100 opacity-75'
      } ${isHovered && isInteractable ? 'transform scale-[1.02]' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="p-6">
        {/* En-tête avec symbole et action */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
              actionConfig?.value === 'BUY' ? 'bg-green-500' :
              actionConfig?.value === 'SELL' ? 'bg-red-500' : 'bg-blue-500'
            }`}>
              {recommendation.symbol.substring(0, 2).toUpperCase()}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{recommendation.symbol}</h3>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-medium ${actionConfig?.color || 'text-gray-600'}`}>
                  {actionConfig?.icon} {actionConfig?.label || recommendation.action}
                </span>
                {riskConfig && (
                  <span className={`text-xs px-2 py-1 rounded-full ${riskConfig.bgColor} ${riskConfig.color} font-medium`}>
                    {riskConfig.icon} {riskConfig.label}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Statut et expiration */}
          <div className="text-right">
            {isExpired ? (
              <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full font-medium">
                ⏰ Expirée
              </span>
            ) : isExpiringSoon ? (
              <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full font-medium">
                ⚠️ Expire bientôt
              </span>
            ) : (
              <span className="text-xs text-gray-500">
                {formatTimeAgo(recommendation.created_at)}
              </span>
            )}
          </div>
        </div>

        {/* Prix cible et P&L estimé */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Prix cible</p>
            <p className="text-lg font-bold text-gray-900">{recommendation.target_price.toFixed(2)}€</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">P&L estimé</p>
            <p className={`text-lg font-bold ${
              recommendation.estimated_pnl >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatPnL(recommendation.estimated_pnl, recommendation.estimated_pnl_percentage)}
            </p>
          </div>
        </div>

        {/* Score de confiance */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-500">Confiance IA</span>
            <span className={`text-sm font-semibold ${getConfidenceColor(recommendation.confidence)}`}>
              {formatConfidence(recommendation.confidence)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                recommendation.confidence >= 80 ? 'bg-green-500' :
                recommendation.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${recommendation.confidence}%` }}
            />
          </div>
        </div>

        {/* Raisonnement IA */}
        <div className="mb-6">
          <p className="text-sm text-gray-700 leading-relaxed">
            {isExpanded || recommendation.reasoning.length <= 150
              ? recommendation.reasoning
              : `${recommendation.reasoning.substring(0, 150)}...`
            }
          </p>
          {recommendation.reasoning.length > 150 && onExpand && (
            <button
              onClick={handleExpand}
              className="text-xs text-blue-600 hover:text-blue-800 mt-1 focus:outline-none"
            >
              {isExpanded ? 'Voir moins' : 'Voir plus'}
            </button>
          )}
        </div>

        {/* Boutons d'action */}
        {isInteractable ? (
          <div className="flex space-x-3">
            <button
              onClick={handleAccept}
              disabled={disabled}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span>Accepter</span>
            </button>
            <button
              onClick={handleReject}
              disabled={disabled}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
              <span>Rejeter</span>
            </button>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <span className="text-sm text-gray-500">
              {recommendation.status === 'ACCEPTED' && '✅ Recommandation acceptée'}
              {recommendation.status === 'REJECTED' && '❌ Recommandation rejetée'}
              {recommendation.status === 'EXPIRED' && '⏰ Recommandation expirée'}
              {recommendation.status === 'PENDING' && isExpired && '⏰ Recommandation expirée'}
            </span>
          </div>
        )}

        {/* Données de marché (si disponibles et en mode étendu) */}
        {isExpanded && recommendation.market_data && Object.keys(recommendation.market_data).length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Données de marché</h4>
            <div className="grid grid-cols-2 gap-3 text-xs">
              {Object.entries(recommendation.market_data).slice(0, 4).map(([key, value]) => (
                <div key={key} className="bg-gray-50 p-2 rounded">
                  <span className="text-gray-500 capitalize">{key.replace('_', ' ')}:</span>
                  <span className="font-medium text-gray-900 ml-1">
                    {typeof value === 'number' ? value.toFixed(2) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}