'use client';

interface PositionCardProps {
  symbol: string;
  side?: string;
  size?: string | number;
  entryPrice?: string | number;
  markPrice?: string | number;
  pnl?: string | number;
  pnlPercentage?: number;
  className?: string;
}

const formatNumber = (value?: string | number | null, digits = 4) => {
  if (value === undefined || value === null) return '—';
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric)) return String(value);
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  }).format(numeric);
};

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

const normalizeSide = (side?: string) => {
  if (!side) return '—';
  const normalized = side.toLowerCase();
  if (normalized.startsWith('b')) return 'Achat';
  if (normalized.startsWith('s') || normalized.startsWith('a')) return 'Vente';
  if (normalized.startsWith('l')) return 'Long';
  if (normalized.startsWith('r') || normalized.startsWith('sh')) return 'Short';
  return side;
};

export default function PositionCard({
  symbol,
  side,
  size,
  entryPrice,
  markPrice,
  pnl,
  pnlPercentage,
  className = '',
}: PositionCardProps) {
  const pnlValue = typeof pnl === 'number' ? pnl : Number(pnl);
  const isPositivePnl = Number.isFinite(pnlValue) && pnlValue > 0;
  const isNegativePnl = Number.isFinite(pnlValue) && pnlValue < 0;

  const sideColor = () => {
    const normalizedSide = normalizeSide(side);
    if (normalizedSide === 'Long' || normalizedSide === 'Achat')
      return 'text-green-600 bg-green-50';
    if (normalizedSide === 'Short' || normalizedSide === 'Vente')
      return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  return (
    <div
      className={`bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow ${className}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-black">{symbol}</h3>
          <span
            className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${sideColor()}`}
          >
            {normalizeSide(side)}
          </span>
        </div>
        <div className="text-right">
          <div
            className={`text-lg font-semibold ${
              isPositivePnl
                ? 'text-green-600'
                : isNegativePnl
                  ? 'text-red-600'
                  : 'text-gray-900'
            }`}
          >
            {formatCurrency(pnl)}
          </div>
          {pnlPercentage !== undefined && Number.isFinite(pnlPercentage) && (
            <div
              className={`text-sm ${
                pnlPercentage > 0
                  ? 'text-green-600'
                  : pnlPercentage < 0
                    ? 'text-red-600'
                    : 'text-gray-500'
              }`}
            >
              {pnlPercentage > 0 ? '+' : ''}
              {pnlPercentage.toFixed(2)}%
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-500 mb-1">Taille</p>
          <p className="font-medium text-gray-900">{formatNumber(size)}</p>
        </div>
        <div>
          <p className="text-gray-500 mb-1">Prix d&apos;entrée</p>
          <p className="font-medium text-gray-900">
            {formatNumber(entryPrice, 2)}
          </p>
        </div>
        <div>
          <p className="text-gray-500 mb-1">Prix actuel</p>
          <p className="font-medium text-gray-900">
            {formatNumber(markPrice, 2)}
          </p>
        </div>
        <div>
          <p className="text-gray-500 mb-1">Variation</p>
          <div className="flex items-center gap-1">
            {entryPrice &&
            markPrice &&
            Number.isFinite(Number(entryPrice)) &&
            Number.isFinite(Number(markPrice)) ? (
              (() => {
                const change =
                  ((Number(markPrice) - Number(entryPrice)) /
                    Number(entryPrice)) *
                  100;
                return (
                  <span
                    className={`font-medium ${
                      change > 0
                        ? 'text-green-600'
                        : change < 0
                          ? 'text-red-600'
                          : 'text-gray-900'
                    }`}
                  >
                    {change > 0 ? '+' : ''}
                    {change.toFixed(2)}%
                  </span>
                );
              })()
            ) : (
              <span className="font-medium text-gray-900">—</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
