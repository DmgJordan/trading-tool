import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type {
  AuthState,
  AuthActions,
  LoginRequest,
  RegisterRequest,
  User,
} from './types';
import { authApi } from '@/services/api/auth.api';

interface AuthStore extends AuthState, AuthActions {}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // État initial
      user: null,
      tokens: null,
      isAuthenticated: false,
      isInitialized: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true, error: null });

          const tokens = await authApi.login(credentials);

          /**
           * ✅ OPTIMISÉ : Système hybride
           * - access_token → localStorage (utilisé par intercepteurs HTTP)
           * - refresh_token → cookie HttpOnly (géré par backend, sécurisé)
           *
           * On ne stocke QUE l'access_token en localStorage pour limiter
           * l'exposition en cas de XSS (durée courte : 15-30min)
           */
          localStorage.setItem(
            'auth_tokens',
            JSON.stringify({
              access_token: tokens.access_token,
              // refresh_token omis → sécurisé dans cookie HttpOnly
            })
          );

          const user = await authApi.getMe();

          set({
            user,
            tokens,
            isAuthenticated: true,
            isInitialized: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } })?.response
              ?.data?.detail || 'Erreur de connexion';
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isInitialized: true,
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      register: async (userData: RegisterRequest) => {
        try {
          set({ isLoading: true, error: null });

          const tokens = await authApi.register(userData);

          /**
           * ✅ OPTIMISÉ : Système hybride (même logique que login)
           * - access_token → localStorage uniquement
           * - refresh_token → cookie HttpOnly (backend)
           */
          localStorage.setItem(
            'auth_tokens',
            JSON.stringify({
              access_token: tokens.access_token,
              // refresh_token omis → sécurisé dans cookie HttpOnly
            })
          );

          const user = await authApi.getMe();

          set({
            user,
            tokens,
            isAuthenticated: true,
            isInitialized: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } })?.response
              ?.data?.detail || "Erreur lors de l'inscription";
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isInitialized: true,
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch (error) {
          // Ignorer les erreurs de logout côté serveur
          console.warn('Erreur lors de la déconnexion côté serveur:', error);
        } finally {
          // Nettoyer l'état local et le localStorage
          localStorage.removeItem('auth_tokens');
          localStorage.removeItem('user');
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isInitialized: true,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshToken: async () => {
        try {
          const tokens = localStorage.getItem('auth_tokens');
          if (!tokens) {
            throw new Error('Aucun token de rafraîchissement disponible');
          }

          JSON.parse(tokens); // Vérifier la validité du token
          // L'API interceptor gère automatiquement le rafraîchissement
          const user = await authApi.getMe();

          set({ user, isAuthenticated: true, isInitialized: true });
        } catch (error) {
          // Échec du rafraîchissement, déconnecter l'utilisateur
          get().logout();
          throw error;
        }
      },

      updateUser: async (userData: Partial<User>) => {
        try {
          set({ isLoading: true, error: null });

          const updatedUser = await authApi.updateUser(userData);

          set({
            user: updatedUser,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage =
            (error as { response?: { data?: { detail?: string } } })?.response
              ?.data?.detail || 'Erreur lors de la mise à jour';
          set({
            isInitialized: true,
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      setUser: (user: User) => {
        set({ user });
      },

      clearError: () => {
        set({ error: null });
      },

      // Nouvelle méthode pour initialiser l'état d'authentification
      initialize: async () => {
        try {
          const tokens = localStorage.getItem('auth_tokens');
          const currentState = get();

          // Si l'utilisateur est marqué comme authentifié mais n'a pas de tokens, le déconnecter
          if (currentState.isAuthenticated && !tokens) {
            console.warn(
              'Utilisateur authentifié sans tokens - déconnexion forcée'
            );
            set({
              user: null,
              tokens: null,
              isAuthenticated: false,
              isInitialized: true,
              isLoading: false,
              error: null,
            });
            return;
          }

          if (tokens && !currentState.isAuthenticated) {
            // Essayer de récupérer les informations utilisateur
            await get().refreshToken();
          } else {
            // Pas de tokens ou déjà authentifié avec tokens valides
            set({ isInitialized: true });
          }
        } catch (error) {
          // Échec de l'initialisation, déconnecter par sécurité
          console.warn(
            "Échec de l'initialisation de l'authentification:",
            error
          );
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isInitialized: true,
            isLoading: false,
            error: null,
          });
        }
      },
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => localStorage),
      // Ne persister que l'utilisateur, pas les tokens (sécurité)
      partialize: state => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// TODO: déplacer la synchronisation des tokens vers un provider dédié une fois la session entièrement basée sur cookies
