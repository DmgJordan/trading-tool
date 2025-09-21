'use client';

import { useState } from 'react';

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

interface PositionsViewProps {
  perpPositions: Position[];
  spotPositions: SpotPosition[];
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

export default function PositionsView({ perpPositions, spotPositions, className = '' }: PositionsViewProps) {
  const [activeTab, setActiveTab] = useState<'perp' | 'spot'>('perp');

  const tabs = [
    { id: 'perp', label: 'Perpétuelles', count: perpPositions.length },
    { id: 'spot', label: 'Spot', count: spotPositions.length },
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Onglets */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'perp' | 'spot')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 flex items-center gap-2
                ${activeTab === tab.id
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
              <span className={`
                py-0.5 px-2 rounded-full text-xs font-medium
                ${activeTab === tab.id
                  ? 'bg-black text-white'
                  : 'bg-gray-100 text-gray-600'
                }
              `}>
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'perp' && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-black">Positions perpétuelles</h3>
            <p className="text-sm text-gray-500">Vos positions à levier ouvertes</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Marché', 'Sens', 'Taille', 'Prix d' + 'entrée', 'Prix actuel', 'PNL latent', 'ROE'].map(header => (
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
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="text-4xl mb-4">📈</div>
                      <h4 className="text-lg font-semibold text-black mb-2">
                        Aucune position perpétuelle
                      </h4>
                      <p className="text-gray-500">
                        Ouvrez votre première position pour commencer le trading à levier.
                      </p>
                    </td>
                  </tr>
                ) : (
                  perpPositions.map((position, index) => {
                    const pnlValue = Number(position.pnl);
                    const entryValue = Number(position.entryPx);
                    const markValue = Number(position.markPx);
                    const roe = entryValue > 0 && Number.isFinite(markValue) && Number.isFinite(entryValue)
                      ? ((markValue - entryValue) / entryValue) * 100
                      : NaN;

                    return (
                      <tr key={`${position.symbol}-${index}`} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-black">{position.symbol}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            normalizeSide(position.side) === 'Long' || normalizeSide(position.side) === 'Achat'
                              ? 'bg-green-100 text-green-800'
                              : normalizeSide(position.side) === 'Short' || normalizeSide(position.side) === 'Vente'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {normalizeSide(position.side)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(position.size)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(position.entryPx, 2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(position.markPx, 2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <span className={
                            Number.isFinite(pnlValue) && pnlValue > 0 ? 'text-green-600' :
                            Number.isFinite(pnlValue) && pnlValue < 0 ? 'text-red-600' : 'text-gray-900'
                          }>
                            {formatCurrency(position.pnl)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          {Number.isFinite(roe) ? (
                            <span className={
                              roe > 0 ? 'text-green-600' :
                              roe < 0 ? 'text-red-600' : 'text-gray-900'
                            }>
                              {roe > 0 ? '+' : ''}{roe.toFixed(2)}%
                            </span>
                          ) : '—'}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'spot' && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-black">Actifs spot</h3>
            <p className="text-sm text-gray-500">Vos soldes d'actifs disponibles</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Actif', 'Solde total', 'Disponible', 'Valeur USD', 'Allocation'].map(header => (
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
                    <td colSpan={5} className="px-6 py-12 text-center">
                      <div className="text-4xl mb-4">💰</div>
                      <h4 className="text-lg font-semibold text-black mb-2">
                        Aucun actif spot
                      </h4>
                      <p className="text-gray-500">
                        Déposez des fonds pour commencer le trading spot.
                      </p>
                    </td>
                  </tr>
                ) : (
                  (() => {
                    const totalUsdValue = spotPositions.reduce((sum, pos) => sum + Number(pos.usdValue || 0), 0);

                    return spotPositions.map((position, index) => {
                      const usdValue = Number(position.usdValue || 0);
                      const allocation = totalUsdValue > 0 ? (usdValue / totalUsdValue) * 100 : 0;

                      return (
                        <tr key={`${position.asset}-${index}`} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="font-medium text-black">{position.asset}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatNumber(position.total)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatNumber(position.available)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {formatCurrency(position.usdValue)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {allocation > 0.01 ? `${allocation.toFixed(2)}%` : '<0.01%'}
                          </td>
                        </tr>
                      );
                    });
                  })()
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}