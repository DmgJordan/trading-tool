'use client';

import { useState } from 'react';
import { useNotifications } from '@/hooks';
import { formatDateTime } from '@/utils/formatters';

interface ClaudeResponseProps {
  response: string;
  selectedAssets: string[];
  timestamp?: Date;
  className?: string;
}

export default function ClaudeResponse({
  response,
  selectedAssets,
  timestamp = new Date(),
  className = '',
}: ClaudeResponseProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const { success } = useNotifications();

  const formatTimestamp = (date: Date) => {
    return new Intl.DateTimeFormat('fr-FR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  };

  const handleCopyResponse = async () => {
    try {
      await navigator.clipboard.writeText(response);
      success('Analyse copiée dans le presse-papiers !');
    } catch (error) {
      console.error('Failed to copy response:', error);
    }
  };

  const handleExportAnalysis = () => {
    const analysisData = {
      timestamp: timestamp.toISOString(),
      selectedAssets,
      response,
    };

    const blob = new Blob([JSON.stringify(analysisData, null, 2)], {
      type: 'application/json',
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analyse-trading-${selectedAssets.join('-')}-${timestamp.getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className={`bg-white border border-gray-200 rounded-xl shadow-sm ${className}`}
    >
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-4 h-4 text-white"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-black">
                  Analyse Claude
                </h3>
                <p className="text-sm text-gray-500">
                  {formatTimestamp(timestamp)}
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 rounded-md transition-colors"
              title={isExpanded ? 'Réduire' : 'Développer'}
            >
              <svg
                className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>

            <button
              onClick={handleCopyResponse}
              className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 rounded-md transition-colors"
              title="Copier la réponse"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
            </button>

            <button
              onClick={handleExportAnalysis}
              className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 rounded-md transition-colors"
              title="Exporter l'analyse"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Assets analyzed */}
        <div className="mt-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">
              {selectedAssets.length === 1
                ? 'Actif analysé :'
                : 'Actifs analysés :'}
            </span>
            <div className="flex flex-wrap gap-1">
              {selectedAssets.map(asset => (
                <span
                  key={asset}
                  className="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-md"
                >
                  {asset}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Response content */}
      {isExpanded && (
        <div className="px-6 py-6">
          <div className="prose prose-sm max-w-none">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 font-mono text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
              {response}
            </div>
          </div>
        </div>
      )}

      {/* Footer with metadata */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 rounded-b-xl">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Analyse générée par Claude</span>
          <span>{response.length} caractères</span>
        </div>
      </div>
    </div>
  );
}
