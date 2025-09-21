'use client';

import { useEffect, useState } from 'react';
import { usePreferencesStore } from '../../store/preferencesStore';

interface AssetSelectorProps {
  onSelectionChange: (selectedAssets: string[]) => void;
  selectedAssets: string[];
  className?: string;
}

export default function AssetSelector({
  onSelectionChange,
  selectedAssets,
  className = ''
}: AssetSelectorProps) {
  const { preferences, isLoading, loadPreferences } = usePreferencesStore();
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);

  // Load user preferences on component mount
  useEffect(() => {
    loadPreferences().catch(console.error);
  }, [loadPreferences]);

  // Extract preferred assets from user preferences
  useEffect(() => {
    if (preferences?.preferred_assets) {
      let assets: string[] = [];

      // Handle both string and array formats
      if (typeof preferences.preferred_assets === 'string') {
        assets = preferences.preferred_assets
          .split(',')
          .map(asset => asset.trim().toUpperCase())
          .filter(asset => asset.length > 0);
      } else if (Array.isArray(preferences.preferred_assets)) {
        assets = preferences.preferred_assets
          .map(asset => String(asset).trim().toUpperCase())
          .filter(asset => asset.length > 0);
      }

      setAvailableAssets(assets);
    }
  }, [preferences?.preferred_assets]);

  const handleAssetToggle = (asset: string) => {
    const newSelection = selectedAssets.includes(asset)
      ? selectedAssets.filter(a => a !== asset)
      : [...selectedAssets, asset];

    onSelectionChange(newSelection);
  };

  const handleSelectAll = () => {
    onSelectionChange(availableAssets);
  };

  const handleClearAll = () => {
    onSelectionChange([]);
  };

  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="h-10 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (availableAssets.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="text-4xl mb-4">⚙️</div>
        <h3 className="text-lg font-semibold text-black mb-2">
          Aucun actif configuré
        </h3>
        <p className="text-gray-600 mb-4">
          Vous devez d'abord configurer vos actifs préférés dans les préférences.
        </p>
        <button
          onClick={() => window.location.href = '/preferences'}
          className="px-4 py-2 bg-black text-white font-medium rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 transition-colors"
        >
          Configurer les préférences
        </button>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Asset selection controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-lg font-medium text-black">
            Vos actifs préférés
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {availableAssets.length} actif{availableAssets.length > 1 ? 's' : ''} disponible{availableAssets.length > 1 ? 's' : ''}
          </p>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={handleSelectAll}
            disabled={selectedAssets.length === availableAssets.length}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Tout sélectionner
          </button>
          <button
            onClick={handleClearAll}
            disabled={selectedAssets.length === 0}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Tout désélectionner
          </button>
        </div>
      </div>

      {/* Asset grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        {availableAssets.map((asset) => {
          const isSelected = selectedAssets.includes(asset);

          return (
            <button
              key={asset}
              onClick={() => handleAssetToggle(asset)}
              className={`p-3 rounded-lg border-2 font-medium text-sm transition-all duration-200 ${
                isSelected
                  ? 'border-black bg-black text-white'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <span>{asset}</span>
                {isSelected && (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selection summary */}
      {selectedAssets.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <h4 className="font-medium text-blue-900">
                {selectedAssets.length} actif{selectedAssets.length > 1 ? 's' : ''} sélectionné{selectedAssets.length > 1 ? 's' : ''}
              </h4>
              <p className="text-blue-800 text-sm mt-1">
                {selectedAssets.join(', ')}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}