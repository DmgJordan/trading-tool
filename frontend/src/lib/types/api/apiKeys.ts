/**
 * Types pour les tests de clés API
 */

export interface TestStoredKeyResponse {
  status: 'success' | 'error';
  message: string;
  data?: {
    api_version?: string;
    model_used?: string;
    available_models?: string[];
    plan_type?: string;
    rate_limit?: number;
    monthly_calls_used?: number;
    monthly_calls_limit?: number;
    wallet_address?: string;
    network?: 'mainnet' | 'testnet';
    user_state_available?: boolean;
    account_value?: number;
    open_positions?: number;
  };
  validation?: {
    api_type: string;
    connector_type: string;
    authentication_method: string;
    network?: string;
    sdk_used?: boolean;
  };
  timestamp: string;
}

export interface TestNewKeyRequest {
  api_key: string;
  api_type: 'anthropic' | 'coingecko' | 'hyperliquid';
}

export type TestNewKeyResponse = TestStoredKeyResponse;
