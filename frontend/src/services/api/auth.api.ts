import { z } from 'zod';
import http from '@/services/http/client';
import type {
  LoginRequest,
  RegisterRequest,
  AuthTokens,
  User,
} from '@/lib/types/auth';

/**
 * Transform nullable strings from backend to optional strings
 * Backend returns null for empty fields, we convert to undefined
 */
const nullableString = z
  .string()
  .nullable()
  .optional()
  .transform(val => val ?? undefined);

const authTokensSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().default('Bearer'),
});

const userSchema: z.ZodType<User> = z
  .object({
    id: z.number(),
    email: z.string().email(),
    username: z.string(),
    hyperliquid_api_key: nullableString,
    hyperliquid_public_address: nullableString,
    anthropic_api_key: nullableString,
    coingecko_api_key: nullableString,
    hyperliquid_api_key_status: nullableString,
    anthropic_api_key_status: nullableString,
    coingecko_api_key_status: nullableString,
    created_at: z.string(),
    updated_at: z
      .string()
      .optional()
      .transform(val => val ?? undefined),
  })
  .passthrough();

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthTokens> => {
    const response = await http.post<unknown>('/auth/login', credentials);
    return authTokensSchema.parse(response);
  },
  register: async (userData: RegisterRequest): Promise<AuthTokens> => {
    const response = await http.post<unknown>('/auth/register', userData);
    return authTokensSchema.parse(response);
  },
  logout: async (): Promise<void> => {
    await http.post('/auth/logout', undefined, { auth: true });
  },
  getMe: async (): Promise<User> => {
    const response = await http.get<unknown>('/users/me', { auth: true });
    const parsed = userSchema.parse(response);
    return parsed;
  },
  updateUser: async (userData: Partial<User>): Promise<User> => {
    const response = await http.put<unknown>('/users/me', userData, {
      auth: true,
    });
    return userSchema.parse(response);
  },
};

export default authApi;
