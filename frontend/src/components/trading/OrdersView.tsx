'use client';

import { useState } from 'react';

interface Order {
  symbol?: string;
  coin?: string;
  side?: string;
  dir?: string;
  sz?: string | number;
  size?: string | number;
  px?: string | number;
  price?: string | number;
  isTrigger?: boolean;
  triggerPx?: string | number;
  timestamp?: number;
  hash?: string;
}

interface Fill {
  symbol?: string;
  coin?: string;
  side?: string;
  dir?: string;
  sz?: string | number;
  size?: string | number;
  px?: string | number;
  price?: string | number;
  time?: number;
  hash?: string;
}

interface OrdersViewProps {
  openOrders: Order[];
  fills: Fill[];
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

const formatTimestamp = (value?: number) => {
  if (!value) return '—';
  const isSeconds = value < 1e12;
  const date = new Date(isSeconds ? value * 1000 : value);
  return new Intl.DateTimeFormat('fr-FR', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
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

export default function OrdersView({
  openOrders,
  fills,
  className = '',
}: OrdersViewProps) {
  const [activeTab, setActiveTab] = useState<'open' | 'history'>('open');

  const tabs = [
    { id: 'open', label: 'Ordres ouverts', count: openOrders.length },
    { id: 'history', label: 'Historique', count: fills.length },
  ];

  const computeFillValue = (fill: Fill) => {
    const size = fill.sz ?? fill.size;
    const price = fill.px ?? fill.price;
    if (!size || !price) return null;

    const numericSize = Number(size);
    const numericPrice = Number(price);
    if (!Number.isFinite(numericSize) || !Number.isFinite(numericPrice))
      return null;
    return numericSize * numericPrice;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Onglets */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8" aria-label="Tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'open' | 'history')}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 flex items-center gap-2
                ${
                  activeTab === tab.id
                    ? 'border-black text-black'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
              <span
                className={`
                py-0.5 px-2 rounded-full text-xs font-medium
                ${
                  activeTab === tab.id
                    ? 'bg-black text-white'
                    : 'bg-gray-100 text-gray-600'
                }
              `}
              >
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Ordres ouverts */}
      {activeTab === 'open' && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-black">Ordres ouverts</h3>
            <p className="text-sm text-gray-500">
              Ordres limites et conditionnels actifs
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {[
                    'Marché',
                    'Sens',
                    'Taille',
                    'Prix',
                    'Type',
                    'Déclenchement',
                    'Actions',
                  ].map(header => (
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
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="text-4xl mb-4">📋</div>
                      <h4 className="text-lg font-semibold text-black mb-2">
                        Aucun ordre ouvert
                      </h4>
                      <p className="text-gray-500">
                        Vos ordres limites et conditionnels apparaîtront ici.
                      </p>
                    </td>
                  </tr>
                ) : (
                  openOrders.map((order, index) => (
                    <tr
                      key={`${order.symbol ?? order.coin}-${order.px ?? order.price}-${index}`}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-black">
                          {order.symbol ?? order.coin ?? '—'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            normalizeSide(order.side ?? order.dir) === 'Long' ||
                            normalizeSide(order.side ?? order.dir) === 'Achat'
                              ? 'bg-green-100 text-green-800'
                              : normalizeSide(order.side ?? order.dir) ===
                                    'Short' ||
                                  normalizeSide(order.side ?? order.dir) ===
                                    'Vente'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {normalizeSide(order.side ?? order.dir)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(order.sz ?? order.size)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(order.px ?? order.price, 2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            order.isTrigger
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {order.isTrigger ? 'Conditionnel' : 'Limité'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {order.triggerPx
                          ? formatNumber(order.triggerPx, 2)
                          : '—'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button className="text-red-600 hover:text-red-900 text-sm font-medium">
                          Annuler
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Historique des trades */}
      {activeTab === 'history' && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-black">
                Historique des trades
              </h3>
              <p className="text-sm text-gray-500">Vos dernières exécutions</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="text-sm text-gray-500 hover:text-gray-700">
                Filtrer
              </button>
              <button className="text-sm text-gray-500 hover:text-gray-700">
                Exporter
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {[
                    'Date',
                    'Marché',
                    'Sens',
                    'Taille',
                    'Prix',
                    'Valeur',
                    'Hash',
                  ].map(header => (
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
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="text-4xl mb-4">📊</div>
                      <h4 className="text-lg font-semibold text-black mb-2">
                        Aucun trade récent
                      </h4>
                      <p className="text-gray-500">
                        Votre historique de trading apparaîtra ici.
                      </p>
                    </td>
                  </tr>
                ) : (
                  fills.map((fill, index) => {
                    const value = computeFillValue(fill);
                    return (
                      <tr
                        key={`${fill.time}-${fill.hash}-${index}`}
                        className="hover:bg-gray-50"
                      >
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatTimestamp(fill.time)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-black">
                            {fill.symbol ?? fill.coin ?? '—'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              normalizeSide(fill.side ?? fill.dir) === 'Long' ||
                              normalizeSide(fill.side ?? fill.dir) === 'Achat'
                                ? 'bg-green-100 text-green-800'
                                : normalizeSide(fill.side ?? fill.dir) ===
                                      'Short' ||
                                    normalizeSide(fill.side ?? fill.dir) ===
                                      'Vente'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {normalizeSide(fill.side ?? fill.dir)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(fill.sz ?? fill.size)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(fill.px ?? fill.price, 2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {value === null ? '—' : formatCurrency(value)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500 font-mono">
                          {fill.hash ? (
                            <span title={fill.hash}>
                              {fill.hash.slice(0, 8)}…{fill.hash.slice(-6)}
                            </span>
                          ) : (
                            '—'
                          )}
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
    </div>
  );
}
