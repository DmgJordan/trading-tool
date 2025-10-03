import { formatNumber } from '@/utils/formatters';
import { INDICATOR_CARD_CLASSES, getVolumeSpikeColor } from '@/utils/ui';

interface VolumeIndicators {
  current: number;
  avg20: number;
  spike_ratio: number;
}

interface VolumeCardProps {
  title: string;
  indicators: VolumeIndicators;
  timeframe: string;
  className?: string;
}

export default function VolumeCard({
  title,
  indicators,
  timeframe,
  className = '',
}: VolumeCardProps) {
  return (
    <div className={`${INDICATOR_CARD_CLASSES.volume} p-4 rounded-xl border-2 border-gray-300 ${className}`}>
      <div className="text-center mb-2">
        <h4 className="text-sm font-semibold text-gray-700">{title}</h4>
        <div className="text-xs text-gray-500">{timeframe}</div>
      </div>
      <div className="text-center">
        <div className={`text-lg font-bold ${getVolumeSpikeColor(indicators.spike_ratio)}`}>
          {formatNumber(indicators.spike_ratio, 2)}x
        </div>
        <div className="text-sm text-gray-600 mt-1">Volume Spike</div>
        <div className="text-xs mt-1">
          Current: {formatNumber(indicators.current, 0)}
        </div>
        <div className="text-xs">
          Avg20: {formatNumber(indicators.avg20, 0)}
        </div>
      </div>
    </div>
  );
}
