'use client';

import { useState, useEffect } from 'react';
import { ohlcvApi, CCXTTestResponse, ExchangeListResponse, OHLCVCandle, CurrentPriceInfo } from '../lib/api';

interface CCXTTestState {
  status: 'idle' | 'testing' | 'success' | 'error';
  message: string;
  data: OHLCVCandle[] | null;
  currentPriceInfo: CurrentPriceInfo | null;
  exchange: string;
  symbol: string;
  timeframe: string;
}

export default function CCXTTest() {
  const [testState, setTestState] = useState<CCXTTestState>({
    status: 'idle',
    message: '',
    data: null,
    currentPriceInfo: null,
    exchange: '',
    symbol: '',
    timeframe: ''
  });

  const [availableData, setAvailableData] = useState<ExchangeListResponse | null>(null);
  const [selectedExchange, setSelectedExchange] = useState('binance');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h');
  const [limit, setLimit] = useState(50);

  // Charger les exchanges et timeframes disponibles au montage
  useEffect(() => {
    loadAvailableData();
  }, []);

  const loadAvailableData = async () => {
    try {
      const data = await ohlcvApi.getAvailableExchanges();
      setAvailableData(data);
    } catch (error) {
      console.error('Erreur chargement des exchanges:', error);
    }
  };

  const testCCXTConnection = async () => {
    setTestState({
      status: 'testing',
      message: `Test CCXT en cours pour ${selectedExchange} ${selectedSymbol} ${selectedTimeframe}...`,
      data: null,
      currentPriceInfo: null,
      exchange: selectedExchange,
      symbol: selectedSymbol,
      timeframe: selectedTimeframe
    });

    try {
      const result = await ohlcvApi.testCCXT({
        exchange: selectedExchange,
        symbol: selectedSymbol,
        timeframe: selectedTimeframe,
        limit: limit
      });

      if (result.status === 'success') {
        setTestState({
          status: 'success',
          message: `${result.message} - ${result.count} bougies récupérées`,
          data: result.data || null,
          currentPriceInfo: result.current_price_info || null,
          exchange: result.exchange || selectedExchange,
          symbol: result.symbol || selectedSymbol,
          timeframe: result.timeframe || selectedTimeframe
        });
      } else {
        setTestState({
          status: 'error',
          message: result.message,
          data: null,
          currentPriceInfo: null,
          exchange: selectedExchange,
          symbol: selectedSymbol,
          timeframe: selectedTimeframe
        });
      }
    } catch (error) {
      setTestState({
        status: 'error',
        message: `Erreur: ${error instanceof Error ? error.message : 'Connexion échouée'}`,
        data: null,
        currentPriceInfo: null,
        exchange: selectedExchange,
        symbol: selectedSymbol,
        timeframe: selectedTimeframe
      });
    }
  };

  const getStatusIcon = (status: 'idle' | 'testing' | 'success' | 'error') => {
    switch (status) {
      case 'success':
        return <span className="text-black text-xl font-bold">✓</span>;
      case 'error':
        return <span className="text-black text-xl font-bold">✗</span>;
      case 'testing':
        return <span className="text-black text-xl animate-spin">⟳</span>;
      default:
        return <span className="text-gray-400 text-xl">○</span>;
    }
  };

  const getStatusColor = (status: 'idle' | 'testing' | 'success' | 'error') => {
    switch (status) {
      case 'success':
        return 'border-black bg-gray-100';
      case 'error':
        return 'border-black bg-gray-200';
      case 'testing':
        return 'border-black bg-gray-50';
      default:
        return 'border-gray-300 bg-white';
    }
  };

  const formatOHLCVData = (data: OHLCVCandle[]) => {
    if (!data || data.length === 0) return 'Aucune donnée';

    return data.slice(0, 10).map((candle, index) => (
      <div key={index} className="bg-gray-50 p-3 rounded border text-sm">
        <div className="grid grid-cols-2 gap-2">
          <div><strong>Date:</strong> {new Date(candle.timestamp).toLocaleString('fr-FR')}</div>
          <div><strong>O:</strong> {candle.open.toFixed(4)}</div>
          <div><strong>H:</strong> {candle.high.toFixed(4)}</div>
          <div><strong>L:</strong> {candle.low.toFixed(4)}</div>
          <div><strong>C:</strong> {candle.close.toFixed(4)}</div>
          <div><strong>V:</strong> {candle.volume.toFixed(2)}</div>
        </div>
      </div>
    ));
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-black p-8 sm:p-10">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold text-black mb-3">
          Test CCXT - Données OHLCV
        </h2>
        <p className="text-gray-600">
          Récupérez des données de bougies depuis les exchanges via CCXT
        </p>
      </div>

      {/* Configuration des paramètres */}
      <div className="mb-8 p-6 bg-gray-50 rounded-xl border border-gray-300">
        <h3 className="text-xl font-semibold text-black mb-4">Paramètres de test</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Exchange */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">Exchange</label>
            <select
              value={selectedExchange}
              onChange={(e) => setSelectedExchange(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              {availableData?.exchanges.map((exchange) => (
                <option key={exchange} value={exchange}>
                  {exchange.charAt(0).toUpperCase() + exchange.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Symbole */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">Symbole</label>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="ETH/USDT">ETH/USDT</option>
              <option value="ADA/USDT">ADA/USDT</option>
              <option value="SOL/USDT">SOL/USDT</option>
              <option value="MATIC/USDT">MATIC/USDT</option>
              <option value="LINK/USDT">LINK/USDT</option>
              <option value="AVAX/USDT">AVAX/USDT</option>
              <option value="DOT/USDT">DOT/USDT</option>
            </select>
          </div>

          {/* Timeframe */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">Timeframe</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              {availableData?.timeframes.map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
          </div>

          {/* Limite */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">Nombre de bougies</label>
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </div>
        </div>
      </div>

      {/* Section de test */}
      <div className={`p-6 rounded-xl border-2 transition-all duration-300 ${getStatusColor(testState.status)}`}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              {getStatusIcon(testState.status)}
            </div>
            <div>
              <h3 className="font-semibold text-black text-lg">Test de Connexion CCXT</h3>
              <p className="text-gray-700 mt-1">
                {selectedExchange.charAt(0).toUpperCase() + selectedExchange.slice(1)} - {selectedSymbol} - {selectedTimeframe}
              </p>
            </div>
          </div>
          <button
            onClick={testCCXTConnection}
            disabled={testState.status === 'testing'}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-sm hover:shadow-md"
          >
            {testState.status === 'testing' ? 'Test...' : 'Tester CCXT'}
          </button>
        </div>
      </div>

      {/* Message de statut */}
      {testState.message && (
        <div className="mt-8 p-5 bg-gray-100 rounded-xl border-2 border-gray-300">
          <p className="text-black text-center font-medium">{testState.message}</p>
        </div>
      )}

      {/* Affichage du prix actuel */}
      {testState.currentPriceInfo && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-black mb-4">💰 Prix Actuel - {testState.symbol}</h3>
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border-2 border-gray-300 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-black">
                  ${testState.currentPriceInfo.current_price.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                </div>
                <div className="text-sm text-gray-600 mt-1">Prix Actuel</div>
              </div>

              {testState.currentPriceInfo.change_24h_percent !== undefined && (
                <div className="text-center">
                  <div className={`text-2xl font-bold ${testState.currentPriceInfo.change_24h_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {testState.currentPriceInfo.change_24h_percent >= 0 ? '+' : ''}{testState.currentPriceInfo.change_24h_percent.toFixed(2)}%
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Variation 24h</div>
                </div>
              )}

              {testState.currentPriceInfo.bid && testState.currentPriceInfo.ask && (
                <div className="text-center">
                  <div className="text-lg font-semibold text-blue-600">
                    ${testState.currentPriceInfo.bid.toFixed(2)} / ${testState.currentPriceInfo.ask.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Bid / Ask</div>
                </div>
              )}

              {testState.currentPriceInfo.volume_24h && (
                <div className="text-center">
                  <div className="text-lg font-semibold text-purple-600">
                    {testState.currentPriceInfo.volume_24h.toLocaleString('fr-FR', { maximumFractionDigits: 0 })}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Volume 24h</div>
                </div>
              )}
            </div>

            {testState.currentPriceInfo.datetime && (
              <div className="mt-4 text-center text-sm text-gray-600">
                Dernière mise à jour : {new Date(testState.currentPriceInfo.datetime).toLocaleString('fr-FR')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Affichage des données OHLCV */}
      {testState.data && testState.data.length > 0 && (
        <div className="mt-8">
          <div className="mb-4 flex justify-between items-center">
            <h3 className="text-xl font-semibold text-black">
              Données OHLCV ({testState.data.length} bougies)
            </h3>
            <span className="text-sm text-gray-600">
              {testState.exchange} - {testState.symbol} - {testState.timeframe}
            </span>
          </div>

          <div className="bg-gray-50 rounded-xl border-2 border-gray-300 p-4 max-h-96 overflow-y-auto">
            <div className="space-y-3">
              {formatOHLCVData(testState.data)}
            </div>

            {testState.data.length > 10 && (
              <div className="mt-4 text-center text-sm text-gray-600">
                ... et {testState.data.length - 10} autres bougies (seules les 10 premières sont affichées)
              </div>
            )}
          </div>

          {/* Données brutes en JSON */}
          <details className="mt-4">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-black">
              Voir les données brutes (JSON)
            </summary>
            <div className="mt-2 p-4 bg-gray-900 text-green-400 rounded-lg text-xs overflow-x-auto">
              <pre>{JSON.stringify(testState.data, null, 2)}</pre>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}