'use client';

import { ReactNode } from 'react';

interface QuickAction {
  id: string;
  label: string;
  icon?: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning';
  disabled?: boolean;
  onClick: () => void;
}

interface QuickActionsProps {
  actions: QuickAction[];
  className?: string;
}

export default function QuickActions({
  actions,
  className = '',
}: QuickActionsProps) {
  const getButtonClasses = (
    variant: QuickAction['variant'] = 'secondary',
    disabled = false
  ) => {
    const baseClasses =
      'inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 border-2';

    if (disabled) {
      return `${baseClasses} bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed`;
    }

    switch (variant) {
      case 'primary':
        return `${baseClasses} bg-black text-white border-black hover:bg-white hover:text-black`;
      case 'success':
        return `${baseClasses} bg-green-600 text-white border-green-600 hover:bg-white hover:text-green-600`;
      case 'warning':
        return `${baseClasses} bg-orange-600 text-white border-orange-600 hover:bg-white hover:text-orange-600`;
      case 'secondary':
      default:
        return `${baseClasses} bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:border-gray-400`;
    }
  };

  return (
    <div className={`flex flex-wrap gap-3 ${className}`}>
      {actions.map(action => (
        <button
          key={action.id}
          onClick={action.onClick}
          disabled={action.disabled}
          className={getButtonClasses(action.variant, action.disabled)}
        >
          {action.icon && <span className="text-base">{action.icon}</span>}
          {action.label}
        </button>
      ))}
    </div>
  );
}
