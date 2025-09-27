import apiClient from './client';
import {
  HyperliquidConnectorResponse,
  HyperliquidUserInfoData,
  HyperliquidPortfolioSummary,
  HyperliquidFill,
  HyperliquidOpenOrder,
  HyperliquidUserState,
  HyperliquidSpotUserState,
  HyperliquidPerpPosition,
} from '../types/hyperliquid';

interface HyperliquidUserInfoRaw {
  wallet_address?: string;
  network?: 'mainnet' | 'testnet';
  retrieved_at?: string;
  portfolio_summary?: Record<string, unknown>;
  user_state?: Record<string, unknown> | null;
  spot_user_state?: Record<string, unknown> | null;
  portfolio?: Record<string, unknown> | null;
  fills?: Array<Record<string, unknown>>;
  open_orders?: Array<Record<string, unknown>>;
  frontend_open_orders?: Record<string, unknown> | null;
}

interface HyperliquidConnectorResponseRaw {
  status: 'success' | 'error';
  message: string;
  data?: HyperliquidUserInfoRaw;
  timestamp: string;
}

const normalizeNumber = (value: unknown): number | null => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const normalizePortfolioSummary = (
  raw?: Record<string, unknown>
): HyperliquidPortfolioSummary => {
  return {
    accountValue: normalizeNumber(raw?.account_value ?? raw?.accountValue),
    totalMarginUsed: normalizeNumber(raw?.total_margin ?? raw?.totalMargin),
    totalUnrealizedPnl: normalizeNumber(
      raw?.total_unrealized_pnl ??
        raw?.totalUnrealizedPnl ??
        raw?.totalUnrealizedPnL
    ),
    withdrawableBalance: normalizeNumber(
      raw?.withdrawable_balance ?? raw?.withdrawableBalance ?? raw?.withdrawable
    ),
    perpPositionCount:
      typeof raw?.perp_position_count === 'number'
        ? (raw?.perp_position_count as number)
        : typeof raw?.perpPositionCount === 'number'
          ? (raw?.perpPositionCount as number)
          : 0,
    assetPositionCount:
      typeof raw?.asset_position_count === 'number'
        ? (raw?.asset_position_count as number)
        : typeof raw?.assetPositionCount === 'number'
          ? (raw?.assetPositionCount as number)
          : 0,
  };
};

const normalizeFills = (
  raw?: Array<Record<string, unknown>>
): HyperliquidFill[] => {
  if (!Array.isArray(raw)) return [];

  return raw.map(fill => ({
    time: typeof fill?.time === 'number' ? fill.time : undefined,
    symbol:
      typeof fill?.symbol === 'string'
        ? fill.symbol
        : typeof fill?.coin === 'string'
          ? (fill.coin as string)
          : undefined,
    coin: typeof fill?.coin === 'string' ? fill.coin : undefined,
    side:
      typeof fill?.side === 'string'
        ? fill.side
        : typeof fill?.dir === 'string'
          ? (fill.dir as string)
          : undefined,
    dir: typeof fill?.dir === 'string' ? fill.dir : undefined,
    sz:
      typeof fill?.sz === 'string'
        ? fill.sz
        : typeof fill?.size === 'string'
          ? (fill.size as string)
          : undefined,
    size: typeof fill?.size === 'string' ? fill.size : undefined,
    px:
      typeof fill?.px === 'string'
        ? fill.px
        : typeof fill?.price === 'string'
          ? (fill.price as string)
          : typeof fill?.limitPx === 'string'
            ? (fill.limitPx as string)
            : undefined,
    price: typeof fill?.price === 'string' ? fill.price : undefined,
    hash: typeof fill?.hash === 'string' ? fill.hash : undefined,
    orderId: typeof fill?.orderId === 'string' ? fill.orderId : undefined,
  }));
};

const normalizeOpenOrders = (
  raw?: Array<Record<string, unknown>>
): HyperliquidOpenOrder[] => {
  if (!Array.isArray(raw)) return [];

  return raw.map(order => ({
    coin: typeof order?.coin === 'string' ? order.coin : undefined,
    symbol: typeof order?.symbol === 'string' ? order.symbol : undefined,
    sz:
      typeof order?.sz === 'string'
        ? order.sz
        : typeof order?.size === 'string'
          ? (order.size as string)
          : undefined,
    size: typeof order?.size === 'string' ? order.size : undefined,
    px:
      typeof order?.px === 'string'
        ? order.px
        : typeof order?.price === 'string'
          ? (order.price as string)
          : typeof order?.limitPx === 'string'
            ? (order.limitPx as string)
            : typeof order?.limit_px === 'string'
              ? (order.limit_px as string)
              : undefined,
    price: typeof order?.price === 'string' ? order.price : undefined,
    side:
      typeof order?.side === 'string'
        ? order.side
        : typeof order?.dir === 'string'
          ? (order.dir as string)
          : undefined,
    dir: typeof order?.dir === 'string' ? order.dir : undefined,
    isTrigger:
      typeof order?.isTrigger === 'boolean' ? order.isTrigger : undefined,
    tif: typeof order?.tif === 'string' ? order.tif : undefined,
    triggerPx:
      typeof order?.triggerPx === 'string' ? order.triggerPx : undefined,
    reduceOnly:
      typeof order?.reduceOnly === 'boolean' ? order.reduceOnly : undefined,
    cloid: typeof order?.cloid === 'string' ? order.cloid : undefined,
    oid: typeof order?.oid === 'number' ? order.oid : undefined,
  }));
};

const normalizeUserState = (
  raw?: Record<string, unknown> | null
): HyperliquidUserState | null => {
  if (!raw) return null;

  const marginSummaryRaw = raw.marginSummary as
    | Record<string, unknown>
    | undefined;
  const crossMarginSummaryRaw = raw.crossMarginSummary as
    | Record<string, unknown>
    | undefined;
  const normalizeSummary = (
    summary?: Record<string, unknown>
  ): Record<string, unknown> | null =>
    summary && typeof summary === 'object' ? summary : null;

  const perpPositionsRaw = Array.isArray(raw.perpPositions)
    ? (raw.perpPositions as HyperliquidPerpPosition[])
    : Array.isArray(raw.assetPositions)
      ? (raw.assetPositions as HyperliquidPerpPosition[])
      : null;

  return {
    ...raw,
    marginSummary: normalizeSummary(marginSummaryRaw),
    crossMarginSummary: normalizeSummary(crossMarginSummaryRaw),
    perpPositions: perpPositionsRaw,
    assetPositions: Array.isArray(raw.assetPositions)
      ? (raw.assetPositions as HyperliquidPerpPosition[])
      : perpPositionsRaw,
    withdrawables:
      typeof raw.withdrawables === 'object' && raw.withdrawables !== null
        ? (raw.withdrawables as Record<string, unknown>)
        : null,
    openOrders: Array.isArray(raw.openOrders)
      ? normalizeOpenOrders(raw.openOrders as Array<Record<string, unknown>>)
      : null,
  };
};

const normalizeSpotUserState = (
  raw?: Record<string, unknown> | null
): HyperliquidSpotUserState | null => {
  if (!raw) return null;

  const spotBalances = raw.balances || raw.tokenBalances;
  const normalizeBalances = () => {
    if (spotBalances && typeof spotBalances === 'object') {
      return spotBalances as Record<string, unknown>;
    }
    return null;
  };

  const spotAssetPositions = Array.isArray(raw.assetPositions)
    ? (raw.assetPositions as Array<Record<string, unknown>>)
    : Array.isArray(raw.positions)
      ? (raw.positions as Array<Record<string, unknown>>)
      : null;

  return {
    ...raw,
    balances: normalizeBalances(),
    assetPositions:
      spotAssetPositions as HyperliquidSpotUserState['assetPositions'],
  };
};

const normalizeUserInfo = (
  raw: HyperliquidUserInfoRaw | undefined,
  timestamp: string
): HyperliquidUserInfoData | undefined => {
  if (!raw?.wallet_address || !raw.network) {
    return undefined;
  }

  const retrievedAt =
    typeof raw.retrieved_at === 'string' ? raw.retrieved_at : timestamp;

  return {
    walletAddress: raw.wallet_address,
    network: raw.network,
    retrievedAt,
    portfolioSummary: normalizePortfolioSummary(raw.portfolio_summary ?? {}),
    userState: normalizeUserState(raw.user_state ?? null),
    spotUserState: normalizeSpotUserState(raw.spot_user_state ?? null),
    portfolio: raw.portfolio ?? null,
    fills: normalizeFills(raw.fills),
    openOrders: normalizeOpenOrders(raw.open_orders),
    frontendOpenOrders: raw.frontend_open_orders ?? null,
  };
};

export interface HyperliquidUserInfoOptions {
  useTestnet?: boolean;
}

export const hyperliquidApi = {
  async getUserInfo(
    options: HyperliquidUserInfoOptions = {}
  ): Promise<HyperliquidConnectorResponse> {
    const response = await apiClient.post<HyperliquidConnectorResponseRaw>(
      '/connectors/user-info',
      {
        service_type: 'hyperliquid',
        use_testnet: options.useTestnet ?? false,
      }
    );

    const raw = response.data;
    const normalizedData = normalizeUserInfo(raw.data, raw.timestamp);

    return {
      status: raw.status,
      message: raw.message,
      data: normalizedData,
      timestamp: raw.timestamp,
    };
  },
};
