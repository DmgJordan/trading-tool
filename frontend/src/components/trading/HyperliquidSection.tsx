'use client';

import { useEffect, useMemo, useState } from 'react';
import type { ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useHyperliquidStore } from '../../store/hyperliquidStore';
import {
  HyperliquidFill,
  HyperliquidPerpPosition,
  HyperliquidSpotUserState,
} from '../../lib/types/hyperliquid';

// Composants trading réutilisés
import TradingTabs from '../trading/TradingTabs';
import MetricsHeader from '../trading/MetricsHeader';
import PortfolioOverview from '../trading/PortfolioOverview';
import PositionsView from '../trading/PositionsView';
import OrdersView from '../trading/OrdersView';

const derivePerpPositions = (
  positions: HyperliquidPerpPosition[] | null | undefined
) => {
  if (!Array.isArray(positions)) return [];

  return positions.map(position => {
    const nested =
      position?.position && typeof position.position === 'object'
        ? position.position
        : undefined;

    const base = nested && typeof nested === 'object' ? nested : position;

    const size =
      (base?.szi as string | undefined) ||
      (base?.sz as string | undefined) ||
      (base?.size as string | undefined) ||
      position.sz ||
      position.size;

    const entryPx =
      (base?.entryPx as string | undefined) ||
      (base?.entry_px as string | undefined) ||
      position.entryPx ||
      position.entry_px;

    const markPx =
      (base?.markPx as string | undefined) ||
      (base?.mark_px as string | undefined) ||
      (base?.oraclePx as string | undefined) ||
      (base?.oracle_px as string | undefined) ||
      position.markPx ||
      position.mark_px;

    const pnl =
      (base?.unrealizedPnl as string | undefined) ||
      (base?.unrealized_pnl as string | undefined) ||
      position.unrealizedPnl ||
      position.unrealized_pnl;

    const side = String(
      (base?.side as string | undefined) ||
        position.side ||
        (position as { dir?: string }).dir ||
        ''
    );

    const symbol =
      (position.symbol ||
        position.coin ||
        position.asset ||
        (base?.coin as string)) ??
      '—';

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

const deriveSpotPositions = (
  spotState: HyperliquidSpotUserState | null | undefined
) => {
  if (!spotState) return [];

  const positionsArray = Array.isArray(spotState.assetPositions)
    ? spotState.assetPositions
    : Array.isArray(spotState.positions)
      ? spotState.positions
      : null;

  if (positionsArray) {
    return positionsArray.map(position => ({
      asset:
        (position as { coin?: string; asset?: string; symbol?: string }).coin ||
        (position as { asset?: string }).asset ||
        (position as { symbol?: string }).symbol ||
        '—',
      total:
        (position as { total?: string; balance?: string }).total ||
        (position as { balance?: string }).balance,
      available: (position as { available?: string }).available,
      usdValue:
        (position as { usdValue?: string; usd_value?: string }).usdValue ||
        (position as { usd_value?: string }).usd_value,
    }));
  }

  const balances = spotState.balances || spotState.tokenBalances;
  if (balances && typeof balances === 'object') {
    return Object.entries(balances)
      .map(([asset, value]) => ({
        asset,
        total:
          typeof value === 'string' || typeof value === 'number'
            ? String(value)
            : undefined,
      }))
      .filter(entry => entry.total !== undefined);
  }

  return [];
};

const computeFillValue = (fill: HyperliquidFill) => {
  const size = fill.sz ?? fill.size;
  const price = fill.px ?? fill.price;
  if (!size || !price) return null;

  const numericSize = Number(size);
  const numericPrice = Number(price);
  if (!Number.isFinite(numericSize) || !Number.isFinite(numericPrice))
    return null;
  return numericSize * numericPrice;
};

interface HyperliquidSectionProps {
  className?: string;
}

export default function HyperliquidSection({
  className = '',
}: HyperliquidSectionProps) {
  const router = useRouter();
  const data = useHyperliquidStore(state => state.data);
  const isLoading = useHyperliquidStore(state => state.isLoading);
  const error = useHyperliquidStore(state => state.error);
  const lastUpdated = useHyperliquidStore(state => state.lastUpdated);
  const useTestnet = useHyperliquidStore(state => state.useTestnet);
  const fetchUserInfo = useHyperliquidStore(state => state.fetchUserInfo);
  const setUseTestnet = useHyperliquidStore(state => state.setUseTestnet);
  const clearError = useHyperliquidStore(state => state.clearError);

  // État pour la navigation par onglets Hyperliquid
  const [activeHyperTab, setActiveHyperTab] = useState('portfolio');

  // Calcul des données dérivées
  const perpPositions = useMemo(
    () =>
      derivePerpPositions(
        data?.user_state?.perpPositions ?? data?.user_state?.assetPositions
      ),
    [data?.user_state?.perpPositions, data?.user_state?.assetPositions]
  );

  const spotPositions = useMemo(
    () => deriveSpotPositions(data?.spot_user_state),
    [data?.spot_user_state]
  );

  const fills = useMemo(
    () => (Array.isArray(data?.fills) ? data?.fills.slice(0, 25) : []),
    [data?.fills]
  );
  const openOrders = useMemo(
    () => (Array.isArray(data?.open_orders) ? data?.open_orders : []),
    [data?.open_orders]
  );

  // Configuration des onglets Hyperliquid
  const hyperTabs = useMemo(
    () => [
      {
        id: 'portfolio',
        label: 'Portfolio',
        icon: '📊',
        count: undefined,
      },
      {
        id: 'positions',
        label: 'Positions',
        icon: '📈',
        count: perpPositions.length + spotPositions.length || undefined,
      },
      {
        id: 'orders',
        label: 'Ordres',
        icon: '📋',
        count: openOrders.length + fills.length || undefined,
      },
    ],
    [
      perpPositions.length,
      spotPositions.length,
      openOrders.length,
      fills.length,
    ]
  );

  // Calcul du volume 14 jours (simulation)
  const volume14d = useMemo(() => {
    if (!fills.length) return null;
    const recent = fills.slice(0, 10);
    return (
      recent.reduce((sum, fill) => {
        const value = computeFillValue(fill);
        return sum + (value || 0);
      }, 0) * 14
    );
  }, [fills]);

  // Frais moyens (simulation)
  const fees = useMemo(
    () => ({
      taker: 0.0005, // 0.05%
      maker: 0.0002, // 0.02%
    }),
    []
  );

  // Chargement initial des données Hyperliquid
  useEffect(() => {
    fetchUserInfo().catch(error => {
      console.error('Échec de la récupération des données Hyperliquid:', error);
    });
  }, [fetchUserInfo]);

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

  const handleQuickAction = (actionId: string) => {
    switch (actionId) {
      case 'deposit':
        console.log('Déposer des fonds');
        break;
      case 'withdraw':
        console.log('Retirer des fonds');
        break;
      case 'transfer':
        console.log('Transférer des fonds');
        break;
      case 'settings':
        router.push('/account');
        break;
      default:
        console.log('Action non reconnue:', actionId);
    }
  };

  const networkLabel = useTestnet ? 'Testnet' : 'Mainnet';
  const retrievedAt = data?.retrieved_at || lastUpdated;

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header de section avec contrôles */}
      <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-black">Portfolio Trading</h2>
          <p className="text-gray-600 mt-2">
            Suivi de vos positions et ordres Hyperliquid en temps réel
          </p>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
            <p className="text-xs text-gray-500 uppercase tracking-wide">
              Réseau
            </p>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm font-semibold text-black">
                {networkLabel}
              </span>
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
              isLoading
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-black text-white hover:bg-white hover:text-black'
            }`}
          >
            {isLoading ? 'Rafraîchissement…' : 'Rafraîchir'}
          </button>
        </div>
      </div>

      {/* Gestion des erreurs */}
      {error && (
        <div className="border-l-4 border-red-500 bg-red-50 px-4 py-3 rounded-md text-sm text-red-700 flex flex-col gap-2">
          <div className="font-semibold">
            Erreur lors de la récupération des données Hyperliquid
          </div>
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
              onClick={() => router.push('/account')}
              className="text-sm font-semibold text-red-700 hover:text-red-900"
            >
              Configurer les clés API
            </button>
          </div>
        </div>
      )}

      {/* Message si aucune donnée */}
      {!isLoading && !data && !error && (
        <div className="border border-dashed border-gray-300 rounded-xl bg-white px-6 py-5 text-sm text-gray-600">
          Aucune donnée Hyperliquid n&apos;a encore été récupérée. Vérifiez que
          votre clé API <em>et</em> votre adresse publique Hyperliquid sont bien
          configurées puis utilisez le bouton « Rafraîchir » pour charger vos
          informations de trading.
        </div>
      )}

      {/* Header avec métriques principales */}
      {data && (
        <MetricsHeader
          portfolioSummary={data.portfolio_summary}
          volume14d={volume14d}
          fees={fees}
        />
      )}

      {/* Navigation par onglets et contenu */}
      {data && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm">
          <TradingTabs
            tabs={hyperTabs}
            activeTab={activeHyperTab}
            onTabChange={setActiveHyperTab}
            className="px-6"
          />

          {/* Contenu des onglets */}
          <div className="px-6 py-6">
            {activeHyperTab === 'portfolio' && (
              <PortfolioOverview
                perpPositions={perpPositions}
                spotPositions={spotPositions}
                portfolioSummary={data.portfolio_summary}
                onAction={handleQuickAction}
              />
            )}

            {activeHyperTab === 'positions' && (
              <PositionsView
                perpPositions={perpPositions}
                spotPositions={spotPositions}
              />
            )}

            {activeHyperTab === 'orders' && (
              <OrdersView openOrders={openOrders} fills={fills} />
            )}
          </div>
        </div>
      )}

      {/* Footer avec dernière mise à jour */}
      {retrievedAt && (
        <p className="text-xs text-gray-500 text-right">
          Dernière mise à jour Hyperliquid :{' '}
          {new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          }).format(new Date(retrievedAt))}
        </p>
      )}
    </div>
  );
}
