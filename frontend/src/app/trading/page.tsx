'use client';

import { useEffect, useMemo } from 'react';
import type { ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '../../components/Navbar';
import { useAuthStore } from '../../store/authStore';
import { useHyperliquidStore } from '../../store/hyperliquidStore';
import {
  HyperliquidFill,
  HyperliquidPerpPosition,
  HyperliquidSpotUserState
} from '../../lib/types/hyperliquid';

const formatCurrency = (value?: number | null) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return '—';
  }

  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value);
};

const formatNumber = (value?: string | number | null, digits = 4) => {
  if (value === undefined || value === null) return '—';
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  }).format(numeric);
};

const formatTimestamp = (value?: number) => {
  if (!value) return '—';
  const isSeconds = value < 1e12;
  const date = new Date(isSeconds ? value * 1000 : value);
  return new Intl.DateTimeFormat('fr-FR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
};

const derivePerpPositions = (positions: HyperliquidPerpPosition[] | null | undefined) => {
  if (!Array.isArray(positions)) return [];

  return positions.map((position) => {
    const nested = position?.position && typeof position.position === 'object'
      ? position.position
      : undefined;

    const base = nested && typeof nested === 'object' ? nested : position;

    const size = (base?.szi as string | undefined)
      || (base?.sz as string | undefined)
      || (base?.size as string | undefined)
      || position.sz
      || position.size;

    const entryPx = (base?.entryPx as string | undefined)
      || (base?.entry_px as string | undefined)
      || position.entryPx
      || position.entry_px;

    const markPx = (base?.markPx as string | undefined)
      || (base?.mark_px as string | undefined)
      || (base?.oraclePx as string | undefined)
      || (base?.oracle_px as string | undefined)
      || position.markPx
      || position.mark_px;

    const pnl = (base?.unrealizedPnl as string | undefined)
      || (base?.unrealized_pnl as string | undefined)
      || position.unrealizedPnl
      || position.unrealized_pnl;

    const side = (base?.side as string | undefined)
      || position.side
      || (position as { dir?: string }).dir;

    const symbol = (position.symbol || position.coin || position.asset || (base?.coin as string)) ?? '—';

    return {
      symbol,
      side,
      size,
      entryPx,
      markPx,
      pnl,
    };
  });
};

const deriveSpotPositions = (spotState: HyperliquidSpotUserState | null | undefined) => {
  if (!spotState) return [];

  const positionsArray = Array.isArray(spotState.assetPositions)
    ? spotState.assetPositions
    : Array.isArray(spotState.positions)
      ? spotState.positions
      : null;

  if (positionsArray) {
    return positionsArray.map(position => ({
      asset: (position as { coin?: string; asset?: string; symbol?: string }).coin
        || (position as { asset?: string }).asset
        || (position as { symbol?: string }).symbol
        || '—',
      total: (position as { total?: string; balance?: string }).total
        || (position as { balance?: string }).balance,
      available: (position as { available?: string }).available,
      usdValue: (position as { usdValue?: string; usd_value?: string }).usdValue
        || (position as { usd_value?: string }).usd_value,
    }));
  }

  const balances = spotState.balances || spotState.tokenBalances;
  if (balances && typeof balances === 'object') {
    return Object.entries(balances)
      .map(([asset, value]) => ({
        asset,
        total: typeof value === 'string' || typeof value === 'number' ? String(value) : undefined,
      }))
      .filter(entry => entry.total !== undefined);
  }

  return [];
};

const normalizeSide = (side?: string) => {
  if (!side) return '—';
  const normalized = side.toLowerCase();
  if (normalized.startsWith('b')) return 'Achat';
  if (normalized.startsWith('s') || normalized.startsWith('a')) return 'Vente';
  if (normalized.startsWith('l')) return 'Long';
  if (normalized.startsWith('r') || normalized.startsWith('sh')) return 'Short';
  return side;
};

const computeFillValue = (fill: HyperliquidFill) => {
  const size = fill.sz ?? fill.size;
  const price = fill.px ?? fill.price;
  if (!size || !price) return null;

  const numericSize = Number(size);
  const numericPrice = Number(price);
  if (!Number.isFinite(numericSize) || !Number.isFinite(numericPrice)) return null;
  return numericSize * numericPrice;
};

export default function TradingPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const data = useHyperliquidStore(state => state.data);
  const isLoading = useHyperliquidStore(state => state.isLoading);
  const error = useHyperliquidStore(state => state.error);
  const lastUpdated = useHyperliquidStore(state => state.lastUpdated);
  const useTestnet = useHyperliquidStore(state => state.useTestnet);
  const fetchUserInfo = useHyperliquidStore(state => state.fetchUserInfo);
  const setUseTestnet = useHyperliquidStore(state => state.setUseTestnet);
  const clearError = useHyperliquidStore(state => state.clearError);

  useEffect(() => {
    if (!isAuthenticated && user === null) {
      router.push('/login');
    }
  }, [isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserInfo().catch(error => {
        console.error('Échec de la récupération des données Hyperliquid:', error);
      });
    }
  }, [isAuthenticated, fetchUserInfo]);

  const summaryCards = useMemo(() => {
    const summary = data?.portfolioSummary;
    return [
      {
        title: 'Valeur du compte',
        value: formatCurrency(summary?.accountValue ?? null),
      },
      {
        title: 'Marge utilisée',
        value: formatCurrency(summary?.totalMarginUsed ?? null),
      },
      {
        title: 'PNL latent',
        value: summary?.totalUnrealizedPnl === undefined || summary?.totalUnrealizedPnl === null
          ? '—'
          : formatCurrency(summary.totalUnrealizedPnl),
        emphasis: (summary?.totalUnrealizedPnl ?? 0) > 0
          ? 'text-green-600'
          : (summary?.totalUnrealizedPnl ?? 0) < 0
            ? 'text-red-600'
            : 'text-black',
      },
      {
        title: 'Solde retirable',
        value: formatCurrency(summary?.withdrawableBalance ?? null),
      },
      {
        title: 'Positions perp',
        value: summary?.perpPositionCount ?? 0,
      },
      {
        title: 'Positions spot',
        value: summary?.assetPositionCount ?? 0,
      },
    ];
  }, [data?.portfolioSummary]);

  const perpPositions = useMemo(
    () => derivePerpPositions(data?.userState?.perpPositions ?? data?.userState?.assetPositions),
    [data?.userState?.perpPositions, data?.userState?.assetPositions],
  );

  const spotPositions = useMemo(
    () => deriveSpotPositions(data?.spotUserState),
    [data?.spotUserState],
  );

  const fills = useMemo(() => (Array.isArray(data?.fills) ? data?.fills.slice(0, 25) : []), [data?.fills]);
  const openOrders = useMemo(() => (Array.isArray(data?.openOrders) ? data?.openOrders : []), [data?.openOrders]);

  const handleRefresh = () => {
    fetchUserInfo().catch(err => {
      console.error('Erreur lors du rafraîchissement Hyperliquid:', err);
    });
  };

  const handleNetworkChange = async (event: ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = event.target.value === 'testnet';
    try {
      await setUseTestnet(selectedValue);
    } catch (err) {
      console.error('Impossible de changer de réseau Hyperliquid:', err);
    }
  };

  const networkLabel = useTestnet ? 'Testnet' : 'Mainnet';
  const retrievedAt = data?.retrievedAt || lastUpdated;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-black">Trading Hyperliquid</h1>
            <p className="text-gray-600 mt-2">
              Suivi de votre portefeuille, positions et exécutions en direct depuis Hyperliquid.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
              <p className="text-xs text-gray-500 uppercase tracking-wide">Réseau</p>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-sm font-semibold text-black">{networkLabel}</span>
                <select
                  value={useTestnet ? 'testnet' : 'mainnet'}
                  onChange={handleNetworkChange}
                  disabled={isLoading}
                  className="border border-gray-200 rounded-md text-sm text-black focus:outline-none focus:ring-2 focus:ring-black px-2 py-1 bg-white"
                >
                  <option value="mainnet">Mainnet</option>
                  <option value="testnet">Testnet</option>
                </select>
              </div>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className={`inline-flex items-center justify-center px-5 py-3 rounded-lg text-sm font-semibold transition-colors border-2 border-black ${
                isLoading ? 'bg-gray-200 text-gray-500 cursor-not-allowed' : 'bg-black text-white hover:bg-white hover:text-black'
              }`}
            >
              {isLoading ? 'Rafraîchissement…' : 'Rafraîchir'}
            </button>
          </div>
        </div>

        {error && (
          <div className="border-l-4 border-red-500 bg-red-50 px-4 py-3 rounded-md text-sm text-red-700 flex flex-col gap-2">
            <div className="font-semibold">Erreur lors de la récupération des données Hyperliquid</div>
            <span>{error}</span>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  clearError();
                  handleRefresh();
                }}
                className="text-sm font-semibold text-red-700 hover:text-red-900"
              >
                Réessayer
              </button>
              <button
                onClick={() => router.push('/')}
                className="text-sm font-semibold text-red-700 hover:text-red-900"
              >
                Ouvrir la configuration API
              </button>
            </div>
          </div>
        )}

        {!isLoading && !data && !error && (
          <div className="border border-dashed border-gray-300 rounded-xl bg-white px-6 py-5 text-sm text-gray-600">
            Aucune donnée Hyperliquid n&apos;a encore été récupérée. Vérifiez que votre clé API <em>et</em> votre adresse publique Hyperliquid sont bien configurées puis utilisez le bouton « Rafraîchir » pour charger vos informations de trading.
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-4">
          {summaryCards.map(card => (
            <div key={card.title} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <p className="text-xs text-gray-500 uppercase tracking-wide">{card.title}</p>
              <p className={`mt-3 text-xl font-semibold ${card.emphasis ?? 'text-black'}`}>
                {card.value}
              </p>
            </div>
          ))}
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-black">Positions perpétuelles</h2>
              <p className="text-xs text-gray-500">Vos positions à levier ouvertes et leurs métriques clés</p>
            </div>
            <span className="text-xs text-gray-500">{perpPositions.length} position(s)</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Marché', 'Sens', 'Taille', 'Prix d’entrée', 'Prix actuel', 'PNL latent'].map(header => (
                    <th
                      key={header}
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {perpPositions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-6 text-center text-sm text-gray-500">
                      Aucune position perpétuelle ouverte pour le moment.
                    </td>
                  </tr>
                ) : (
                  perpPositions.map(position => (
                    <tr key={`${position.symbol}-${position.entryPx}-${position.size}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{position.symbol}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{normalizeSide(position.side)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(position.size)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(position.entryPx, 2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(position.markPx, 2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                        {(() => {
                          const pnlValue = position.pnl ? Number(position.pnl) : NaN;
                          if (!Number.isFinite(pnlValue)) return position.pnl ?? '—';
                          const formatted = formatCurrency(pnlValue);
                          return (
                            <span className={pnlValue > 0 ? 'text-green-600' : pnlValue < 0 ? 'text-red-600' : 'text-gray-700'}>
                              {formatted}
                            </span>
                          );
                        })()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-black">Portefeuille Spot</h2>
              <p className="text-xs text-gray-500">Soldes des actifs disponibles sur votre compte Hyperliquid</p>
            </div>
            <span className="text-xs text-gray-500">{spotPositions.length} actif(s)</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Actif', 'Solde total', 'Disponible', 'Valeur USD'].map(header => (
                    <th
                      key={header}
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {spotPositions.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-6 text-center text-sm text-gray-500">
                      Aucun actif disponible.
                    </td>
                  </tr>
                ) : (
                  spotPositions.map(position => (
                    <tr key={`${position.asset}-${position.total}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{position.asset}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(position.total)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(position.available)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatCurrency(Number(position.usdValue))}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-black">Historique des derniers trades</h2>
              <p className="text-xs text-gray-500">Les 25 dernières exécutions enregistrées sur votre compte</p>
            </div>
            <span className="text-xs text-gray-500">{fills.length} trade(s)</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Date', 'Marché', 'Sens', 'Taille', 'Prix', 'Valeur', 'Hash'].map(header => (
                    <th
                      key={header}
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {fills.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-6 text-center text-sm text-gray-500">
                      Aucun trade récent trouvé.
                    </td>
                  </tr>
                ) : (
                  fills.map(fill => {
                    const value = computeFillValue(fill);
                    return (
                      <tr key={`${fill.time}-${fill.hash}`} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatTimestamp(fill.time)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{fill.symbol ?? fill.coin ?? '—'}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{normalizeSide(fill.side ?? fill.dir)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(fill.sz ?? fill.size)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(fill.px ?? fill.price, 2)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{value === null ? '—' : formatCurrency(value)}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                          {fill.hash ? `${fill.hash.slice(0, 8)}…${fill.hash.slice(-6)}` : '—'}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm mb-8">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-black">Ordres ouverts</h2>
              <p className="text-xs text-gray-500">Ordres limites ou conditionnels actuellement actifs</p>
            </div>
            <span className="text-xs text-gray-500">{openOrders.length} ordre(s)</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Marché', 'Sens', 'Taille', 'Prix', 'Type', 'Déclenchement'].map(header => (
                    <th
                      key={header}
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {openOrders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-6 text-center text-sm text-gray-500">
                      Aucun ordre en attente.
                    </td>
                  </tr>
                ) : (
                  openOrders.map((order, index) => (
                    <tr key={`${order.symbol ?? order.coin}-${order.px ?? order.price}-${index}`} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">{order.symbol ?? order.coin ?? '—'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{normalizeSide(order.side ?? order.dir)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(order.sz ?? order.size)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatNumber(order.px ?? order.price, 2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{order.isTrigger ? 'Conditionnel' : 'Limité'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{order.triggerPx ? formatNumber(order.triggerPx, 2) : '—'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {retrievedAt && (
          <p className="text-xs text-gray-500 text-right">
            Dernière mise à jour : {new Intl.DateTimeFormat('fr-FR', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            }).format(new Date(retrievedAt))}
          </p>
        )}
      </main>
    </div>
  );
}
