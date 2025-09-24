'use client';

import { useState, useEffect } from 'react';
import {
  ohlcvApi,
  ExchangeListResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
  CurrentPriceInfo,
  MAIndicators,
  VolumeIndicators
} from '../lib/api';

interface MultiTimeframeState {
  status: 'idle' | 'testing' | 'success' | 'error';
  message: string;
  data: MultiTimeframeResponse | null;
  exchange: string;
  symbol: string;
  profile: 'short' | 'medium' | 'long';
}

export default function CCXTTest() {
  const [testState, setTestState] = useState<MultiTimeframeState>({
    status: 'idle',
    message: '',
    data: null,
    exchange: '',
    symbol: '',
    profile: 'medium'
  });

  const [availableData, setAvailableData] = useState<ExchangeListResponse | null>(null);
  const [selectedExchange, setSelectedExchange] = useState('binance');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [selectedProfile, setSelectedProfile] = useState<'short' | 'medium' | 'long'>('medium');

  // Charger les exchanges disponibles au montage
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

  const testMultiTimeframes = async () => {
    setTestState({
      status: 'testing',
      message: `Analyse multi-timeframes en cours pour ${selectedExchange} ${selectedSymbol} (${selectedProfile})...`,
      data: null,
      exchange: selectedExchange,
      symbol: selectedSymbol,
      profile: selectedProfile
    });

    try {
      const request: MultiTimeframeRequest = {
        exchange: selectedExchange,
        symbol: selectedSymbol,
        profile: selectedProfile
      };

      const result = await ohlcvApi.getMultiTimeframeAnalysis(request);

      setTestState({
        status: 'success',
        message: `Analyse terminée avec succès pour ${selectedProfile} terme`,
        data: result,
        exchange: selectedExchange,
        symbol: selectedSymbol,
        profile: selectedProfile
      });

    } catch (error) {
      setTestState({
        status: 'error',
        message: `Erreur: ${error instanceof Error ? error.message : 'Analyse échouée'}`,
        data: null,
        exchange: selectedExchange,
        symbol: selectedSymbol,
        profile: selectedProfile
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

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toLocaleString('fr-FR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  };

  const getProfileLabel = (profile: string) => {
    switch (profile) {
      case 'short':
        return 'Court terme (15m/1h/5m)';
      case 'medium':
        return 'Moyen terme (1h/1D/15m)';
      case 'long':
        return 'Long terme (1D/1W/4h)';
      default:
        return profile;
    }
  };

  const getRSIColor = (rsi: number) => {
    if (rsi >= 70) return 'text-red-600';
    if (rsi <= 30) return 'text-green-600';
    if (rsi >= 50) return 'text-blue-600';
    return 'text-yellow-600';
  };

  const getRSILabel = (rsi: number) => {
    if (rsi >= 70) return 'Surachat';
    if (rsi <= 30) return 'Survente';
    if (rsi >= 50) return 'Haussier';
    return 'Baissier';
  };

  const renderMACard = (title: string, ma: MAIndicators, tf: string) => (
    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-xl border-2 border-gray-300">
      <div className="text-center mb-2">
        <h4 className="text-sm font-semibold text-gray-700">{title}</h4>
        <div className="text-xs text-gray-500">{tf}</div>
      </div>
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span>MA20:</span>
          <span className="font-semibold">{formatNumber(ma.ma20)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>MA50:</span>
          <span className="font-semibold">{formatNumber(ma.ma50)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>MA200:</span>
          <span className="font-semibold">{formatNumber(ma.ma200)}</span>
        </div>
      </div>
    </div>
  );

  const renderVolumeCard = (title: string, volume: VolumeIndicators, tf: string) => (
    <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-xl border-2 border-gray-300">
      <div className="text-center mb-2">
        <h4 className="text-sm font-semibold text-gray-700">{title}</h4>
        <div className="text-xs text-gray-500">{tf}</div>
      </div>
      <div className="text-center">
        <div className={`text-lg font-bold ${volume.spike_ratio >= 1.5 ? 'text-orange-600' : 'text-green-600'}`}>
          {formatNumber(volume.spike_ratio, 2)}x
        </div>
        <div className="text-sm text-gray-600 mt-1">Volume Spike</div>
        <div className="text-xs mt-1">Current: {formatNumber(volume.current, 0)}</div>
        <div className="text-xs">Avg20: {formatNumber(volume.avg20, 0)}</div>
      </div>
    </div>
  );

  const renderCandles = (candles: number[][]) => {
    if (!candles || candles.length === 0) return <div>Aucune données de bougies</div>;

    return (
      <div className="bg-gray-50 rounded-xl border-2 border-gray-300 p-4 max-h-96 overflow-y-auto">
        <div className="space-y-2">
          {candles.slice(-10).map((candle, index) => (
            <div key={index} className="bg-white p-2 rounded border text-xs">
              <div className="grid grid-cols-3 gap-2">
                <div><strong>Date:</strong> {new Date(candle[0]).toLocaleString('fr-FR')}</div>
                <div><strong>O:</strong> {candle[1].toFixed(4)}</div>
                <div><strong>H:</strong> {candle[2].toFixed(4)}</div>
                <div><strong>L:</strong> {candle[3].toFixed(4)}</div>
                <div><strong>C:</strong> {candle[4].toFixed(4)}</div>
                <div><strong>V:</strong> {candle[5].toFixed(2)}</div>
              </div>
            </div>
          ))}
        </div>
        {candles.length > 10 && (
          <div className="mt-3 text-center text-sm text-gray-600">
            ... et {candles.length - 10} autres bougies (10 dernières affichées)
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-black p-8 sm:p-10">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold text-black mb-3">
          Analyse Multi-Timeframes
        </h2>
        <p className="text-gray-600">
          Analyse technique sur plusieurs timeframes selon votre profil de trading
        </p>
      </div>

      {/* Configuration des paramètres */}
      <div className="mb-8 p-6 bg-gray-50 rounded-xl border border-gray-300">
        <h3 className="text-xl font-semibold text-black mb-4">Paramètres d'analyse</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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

          {/* Profil de trading */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">Profil de trading</label>
            <select
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value as 'short' | 'medium' | 'long')}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              <option value="short">Court terme</option>
              <option value="medium">Moyen terme</option>
              <option value="long">Long terme</option>
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
              <h3 className="font-semibold text-black text-lg">Analyse Multi-Timeframes</h3>
              <p className="text-gray-700 mt-1">
                {selectedExchange.charAt(0).toUpperCase() + selectedExchange.slice(1)} - {selectedSymbol} - {getProfileLabel(selectedProfile)}
              </p>
            </div>
          </div>
          <button
            onClick={testMultiTimeframes}
            disabled={testState.status === 'testing'}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-sm hover:shadow-md"
          >
            {testState.status === 'testing' ? 'Analyse...' : 'Lancer l\'analyse'}
          </button>
        </div>
      </div>

      {/* Message de statut */}
      {testState.message && (
        <div className="mt-8 p-5 bg-gray-100 rounded-xl border-2 border-gray-300">
          <p className="text-black text-center font-medium">{testState.message}</p>
        </div>
      )}

      {/* Affichage des résultats multi-timeframes */}
      {testState.data && (
        <div className="mt-8">
          <div className="mb-6 text-center">
            <h3 className="text-2xl font-semibold text-black mb-2">📊 {testState.data.symbol}</h3>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border-2 border-gray-300 p-4 inline-block">
              <div className="text-3xl font-bold text-black">
                ${formatNumber(testState.data.current_price.current_price, 4)}
              </div>
              {testState.data.current_price.change_24h_percent !== null && testState.data.current_price.change_24h_percent !== undefined && (
                <div className={`text-lg font-semibold mt-1 ${testState.data.current_price.change_24h_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {testState.data.current_price.change_24h_percent >= 0 ? '+' : ''}{formatNumber(testState.data.current_price.change_24h_percent, 2)}%
                  <span className="text-sm text-gray-600 ml-1">24h</span>
                </div>
              )}
              {testState.data.current_price.volume_24h && (
                <div className="text-sm text-gray-600 mt-1">
                  Volume 24h: {formatNumber(testState.data.current_price.volume_24h, 0)}
                </div>
              )}
            </div>
          </div>

          {/* Timeframe Principal */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-black mb-4">🎯 Timeframe Principal - {testState.data.tf}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

              {/* RSI Principal */}
              <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className={`text-2xl font-bold ${getRSIColor(testState.data.features.rsi14)}`}>
                    {formatNumber(testState.data.features.rsi14, 1)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">RSI (14)</div>
                  <div className="text-xs mt-1 font-medium">{getRSILabel(testState.data.features.rsi14)}</div>
                </div>
              </div>

              {/* ATR Principal */}
              <div className="bg-gradient-to-br from-orange-50 to-red-50 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {formatNumber(testState.data.features.atr14, 4)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">ATR (14)</div>
                  <div className="text-xs mt-1">Volatilité</div>
                </div>
              </div>

              {/* MA Principal */}
              {renderMACard("Moyennes Mobiles", testState.data.features.ma, testState.data.tf)}

              {/* Volume Principal */}
              {renderVolumeCard("Volume", testState.data.features.volume, testState.data.tf)}
            </div>

            {/* Bougies du Timeframe Principal */}
            <div className="mt-6">
              <h5 className="text-md font-semibold text-black mb-3">📈 Dernières Bougies ({testState.data.tf})</h5>
              {renderCandles(testState.data.features.last_20_candles)}
            </div>
          </div>

          {/* Timeframe Supérieur */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-black mb-4">⬆️ Contexte Supérieur - {testState.data.higher_tf.tf}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

              {/* RSI Supérieur */}
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className={`text-xl font-bold ${getRSIColor(testState.data.higher_tf.rsi14)}`}>
                    {formatNumber(testState.data.higher_tf.rsi14, 1)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">RSI</div>
                  <div className="text-xs mt-1">{getRSILabel(testState.data.higher_tf.rsi14)}</div>
                </div>
              </div>

              {/* ATR Supérieur */}
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className="text-xl font-bold text-gray-600">
                    {formatNumber(testState.data.higher_tf.atr14, 4)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">ATR</div>
                </div>
              </div>

              {/* Structure de marché */}
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className="text-sm font-bold text-orange-600">
                    {testState.data.higher_tf.structure}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Structure</div>
                  <div className="text-xs mt-1">
                    R: {formatNumber(testState.data.higher_tf.nearest_resistance)}
                  </div>
                </div>
              </div>

              {/* MA Supérieur */}
              {renderMACard("MA Contexte", testState.data.higher_tf.ma, testState.data.higher_tf.tf)}
            </div>
          </div>

          {/* Timeframe Inférieur */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-black mb-4">⬇️ Contexte Inférieur - {testState.data.lower_tf.tf}</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">

              {/* RSI Inférieur */}
              <div className="bg-gradient-to-br from-green-50 to-teal-50 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className={`text-xl font-bold ${getRSIColor(testState.data.lower_tf.rsi14)}`}>
                    {formatNumber(testState.data.lower_tf.rsi14, 1)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">RSI</div>
                  <div className="text-xs mt-1">{getRSILabel(testState.data.lower_tf.rsi14)}</div>
                </div>
              </div>

              {/* Volume Inférieur */}
              {renderVolumeCard("Volume Court Terme", testState.data.lower_tf.volume, testState.data.lower_tf.tf)}

              {/* Info Timeframe */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl border-2 border-gray-300">
                <div className="text-center">
                  <div className="text-xl font-bold text-indigo-600">
                    {testState.data.lower_tf.last_20_candles.length}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Bougies</div>
                  <div className="text-xs mt-1">Disponibles</div>
                </div>
              </div>
            </div>

            {/* Dernières bougies */}
            <div>
              <h5 className="text-md font-semibold text-black mb-3">📈 Dernières Bougies ({testState.data.lower_tf.tf})</h5>
              {renderCandles(testState.data.lower_tf.last_20_candles)}
            </div>
          </div>

          {/* JSON complet */}
          <details className="mt-8">
            <summary className="cursor-pointer text-lg font-semibold text-gray-700 hover:text-black mb-4">
              🔍 Données JSON Complètes
            </summary>
            <div className="mt-4 p-4 bg-gray-900 text-green-400 rounded-lg text-xs overflow-x-auto max-h-96 overflow-y-auto">
              <pre>{JSON.stringify(testState.data, null, 2)}</pre>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}