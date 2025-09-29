export interface HyperliquidPortfolioSummary {
  accountValue?: number | null;
  totalMarginUsed?: number | null;
  totalUnrealizedPnl?: number | null;
  withdrawableBalance?: number | null;
  perpPositionCount: number;
  assetPositionCount: number;
}

export interface HyperliquidPerpPositionDetails {
  sz?: string;
  size?: string;
  szi?: string;
  entryPx?: string;
  entry_px?: string;
  markPx?: string;
  mark_px?: string;
  oraclePx?: string;
  oracle_px?: string;
  leverage?: string;
  leverageValue?: string;
  leverageType?: string;
  side?: string;
  type?: string;
  position?: Record<string, unknown>;
  marginUsed?: string;
  positionValue?: string;
  unrealizedPnl?: string;
  unrealized_pnl?: string;
  [key: string]: unknown;
}

export interface HyperliquidPerpPosition {
  symbol?: string;
  coin?: string;
  asset?: string;
  position?: HyperliquidPerpPositionDetails;
  sz?: string;
  size?: string;
  entryPx?: string;
  entry_px?: string;
  markPx?: string;
  mark_px?: string;
  unrealizedPnl?: string;
  unrealized_pnl?: string;
  oraclePx?: string;
  oracle_px?: string;
  [key: string]: unknown;
}

export interface HyperliquidAssetPosition {
  coin?: string;
  asset?: string;
  total?: string;
  balance?: string;
  available?: string;
  usdValue?: string;
  usd_value?: string;
  [key: string]: unknown;
}

export interface HyperliquidFill {
  time?: number;
  symbol?: string;
  coin?: string;
  side?: string;
  dir?: string;
  sz?: string;
  size?: string;
  px?: string;
  price?: string;
  hash?: string;
  orderId?: string;
  [key: string]: unknown;
}

export interface HyperliquidOpenOrder {
  coin?: string;
  symbol?: string;
  asset?: string;
  sz?: string;
  size?: string;
  px?: string;
  price?: string;
  limitPx?: string;
  limit_px?: string;
  side?: string;
  dir?: string;
  isTrigger?: boolean;
  tif?: string;
  triggerPx?: string;
  reduceOnly?: boolean;
  cloid?: string;
  oid?: number;
  [key: string]: unknown;
}

export interface HyperliquidMarginSummary {
  accountValue?: string | null;
  totalMarginUsed?: string | null;
  totalNtlPos?: string | null;
  totalRawUsd?: string | null;
  raw?: Record<string, unknown> | null;
}

export interface HyperliquidUserState {
  marginSummary?: HyperliquidMarginSummary | null;
  crossMarginSummary?: HyperliquidMarginSummary | null;
  perpPositions?: HyperliquidPerpPosition[] | null;
  assetPositions?: HyperliquidAssetPosition[] | null;
  withdrawables?: Record<string, unknown> | null;
  crossMaintenanceMarginUsed?: string | null;
  [key: string]: unknown;
}

export interface HyperliquidSpotBalanceEntry {
  asset: string;
  total?: string;
  available?: string;
  usdValue?: string;
  [key: string]: unknown;
}

export interface HyperliquidSpotUserState {
  balances?: Record<string, unknown> | null;
  tokenBalances?: Record<string, unknown> | null;
  assetPositions?: HyperliquidSpotBalanceEntry[] | null;
  positions?: HyperliquidSpotBalanceEntry[] | null;
  [key: string]: unknown;
}

export interface HyperliquidPortfolioData {
  [key: string]: unknown;
}

export interface HyperliquidUserInfoData {
  wallet_address: string;
  network: 'mainnet' | 'testnet';
  retrieved_at: string;
  portfolio_summary: HyperliquidPortfolioSummary;
  user_state: HyperliquidUserState | null;
  spot_user_state: HyperliquidSpotUserState | null;
  portfolio: HyperliquidPortfolioData | null;
  fills: HyperliquidFill[];
  open_orders: HyperliquidOpenOrder[];
  frontend_open_orders?: Record<string, unknown> | null;
}

export interface HyperliquidConnectorResponse {
  status: 'success' | 'error';
  message: string;
  data?: HyperliquidUserInfoData;
  timestamp: string;
}
