'use client';

import { useMemo } from 'react';

interface PnlDataPoint {
  timestamp: number;
  pnl: number;
}

interface PnlChartProps {
  data?: PnlDataPoint[];
  width?: number;
  height?: number;
  className?: string;
}

export default function PnlChart({ data = [], width = 200, height = 60, className = '' }: PnlChartProps) {
  const chartData = useMemo(() => {
    if (!data.length) {
      // Données de démonstration si aucune donnée fournie
      const now = Date.now();
      return Array.from({ length: 20 }, (_, i) => ({
        timestamp: now - (19 - i) * 3600000, // Points horaires
        pnl: Math.sin(i * 0.3) * 50 + Math.random() * 20 - 10,
      }));
    }
    return data;
  }, [data]);

  const { pathData, minPnl, maxPnl, isPositive } = useMemo(() => {
    if (chartData.length === 0) {
      return { pathData: '', minPnl: 0, maxPnl: 0, isPositive: true };
    }

    const minPnl = Math.min(...chartData.map(d => d.pnl));
    const maxPnl = Math.max(...chartData.map(d => d.pnl));
    const range = maxPnl - minPnl || 1;

    const points = chartData.map((point, index) => {
      const x = (index / (chartData.length - 1)) * width;
      const y = height - ((point.pnl - minPnl) / range) * height;
      return `${x},${y}`;
    });

    const pathData = `M ${points.join(' L ')}`;
    const currentPnl = chartData[chartData.length - 1]?.pnl || 0;
    const isPositive = currentPnl >= 0;

    return { pathData, minPnl, maxPnl, isPositive };
  }, [chartData, width, height]);

  const strokeColor = isPositive ? '#16a34a' : '#dc2626'; // green-600 or red-600
  const fillColor = isPositive ? 'rgba(22, 163, 74, 0.1)' : 'rgba(220, 38, 38, 0.1)';

  return (
    <div className={`${className}`}>
      <svg width={width} height={height} className="overflow-visible">
        <defs>
          <linearGradient id="pnlGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={strokeColor} stopOpacity="0.3" />
            <stop offset="100%" stopColor={strokeColor} stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Zone de remplissage */}
        {pathData && (
          <path
            d={`${pathData} L ${width},${height} L 0,${height} Z`}
            fill="url(#pnlGradient)"
          />
        )}

        {/* Ligne du graphique */}
        {pathData && (
          <path
            d={pathData}
            stroke={strokeColor}
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Ligne de zéro si nécessaire */}
        {minPnl < 0 && maxPnl > 0 && (
          <line
            x1="0"
            y1={height - ((-minPnl) / (maxPnl - minPnl)) * height}
            x2={width}
            y2={height - ((-minPnl) / (maxPnl - minPnl)) * height}
            stroke="#9ca3af"
            strokeWidth="1"
            strokeDasharray="2,2"
            opacity="0.5"
          />
        )}

        {/* Point final */}
        {chartData.length > 0 && (
          <circle
            cx={(chartData.length - 1) / (chartData.length - 1) * width}
            cy={height - ((chartData[chartData.length - 1].pnl - minPnl) / (maxPnl - minPnl || 1)) * height}
            r="3"
            fill={strokeColor}
            stroke="white"
            strokeWidth="2"
          />
        )}
      </svg>
    </div>
  );
}