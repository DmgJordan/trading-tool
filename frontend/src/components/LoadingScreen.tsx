'use client';

interface LoadingScreenProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'fullscreen' | 'inline';
}

export default function LoadingScreen({
  message = "Chargement...",
  size = 'medium',
  variant = 'fullscreen'
}: LoadingScreenProps) {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  const logoSizeClasses = {
    small: 'w-8 h-8 text-lg',
    medium: 'w-12 h-12 text-xl',
    large: 'w-16 h-16 text-2xl'
  };

  const containerClasses = variant === 'fullscreen'
    ? 'min-h-screen bg-white flex items-center justify-center'
    : 'flex items-center justify-center p-8';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        {/* Logo de l'application */}
        <div className={`${logoSizeClasses[size]} bg-black rounded-full flex items-center justify-center mx-auto mb-4`}>
          <span className="text-white font-bold">T</span>
        </div>

        {/* Spinner de chargement */}
        <div className={`animate-spin ${sizeClasses[size]} border-4 border-black border-t-transparent rounded-full mx-auto mb-4`}></div>

        {/* Message de chargement */}
        <p className="text-gray-600 font-medium">{message}</p>

        {/* Indicateur de progression pour les longs chargements */}
        {variant === 'fullscreen' && (
          <div className="mt-6 w-48 mx-auto">
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div className="bg-black h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Composant LoadingOverlay pour les chargements en surimpression
export function LoadingOverlay({
  isVisible,
  message = "Chargement...",
  onCancel
}: {
  isVisible: boolean;
  message?: string;
  onCancel?: () => void;
}) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-8 max-w-sm mx-4 shadow-xl">
        <LoadingScreen message={message} variant="inline" size="medium" />

        {onCancel && (
          <button
            onClick={onCancel}
            className="mt-4 w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Annuler
          </button>
        )}
      </div>
    </div>
  );
}

// Composant LoadingSkeleton pour le contenu en cours de chargement
export function LoadingSkeleton({
  lines = 3,
  className = ""
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className={`bg-gray-200 rounded h-4 mb-3 ${
            i === lines - 1 ? 'w-3/4' : 'w-full'
          }`}
        ></div>
      ))}
    </div>
  );
}