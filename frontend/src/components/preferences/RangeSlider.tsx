'use client';

import { useState, useEffect } from 'react';
import { SliderConfig } from '../../lib/types/preferences';

interface RangeSliderProps {
  value: number;
  onChange: (value: number) => void;
  config: SliderConfig;
  label: string;
  description?: string;
  error?: string;
  disabled?: boolean;
  showValue?: boolean;
  className?: string;
}

export default function RangeSlider({
  value,
  onChange,
  config,
  label,
  description,
  error,
  disabled = false,
  showValue = true,
  className = ''
}: RangeSliderProps) {
  const [internalValue, setInternalValue] = useState(value ?? config.min);
  const [isDragging, setIsDragging] = useState(false);

  // Synchroniser avec la valeur externe quand elle change
  useEffect(() => {
    if (!isDragging) {
      setInternalValue(value ?? config.min);
    }
  }, [value, isDragging, config.min]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    setInternalValue(newValue);
  };

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    onChange(internalValue);
  };

  const handleKeyUp = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      onChange(internalValue);
    }
  };

  const formatValue = config.formatValue || ((val) => `${val}${config.unit}`);
  const safeInternalValue = internalValue ?? config.min;
  const percentage = ((safeInternalValue - config.min) / (config.max - config.min)) * 100;

  // Calculer la couleur basée sur la valeur (vert = sûr, rouge = risqué)
  const getSliderColor = () => {
    if (disabled) return 'bg-gray-300';
    if (percentage <= 33) return 'bg-green-500';
    if (percentage <= 66) return 'bg-blue-500';
    return 'bg-red-500';
  };

  const getTrackColor = () => {
    if (disabled) return 'bg-gray-200';
    return 'bg-gray-200';
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Label et valeur */}
      <div className="flex justify-between items-center">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            {label}
          </label>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
        {showValue && (
          <div className="text-right">
            <span className={`text-lg font-bold ${
              disabled ? 'text-gray-400' : 'text-black'
            }`}>
              {formatValue(safeInternalValue)}
            </span>
            <div className="text-xs text-gray-500">
              {config.min}{config.unit} - {config.max}{config.unit}
            </div>
          </div>
        )}
      </div>

      {/* Slider */}
      <div className="relative">
        <div className={`h-2 rounded-full ${getTrackColor()}`}>
          {/* Track rempli */}
          <div
            className={`h-2 rounded-full transition-all duration-200 ${getSliderColor()}`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Input range */}
        <input
          type="range"
          min={config.min}
          max={config.max}
          step={config.step}
          value={safeInternalValue}
          onChange={handleChange}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onKeyUp={handleKeyUp}
          disabled={disabled}
          className="absolute top-0 left-0 w-full h-2 opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />

        {/* Thumb personnalisé */}
        <div
          className={`absolute top-1/2 w-6 h-6 rounded-full border-2 border-white shadow-lg transform -translate-y-1/2 transition-all duration-200 ${
            disabled
              ? 'bg-gray-400 cursor-not-allowed'
              : `${getSliderColor()} cursor-pointer hover:scale-110 active:scale-95`
          }`}
          style={{ left: `calc(${percentage}% - 12px)` }}
        />
      </div>

      {/* Marqueurs de valeurs importantes */}
      <div className="flex justify-between text-xs text-gray-400">
        <span>{config.min}{config.unit}</span>
        {config.max > 10 && (
          <span>{Math.round((config.min + config.max) / 2)}{config.unit}</span>
        )}
        <span>{config.max}{config.unit}</span>
      </div>

      {/* Message d'erreur */}
      {error && (
        <p className="text-sm text-red-600 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}

      {/* Conseils contextuels */}
      {!error && (
        <div className="text-xs text-gray-500">
          {percentage <= 25 && '💚 Très conservateur'}
          {percentage > 25 && percentage <= 50 && '🔵 Modéré'}
          {percentage > 50 && percentage <= 75 && '🟠 Risqué'}
          {percentage > 75 && '🔴 Très risqué'}
        </div>
      )}
    </div>
  );
}