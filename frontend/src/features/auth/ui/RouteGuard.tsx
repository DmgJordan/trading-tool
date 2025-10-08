'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/features/auth/model/store';
import LoadingScreen from '@/shared/ui/LoadingScreen';
import { isTokenExpired, getAccessToken } from '@/lib/auth/token-utils';

interface RouteGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function RouteGuard({ children, fallback }: RouteGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated, initialize, logout } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getAccessToken();

        // Cas 1: Pas de token du tout
        if (!token) {
          console.log('[RouteGuard] Aucun token trouvé');
          setIsLoading(false);
          return;
        }

        // Cas 2: Token présent mais expiré
        if (isTokenExpired(token)) {
          console.warn('[RouteGuard] Token expiré détecté, tentative de refresh via initialize');
          try {
            await initialize();
          } catch (error) {
            console.warn('[RouteGuard] Échec initialize, redirection vers login');
            await logout();
            router.push('/login');
            return;
          }
        } else if (!isAuthenticated) {
          // Cas 3: Token valide mais store pas initialisé
          console.log('[RouteGuard] Token valide trouvé, initialisation du store');
          await initialize();
        }
      } catch (error) {
        console.warn(
          "[RouteGuard] Erreur lors de la vérification de l'authentification:",
          error
        );
        // En cas d'erreur, rediriger vers login par sécurité
        await logout();
        router.push('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []); // Déclenchement unique au mount

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
