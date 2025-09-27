'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../store/authStore';
import { AIRecommendation } from '../../lib/types/ai_recommendations';
import {
  useRecommendationsStore,
  useInitializeRecommendations,
} from '../../store/recommendationsStore';
import Navbar from '../../components/Navbar';
import DashboardHeader from '../../components/dashboard/DashboardHeader';
import RecommendationGrid from '../../components/dashboard/RecommendationGrid';
import HyperliquidSection from '../../components/dashboard/HyperliquidSection';
import {
  AcceptRecommendationModal,
  RejectRecommendationModal,
} from '../../components/dashboard/ConfirmModal';
import { StatsLoadingSkeleton } from '../../components/dashboard/LoadingSkeleton';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { initialize } = useInitializeRecommendations();

  // État du store
  const {
    recommendations,
    stats,
    isLoading,
    isGenerating,
    error,
    lastGenerated,
    generateRecommendations,
    acceptRecommendation,
    rejectRecommendation,
    loadRecommendations,
    loadStats,
    clearError,
  } = useRecommendationsStore();

  // Calculs dérivés simples
  const pendingRecommendations = recommendations.filter(
    r => r.status === 'PENDING'
  );
  const isAnyLoading = isLoading || isGenerating;

  // État local pour les modales
  const [acceptModal, setAcceptModal] = useState<{
    isOpen: boolean;
    recommendation: AIRecommendation | null;
    isLoading: boolean;
  }>({
    isOpen: false,
    recommendation: null,
    isLoading: false,
  });

  const [rejectModal, setRejectModal] = useState<{
    isOpen: boolean;
    recommendation: AIRecommendation | null;
    isLoading: boolean;
  }>({
    isOpen: false,
    recommendation: null,
    isLoading: false,
  });

  // État pour les notifications toast
  const [toast, setToast] = useState<{
    message: string;
    type: 'success' | 'error';
    isVisible: boolean;
  }>({
    message: '',
    type: 'success',
    isVisible: false,
  });

  // Redirection si non authentifié
  useEffect(() => {
    if (!isAuthenticated && user === null) {
      router.push('/login');
      return;
    }
  }, [isAuthenticated, user, router]);

  // Initialisation des données
  useEffect(() => {
    console.log('Dashboard useEffect - Auth status:', {
      isAuthenticated,
      user: !!user,
    });
    if (isAuthenticated && user) {
      console.log('Initializing dashboard...');
      initialize().catch(error => {
        console.error('Initialize failed:', error);
      });
    }
  }, [isAuthenticated, user]); // Retirer initialize des dépendances

  // Gestion des erreurs
  useEffect(() => {
    if (error) {
      showToast(error, 'error');
      clearError();
    }
  }, [error, clearError]);

  // Auto-nettoyage des toasts
  useEffect(() => {
    if (toast.isVisible) {
      const timer = setTimeout(() => {
        setToast(prev => ({ ...prev, isVisible: false }));
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [toast.isVisible]);

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type, isVisible: true });
  };

  const handleGenerate = async () => {
    try {
      await generateRecommendations();
      showToast('Nouvelles recommandations générées avec succès!', 'success');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur lors de la génération';
      showToast(errorMessage, 'error');
    }
  };

  const handleAcceptClick = (id: number) => {
    const recommendation = recommendations.find(r => r.id === id);
    if (recommendation) {
      setAcceptModal({
        isOpen: true,
        recommendation,
        isLoading: false,
      });
    }
  };

  const handleRejectClick = (id: number) => {
    const recommendation = recommendations.find(r => r.id === id);
    if (recommendation) {
      setRejectModal({
        isOpen: true,
        recommendation,
        isLoading: false,
      });
    }
  };

  const handleAcceptConfirm = async () => {
    if (!acceptModal.recommendation) return;

    try {
      setAcceptModal(prev => ({ ...prev, isLoading: true }));
      await acceptRecommendation(acceptModal.recommendation.id);
      setAcceptModal({ isOpen: false, recommendation: null, isLoading: false });
      showToast('Recommandation acceptée avec succès!', 'success');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Erreur lors de l'acceptation";
      showToast(errorMessage, 'error');
      setAcceptModal(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleRejectConfirm = async () => {
    if (!rejectModal.recommendation) return;

    try {
      setRejectModal(prev => ({ ...prev, isLoading: true }));
      await rejectRecommendation(rejectModal.recommendation.id);
      setRejectModal({ isOpen: false, recommendation: null, isLoading: false });
      showToast('Recommandation rejetée', 'success');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Erreur lors du rejet';
      showToast(errorMessage, 'error');
      setRejectModal(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleRefresh = async () => {
    try {
      await Promise.all([loadRecommendations(), loadStats()]);
      showToast('Données mises à jour', 'success');
    } catch {
      showToast('Erreur lors de la mise à jour', 'error');
    }
  };

  // Ne rien afficher pendant la vérification d'authentification
  if (!isAuthenticated || !user) {
    return null;
  }

  console.log('Dashboard render - loading states:', {
    isLoading,
    isGenerating,
    recommendationsCount: recommendations.length,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-8">
        {/* Header avec statistiques */}
        {isLoading && !stats ? (
          <StatsLoadingSkeleton />
        ) : (
          <DashboardHeader
            stats={stats}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            lastGenerated={lastGenerated}
          />
        )}

        {/* Actions rapides */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div className="mb-4 sm:mb-0">
            <h2 className="text-xl font-semibold text-gray-900">
              Vos recommandations
            </h2>
            <p className="text-sm text-gray-600">
              {pendingRecommendations.length} recommandation
              {pendingRecommendations.length !== 1 ? 's' : ''} en attente
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleRefresh}
              disabled={isAnyLoading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <svg
                className={`w-4 h-4 ${isAnyLoading ? 'animate-spin' : ''}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Actualiser</span>
            </button>

            <button
              onClick={() => router.push('/preferences')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Préférences</span>
            </button>
          </div>
        </div>

        {/* Grille des recommandations */}
        <RecommendationGrid
          recommendations={recommendations}
          onAccept={handleAcceptClick}
          onReject={handleRejectClick}
          isLoading={isLoading}
          isEmpty={recommendations.length === 0 && !isLoading}
          emptyAction={
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="px-6 py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isGenerating ? 'Génération...' : 'Générer des recommandations'}
            </button>
          }
        />

        {/* Section Hyperliquid Trading */}
        <div className="mt-12">
          <HyperliquidSection />
        </div>
      </main>

      {/* Modales de confirmation */}
      <AcceptRecommendationModal
        isOpen={acceptModal.isOpen}
        onClose={() =>
          setAcceptModal({
            isOpen: false,
            recommendation: null,
            isLoading: false,
          })
        }
        onConfirm={handleAcceptConfirm}
        isLoading={acceptModal.isLoading}
        symbol={acceptModal.recommendation?.symbol || ''}
        action={acceptModal.recommendation?.action || ''}
        targetPrice={acceptModal.recommendation?.target_price || 0}
      />

      <RejectRecommendationModal
        isOpen={rejectModal.isOpen}
        onClose={() =>
          setRejectModal({
            isOpen: false,
            recommendation: null,
            isLoading: false,
          })
        }
        onConfirm={handleRejectConfirm}
        isLoading={rejectModal.isLoading}
        symbol={rejectModal.recommendation?.symbol || ''}
        action={rejectModal.recommendation?.action || ''}
      />

      {/* Toast notifications */}
      {toast.isVisible && (
        <div className="fixed bottom-4 right-4 z-50">
          <div
            className={`px-6 py-4 rounded-lg shadow-lg text-white max-w-sm ${
              toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`}
          >
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                {toast.type === 'success' ? (
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                ) : (
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                )}
              </svg>
              <span className="text-sm font-medium">{toast.message}</span>
              <button
                onClick={() =>
                  setToast(prev => ({ ...prev, isVisible: false }))
                }
                className="ml-2 text-white hover:text-gray-200"
              >
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
