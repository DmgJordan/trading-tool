import { getStatusColor, getStatusIcon } from '@/shared/lib/ui';
import type { StatusBadgeProps } from '@/lib/types/components/ui';

export default function StatusBadge({
  status,
  label,
  showIcon = true,
  size = 'medium',
  className = '',
}: StatusBadgeProps) {
  const colorClasses = getStatusColor(status);
  const icon = getStatusIcon(status);

  const sizeClasses = {
    small: 'text-xs px-2 py-1',
    medium: 'text-sm px-3 py-1.5',
    large: 'text-base px-4 py-2',
  };

  const iconSizes = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg',
  };

  return (
    <span
      className={`
        inline-flex items-center gap-2 rounded-full border-2 font-medium
        ${sizeClasses[size]}
        ${colorClasses}
        ${className}
      `}
    >
      {showIcon && <span className={iconSizes[size]}>{icon}</span>}
      {label && <span>{label}</span>}
    </span>
  );
}
