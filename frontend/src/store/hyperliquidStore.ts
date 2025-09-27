import { create } from 'zustand';
import { hyperliquidApi } from '../lib/api/hyperliquid';
import {
  HyperliquidConnectorResponse,
  HyperliquidUserInfoData,
} from '../lib/types/hyperliquid';

interface HyperliquidState {
  data: HyperliquidUserInfoData | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  useTestnet: boolean;
}

interface HyperliquidActions {
  fetchUserInfo: (options?: {
    useTestnet?: boolean;
  }) => Promise<HyperliquidConnectorResponse>;
  setUseTestnet: (useTestnet: boolean) => Promise<void>;
  clearError: () => void;
}

type HyperliquidStore = HyperliquidState & HyperliquidActions;

export const useHyperliquidStore = create<HyperliquidStore>()((set, get) => ({
  data: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
  useTestnet: false,

  async fetchUserInfo(options = {}) {
    const targetUseTestnet = options.useTestnet ?? get().useTestnet;
    set({ isLoading: true, error: null });

    try {
      const response = await hyperliquidApi.getUserInfo({
        useTestnet: targetUseTestnet,
      });

      if (response.status !== 'success' || !response.data) {
        throw new Error(
          response.message || 'Impossible de récupérer les données Hyperliquid'
        );
      }

      set({
        data: response.data,
        isLoading: false,
        error: null,
        lastUpdated: response.data.retrievedAt || response.timestamp,
        useTestnet: targetUseTestnet,
      });

      return response;
    } catch (error: unknown) {
      const message =
        (error as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ||
        (error instanceof Error ? error.message : 'Erreur inconnue');

      set({ isLoading: false, error: message });
      throw error;
    }
  },

  async setUseTestnet(useTestnet: boolean) {
    set({ useTestnet });
    await get().fetchUserInfo({ useTestnet });
  },

  clearError() {
    set({ error: null });
  },
}));
