'use client';

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
  className?: string;
}

const claudeModels = [
  {
    id: 'claude-3-5-haiku-20241022',
    name: 'Claude Haiku 3.5',
    description: 'Ultra-rapide et économique',
    icon: '⚡',
    speed: 'Ultra rapide',
    cost: 'Faible',
  },
  {
    id: 'claude-sonnet-4-5-20250929',
    name: 'Claude Sonnet 4.5',
    description: 'Intelligence supérieure optimisée',
    icon: '🚀',
    speed: 'Rapide',
    cost: 'Modéré',
    recommended: true,
  },
  {
    id: 'claude-opus-4-1-20250805',
    name: 'Claude Opus 4.1',
    description: 'Analyse la plus puissante et précise',
    icon: '🎯',
    speed: 'Plus lent',
    cost: 'Élevé',
  },
];

export default function ModelSelector({
  selectedModel,
  onModelChange,
  className = '',
}: ModelSelectorProps) {
  return (
    <div className={`space-y-5 ${className}`}>
      <div>
        <h3 className="text-lg font-semibold text-black mb-2">Modèle Claude</h3>
        <p className="text-sm text-gray-600">
          Choisissez le modèle Claude pour votre analyse trading
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {claudeModels.map(model => {
          const isSelected = selectedModel === model.id;

          return (
            <button
              key={model.id}
              onClick={() => onModelChange(model.id)}
              className={`relative p-5 rounded-xl border-2 text-left transition-all duration-200 hover:shadow-lg ${
                isSelected
                  ? 'border-black bg-black text-white shadow-xl scale-[1.02]'
                  : 'border-gray-200 bg-white text-gray-900 hover:border-gray-400 hover:bg-gray-50'
              }`}
            >
              {/* Recommended badge */}
              {model.recommended && (
                <div className="absolute -top-2 -right-2 z-10">
                  <div
                    className={`px-2.5 py-1 rounded-full text-xs font-semibold shadow-md ${
                      isSelected ? 'bg-white text-black' : 'bg-black text-white'
                    }`}
                  >
                    ⭐ Recommandé
                  </div>
                </div>
              )}

              <div className="flex flex-col h-full">
                {/* Header avec icône et nom */}
                <div className="flex items-center space-x-3 mb-3">
                  <div className="text-3xl">{model.icon}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-bold text-base">{model.name}</h4>
                      {isSelected && (
                        <svg
                          className="w-5 h-5 flex-shrink-0"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                </div>

                {/* Description */}
                <p
                  className={`text-sm mb-4 flex-grow ${
                    isSelected ? 'text-gray-200' : 'text-gray-600'
                  }`}
                >
                  {model.description}
                </p>

                {/* Métriques */}
                <div
                  className={`flex items-center justify-between text-xs border-t pt-3 ${
                    isSelected ? 'border-gray-700' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-1">
                    <span
                      className={`font-medium ${
                        isSelected ? 'text-gray-300' : 'text-gray-500'
                      }`}
                    >
                      ⚡
                    </span>
                    <span className="font-medium">{model.speed}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span
                      className={`font-medium ${
                        isSelected ? 'text-gray-300' : 'text-gray-500'
                      }`}
                    >
                      💰
                    </span>
                    <span className="font-medium">{model.cost}</span>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Model info */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <svg
              className="w-5 h-5 text-blue-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="flex-1 text-sm text-blue-900">
            <p className="font-semibold mb-2">À propos des modèles</p>
            <div className="space-y-1.5 text-blue-800">
              <p>
                <strong className="font-semibold">Haiku 3.5</strong> :
                Ultra-rapide pour analyses immédiates et résumés concis
              </p>
              <p>
                <strong className="font-semibold">Sonnet 4.5</strong> :
                Intelligence supérieure pour analyses complexes (recommandé)
              </p>
              <p>
                <strong className="font-semibold">Opus 4.1</strong> : Le plus
                puissant pour analyses institutionnelles critiques
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
