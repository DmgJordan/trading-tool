import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  AIRecommendation,
  AIRecommendationRequest,
  DashboardStats,
  RecommendationsState,
  RecommendationsActions
} from '../lib/types/ai_recommendations';
import {
  aiRecommendationsApi,
  aiRecommendationsApiWithRetry,
  recommendationsCache
} from '../lib/api/ai_recommendations';

interface RecommendationsStore extends RecommendationsState, RecommendationsActions {
  refreshRecommendations: () => Promise<void>;
  cleanupExpiredRecommendations: () => Promise<void>;
}

export const useRecommendationsStore = create<RecommendationsStore>()(
  persist(
    (set, get) => ({
      // État initial
      recommendations: [],
      stats: null,
      isLoading: false,
      isGenerating: false,
      error: null,
      lastGenerated: null,
      selectedRecommendation: null,

      // Actions
      loadRecommendations: async () => {
        try {
          console.log('loadRecommendations: Starting...');
          set({ isLoading: true, error: null });

          // Vérifier d'abord le cache local
          const cachedRecommendations = recommendationsCache.getRecommendations();
          if (cachedRecommendations) {
            console.log('loadRecommendations: Using cached data');
            set({
              recommendations: cachedRecommendations,
              isLoading: false
            });
            return;
          }

          console.log('loadRecommendations: Fetching from API...');
          // Charger depuis l'API avec retry
          const recommendations = await aiRecommendationsApiWithRetry.getRecommendations();

          // Mettre en cache les résultats
          recommendationsCache.setRecommendations(recommendations);

          console.log('loadRecommendations: Success, got', recommendations.length, 'recommendations');
          set({
            recommendations,
            isLoading: false,
            error: null
          });
        } catch (error: any) {
          console.error('loadRecommendations: Error', error);
          const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors du chargement des recommandations';
          set({
            isLoading: false,
            error: errorMessage
          });
          throw error;
        }
      },

      generateRecommendations: async (request?: AIRecommendationRequest) => {
        try {
          set({ isGenerating: true, error: null });

          // Valider la requête si fournie
          if (request) {
            const validation = await aiRecommendationsApi.validateGenerationRequest(request);
            if (!validation.isValid) {
              const errorMessage = Object.values(validation.errors || {}).flat().join(', ');
              throw new Error(`Paramètres invalides: ${errorMessage}`);
            }
          }

          // Générer les recommandations avec retry
          const response = await aiRecommendationsApiWithRetry.generateRecommendations(request);

          // Recharger toutes les recommandations pour avoir la liste complète
          const allRecommendations = await aiRecommendationsApiWithRetry.getRecommendations();

          // Mettre en cache les nouvelles recommandations
          recommendationsCache.setRecommendations(allRecommendations);

          set({
            recommendations: allRecommendations,
            lastGenerated: response.generated_at,
            isGenerating: false,
            error: null
          });

          // Recharger les stats
          get().loadStats();

        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la génération des recommandations';
          set({
            isGenerating: false,
            error: errorMessage
          });
          throw error;
        }
      },

      acceptRecommendation: async (id: number, note?: string) => {
        try {
          set({ error: null });

          // Optimistic update - marquer comme acceptée localement
          const currentRecommendations = get().recommendations;
          const optimisticRecommendations = currentRecommendations.map(rec =>
            rec.id === id ? { ...rec, status: 'ACCEPTED' as const } : rec
          );
          set({ recommendations: optimisticRecommendations });

          // Appeler l'API avec retry
          const updatedRecommendation = await aiRecommendationsApiWithRetry.acceptRecommendation(id, note);

          // Mettre à jour avec la réponse du serveur
          const updatedRecommendations = currentRecommendations.map(rec =>
            rec.id === id ? updatedRecommendation : rec
          );

          // Mettre en cache les résultats mis à jour
          recommendationsCache.setRecommendations(updatedRecommendations);

          set({
            recommendations: updatedRecommendations,
            error: null
          });

          // Recharger les stats
          get().loadStats();

        } catch (error: any) {
          // Rollback optimistic update en cas d'erreur
          get().loadRecommendations();

          const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de l\'acceptation de la recommandation';
          set({ error: errorMessage });
          throw error;
        }
      },

      rejectRecommendation: async (id: number, note?: string) => {
        try {
          set({ error: null });

          // Optimistic update - marquer comme rejetée localement
          const currentRecommendations = get().recommendations;
          const optimisticRecommendations = currentRecommendations.map(rec =>
            rec.id === id ? { ...rec, status: 'REJECTED' as const } : rec
          );
          set({ recommendations: optimisticRecommendations });

          // Appeler l'API avec retry
          const updatedRecommendation = await aiRecommendationsApiWithRetry.rejectRecommendation(id, note);

          // Mettre à jour avec la réponse du serveur
          const updatedRecommendations = currentRecommendations.map(rec =>
            rec.id === id ? updatedRecommendation : rec
          );

          // Mettre en cache les résultats mis à jour
          recommendationsCache.setRecommendations(updatedRecommendations);

          set({
            recommendations: updatedRecommendations,
            error: null
          });

          // Recharger les stats
          get().loadStats();

        } catch (error: any) {
          // Rollback optimistic update en cas d'erreur
          get().loadRecommendations();

          const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors du rejet de la recommandation';
          set({ error: errorMessage });
          throw error;
        }
      },

      loadStats: async () => {
        try {
          console.log('loadStats: Starting...');
          const stats = await aiRecommendationsApiWithRetry.getDashboardStats();
          console.log('loadStats: Success', stats);
          set({ stats, error: null });
        } catch (error: any) {
          console.warn('loadStats: Error (non-critical)', error);
          // Les erreurs de stats ne sont pas critiques, on les log mais on ne bloque pas l'UI
        }
      },

      setSelectedRecommendation: (recommendation: AIRecommendation | null) => {
        set({ selectedRecommendation: recommendation });
      },

      clearError: () => {
        set({ error: null });
      },

      // Actions utilitaires pour la gestion du cache
      refreshRecommendations: async () => {
        // Forcer le rechargement en vidant le cache
        recommendationsCache.clearCache();
        await get().loadRecommendations();
      },

      cleanupExpiredRecommendations: async () => {
        try {
          await aiRecommendationsApi.cleanupExpiredRecommendations();
          // Recharger simplement sans utiliser refreshRecommendations pour éviter la récursion
          recommendationsCache.clearCache();
          await get().loadRecommendations();
        } catch (error: any) {
          console.warn('Erreur lors du nettoyage des recommandations expirées:', error);
        }
      }

    }),
    {
      name: 'recommendations-store',
      storage: createJSONStorage(() => localStorage),
      // Ne persister que les données importantes, pas les états de chargement
      partialize: (state) => ({
        lastGenerated: state.lastGenerated,
        selectedRecommendation: state.selectedRecommendation,
      }),
      // Rehydrater le store au démarrage
      onRehydrateStorage: () => (state) => {
        // Nettoyer les états de chargement après la rehydratation
        if (state) {
          state.isLoading = false;
          state.isGenerating = false;
          state.error = null;
        }
      }
    }
  )
);

// Sélecteurs utiles pour les composants
export const useRecommendationsSelectors = {
  // Recommandations filtrées par statut
  usePendingRecommendations: () => {
    return useRecommendationsStore(state =>
      state.recommendations.filter(rec => rec.status === 'PENDING')
    );
  },

  useAcceptedRecommendations: () => {
    return useRecommendationsStore(state =>
      state.recommendations.filter(rec => rec.status === 'ACCEPTED')
    );
  },

  useRejectedRecommendations: () => {
    return useRecommendationsStore(state =>
      state.recommendations.filter(rec => rec.status === 'REJECTED')
    );
  },

  // Recommandations par action
  useBuyRecommendations: () => {
    return useRecommendationsStore(state =>
      state.recommendations.filter(rec => rec.action === 'BUY' && rec.status === 'PENDING')
    );
  },

  useSellRecommendations: () => {
    return useRecommendationsStore(state =>
      state.recommendations.filter(rec => rec.action === 'SELL' && rec.status === 'PENDING')
    );
  },

  useHoldRecommendations: () => {
    return useRecommendationsStore(state =>
      state.recommendations.filter(rec => rec.action === 'HOLD' && rec.status === 'PENDING')
    );
  },

  // Statistiques calculées
  useCalculatedStats: () => {
    return useRecommendationsStore(state => {
      const recommendations = state.recommendations;
      const pending = recommendations.filter(rec => rec.status === 'PENDING');
      const totalEstimatedPnL = pending.reduce((sum, rec) => sum + rec.estimated_pnl, 0);
      const avgConfidence = pending.length > 0
        ? pending.reduce((sum, rec) => sum + rec.confidence, 0) / pending.length
        : 0;

      return {
        pendingCount: pending.length,
        totalEstimatedPnL,
        avgConfidence,
        highConfidenceCount: pending.filter(rec => rec.confidence >= 80).length,
        highRiskCount: pending.filter(rec => rec.risk_level === 'HIGH').length
      };
    });
  },

  // État de chargement global
  useIsLoading: () => {
    return useRecommendationsStore(state => state.isLoading || state.isGenerating);
  }
};

// Hook personnalisé pour initialiser le store
export const useInitializeRecommendations = () => {
  const { loadRecommendations, loadStats } = useRecommendationsStore();

  const initialize = async () => {
    try {
      // Charger les données principales seulement
      await Promise.all([
        loadRecommendations(),
        loadStats()
      ]);
    } catch (error) {
      console.error('Erreur lors de l\'initialisation des recommandations:', error);
    }
  };

  return { initialize };
};