import { getRSIColor, getRSILabel } from '@/utils/ui';
import { formatNumber } from '@/utils/formatters';

interface RSIIndicatorProps {
  value: number;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
  className?: string;
}

export default function RSIIndicator({
  value,
  size = 'medium',
  showLabel = true,
  className = '',
}: RSIIndicatorProps) {
  const sizeClasses = {
    small: 'text-lg',
    medium: 'text-2xl',
    large: 'text-3xl',
  };

  return (
    <div className={`bg-gradient-to-br from-purple-50 to-indigo-50 p-4 rounded-xl border-2 border-gray-300 ${className}`}>
      <div className="text-center">
        <div className={`${sizeClasses[size]} font-bold ${getRSIColor(value)}`}>
          {formatNumber(value, 1)}
        </div>
        <div className="text-sm text-gray-600 mt-1">RSI (14)</div>
        {showLabel && (
          <div className="text-xs mt-1 font-medium">
            {getRSILabel(value)}
          </div>
        )}
      </div>
    </div>
  );
}
