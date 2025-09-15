import axios from 'axios';
import { LoginRequest, RegisterRequest, AuthTokens, User } from '../types/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'accès aux requêtes
api.interceptors.request.use((config) => {
  const tokens = localStorage.getItem('auth_tokens');
  if (tokens) {
    const { access_token } = JSON.parse(tokens);
    if (config.headers) {
      config.headers.Authorization = `Bearer ${access_token}`;
    }
  }
  return config;
});

// Intercepteur pour gérer l'expiration des tokens
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expiré, essayer de le rafraîchir
      const tokens = localStorage.getItem('auth_tokens');
      if (tokens) {
        try {
          const { refresh_token } = JSON.parse(tokens);
          const newTokens = await refreshTokens(refresh_token);

          // Mettre à jour les tokens stockés
          localStorage.setItem('auth_tokens', JSON.stringify(newTokens));

          // Relancer la requête originale avec le nouveau token
          if (error.config && error.config.headers) {
            error.config.headers.Authorization = `Bearer ${newTokens.access_token}`;
            return api.request(error.config);
          }
        } catch {
          // Impossible de rafraîchir, déconnecter l'utilisateur
          localStorage.removeItem('auth_tokens');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<AuthTokens> => {
    const response = await api.post<AuthTokens>('/auth/register', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  updateUser: async (userData: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/users/me', userData);
    return response.data;
  },
};

const refreshTokens = async (refreshToken: string): Promise<AuthTokens> => {
  const response = await axios.post<AuthTokens>(
    `${API_BASE_URL}/auth/refresh`,
    { refresh_token: refreshToken }
  );
  return response.data;
};

export default api;