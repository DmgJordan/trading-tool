'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '../../components/Navbar';
import { useAuthStore } from '../../store/authStore';

export default function TradingPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated && user === null) {
      router.push('/login');
    }
  }, [isAuthenticated, user, router]);

  // Ne rien afficher pendant la vérification d'authentification
  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        {/* Header de la page */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-black mb-4">
            Trading Avancé
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Cette page est prête à accueillir votre nouvelle fonctionnalité de trading.
            Les données Hyperliquid sont maintenant disponibles dans le Dashboard.
          </p>
        </div>

        {/* Zone de contenu principal */}
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-12">
          <div className="text-center">
            <div className="text-6xl mb-6">🚀</div>
            <h2 className="text-xl font-semibold text-black mb-4">
              Nouvelle fonctionnalité en cours de développement
            </h2>
            <p className="text-gray-600 mb-8">
              Cette zone est maintenant libérée pour implémenter votre nouvelle fonctionnalité de trading.
            </p>

            {/* Bouton de navigation vers le dashboard */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="px-6 py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
              >
                Voir le Portfolio Hyperliquid
              </button>
              <button
                onClick={() => router.push('/preferences')}
                className="px-6 py-3 border-2 border-black text-black font-semibold rounded-lg hover:bg-black hover:text-white focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
              >
                Configurer les préférences
              </button>
            </div>
          </div>
        </div>

        {/* Informations sur la migration */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start space-x-3">
            <div className="text-blue-600 text-xl">ℹ️</div>
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">
                Migration réalisée avec succès
              </h3>
              <p className="text-blue-800 text-sm leading-relaxed">
                Toutes les fonctionnalités de monitoring Hyperliquid (positions, ordres, métriques)
                ont été déplacées vers la section "Portfolio Trading" du Dashboard.
                Cette page est maintenant disponible pour votre nouvelle fonctionnalité.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
