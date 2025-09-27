import { LoginRequest, RegisterRequest, AuthTokens, User } from '../types/auth';
import apiClient from './client';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>(
      '/auth/login',
      credentials
    );
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>(
      '/auth/register',
      userData
    );
    return response.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  updateUser: async (userData: Partial<User>): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', userData);
    return response.data;
  },
};

export default apiClient;
