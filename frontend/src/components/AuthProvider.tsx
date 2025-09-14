'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '../store/authStore';

interface AuthProviderProps {
  children: React.ReactNode;
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const [isInitialized, setIsInitialized] = useState(false);
  const { isAuthenticated, refreshToken, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  // Pages publiques qui ne nécessitent pas d'authentification
  const publicPages = ['/login'];
  const isPublicPage = publicPages.some(page => pathname.startsWith(page));

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Vérifier si des tokens existent dans le localStorage
        if (typeof window !== 'undefined') {
          const tokens = localStorage.getItem('auth_tokens');

          if (tokens && !isAuthenticated) {
            // Essayer de récupérer les informations utilisateur
            await refreshToken();
          }
        }
      } catch (error) {
        // Si le rafraîchissement échoue, déconnecter l'utilisateur
        console.warn('Échec de l\'initialisation de l\'authentification:', error);
        logout();
      } finally {
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  useEffect(() => {
    if (isInitialized) {
      // Rediriger les utilisateurs non authentifiés vers la page de connexion
      if (!isAuthenticated && !isPublicPage) {
        router.push('/login');
      }
      // Rediriger les utilisateurs authentifiés depuis la page de connexion
      else if (isAuthenticated && isPublicPage) {
        router.push('/');
      }
    }
  }, [isInitialized, isAuthenticated, isPublicPage, router]);

  // Afficher un spinner de chargement pendant l'initialisation
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">T</span>
          </div>
          <div className="animate-spin w-8 h-8 border-4 border-black border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gray-600 mt-4">Chargement...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}