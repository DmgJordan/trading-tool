import { useState, useCallback } from 'react';
import type { Status } from '@/shared/lib/ui';

export interface Notification {
  id: string;
  message: string;
  type: Status;
  duration?: number;
}

/**
 * Hook pour gérer les notifications toast
 * Usage: const { notify, notifications, removeNotification } = useNotifications();
 */
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const notify = useCallback(
    (message: string, type: Status = 'info', duration: number = 5000) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      const notification: Notification = {
        id,
        message,
        type,
        duration,
      };

      setNotifications(prev => [...prev, notification]);

      return id;
    },
    []
  );

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Helpers pour types spécifiques
  const success = useCallback(
    (message: string, duration?: number) =>
      notify(message, 'success', duration),
    [notify]
  );

  const error = useCallback(
    (message: string, duration?: number) => notify(message, 'error', duration),
    [notify]
  );

  const warning = useCallback(
    (message: string, duration?: number) =>
      notify(message, 'warning', duration),
    [notify]
  );

  const info = useCallback(
    (message: string, duration?: number) => notify(message, 'info', duration),
    [notify]
  );

  return {
    notifications,
    notify,
    removeNotification,
    success,
    error,
    warning,
    info,
  };
};
