'use client';

import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import RouteGuard from './RouteGuard';
import LoadingScreen from './LoadingScreen';

interface AuthProviderProps {
  children: React.ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const { isInitialized, initialize } = useAuthStore();

  useEffect(() => {
    if (!isInitialized) {
      initialize();
    }
  }, [isInitialized, initialize]);

  // Afficher un écran de chargement pendant l'initialisation
  if (!isInitialized) {
    return <LoadingScreen message="Initialisation de l'authentification..." />;
  }

  // Utiliser RouteGuard pour protéger les routes
  return (
    <RouteGuard>
      {children}
    </RouteGuard>
  );
}