'use client';

interface LoadingSkeletonProps {
  count?: number;
  className?: string;
}

export default function LoadingSkeleton({ count = 3, className = '' }: LoadingSkeletonProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            {/* En-tête de la carte */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                <div>
                  <div className="h-4 bg-gray-200 rounded w-16 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-24"></div>
                </div>
              </div>
              <div className="w-16 h-6 bg-gray-200 rounded-full"></div>
            </div>

            {/* Prix et P&L */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="h-3 bg-gray-200 rounded w-20 mb-1"></div>
                <div className="h-6 bg-gray-200 rounded w-24"></div>
              </div>
              <div>
                <div className="h-3 bg-gray-200 rounded w-16 mb-1"></div>
                <div className="h-6 bg-gray-200 rounded w-28"></div>
              </div>
            </div>

            {/* Barre de confiance */}
            <div className="mb-4">
              <div className="h-3 bg-gray-200 rounded w-20 mb-2"></div>
              <div className="w-full bg-gray-200 rounded-full h-2"></div>
            </div>

            {/* Raisonnement */}
            <div className="mb-6">
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-4/5 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-3/4"></div>
            </div>

            {/* Boutons d'action */}
            <div className="flex space-x-3">
              <div className="flex-1 h-10 bg-gray-200 rounded-lg"></div>
              <div className="flex-1 h-10 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function StatsLoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
              <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function HeaderLoadingSkeleton() {
  return (
    <div className="animate-pulse mb-8">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div className="mb-4 lg:mb-0">
          <div className="h-8 bg-gray-200 rounded w-48 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-64"></div>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="w-40 h-10 bg-gray-200 rounded-lg"></div>
          <div className="w-48 h-10 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    </div>
  );
}