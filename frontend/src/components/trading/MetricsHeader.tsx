'use client';

import { useMemo } from 'react';

interface MetricsHeaderProps {
  portfolioSummary?: {
    accountValue?: number | null;
    totalUnrealizedPnl?: number | null;
    totalMarginUsed?: number | null;
    withdrawableBalance?: number | null;
  } | null;
  volume14d?: number | null;
  fees?: {
    taker?: number;
    maker?: number;
  };
  className?: string;
}

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

const formatPercentage = (value?: number) => {
  if (value === undefined || Number.isNaN(value)) return '—';
  return `${(value * 100).toFixed(4)}%`;
};

export default function MetricsHeader({ portfolioSummary, volume14d, fees, className = '' }: MetricsHeaderProps) {
  const pnlData = useMemo(() => {
    const pnl = portfolioSummary?.totalUnrealizedPnl ?? 0;
    const accountValue = portfolioSummary?.accountValue ?? 0;
    const percentage = accountValue > 0 ? (pnl / accountValue) * 100 : 0;

    return {
      value: pnl,
      percentage,
      isPositive: pnl > 0,
      isNegative: pnl < 0,
    };
  }, [portfolioSummary]);

  const metrics = [
    {
      label: 'Volume 14J',
      value: formatCurrency(volume14d),
      className: 'text-gray-900',
    },
    {
      label: 'Valeur du compte',
      value: formatCurrency(portfolioSummary?.accountValue),
      className: 'text-gray-900 font-semibold',
    },
    {
      label: 'PNL',
      value: (
        <div className="flex flex-col items-end">
          <span className={`font-semibold ${
            pnlData.isPositive ? 'text-green-600' :
            pnlData.isNegative ? 'text-red-600' : 'text-gray-900'
          }`}>
            {formatCurrency(pnlData.value)}
          </span>
          {pnlData.percentage !== 0 && (
            <span className={`text-xs ${
              pnlData.isPositive ? 'text-green-600' :
              pnlData.isNegative ? 'text-red-600' : 'text-gray-500'
            }`}>
              {pnlData.isPositive ? '+' : ''}{pnlData.percentage.toFixed(2)}%
            </span>
          )}
        </div>
      ),
      className: '',
    },
    {
      label: 'Frais (Taker / Maker)',
      value: `${formatPercentage(fees?.taker)} / ${formatPercentage(fees?.maker)}`,
      className: 'text-gray-600 text-sm',
    },
  ];

  return (
    <div className={`bg-white border border-gray-200 rounded-xl p-6 shadow-sm ${className}`}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="text-center md:text-left">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">
              {metric.label}
            </p>
            <div className={`text-lg ${metric.className}`}>
              {metric.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}