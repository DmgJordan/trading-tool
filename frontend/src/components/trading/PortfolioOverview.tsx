'use client';

import PositionCard from './PositionCard';
import QuickActions from './QuickActions';
import PnlChart from './PnlChart';

interface Position {
  symbol: string;
  side?: string;
  size?: string | number;
  entryPx?: string | number;
  markPx?: string | number;
  pnl?: string | number;
}

interface SpotPosition {
  asset: string;
  total?: string;
  available?: string;
  usdValue?: string;
}

interface PortfolioOverviewProps {
  perpPositions: Position[];
  spotPositions: SpotPosition[];
  portfolioSummary?: {
    accountValue?: number | null;
    totalUnrealizedPnl?: number | null;
    totalMarginUsed?: number | null;
    withdrawableBalance?: number | null;
  } | null;
  onAction?: (actionId: string) => void;
  className?: string;
}

const formatCurrency = (value?: string | number | null) => {
  if (value === undefined || value === null) return '—';
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric)) return '—';
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(numeric);
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

export default function PortfolioOverview({
  perpPositions,
  spotPositions,
  portfolioSummary,
  onAction,
  className = '',
}: PortfolioOverviewProps) {
  const quickActions = [
    {
      id: 'deposit',
      label: 'Déposer',
      icon: '💰',
      variant: 'success' as const,
      onClick: () => onAction?.('deposit'),
    },
    {
      id: 'withdraw',
      label: 'Retirer',
      icon: '💸',
      variant: 'secondary' as const,
      onClick: () => onAction?.('withdraw'),
    },
    {
      id: 'transfer',
      label: 'Transférer',
      icon: '🔄',
      variant: 'secondary' as const,
      onClick: () => onAction?.('transfer'),
    },
    {
      id: 'settings',
      label: 'Paramètres',
      icon: '⚙️',
      variant: 'secondary' as const,
      onClick: () => onAction?.('settings'),
    },
  ];

  // Calculer le PNL total avec pourcentage
  const totalPnl = portfolioSummary?.totalUnrealizedPnl ?? 0;
  const accountValue = portfolioSummary?.accountValue ?? 0;
  const pnlPercentage = accountValue > 0 ? (totalPnl / accountValue) * 100 : 0;

  // Top positions perpétuelles (limitées à 4)
  const topPerpPositions = perpPositions.slice(0, 4);

  // Top actifs spot avec valeur USD significative
  const significantSpotPositions = spotPositions
    .filter(pos => Number(pos.usdValue) > 1)
    .sort((a, b) => Number(b.usdValue) - Number(a.usdValue))
    .slice(0, 4);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Résumé du compte avec mini-graphique */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-black mb-2">
              Résumé du portefeuille
            </h2>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-black">
                {formatCurrency(portfolioSummary?.accountValue)}
              </div>
              <div
                className={`flex items-center gap-2 text-sm ${
                  totalPnl > 0
                    ? 'text-green-600'
                    : totalPnl < 0
                      ? 'text-red-600'
                      : 'text-gray-500'
                }`}
              >
                <span className="font-medium">
                  {totalPnl > 0 ? '+' : ''}
                  {formatCurrency(totalPnl)}
                </span>
                {pnlPercentage !== 0 && (
                  <span>
                    ({totalPnl > 0 ? '+' : ''}
                    {pnlPercentage.toFixed(2)}%)
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500 mb-2">Performance PNL</p>
            <PnlChart width={120} height={40} />
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">
              Marge utilisée
            </p>
            <p className="text-lg font-semibold text-black mt-1">
              {formatCurrency(portfolioSummary?.totalMarginUsed)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">
              Solde retirable
            </p>
            <p className="text-lg font-semibold text-black mt-1">
              {formatCurrency(portfolioSummary?.withdrawableBalance)}
            </p>
          </div>
          <div className="col-span-2 md:col-span-1">
            <p className="text-xs text-gray-500 uppercase tracking-wide">
              Positions
            </p>
            <p className="text-lg font-semibold text-black mt-1">
              {perpPositions.length} Perp • {spotPositions.length} Spot
            </p>
          </div>
        </div>

        <QuickActions actions={quickActions} />
      </div>

      {/* Positions perpétuelles principales */}
      {topPerpPositions.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-black">
              Positions perpétuelles principales
            </h3>
            <span className="text-sm text-gray-500">
              {perpPositions.length} position(s) au total
            </span>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {topPerpPositions.map((position, index) => {
              const entryValue = Number(position.entryPx);
              const markValue = Number(position.markPx);
              const pnlPercentage =
                entryValue > 0 &&
                Number.isFinite(markValue) &&
                Number.isFinite(entryValue)
                  ? ((markValue - entryValue) / entryValue) * 100
                  : undefined;

              return (
                <PositionCard
                  key={`${position.symbol}-${index}`}
                  symbol={position.symbol}
                  side={position.side}
                  size={position.size}
                  entryPrice={position.entryPx}
                  markPrice={position.markPx}
                  pnl={position.pnl}
                  pnlPercentage={pnlPercentage}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* Actifs spot principaux */}
      {significantSpotPositions.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-black">
              Actifs spot principaux
            </h3>
            <span className="text-sm text-gray-500">
              {spotPositions.length} actif(s) au total
            </span>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {significantSpotPositions.map((position, index) => (
              <div
                key={`${position.asset}-${index}`}
                className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm"
              >
                <h4 className="font-semibold text-black mb-2">
                  {position.asset}
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Total</span>
                    <span className="font-medium">
                      {formatNumber(position.total)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Disponible</span>
                    <span className="font-medium">
                      {formatNumber(position.available)}
                    </span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="text-gray-500">Valeur USD</span>
                    <span className="font-semibold text-black">
                      {formatCurrency(position.usdValue)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Message si aucune position */}
      {perpPositions.length === 0 && spotPositions.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-lg font-semibold text-black mb-2">
            Aucune position ouverte
          </h3>
          <p className="text-gray-500 mb-6">
            Commencez par déposer des fonds et ouvrir votre première position.
          </p>
          <QuickActions
            actions={quickActions.slice(0, 2)}
            className="justify-center"
          />
        </div>
      )}
    </div>
  );
}
