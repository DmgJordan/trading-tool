export type RecommendationAction = 'BUY' | 'SELL' | 'HOLD';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type RecommendationStatus =
  | 'PENDING'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'EXPIRED';

export interface AIRecommendation {
  id: number;
  user_id: number;
  symbol: string;
  action: RecommendationAction;
  target_price: number;
  confidence: number; // 0-100
  reasoning: string;
  risk_level: RiskLevel;
  estimated_pnl: number;
  estimated_pnl_percentage: number;
  market_data: Record<string, unknown>;
  status: RecommendationStatus;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface AIRecommendationRequest {
  symbols?: string[];
  time_horizon?: 'SHORT_TERM' | 'MEDIUM_TERM' | 'LONG_TERM';
  max_recommendations?: number;
  min_confidence?: number;
}

export interface AIRecommendationResponse {
  id: number;
  symbol: string;
  action: RecommendationAction;
  target_price: number;
  confidence: number;
  reasoning: string;
  risk_level: RiskLevel;
  estimated_pnl: number;
  estimated_pnl_percentage: number;
  expires_at: string;
  created_at: string;
}

export interface RecommendationAction_Update {
  status: RecommendationStatus;
  user_note?: string;
}

// Types pour les statistiques du dashboard
export interface DashboardStats {
  total_recommendations: number;
  pending_recommendations: number;
  accepted_recommendations: number;
  rejected_recommendations: number;
  total_estimated_pnl: number;
  total_estimated_pnl_percentage: number;
  last_generated_at: string | null;
}

// États pour l'interface utilisateur
export interface RecommendationsState {
  recommendations: AIRecommendation[];
  stats: DashboardStats | null;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;
  lastGenerated: string | null;
  selectedRecommendation: AIRecommendation | null;
}

export interface RecommendationsActions {
  loadRecommendations: () => Promise<void>;
  generateRecommendations: (request?: AIRecommendationRequest) => Promise<void>;
  acceptRecommendation: (id: number, note?: string) => Promise<void>;
  rejectRecommendation: (id: number, note?: string) => Promise<void>;
  loadStats: () => Promise<void>;
  setSelectedRecommendation: (recommendation: AIRecommendation | null) => void;
  clearError: () => void;
}

// Types pour les composants UI
export interface RecommendationCardProps {
  recommendation: AIRecommendation;
  onAccept: (id: number) => void;
  onReject: (id: number) => void;
  onExpand?: (id: number) => void;
  isExpanded?: boolean;
  disabled?: boolean;
}

export interface GenerateButtonProps {
  onGenerate: () => void;
  isLoading: boolean;
  disabled?: boolean;
  lastGenerated?: string | null;
}

export interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  confirmColor?: 'green' | 'red' | 'blue';
  isLoading?: boolean;
}

// Constantes utiles pour l'interface
export const RECOMMENDATION_ACTIONS = [
  {
    value: 'BUY',
    label: 'Acheter',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    icon: '📈',
  },
  {
    value: 'SELL',
    label: 'Vendre',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    icon: '📉',
  },
  {
    value: 'HOLD',
    label: 'Conserver',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    icon: '⏸️',
  },
] as const;

export const RISK_LEVELS = [
  {
    value: 'LOW',
    label: 'Faible',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    icon: '🟢',
  },
  {
    value: 'MEDIUM',
    label: 'Moyen',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    icon: '🟡',
  },
  {
    value: 'HIGH',
    label: 'Élevé',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    icon: '🔴',
  },
] as const;

export const RECOMMENDATION_STATUS = [
  {
    value: 'PENDING',
    label: 'En attente',
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
  },
  {
    value: 'ACCEPTED',
    label: 'Acceptée',
    color: 'text-green-600',
    bgColor: 'bg-green-100',
  },
  {
    value: 'REJECTED',
    label: 'Rejetée',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
  },
  {
    value: 'EXPIRED',
    label: 'Expirée',
    color: 'text-orange-600',
    bgColor: 'bg-orange-100',
  },
] as const;

// Utilitaires pour formater les données
export const formatPnL = (pnl: number, percentage: number): string => {
  const sign = pnl >= 0 ? '+' : '';
  return `${sign}${pnl.toFixed(2)}€ (${sign}${percentage.toFixed(1)}%)`;
};

export const formatConfidence = (confidence: number): string => {
  return `${confidence}%`;
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 80) return 'text-green-600';
  if (confidence >= 60) return 'text-yellow-600';
  return 'text-red-600';
};

export const getConfidenceBgColor = (confidence: number): string => {
  if (confidence >= 80) return 'bg-green-100';
  if (confidence >= 60) return 'bg-yellow-100';
  return 'bg-red-100';
};

export const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 60) {
    return `il y a ${diffMins} min`;
  } else if (diffHours < 24) {
    return `il y a ${diffHours}h`;
  } else {
    return `il y a ${diffDays}j`;
  }
};

export const isRecommendationExpired = (expiresAt: string): boolean => {
  return new Date(expiresAt) < new Date();
};

export const isRecommendationExpiringSoon = (
  expiresAt: string,
  hoursThreshold: number = 2
): boolean => {
  const expiryTime = new Date(expiresAt);
  const thresholdTime = new Date(Date.now() + hoursThreshold * 60 * 60 * 1000);
  return expiryTime < thresholdTime;
};
