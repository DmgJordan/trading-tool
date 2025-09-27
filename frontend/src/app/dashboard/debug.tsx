'use client';

import { useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import { useRecommendationsStore } from '../../store/recommendationsStore';
import Navbar from '../../components/Navbar';

// Version simplifiée du dashboard pour débogage
export default function DebugDashboard() {
  const { user, isAuthenticated } = useAuthStore();
  const { recommendations, isLoading, error, loadRecommendations } =
    useRecommendationsStore();

  useEffect(() => {
    console.log('Debug Dashboard mounted');

    if (isAuthenticated && user) {
      console.log('User authenticated, loading recommendations...');
      loadRecommendations().catch(err => {
        console.error('Failed to load recommendations:', err);
      });
    }
  }, [isAuthenticated, user, loadRecommendations]);

  console.log('Debug Dashboard render:', {
    isAuthenticated,
    user: !!user,
    recommendations: recommendations.length,
    isLoading,
    error,
  });

  if (!isAuthenticated || !user) {
    return (
      <div>
        <Navbar />
        <div className="p-8">Not authenticated</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Debug Dashboard
        </h1>

        <div className="bg-white rounded-lg p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">État du store</h2>
          <pre className="text-sm bg-gray-100 p-4 rounded">
            {JSON.stringify(
              {
                recommendationsCount: recommendations.length,
                isLoading,
                error,
                user: user?.username,
              },
              null,
              2
            )}
          </pre>
        </div>

        {isLoading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800">Chargement des recommandations...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">Erreur: {error}</p>
          </div>
        )}

        {recommendations.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-green-800">
              {recommendations.length} recommandation(s) chargée(s) avec succès
            </p>
          </div>
        )}

        {!isLoading && !error && recommendations.length === 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <p className="text-gray-600">Aucune recommandation disponible</p>
          </div>
        )}
      </main>
    </div>
  );
}
