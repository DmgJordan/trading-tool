'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '../store/authStore';
import LoadingScreen from './LoadingScreen';

interface RouteGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  fallback?: React.ReactNode;
}

export default function RouteGuard({
  children,
  requireAuth = true,
  fallback,
}: RouteGuardProps) {
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated, refreshToken } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  // Pages publiques qui ne nécessitent pas d'authentification
  const publicRoutes = ['/login'];
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

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

  useEffect(() => {
    if (!isLoading) {
      // Logique de redirection après vérification de l'auth
      if (requireAuth && !isAuthenticated && !isPublicRoute) {
        // Utilisateur non authentifié sur une page protégée
        const currentPath = encodeURIComponent(pathname);
        router.push(`/login?redirect=${currentPath}`);
        return;
      }

      if (!requireAuth && isAuthenticated && isPublicRoute) {
        // Utilisateur authentifié sur une page publique
        router.push('/');
        return;
      }
    }
  }, [
    isLoading,
    isAuthenticated,
    requireAuth,
    isPublicRoute,
    router,
    pathname,
  ]);

  // Affichage pendant le chargement
  if (isLoading) {
    return fallback || <LoadingScreen />;
  }

  // Vérifications de sécurité avant d'afficher le contenu
  if (requireAuth && !isAuthenticated && !isPublicRoute) {
    // L'utilisateur sera redirigé, afficher un loading en attendant
    return fallback || <LoadingScreen message="Redirection en cours..." />;
  }

  if (!requireAuth && isAuthenticated && isPublicRoute) {
    // L'utilisateur sera redirigé, afficher un loading en attendant
    return fallback || <LoadingScreen message="Redirection en cours..." />;
  }

  // Afficher le contenu seulement si toutes les vérifications passent
  return <>{children}</>;
}

// Hook personnalisé pour utiliser RouteGuard facilement
export function useRouteGuard(requireAuth: boolean = true) {
  const { isAuthenticated } = useAuthStore();
  const pathname = usePathname();

  const publicRoutes = ['/login'];
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  const shouldRedirect = requireAuth
    ? !isAuthenticated && !isPublicRoute
    : isAuthenticated && isPublicRoute;

  return {
    isAuthenticated,
    isPublicRoute,
    shouldRedirect,
    canAccess: requireAuth
      ? isAuthenticated
      : !isAuthenticated || !isPublicRoute,
  };
}
