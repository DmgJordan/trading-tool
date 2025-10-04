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

/**
 * Structure du champ `data` retourné selon le type de connecteur
 * - Pour les tests de connexion simples, data est null ou undefined
 * - Pour les requêtes d'infos utilisateur, data contient les détails
 */
export type ConnectorTestData =
  | HyperliquidUserInfo
  | AnthropicApiInfo
  | CoinGeckoApiInfo
  | null
  | undefined;

/**
 * Structure du champ `validation` retourné par les validators
 */
export interface ApiValidationInfo {
  api_type: 'anthropic' | 'coingecko';
  connector_type: 'standard_api';
  authentication_method: 'api_key';
}

export interface DexValidationInfo {
  network: 'mainnet' | 'testnet';
  connector_type: 'hyperliquid';
  sdk_used: boolean;
}

export type ValidationInfo =
  | ApiValidationInfo
  | DexValidationInfo
  | null
  | undefined;

/**
 * Réponse standard des tests de connecteurs
 */
export interface ConnectorTestResponse {
  status: 'success' | 'error';
  message: string;
  data?: ConnectorTestData;
  validation?: ValidationInfo;
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
