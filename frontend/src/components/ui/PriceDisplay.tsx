import { formatPrice, formatPercentageChange, formatVolume } from '@/utils/formatters';
import { getPriceChangeColor, INDICATOR_CARD_CLASSES } from '@/utils/ui';

interface PriceDisplayProps {
  symbol: string;
  price: number;
  change24h?: number | null;
  volume24h?: number | null;
  className?: string;
}

export default function PriceDisplay({
  symbol,
  price,
  change24h,
  volume24h,
  className = '',
}: PriceDisplayProps) {
  return (
    <div className={`text-center ${className}`}>
      <h3 className="text-2xl font-semibold text-black mb-2">
        📊 {symbol}
      </h3>
      <div className={`${INDICATOR_CARD_CLASSES.price} rounded-xl border-2 border-gray-300 p-4 inline-block`}>
        <div className="text-3xl font-bold text-black">
          ${formatPrice(price)}
        </div>

        {change24h !== null && change24h !== undefined && (
          <div className={`text-lg font-semibold mt-1 ${getPriceChangeColor(change24h)}`}>
            {formatPercentageChange(change24h)}
            <span className="text-sm text-gray-600 ml-1">24h</span>
          </div>
        )}

        {volume24h && (
          <div className="text-sm text-gray-600 mt-1">
            Volume 24h: {formatVolume(volume24h)}
          </div>
        )}
      </div>
    </div>
  );
}
