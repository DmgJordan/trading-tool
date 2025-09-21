import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Instance axios centralisée pour toute l'application
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'accès aux requêtes
apiClient.interceptors.request.use((config) => {
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

export default apiClient;