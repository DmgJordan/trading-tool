import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Import dynamique pour éviter les cycles de dépendances
let getAuthStore: () => any;

// Instance axios centralisée pour toute l'application
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'accès aux requêtes
apiClient.interceptors.request.use((config) => {
  // Essayer d'abord localStorage pour les tokens existants
  let access_token = null;
  const storedTokens = localStorage.getItem('auth_tokens');

  if (storedTokens) {
    try {
      const parsedTokens = JSON.parse(storedTokens);
      access_token = parsedTokens.access_token;
    } catch (error) {
      console.error('Erreur lors du parsing des tokens localStorage:', error);
    }
  }

  // Si pas de token dans localStorage, essayer le store Zustand
  if (!access_token && getAuthStore) {
    try {
      const store = getAuthStore();
      if (store?.tokens?.access_token) {
        access_token = store.tokens.access_token;
      }
    } catch (error) {
      console.error('Erreur lors de l\'accès au store Zustand:', error);
    }
  }

  if (access_token && config.headers) {
    config.headers.Authorization = `Bearer ${access_token}`;
  }

  return config;
});

// Intercepteur pour gérer l'expiration des tokens
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const tokens = localStorage.getItem('auth_tokens');
      if (tokens) {
        try {
          const { refresh_token } = JSON.parse(tokens);

          // Appel direct pour éviter l'interception
          const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token
          });

          const newTokens = refreshResponse.data;
          localStorage.setItem('auth_tokens', JSON.stringify(newTokens));

          // Relancer la requête originale
          if (error.config && error.config.headers) {
            error.config.headers.Authorization = `Bearer ${newTokens.access_token}`;
            return apiClient.request(error.config);
          }
        } catch {
          // Déconnexion en cas d'échec
          localStorage.removeItem('auth_tokens');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Fonction pour initialiser la référence au store
export const initializeAuthStore = (store: any) => {
  getAuthStore = () => store;
};

export default apiClient;