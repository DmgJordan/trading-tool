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
    id: 'claude-3-7-sonnet-20250219',
    name: 'Claude Sonnet 3.7',
    description: 'Réflexion étendue et équilibré',
    icon: '💭',
    speed: 'Rapide',
    cost: 'Modéré',
  },
  {
    id: 'claude-sonnet-4-20250514',
    name: 'Claude Sonnet 4',
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
    <div className={`space-y-4 ${className}`}>
      <div>
        <h3 className="text-lg font-medium text-black mb-2">Modèle Claude</h3>
        <p className="text-sm text-gray-600">
          Choisissez le modèle Claude pour votre analyse trading
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {claudeModels.map(model => {
          const isSelected = selectedModel === model.id;

          return (
            <button
              key={model.id}
              onClick={() => onModelChange(model.id)}
              className={`relative p-4 rounded-xl border-2 text-left transition-all duration-200 ${
                isSelected
                  ? 'border-black bg-black text-white'
                  : 'border-gray-200 bg-white text-gray-900 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {/* Recommended badge */}
              {model.recommended && (
                <div className="absolute -top-2 -right-2">
                  <div
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      isSelected ? 'bg-white text-black' : 'bg-black text-white'
                    }`}
                  >
                    Recommandé
                  </div>
                </div>
              )}

              <div className="flex items-start space-x-3">
                <div className="text-2xl">{model.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-semibold truncate">{model.name}</h4>
                    {isSelected && (
                      <svg
                        className="w-4 h-4 flex-shrink-0"
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
                  <p
                    className={`text-sm mb-3 ${
                      isSelected ? 'text-gray-200' : 'text-gray-600'
                    }`}
                  >
                    {model.description}
                  </p>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span
                        className={`font-medium ${
                          isSelected ? 'text-gray-300' : 'text-gray-500'
                        }`}
                      >
                        Vitesse:
                      </span>
                      <br />
                      <span>{model.speed}</span>
                    </div>
                    <div>
                      <span
                        className={`font-medium ${
                          isSelected ? 'text-gray-300' : 'text-gray-500'
                        }`}
                      >
                        Coût:
                      </span>
                      <br />
                      <span>{model.cost}</span>
                    </div>
                  </div>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Model info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <svg
            className="w-4 h-4 text-blue-600 mt-0.5"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">À propos des modèles Claude</p>
            <p>
              <strong>Haiku 3.5</strong> : Ultra-rapide pour analyses immédiates
              et résumés concis.
              <br />
              <strong>Sonnet 3.7</strong> : Réflexion étendue avec excellent
              équilibre performance/prix.
              <br />
              <strong>Sonnet 4</strong> : Intelligence supérieure pour analyses
              complexes, recommandé.
              <br />
              <strong>Opus 4.1</strong> : Le plus puissant pour analyses
              institutionnelles critiques.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
