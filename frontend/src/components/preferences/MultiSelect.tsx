'use client';

import { useState, useRef, useEffect } from 'react';

export interface MultiSelectOption {
  value: string;
  label: string;
  description?: string;
  category?: string;
  isPopular?: boolean;
}

interface MultiSelectProps {
  options: MultiSelectOption[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label: string;
  description?: string;
  placeholder?: string;
  maxItems?: number;
  error?: string;
  disabled?: boolean;
  allowCustom?: boolean;
  customValidator?: (value: string) => { isValid: boolean; error?: string };
  className?: string;
}

export default function MultiSelect({
  options,
  selected,
  onChange,
  label,
  description,
  placeholder = 'Rechercher...',
  maxItems,
  error,
  disabled = false,
  allowCustom = false,
  customValidator,
  className = '',
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [customInput, setCustomInput] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fermer le dropdown en cliquant à l'extérieur
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setShowCustomInput(false);
        setCustomInput('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus sur l'input quand le dropdown s'ouvre
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Filtrer les options selon la recherche
  const filteredOptions = options.filter(
    option =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      option.value.toLowerCase().includes(searchTerm.toLowerCase()) ||
      option.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Grouper par catégorie
  const groupedOptions = filteredOptions.reduce(
    (groups, option) => {
      const category = option.category || 'Autres';
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(option);
      return groups;
    },
    {} as Record<string, MultiSelectOption[]>
  );

  const handleToggleOption = (value: string) => {
    if (disabled) return;

    if (selected.includes(value)) {
      onChange(selected.filter(item => item !== value));
    } else {
      if (maxItems && selected.length >= maxItems) {
        return; // Ne pas ajouter si limite atteinte
      }
      onChange([...selected, value]);
    }
  };

  const handleRemoveItem = (value: string) => {
    if (!disabled) {
      onChange(selected.filter(item => item !== value));
    }
  };

  const handleAddCustom = () => {
    if (!customInput.trim() || selected.includes(customInput.toUpperCase()))
      return;

    const validation = customValidator?.(customInput) || { isValid: true };
    if (!validation.isValid) return;

    if (maxItems && selected.length >= maxItems) return;

    onChange([...selected, customInput.toUpperCase()]);
    setCustomInput('');
    setShowCustomInput(false);
    setSearchTerm('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && showCustomInput) {
      e.preventDefault();
      handleAddCustom();
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setShowCustomInput(false);
    }
  };

  const selectedOptions = selected.map(
    value => options.find(opt => opt.value === value) || { value, label: value }
  );

  const canAddMore = !maxItems || selected.length < maxItems;

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Label */}
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {maxItems && (
            <span className="text-gray-500 ml-1">
              ({selected.length}/{maxItems})
            </span>
          )}
        </label>
        {description && (
          <p className="text-xs text-gray-500 mt-1">{description}</p>
        )}
      </div>

      {/* Selected items */}
      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {selectedOptions.map(option => (
            <span
              key={option.value}
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border-2 ${
                disabled
                  ? 'bg-gray-100 text-gray-400 border-gray-200'
                  : 'bg-white text-black border-black hover:bg-gray-50'
              }`}
            >
              {option.label}
              {!disabled && (
                <button
                  type="button"
                  onClick={() => handleRemoveItem(option.value)}
                  className="ml-2 text-gray-500 hover:text-red-500 transition-colors"
                >
                  ×
                </button>
              )}
            </span>
          ))}
        </div>
      )}

      {/* Dropdown trigger */}
      <div
        className={`relative border-2 rounded-lg cursor-pointer transition-colors ${
          disabled
            ? 'bg-gray-100 border-gray-200 cursor-not-allowed'
            : isOpen
              ? 'border-black bg-white'
              : 'border-gray-300 hover:border-gray-400 bg-white'
        }`}
        onClick={() => !disabled && canAddMore && setIsOpen(!isOpen)}
      >
        <input
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          placeholder={
            canAddMore ? placeholder : `Maximum ${maxItems} éléments atteint`
          }
          disabled={disabled || !canAddMore}
          className="w-full px-4 py-3 bg-transparent outline-none disabled:cursor-not-allowed"
          onFocus={() => !disabled && canAddMore && setIsOpen(true)}
        />
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
          {isOpen ? '▲' : '▼'}
        </div>
      </div>

      {/* Dropdown */}
      {isOpen && canAddMore && (
        <div className="absolute z-50 w-full mt-1 bg-white border-2 border-black rounded-lg shadow-lg max-h-64 overflow-y-auto">
          {/* Bouton pour ajouter custom */}
          {allowCustom && searchTerm && !showCustomInput && (
            <button
              type="button"
              onClick={() => setShowCustomInput(true)}
              className="w-full px-4 py-2 text-left hover:bg-gray-50 border-b border-gray-200 text-blue-600"
            >
              + Ajouter &quot;{searchTerm.toUpperCase()}&quot;
            </button>
          )}

          {/* Input custom */}
          {showCustomInput && (
            <div className="p-3 border-b border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={customInput}
                  onChange={e => setCustomInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Saisir un nouvel élément..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded text-sm"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={handleAddCustom}
                  disabled={!customInput.trim()}
                  className="px-3 py-2 bg-black text-white rounded text-sm disabled:bg-gray-300"
                >
                  +
                </button>
              </div>
            </div>
          )}

          {/* Options groupées */}
          {Object.entries(groupedOptions).map(([category, categoryOptions]) => (
            <div key={category}>
              {Object.keys(groupedOptions).length > 1 && (
                <div className="px-4 py-2 text-xs font-semibold text-gray-600 bg-gray-50 border-b border-gray-200">
                  {category}
                </div>
              )}
              {categoryOptions.map(option => {
                const isSelected = selected.includes(option.value);
                return (
                  <div
                    key={option.value}
                    onClick={() => handleToggleOption(option.value)}
                    className={`px-4 py-3 cursor-pointer transition-colors ${
                      isSelected ? 'bg-black text-white' : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-medium">
                          {option.label}
                          {option.isPopular && (
                            <span className="ml-2 text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                              Populaire
                            </span>
                          )}
                        </div>
                        {option.description && (
                          <div
                            className={`text-xs ${isSelected ? 'text-gray-300' : 'text-gray-500'}`}
                          >
                            {option.description}
                          </div>
                        )}
                      </div>
                      {isSelected && (
                        <svg
                          className="w-5 h-5"
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
                );
              })}
            </div>
          ))}

          {filteredOptions.length === 0 && (
            <div className="px-4 py-3 text-gray-500 text-center">
              Aucun résultat trouvé
            </div>
          )}
        </div>
      )}

      {/* Message d'erreur */}
      {error && (
        <p className="text-sm text-red-600 mt-2 flex items-center">
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
