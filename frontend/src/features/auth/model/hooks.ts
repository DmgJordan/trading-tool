import { useAuthStore } from '@/features/auth/model/store';
import { useRouter, usePathname } from 'next/navigation';
import { isPublicRoute } from '@/constants/routes';

/**
 * Hook personnalisé pour gérer l'authentification
 * Centralise toute la logique d'authentification de l'application
 */
export const useAuth = () => {
  const {
    user,
    tokens,
    isAuthenticated,
    isInitialized,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshToken,
    updateUser,
    clearError,
  } = useAuthStore();

  return {
    // État
    user,
    tokens,
    isAuthenticated,
    isInitialized,
    isLoading,
    error,

    // Actions
    login,
    register,
    logout,
    refreshToken,
    updateUser,
    clearError,

    // Helpers
    isLoggedIn: isAuthenticated && user !== null,
    hasApiKeys: !!user?.anthropic_api_key || !!user?.hyperliquid_api_key,
  };
};

/**
 * Hook pour la protection des routes
 * Gère la logique de redirection automatique
 */
export const useRouteProtection = (requireAuth: boolean = true) => {
  const { isAuthenticated } = useAuthStore();
  const pathname = usePathname();
  const router = useRouter();

  const shouldRedirect = requireAuth
    ? !isAuthenticated && !isPublicRoute(pathname)
    : isAuthenticated && isPublicRoute(pathname);

  const redirectPath = requireAuth
    ? `/login?redirect=${encodeURIComponent(pathname)}`
    : '/';

  return {
    isAuthenticated,
    isPublic: isPublicRoute(pathname),
    shouldRedirect,
    redirectPath,
    redirect: () => router.push(redirectPath),
    canAccess: requireAuth
      ? isAuthenticated
      : !isAuthenticated || !isPublicRoute(pathname),
  };
};

/**
 * Hook pour vérifier la disponibilité des clés API
 */
export const useApiKeys = () => {
  const { user } = useAuthStore();

  return {
    hasAnthropicKey: !!user?.anthropic_api_key,
    hasHyperliquidKey: !!user?.hyperliquid_api_key,
    hasAllKeys: !!user?.anthropic_api_key && !!user?.hyperliquid_api_key,
    needsConfiguration: !user?.anthropic_api_key || !user?.hyperliquid_api_key,
  };
};
