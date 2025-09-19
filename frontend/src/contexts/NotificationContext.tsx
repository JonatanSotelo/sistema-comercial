import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Notificacion } from '@/types';
import { useNotifications } from '@/hooks/useNotifications';

interface NotificationContextType {
  // Estado
  notificaciones: Notificacion[];
  unreadCount: number;
  urgentCount: number;
  recentCount: number;
  loading: boolean;
  error: string | null;
  soundEnabled: boolean;
  toastEnabled: boolean;

  // Acciones
  loadNotificaciones: () => Promise<void>;
  marcarComoLeida: (id: number) => Promise<void>;
  marcarTodasComoLeidas: () => Promise<void>;
  eliminarNotificacion: (id: number) => void;
  agregarNotificacion: (notificacion: Notificacion) => void;
  toggleSound: () => void;
  toggleToast: () => void;

  // Notificaciones toast
  showToast: (notificacion: Notificacion) => void;
  activeToasts: Notificacion[];
  removeToast: (id: number) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const {
    notificaciones,
    loading,
    error,
    unreadCount,
    urgentCount,
    recentCount,
    loadNotificaciones,
    marcarComoLeida,
    marcarTodasComoLeidas,
    eliminarNotificacion,
    agregarNotificacion,
  } = useNotifications();

  const [soundEnabled, setSoundEnabled] = useState(() => {
    const saved = localStorage.getItem('notification_sound_enabled');
    return saved ? JSON.parse(saved) : true;
  });

  const [toastEnabled, setToastEnabled] = useState(() => {
    const saved = localStorage.getItem('notification_toast_enabled');
    return saved ? JSON.parse(saved) : true;
  });

  const [activeToasts, setActiveToasts] = useState<Notificacion[]>([]);

  // Guardar preferencias en localStorage
  useEffect(() => {
    localStorage.setItem('notification_sound_enabled', JSON.stringify(soundEnabled));
  }, [soundEnabled]);

  useEffect(() => {
    localStorage.setItem('notification_toast_enabled', JSON.stringify(toastEnabled));
  }, [toastEnabled]);

  const toggleSound = useCallback(() => {
    setSoundEnabled(prev => !prev);
  }, []);

  const toggleToast = useCallback(() => {
    setToastEnabled(prev => !prev);
  }, []);

  const showToast = useCallback((notificacion: Notificacion) => {
    if (!toastEnabled) return;
    
    setActiveToasts(prev => {
      // Evitar duplicados
      if (prev.some(toast => toast.id === notificacion.id)) {
        return prev;
      }
      return [notificacion, ...prev];
    });
  }, [toastEnabled]);

  const removeToast = useCallback((id: number) => {
    setActiveToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  // Auto-remover toasts después de 5 segundos
  useEffect(() => {
    const timer = setTimeout(() => {
      setActiveToasts(prev => prev.slice(0, 3)); // Mantener solo los 3 más recientes
    }, 5000);

    return () => clearTimeout(timer);
  }, [activeToasts]);

  const value: NotificationContextType = {
    notificaciones,
    unreadCount,
    urgentCount,
    recentCount,
    loading,
    error,
    soundEnabled,
    toastEnabled,
    loadNotificaciones,
    marcarComoLeida,
    marcarTodasComoLeidas,
    eliminarNotificacion,
    agregarNotificacion,
    toggleSound,
    toggleToast,
    showToast,
    activeToasts,
    removeToast,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotificationContext = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotificationContext must be used within a NotificationProvider');
  }
  return context;
};