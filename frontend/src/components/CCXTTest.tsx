'use client';

import { useCCXTAnalysis } from '@/hooks';
import { TRADING_SYMBOLS, TRADING_PROFILES } from '@/constants';
import { getStatusColor, getStatusIcon, getProfileLabel, INDICATOR_CARD_CLASSES } from '@/utils/ui';
import { RSIIndicator, MACard, VolumeCard, PriceDisplay } from '@/components/ui';

export default function CCXTTest() {
  const {
    analysisState,
    availableData,
    selectedExchange,
    selectedSymbol,
    selectedProfile,
    setSelectedExchange,
    setSelectedSymbol,
    setSelectedProfile,
    runAnalysis,
    isAnalyzing,
  } = useCCXTAnalysis();

  const { status, message, data } = analysisState;

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-black p-8 sm:p-10">
      {/* Header */}
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-bold text-black mb-3">
          Analyse Multi-Timeframes
        </h2>
        <p className="text-gray-600">
          Analyse technique sur plusieurs timeframes selon votre profil de trading
        </p>
      </div>

      {/* Configuration */}
      <div className="mb-8 p-6 bg-gray-50 rounded-xl border border-gray-300">
        <h3 className="text-xl font-semibold text-black mb-4">
          Paramètres d&apos;analyse
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Exchange */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Exchange
            </label>
            <select
              value={selectedExchange}
              onChange={e => setSelectedExchange(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              {availableData?.exchanges.map(exchange => (
                <option key={exchange} value={exchange}>
                  {exchange.charAt(0).toUpperCase() + exchange.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Symbole */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Symbole
            </label>
            <select
              value={selectedSymbol}
              onChange={e => setSelectedSymbol(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              {TRADING_SYMBOLS.map(symbol => (
                <option key={symbol} value={symbol}>
                  {symbol}
                </option>
              ))}
            </select>
          </div>

          {/* Profil */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">
              Profil de trading
            </label>
            <select
              value={selectedProfile}
              onChange={e => setSelectedProfile(e.target.value as typeof selectedProfile)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-black focus:outline-none"
            >
              {TRADING_PROFILES.map(profile => (
                <option key={profile.value} value={profile.value}>
                  {profile.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Bouton d'analyse */}
      <div className={`p-6 rounded-xl border-2 transition-all duration-300 ${getStatusColor(status)}`}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <span className="text-xl">{getStatusIcon(status)}</span>
            </div>
            <div>
              <h3 className="font-semibold text-black text-lg">
                Analyse Multi-Timeframes
              </h3>
              <p className="text-gray-700 mt-1">
                {selectedExchange.charAt(0).toUpperCase() + selectedExchange.slice(1)} - {selectedSymbol} - {getProfileLabel(selectedProfile)}
              </p>
            </div>
          </div>
          <button
            onClick={runAnalysis}
            disabled={isAnalyzing}
            className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-sm hover:shadow-md"
          >
            {isAnalyzing ? 'Analyse...' : 'Lancer l\'analyse'}
          </button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className="mt-8 p-5 bg-gray-100 rounded-xl border-2 border-gray-300">
          <p className="text-black text-center font-medium">{message}</p>
        </div>
      )}

      {/* Résultats */}
      {data && (
        <div className="mt-8">
          {/* Prix actuel */}
          <PriceDisplay
            symbol={data.symbol}
            price={data.current_price.current_price}
            change24h={data.current_price.change_24h_percent}
            volume24h={data.current_price.volume_24h}
            className="mb-8"
          />

          {/* Timeframe Principal */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-black mb-4">
              🎯 Timeframe Principal - {data.tf}
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <RSIIndicator value={data.features.rsi14} />

              <div className={`${INDICATOR_CARD_CLASSES.atr} p-4 rounded-xl border-2 border-gray-300`}>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {data.features.atr14.toFixed(4)}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">ATR (14)</div>
                  <div className="text-xs mt-1">Volatilité</div>
                </div>
              </div>

              <MACard
                title="Moyennes Mobiles"
                indicators={data.features.ma}
                timeframe={data.tf}
              />

              <VolumeCard
                title="Volume"
                indicators={data.features.volume}
                timeframe={data.tf}
              />
            </div>
          </div>

          {/* Timeframe Supérieur */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-black mb-4">
              ⬆️ Contexte Supérieur - {data.higher_tf.tf}
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <RSIIndicator value={data.higher_tf.rsi14} size="small" />

              <MACard
                title="MA Contexte"
                indicators={data.higher_tf.ma}
                timeframe={data.higher_tf.tf}
              />

              <div className={`${INDICATOR_CARD_CLASSES.structure} p-4 rounded-xl border-2 border-gray-300`}>
                <div className="text-center">
                  <div className="text-sm font-bold text-orange-600">
                    {data.higher_tf.structure}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Structure</div>
                  <div className="text-xs mt-1">
                    R: {data.higher_tf.nearest_resistance.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Timeframe Inférieur */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-black mb-4">
              ⬇️ Contexte Inférieur - {data.lower_tf.tf}
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <RSIIndicator value={data.lower_tf.rsi14} size="small" />

              <VolumeCard
                title="Volume Court Terme"
                indicators={data.lower_tf.volume}
                timeframe={data.lower_tf.tf}
              />

              <div className={`${INDICATOR_CARD_CLASSES.price} p-4 rounded-xl border-2 border-gray-300`}>
                <div className="text-center">
                  <div className="text-xl font-bold text-indigo-600">
                    {data.lower_tf.last_20_candles.length}
                  </div>
                  <div className="text-sm text-gray-600 mt-1">Bougies</div>
                  <div className="text-xs mt-1">Disponibles</div>
                </div>
              </div>
            </div>
          </div>

          {/* JSON complet */}
          <details className="mt-8">
            <summary className="cursor-pointer text-lg font-semibold text-gray-700 hover:text-black mb-4">
              🔍 Données JSON Complètes
            </summary>
            <div className="mt-4 p-4 bg-gray-900 text-green-400 rounded-lg text-xs overflow-x-auto max-h-96 overflow-y-auto">
              <pre>{JSON.stringify(data, null, 2)}</pre>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
