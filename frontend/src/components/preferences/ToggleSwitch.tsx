'use client';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  description?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'red' | 'purple';
  className?: string;
}

export default function ToggleSwitch({
  checked,
  onChange,
  label,
  description,
  disabled = false,
  size = 'md',
  color = 'blue',
  className = '',
}: ToggleSwitchProps) {
  const sizeClasses = {
    sm: {
      switch: 'w-8 h-4',
      thumb: 'w-3 h-3',
      translate: checked ? 'translate-x-4' : 'translate-x-0.5',
      text: 'text-sm',
    },
    md: {
      switch: 'w-11 h-6',
      thumb: 'w-5 h-5',
      translate: checked ? 'translate-x-5' : 'translate-x-0.5',
      text: 'text-base',
    },
    lg: {
      switch: 'w-14 h-7',
      thumb: 'w-6 h-6',
      translate: checked ? 'translate-x-7' : 'translate-x-0.5',
      text: 'text-lg',
    },
  };

  const colorClasses = {
    blue: checked ? 'bg-blue-600' : 'bg-gray-300',
    green: checked ? 'bg-green-600' : 'bg-gray-300',
    red: checked ? 'bg-red-600' : 'bg-gray-300',
    purple: checked ? 'bg-purple-600' : 'bg-gray-300',
  };

  const currentSize = sizeClasses[size];
  const currentColor = disabled ? 'bg-gray-300' : colorClasses[color];

  const handleClick = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div className={`flex items-center justify-between ${className}`}>
      <div className="flex-1">
        <label
          className={`font-medium cursor-pointer ${currentSize.text} ${
            disabled ? 'text-gray-400' : 'text-gray-900'
          }`}
          onClick={handleClick}
        >
          {label}
        </label>
        {description && (
          <p
            className={`text-sm ${disabled ? 'text-gray-400' : 'text-gray-500'} mt-1`}
          >
            {description}
          </p>
        )}
      </div>

      {/* Switch */}
      <div
        className={`relative inline-flex items-center ${currentSize.switch} ${currentColor} rounded-full transition-colors duration-200 ease-in-out cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
          disabled ? 'cursor-not-allowed opacity-50' : ''
        }`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="switch"
        aria-checked={checked}
        aria-disabled={disabled}
        tabIndex={disabled ? -1 : 0}
      >
        {/* Thumb */}
        <span
          className={`${currentSize.thumb} ${currentSize.translate} inline-block bg-white rounded-full shadow-lg transform transition-transform duration-200 ease-in-out`}
        />

        {/* Icônes optionnelles */}
        {size !== 'sm' && (
          <>
            {/* Icône ON */}
            <span
              className={`absolute left-1 ${checked ? 'opacity-100' : 'opacity-0'} transition-opacity duration-200`}
            >
              <svg
                className="w-3 h-3 text-white"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </span>

            {/* Icône OFF */}
            <span
              className={`absolute right-1 ${!checked ? 'opacity-100' : 'opacity-0'} transition-opacity duration-200`}
            >
              <svg
                className="w-3 h-3 text-gray-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </span>
          </>
        )}
      </div>
    </div>
  );
}

// Composant groupe de toggles pour les notifications
interface ToggleGroupProps {
  title: string;
  description?: string;
  toggles: Array<{
    key: string;
    label: string;
    description?: string;
    checked: boolean;
    disabled?: boolean;
  }>;
  onChange: (key: string, checked: boolean) => void;
  className?: string;
}

export function ToggleGroup({
  title,
  description,
  toggles,
  onChange,
  className = '',
}: ToggleGroupProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {description && (
          <p className="text-sm text-gray-500 mt-1">{description}</p>
        )}
      </div>

      <div className="space-y-3">
        {toggles.map(toggle => (
          <ToggleSwitch
            key={toggle.key}
            checked={toggle.checked}
            onChange={checked => onChange(toggle.key, checked)}
            label={toggle.label}
            description={toggle.description}
            disabled={toggle.disabled}
          />
        ))}
      </div>
    </div>
  );
}
