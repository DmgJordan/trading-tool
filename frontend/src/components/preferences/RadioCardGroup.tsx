'use client';

interface RadioCardOption {
  value: string;
  label: string;
  description: string;
  icon?: string;
  color?: string;
  characteristics?: string[];
  badge?: string;
}

interface RadioCardGroupProps {
  options: RadioCardOption[];
  value: string;
  onChange: (value: string) => void;
  label: string;
  description?: string;
  error?: string;
  disabled?: boolean;
  columns?: 1 | 2 | 3;
  className?: string;
}

export default function RadioCardGroup({
  options,
  value,
  onChange,
  label,
  description,
  error,
  disabled = false,
  columns = 3,
  className = '',
}: RadioCardGroupProps) {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Label et description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
        {description && <p className="text-sm text-gray-500">{description}</p>}
      </div>

      {/* Options en cartes */}
      <div className={`grid gap-4 ${gridClasses[columns]}`}>
        {options.map(option => {
          const isSelected = value === option.value;
          const isDisabled = disabled;

          return (
            <div
              key={option.value}
              onClick={() => !isDisabled && onChange(option.value)}
              className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                isDisabled
                  ? 'cursor-not-allowed opacity-50 bg-gray-50 border-gray-200'
                  : isSelected
                    ? 'border-black bg-black text-white shadow-lg transform scale-[1.02]'
                    : 'border-gray-200 bg-white hover:border-gray-400 hover:shadow-md'
              }`}
            >
              {/* Badge */}
              {option.badge && (
                <div className="absolute top-2 right-2">
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${
                      isSelected
                        ? 'bg-white text-black'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {option.badge}
                  </span>
                </div>
              )}

              {/* Icône et titre */}
              <div className="flex items-center mb-3">
                {option.icon && (
                  <span className="text-2xl mr-3">{option.icon}</span>
                )}
                <h3
                  className={`text-lg font-semibold ${
                    isSelected ? 'text-white' : option.color || 'text-gray-900'
                  }`}
                >
                  {option.label}
                </h3>
              </div>

              {/* Description */}
              <p
                className={`text-sm mb-3 ${
                  isSelected ? 'text-gray-200' : 'text-gray-600'
                }`}
              >
                {option.description}
              </p>

              {/* Caractéristiques */}
              {option.characteristics && option.characteristics.length > 0 && (
                <div className="space-y-1">
                  {option.characteristics.map((characteristic, index) => (
                    <div
                      key={index}
                      className={`flex items-center text-xs ${
                        isSelected ? 'text-gray-300' : 'text-gray-500'
                      }`}
                    >
                      <svg
                        className={`w-3 h-3 mr-2 ${
                          isSelected ? 'text-white' : 'text-green-500'
                        }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {characteristic}
                    </div>
                  ))}
                </div>
              )}

              {/* Indicateur de sélection */}
              {isSelected && (
                <div className="absolute top-4 left-4">
                  <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-black"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                </div>
              )}

              {/* Input radio caché pour l'accessibilité */}
              <input
                type="radio"
                name={label}
                value={option.value}
                checked={isSelected}
                onChange={() => onChange(option.value)}
                disabled={isDisabled}
                className="sr-only"
              />
            </div>
          );
        })}
      </div>

      {/* Message d'erreur */}
      {error && (
        <p className="text-sm text-red-600 flex items-center">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
