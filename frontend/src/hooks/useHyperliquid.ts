import { useHyperliquidStore } from '../store/hyperliquidStore';

/**
 * Hook personnalisé pour interagir avec Hyperliquid
 * Simplifie l'accès aux données et actions du store
 */
export const useHyperliquid = () => {
  const {
    data,
    isLoading,
    error,
    lastUpdated,
    useTestnet,
    fetchUserInfo,
    setUseTestnet,
    clearError,
  } = useHyperliquidStore();

  return {
    // État
    data,
    isLoading,
    error,
    lastUpdated,
    useTestnet,

    // Actions
    fetchUserInfo,
    setUseTestnet,
    clearError,

    // Helpers
    hasData: data !== null,
    portfolioValue: data?.portfolio_summary?.accountValue ?? null,
    positionsCount: data?.portfolio_summary?.perpPositionCount ?? 0,
    walletAddress: data?.wallet_address ?? null,
  };
};

/**
 * Hook pour l'auto-refresh des données Hyperliquid
 */
export const useHyperliquidAutoRefresh = (intervalMs: number = 30000) => {
  const { fetchUserInfo, useTestnet } = useHyperliquidStore();

  const startAutoRefresh = () => {
    const intervalId = setInterval(() => {
      fetchUserInfo({ useTestnet });
    }, intervalMs);

    return () => clearInterval(intervalId);
  };

  return { startAutoRefresh };
};
