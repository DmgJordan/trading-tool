/**
 * Types pour les composants UI réutilisables
 */

import { Status } from '@/utils/ui';
import { MAIndicators, VolumeIndicators } from '../api/ohlcv';

// RSI Indicator
export interface RSIIndicatorProps {
  value: number;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
  className?: string;
}

// Toast notifications
export interface ToastProps {
  id: string;
  message: string;
  type: Status;
  duration?: number;
  onClose: (id: string) => void;
}

export interface ToastContainerProps {
  children: React.ReactNode;
}

// Status Badge
export interface StatusBadgeProps {
  status: Status;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// Price Display
export interface PriceDisplayProps {
  symbol: string;
  price: number;
  change?: number;
  change24h?: number;
  className?: string;
}

// MA Card
export interface MACardProps {
  indicators: MAIndicators;
  timeframe: string;
  className?: string;
}

// Volume Card
export interface VolumeCardProps {
  indicators: VolumeIndicators;
  timeframe: string;
  className?: string;
}
