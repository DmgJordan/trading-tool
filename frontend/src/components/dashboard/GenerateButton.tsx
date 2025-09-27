'use client';

import { useState } from 'react';
import { formatTimeAgo } from '../../lib/types/ai_recommendations';

interface GenerateButtonProps {
  onGenerate: () => void;
  isLoading: boolean;
  disabled?: boolean;
  lastGenerated?: string | null;
  pendingCount?: number;
  className?: string;
}

export default function GenerateButton({
  onGenerate,
  isLoading,
  disabled = false,
  lastGenerated,
  pendingCount = 0,
  className = '',
}: GenerateButtonProps) {
  const [isHovered, setIsHovered] = useState(false);

  const isDisabled = disabled || isLoading;

  const handleClick = () => {
    if (!isDisabled) {
      onGenerate();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div className={`flex flex-col items-end ${className}`}>
      <button
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        disabled={isDisabled}
        className={`relative px-6 py-3 rounded-lg font-semibold text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
          isDisabled
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-black text-white hover:bg-gray-800 active:bg-gray-900 shadow-lg hover:shadow-xl transform hover:scale-[1.02]'
        }`}
      >
        <span className="flex items-center space-x-2">
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span>Génération en cours...</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              <span>Générer recommandations IA</span>
            </>
          )}
        </span>

        {/* Indicateur de nouvelles recommandations disponibles */}
        {!isLoading && pendingCount > 0 && (
          <div className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold">
            {pendingCount > 9 ? '9+' : pendingCount}
          </div>
        )}

        {/* Animation de pulsation lors du survol */}
        {isHovered && !isDisabled && (
          <div className="absolute inset-0 bg-white opacity-10 rounded-lg animate-pulse" />
        )}
      </button>

      {/* Informations sur la dernière génération */}
      {lastGenerated && (
        <p className="text-xs text-gray-500 mt-2">
          Dernière génération: {formatTimeAgo(lastGenerated)}
        </p>
      )}

      {/* Message d'aide */}
      {!lastGenerated && !isLoading && (
        <p className="text-xs text-gray-400 mt-2 max-w-48 text-right">
          Générez vos premières recommandations IA personnalisées
        </p>
      )}
    </div>
  );
}

// Variante compacte pour les espaces restreints
export function CompactGenerateButton({
  onGenerate,
  isLoading,
  disabled = false,
  className = '',
}: Pick<
  GenerateButtonProps,
  'onGenerate' | 'isLoading' | 'disabled' | 'className'
>) {
  const isDisabled = disabled || isLoading;

  return (
    <button
      onClick={() => !isDisabled && onGenerate()}
      disabled={isDisabled}
      className={`p-2 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
        isDisabled
          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
          : 'bg-black text-white hover:bg-gray-800 active:bg-gray-900'
      } ${className}`}
      title="Générer nouvelles recommandations"
    >
      {isLoading ? (
        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
        </svg>
      )}
    </button>
  );
}
