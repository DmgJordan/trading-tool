'use client';

import { useEffect } from 'react';
import { getStatusColor, getStatusIcon, type Status } from '@/utils/ui';

export interface ToastProps {
  id: string;
  message: string;
  type: Status;
  duration?: number;
  onClose: (id: string) => void;
}

export default function Toast({
  id,
  message,
  type,
  duration = 5000,
  onClose,
}: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const colorClasses = getStatusColor(type);
  const icon = getStatusIcon(type);

  return (
    <div
      className={`
        flex items-center gap-3 p-4 rounded-lg border-2 shadow-lg
        min-w-[300px] max-w-[500px] animate-slide-in-right
        ${colorClasses}
      `}
      role="alert"
    >
      <span className="text-2xl flex-shrink-0">{icon}</span>

      <p className="flex-1 font-medium">{message}</p>

      <button
        onClick={() => onClose(id)}
        className="text-current hover:opacity-70 transition-opacity flex-shrink-0"
        aria-label="Fermer"
      >
        ✕
      </button>
    </div>
  );
}

/**
 * Container pour les toasts empilés
 */
export function ToastContainer({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none"
      aria-live="polite"
    >
      <div className="pointer-events-auto">{children}</div>
    </div>
  );
}
