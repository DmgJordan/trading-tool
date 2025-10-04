'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/features/auth/model/store';
import LoadingScreen from '@/shared/ui/LoadingScreen';

interface RouteGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function RouteGuard({ children, fallback }: RouteGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated, refreshToken } = useAuthStore();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Vérifier si on a des tokens stockés
        if (typeof window !== 'undefined') {
          const tokens = localStorage.getItem('auth_tokens');

          if (tokens && !isAuthenticated) {
            // Essayer de rafraîchir l'authentification
            await refreshToken();
          }
        }
      } catch (error) {
        console.warn(
          "Erreur lors de la vérification de l'authentification:",
          error
        );
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [isAuthenticated, refreshToken]);

  /**
   * ⚠️ Redirections SUPPRIMÉES - gérées par middleware SSR
   *
   * Avant (client) :
   * - Redirection après hydration React → flash perceptible
   * - router.push() après isLoading = false
   *
   * Maintenant (SSR) :
   * - Redirection middleware.ts AVANT hydration
   * - Pas de flash, sécurité renforcée
   *
   * RouteGuard = fallback uniquement pour :
   * - Refresh token localStorage
   * - Affichage LoadingScreen pendant init
   */

  /**
   * Affichage pendant initialisation auth
   *
   * LoadingScreen affiché uniquement pendant :
   * - Lecture localStorage tokens
   * - Appel refresh token si nécessaire
   *
   * Durée typique : 100-300ms
   */
  if (isLoading) {
    return fallback || <LoadingScreen />;
  }

  /**
   * Afficher le contenu
   *
   * Sécurité : les redirections sont déjà gérées par middleware SSR
   * Si on arrive ici, c'est que :
   * - Route publique + pas auth → OK
   * - Route protégée + auth → OK
   * - Autres cas → déjà redirigé par middleware (jamais atteint)
   */
  return <>{children}</>;
}
