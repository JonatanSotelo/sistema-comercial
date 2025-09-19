import React from 'react';
import { NotificationToast } from './NotificationToast';
import { useNotificationContext } from '@/contexts/NotificationContext';

export const NotificationToasts: React.FC = () => {
  const { activeToasts, removeToast, marcarComoLeida, soundEnabled } = useNotificationContext();

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {activeToasts.map((notificacion) => (
        <NotificationToast
          key={notificacion.id}
          notificacion={notificacion}
          onClose={() => removeToast(notificacion.id)}
          onMarkAsRead={marcarComoLeida}
          soundEnabled={soundEnabled}
          position="top-right"
        />
      ))}
    </div>
  );
};