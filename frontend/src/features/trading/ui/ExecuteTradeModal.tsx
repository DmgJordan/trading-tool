'use client';

import { useState, useEffect } from 'react';
import type {
  TradeRecommendation,
  ExecuteTradeRequest,
} from '@/lib/types/trading';
import { hyperliquidTradingApi } from '@/features/trading/api/trading.api';
import type { HyperliquidUserInfoData } from '@/lib/types/hyperliquid';

interface ExecuteTradeModalProps {
  isOpen: boolean;
  recommendation: TradeRecommendation | null;
  ticker: string;
  onClose: () => void;
  onExecute: (request: ExecuteTradeRequest) => Promise<void>;
  className?: string;
}

export default function ExecuteTradeModal({
  isOpen,
  recommendation,
  ticker,
  onClose,
  onExecute,
  className = '',
}: ExecuteTradeModalProps) {
  const [portfolioInfo, setPortfolioInfo] = useState<{
    status: string;
    data: HyperliquidUserInfoData;
  } | null>(null);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
  const [useTestnet, setUseTestnet] = useState(true); // Testnet par défaut pour sécurité
  const [customPercentage, setCustomPercentage] = useState<number>(0);
  const [isExecuting, setIsExecuting] = useState(false);

  // Charger les informations du portefeuille quand le modal s'ouvre
  useEffect(() => {
    if (isOpen && recommendation) {
      setCustomPercentage(recommendation.portfolio_percentage);
      loadPortfolioInfo();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, recommendation]);

  const loadPortfolioInfo = async () => {
    setIsLoadingPortfolio(true);
    try {
      const result = await hyperliquidTradingApi.getPortfolioInfo(useTestnet);
      console.log('Portfolio info reçue:', result);
      if (result.status === 'success') {
        setPortfolioInfo(result);
      }
    } catch (error) {
      console.error('Erreur chargement portefeuille:', error);
    } finally {
      setIsLoadingPortfolio(false);
    }
  };

  const handleExecute = async () => {
    if (!recommendation) return;

    setIsExecuting(true);
    try {
      const executeRequest: ExecuteTradeRequest = {
        symbol: ticker,
        direction: recommendation.direction,
        entry_price: recommendation.entry_price,
        stop_loss: recommendation.stop_loss,
        take_profit_1: recommendation.take_profit_1,
        take_profit_2: recommendation.take_profit_2,
        take_profit_3: recommendation.take_profit_3,
        portfolio_percentage: customPercentage,
        use_testnet: useTestnet,
      };

      await onExecute(executeRequest);
      onClose();
    } catch (error) {
      console.error('Erreur exécution trade:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const calculatePositionValue = () => {
    if (
      !portfolioInfo?.data?.user_state?.marginSummary?.accountValue ||
      !recommendation
    )
      return 0;
    const accountValue = parseFloat(
      portfolioInfo.data.user_state.marginSummary.accountValue
    );
    return (accountValue * customPercentage) / 100;
  };

  const calculatePositionSize = () => {
    if (!recommendation) return 0;
    const positionValue = calculatePositionValue();
    return positionValue / recommendation.entry_price;
  };

  const calculateRisk = () => {
    if (!recommendation) return { amount: 0, percentage: 0 };
    const riskPerToken = Math.abs(
      recommendation.entry_price - recommendation.stop_loss
    );
    const positionSize = calculatePositionSize();
    const riskAmount = riskPerToken * positionSize;
    const riskPercentage = (riskPerToken / recommendation.entry_price) * 100;

    return { amount: riskAmount, percentage: riskPercentage };
  };

  if (!isOpen || !recommendation) return null;

  const risk = calculateRisk();
  const positionValue = calculatePositionValue();
  const positionSize = calculatePositionSize();

  const directionColors = {
    long: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-900',
      accent: 'text-green-700',
      button: 'bg-green-600 hover:bg-green-700',
    },
    short: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-900',
      accent: 'text-red-700',
      button: 'bg-red-600 hover:bg-red-700',
    },
  };

  const colors = directionColors[recommendation.direction];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        className={`bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto ${className}`}
      >
        {/* Header */}
        <div className={`${colors.bg} ${colors.border} border-b-2 px-6 py-4`}>
          <div className="flex items-center justify-between">
            <h2 className={`text-xl font-bold ${colors.text}`}>
              Confirmer l&apos;exécution du trade
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
          <p className={`text-sm ${colors.accent} mt-1`}>
            {recommendation.direction.toUpperCase()} {ticker} • Confiance{' '}
            {recommendation.confidence_level}%
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Informations du portefeuille */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">
              Informations du portefeuille
            </h3>
            {isLoadingPortfolio ? (
              <div className="text-center py-4">
                <div className="animate-spin w-6 h-6 border-2 border-gray-300 border-t-gray-900 rounded-full mx-auto"></div>
                <p className="text-sm text-gray-600 mt-2">Chargement...</p>
              </div>
            ) : portfolioInfo?.data ? (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Valeur du compte</div>
                  <div className="font-semibold">
                    $
                    {parseFloat(
                      portfolioInfo.data.user_state?.marginSummary
                        ?.accountValue || '0'
                    ).toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">
                    Balance disponible
                  </div>
                  <div className="font-semibold">
                    $
                    {parseFloat(
                      portfolioInfo.data.user_state?.crossMarginSummary
                        ?.totalRawUsd || '0'
                    ).toLocaleString()}
                  </div>
                </div>
              </div>
            ) : portfolioInfo ? (
              <div className="text-red-600 text-sm">
                Erreur : données du portefeuille manquantes
              </div>
            ) : (
              <div className="text-red-600 text-sm">
                Impossible de charger les informations du portefeuille
              </div>
            )}
          </div>

          {/* Paramètres du trade */}
          <div className="space-y-4">
            <h3 className="font-semibold text-gray-900">Paramètres du trade</h3>

            {/* Pourcentage du portefeuille */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pourcentage du portefeuille
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="range"
                  min="0.1"
                  max="50.0"
                  step="0.1"
                  value={customPercentage}
                  onChange={e => setCustomPercentage(Number(e.target.value))}
                  className="flex-1"
                />
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    min="0.1"
                    max="50.0"
                    step="0.1"
                    value={customPercentage}
                    onChange={e => setCustomPercentage(Number(e.target.value))}
                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                  />
                  <span className="text-sm text-gray-600">%</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Recommandé : {recommendation.portfolio_percentage}% (Max : 50%)
              </p>
            </div>

            {/* Mode testnet */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="testnet"
                checked={useTestnet}
                onChange={e => {
                  setUseTestnet(e.target.checked);
                  if (portfolioInfo) loadPortfolioInfo(); // Recharger avec le nouveau mode
                }}
                className="rounded"
              />
              <label htmlFor="testnet" className="text-sm text-gray-700">
                Utiliser le testnet (mode démo)
              </label>
            </div>
          </div>

          {/* Résumé du trade */}
          <div
            className={`${colors.bg} ${colors.border} border-2 rounded-lg p-4`}
          >
            <h3 className={`font-semibold ${colors.text} mb-3`}>
              Résumé du trade
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Valeur de la position</div>
                <div className="font-semibold">
                  ${positionValue.toLocaleString()}
                </div>
              </div>
              <div>
                <div className="text-gray-600">Taille de la position</div>
                <div className="font-semibold">
                  {positionSize.toFixed(6)} {ticker}
                </div>
              </div>
              <div>
                <div className="text-red-600">Risque maximum</div>
                <div className="font-semibold text-red-700">
                  ${risk.amount.toLocaleString()} ({risk.percentage.toFixed(1)}
                  %)
                </div>
              </div>
              <div>
                <div className="text-green-600">Ratio R/R</div>
                <div className="font-semibold text-green-700">
                  {recommendation.risk_reward_ratio.toFixed(1)}:1
                </div>
              </div>
            </div>

            {/* Prix détaillés */}
            <div className="mt-4 pt-4 border-t border-gray-200 border-opacity-50">
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="text-center">
                  <div className="text-gray-600">Entrée</div>
                  <div className="font-semibold">
                    ${recommendation.entry_price.toLocaleString()}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-red-600">Stop Loss</div>
                  <div className="font-semibold text-red-700">
                    ${recommendation.stop_loss.toLocaleString()}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-green-600">TP1</div>
                  <div className="font-semibold text-green-700">
                    ${recommendation.take_profit_1.toLocaleString()}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-green-600">TP3</div>
                  <div className="font-semibold text-green-700">
                    ${recommendation.take_profit_3.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Avertissements */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <span className="text-yellow-600 text-lg">⚠️</span>
              <div className="text-sm text-yellow-800">
                <p className="font-semibold mb-2">
                  Avertissements importants :
                </p>
                <ul className="space-y-1 text-xs">
                  <li>• Le trading comporte des risques de perte en capital</li>
                  <li>
                    • Cette recommandation n&apos;est pas un conseil financier
                  </li>
                  <li>• Vous êtes responsable de vos décisions de trading</li>
                  <li>
                    • Les ordres seront placés automatiquement sur Hyperliquid
                  </li>
                  {useTestnet && (
                    <li>
                      • Mode testnet activé - Aucun fonds réel ne sera utilisé
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex space-x-4">
            <button
              onClick={onClose}
              className="flex-1 py-3 px-4 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleExecute}
              disabled={isExecuting || !portfolioInfo}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold text-white transition-colors ${colors.button} disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2`}
            >
              {isExecuting ? (
                <>
                  <svg
                    className="animate-spin w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Exécution...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Confirmer et Exécuter</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
