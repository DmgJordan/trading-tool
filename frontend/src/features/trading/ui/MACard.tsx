import { formatNumber } from '@/shared/lib/formatters';
import { INDICATOR_CARD_CLASSES } from '@/shared/lib/ui';

interface MAIndicators {
  ma20: number;
  ma50: number;
  ma200: number;
}

interface MACardProps {
  title: string;
  indicators: MAIndicators;
  timeframe: string;
  className?: string;
}

export default function MACard({
  title,
  indicators,
  timeframe,
  className = '',
}: MACardProps) {
  return (
    <div
      className={`${INDICATOR_CARD_CLASSES.ma} p-4 rounded-xl border-2 border-gray-300 ${className}`}
    >
      <div className="text-center mb-2">
        <h4 className="text-sm font-semibold text-gray-700">{title}</h4>
        <div className="text-xs text-gray-500">{timeframe}</div>
      </div>
      <div className="space-y-1">
        <div className="flex justify-between text-sm">
          <span>MA20:</span>
          <span className="font-semibold">{formatNumber(indicators.ma20)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>MA50:</span>
          <span className="font-semibold">{formatNumber(indicators.ma50)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>MA200:</span>
          <span className="font-semibold">
            {formatNumber(indicators.ma200)}
          </span>
        </div>
      </div>
    </div>
  );
}
