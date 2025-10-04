import { useState, useEffect, useCallback } from 'react';
import {
  ohlcvApi,
  ExchangeListResponse,
  MultiTimeframeRequest,
  MultiTimeframeResponse,
} from '@/services/api';
import type { TradingProfile } from '@/shared/lib/ui';

interface AnalysisState {
  status: 'idle' | 'testing' | 'success' | 'error';
  message: string;
  data: MultiTimeframeResponse | null;
  exchange: string;
  symbol: string;
  profile: TradingProfile;
}

/**
 * Hook personnalisé pour gérer l'analyse multi-timeframes CCXT
 * Centralise toute la logique métier de CCXTTest
 */
export const useCCXTAnalysis = () => {
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    status: 'idle',
    message: '',
    data: null,
    exchange: '',
    symbol: '',
    profile: 'medium',
  });

  const [availableData, setAvailableData] =
    useState<ExchangeListResponse | null>(null);
  const [selectedExchange, setSelectedExchange] = useState('binance');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [selectedProfile, setSelectedProfile] =
    useState<TradingProfile>('medium');

  // Charger les exchanges disponibles
  const loadAvailableExchanges = useCallback(async () => {
    try {
      const data = await ohlcvApi.getAvailableExchanges();
      setAvailableData(data);
    } catch (error) {
      console.error('Erreur chargement des exchanges:', error);
    }
  }, []);

  // Charger au montage
  useEffect(() => {
    loadAvailableExchanges();
  }, [loadAvailableExchanges]);

  // Lancer l'analyse
  const runAnalysis = useCallback(async () => {
    setAnalysisState({
      status: 'testing',
      message: `Analyse multi-timeframes en cours pour ${selectedExchange} ${selectedSymbol} (${selectedProfile})...`,
      data: null,
      exchange: selectedExchange,
      symbol: selectedSymbol,
      profile: selectedProfile,
    });

    try {
      const request: MultiTimeframeRequest = {
        exchange: selectedExchange,
        symbol: selectedSymbol,
        profile: selectedProfile,
      };

      const result = await ohlcvApi.getMultiTimeframeAnalysis(request);

      setAnalysisState({
        status: 'success',
        message: `Analyse terminée avec succès pour ${selectedProfile} terme`,
        data: result,
        exchange: selectedExchange,
        symbol: selectedSymbol,
        profile: selectedProfile,
      });
    } catch (error) {
      setAnalysisState({
        status: 'error',
        message: `Erreur: ${error instanceof Error ? error.message : 'Analyse échouée'}`,
        data: null,
        exchange: selectedExchange,
        symbol: selectedSymbol,
        profile: selectedProfile,
      });
    }
  }, [selectedExchange, selectedSymbol, selectedProfile]);

  // Reset de l'analyse
  const resetAnalysis = useCallback(() => {
    setAnalysisState({
      status: 'idle',
      message: '',
      data: null,
      exchange: '',
      symbol: '',
      profile: 'medium',
    });
  }, []);

  return {
    // État
    analysisState,
    availableData,
    selectedExchange,
    selectedSymbol,
    selectedProfile,

    // Setters
    setSelectedExchange,
    setSelectedSymbol,
    setSelectedProfile,

    // Actions
    runAnalysis,
    resetAnalysis,
    loadAvailableExchanges,

    // Helpers
    isAnalyzing: analysisState.status === 'testing',
    hasData: analysisState.data !== null,
    hasError: analysisState.status === 'error',
  };
};
