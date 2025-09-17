'use client';

import { useState } from 'react';
import { AIRecommendation } from '../../lib/types/ai_recommendations';
import RecommendationCard from './RecommendationCard';
import LoadingSkeleton from './LoadingSkeleton';

interface RecommendationGridProps {
  recommendations: AIRecommendation[];
  onAccept: (id: number) => void;
  onReject: (id: number) => void;
  isLoading?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  emptyAction?: React.ReactNode;
  className?: string;
}

export default function RecommendationGrid({
  recommendations,
  onAccept,
  onReject,
  isLoading = false,
  isEmpty = false,
  emptyMessage = 'Aucune recommandation disponible',
  emptyAction,
  className = ''
}: RecommendationGridProps) {
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());

  const handleExpand = (id: number) => {
    setExpandedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  // Trier les recommandations : en attente d'abord, puis par confiance décroissante
  const sortedRecommendations = [...recommendations].sort((a, b) => {
    // D'abord par statut (PENDING en premier)
    if (a.status === 'PENDING' && b.status !== 'PENDING') return -1;
    if (a.status !== 'PENDING' && b.status === 'PENDING') return 1;

    // Puis par confiance décroissante
    return b.confidence - a.confidence;
  });

  if (isLoading) {
    return (
      <div className={className}>
        <LoadingSkeleton count={3} />
      </div>
    );
  }

  if (isEmpty || recommendations.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-gray-400 text-3xl">🤖</span>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {emptyMessage}
        </h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Générez vos premières recommandations IA pour commencer à recevoir des suggestions de trading personnalisées.
        </p>
        {emptyAction}
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Filtres et tri (optionnel) */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div className="mb-4 sm:mb-0">
          <h2 className="text-xl font-semibold text-gray-900">
            Recommandations ({recommendations.length})
          </h2>
          <p className="text-sm text-gray-600">
            {recommendations.filter(r => r.status === 'PENDING').length} en attente d&apos;action
          </p>
        </div>

        {/* Actions rapides */}
        <div className="flex space-x-2">
          <button
            onClick={() => setExpandedCards(new Set())}
            className="text-xs text-gray-600 hover:text-gray-800 px-3 py-1 rounded border border-gray-300 hover:border-gray-400 transition-colors"
          >
            Réduire tout
          </button>
          <button
            onClick={() => setExpandedCards(new Set(recommendations.map(r => r.id)))}
            className="text-xs text-gray-600 hover:text-gray-800 px-3 py-1 rounded border border-gray-300 hover:border-gray-400 transition-colors"
          >
            Étendre tout
          </button>
        </div>
      </div>

      {/* Grille de cartes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {sortedRecommendations.map((recommendation) => (
          <RecommendationCard
            key={recommendation.id}
            recommendation={recommendation}
            onAccept={onAccept}
            onReject={onReject}
            onExpand={handleExpand}
            isExpanded={expandedCards.has(recommendation.id)}
          />
        ))}
      </div>

      {/* Statistiques en bas */}
      {recommendations.length > 0 && (
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-lg font-bold text-blue-600">
                {recommendations.filter(r => r.action === 'BUY').length}
              </p>
              <p className="text-xs text-gray-600">Achats recommandés</p>
            </div>
            <div>
              <p className="text-lg font-bold text-red-600">
                {recommendations.filter(r => r.action === 'SELL').length}
              </p>
              <p className="text-xs text-gray-600">Ventes recommandées</p>
            </div>
            <div>
              <p className="text-lg font-bold text-green-600">
                {recommendations.filter(r => r.confidence >= 80).length}
              </p>
              <p className="text-xs text-gray-600">Haute confiance (≥80%)</p>
            </div>
            <div>
              <p className="text-lg font-bold text-orange-600">
                {recommendations.filter(r => r.risk_level === 'HIGH').length}
              </p>
              <p className="text-xs text-gray-600">Risque élevé</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Composant spécialisé pour les recommandations filtrées
export function FilteredRecommendationGrid({
  recommendations,
  onAccept,
  onReject,
  filterType = 'all',
  className = ''
}: Omit<RecommendationGridProps, 'isEmpty' | 'emptyMessage' | 'emptyAction'> & {
  filterType?: 'all' | 'pending' | 'buy' | 'sell' | 'hold' | 'high_confidence';
}) {
  const filteredRecommendations = recommendations.filter(rec => {
    switch (filterType) {
      case 'pending':
        return rec.status === 'PENDING';
      case 'buy':
        return rec.action === 'BUY' && rec.status === 'PENDING';
      case 'sell':
        return rec.action === 'SELL' && rec.status === 'PENDING';
      case 'hold':
        return rec.action === 'HOLD' && rec.status === 'PENDING';
      case 'high_confidence':
        return rec.confidence >= 80 && rec.status === 'PENDING';
      default:
        return true;
    }
  });

  const getEmptyMessage = () => {
    switch (filterType) {
      case 'pending':
        return 'Aucune recommandation en attente';
      case 'buy':
        return 'Aucune recommandation d\'achat';
      case 'sell':
        return 'Aucune recommandation de vente';
      case 'hold':
        return 'Aucune recommandation de conservation';
      case 'high_confidence':
        return 'Aucune recommandation haute confiance';
      default:
        return 'Aucune recommandation disponible';
    }
  };

  return (
    <RecommendationGrid
      recommendations={filteredRecommendations}
      onAccept={onAccept}
      onReject={onReject}
      isEmpty={filteredRecommendations.length === 0}
      emptyMessage={getEmptyMessage()}
      className={className}
    />
  );
}