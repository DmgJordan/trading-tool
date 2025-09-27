// Types pour les connecteurs API basés sur les schémas Pydantic

export interface StandardApiKeyTest {
  api_key: string;
  api_type: 'anthropic' | 'openai' | 'coingecko';
}

export interface DexKeyTest {
  private_key: string;
  dex_type: 'hyperliquid';
  use_testnet: boolean;
}

export interface ConnectorTestResponse {
  status: 'success' | 'error';
  message: string;
  data?: Record<string, any>;
  validation?: Record<string, any>;
  timestamp: string;
}

export interface KeyFormatValidation {
  key: string;
  key_type: 'api_key' | 'private_key';
  service_type: string;
}

export interface UserInfoRequest {
  service_type: 'hyperliquid' | 'anthropic' | 'coingecko';
  use_testnet?: boolean;
}

export interface HyperliquidUserInfo {
  wallet_address: string;
  network: 'mainnet' | 'testnet';
  user_state_available: boolean;
  account_value?: number;
  open_positions?: number;
}

export interface AnthropicApiInfo {
  api_version: string;
  model_used: string;
  available_models?: string[];
}

export interface CoinGeckoApiInfo {
  plan_type: string;
  rate_limit?: number;
  monthly_calls_used?: number;
  monthly_calls_limit?: number;
}
