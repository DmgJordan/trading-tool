'use client';

import { useEffect, type ReactNode } from 'react';
import RouteGuard from '@/features/auth/ui/RouteGuard';
import LoadingScreen from '@/shared/ui/LoadingScreen';
import { useAuthStore } from '@/features/auth/model/store';

interface AuthProviderProps {
  children: ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const { isInitialized, initialize } = useAuthStore();

  useEffect(() => {
    if (!isInitialized) {
      initialize();
    }
  }, [isInitialized, initialize]);

  if (!isInitialized) {
    return <LoadingScreen message="Initialisation de l'authentification..." />;
  }

  return <RouteGuard>{children}</RouteGuard>;
}
