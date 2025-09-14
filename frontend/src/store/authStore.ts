import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { AuthState, AuthActions, LoginRequest, RegisterRequest, User } from '../lib/types/auth';
import { authApi } from '../lib/api/auth';

interface AuthStore extends AuthState, AuthActions {}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // État initial
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true, error: null });

          const tokens = await authApi.login(credentials);

          // Stocker les tokens AVANT d'appeler getMe() pour que l'intercepteur les utilise
          localStorage.setItem('auth_tokens', JSON.stringify(tokens));

          const user = await authApi.getMe();

          set({
            user,
            tokens,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erreur de connexion';
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
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

          // Stocker les tokens AVANT d'appeler getMe() pour que l'intercepteur les utilise
          localStorage.setItem('auth_tokens', JSON.stringify(tokens));

          const user = await authApi.getMe();

          set({
            user,
            tokens,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: unknown) {
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erreur lors de l\'inscription';
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
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

          set({ user, isAuthenticated: true });
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
          const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erreur lors de la mise à jour';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
{
      name: 'auth-store',
      storage: createJSONStorage(() => localStorage),
      // Ne persister que l'utilisateur, pas les tokens (sécurité)
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);