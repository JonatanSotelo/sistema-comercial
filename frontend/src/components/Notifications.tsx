import React, { useState, useEffect } from 'react';
import { X, Bell, AlertTriangle, Info, CheckCircle, AlertCircle } from 'lucide-react';
import { useQuery } from 'react-query';
import apiService from '@/services/api';
import { clsx } from 'clsx';

interface Notification {
  id: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  prioridad: 'baja' | 'normal' | 'alta' | 'urgente';
  leida: boolean;
  fecha_creacion: string;
}

export const Notifications: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Obtener notificaciones
  const { data: notificationsData, refetch } = useQuery(
    'notifications',
    () => apiService.getNotificaciones({ per_page: 10 }),
    {
      refetchInterval: 30000, // Refrescar cada 30 segundos
    }
  );

  useEffect(() => {
    if (notificationsData) {
      setNotifications(notificationsData);
    }
  }, [notificationsData]);

  const unreadCount = notifications.filter(n => !n.leida).length;

  const getPriorityIcon = (prioridad: string) => {
    switch (prioridad) {
      case 'urgente':
        return <AlertCircle className="h-4 w-4 text-error-500" />;
      case 'alta':
        return <AlertTriangle className="h-4 w-4 text-warning-500" />;
      case 'normal':
        return <Info className="h-4 w-4 text-primary-500" />;
      case 'baja':
        return <CheckCircle className="h-4 w-4 text-success-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (prioridad: string) => {
    switch (prioridad) {
      case 'urgente':
        return 'border-l-error-500 bg-error-50';
      case 'alta':
        return 'border-l-warning-500 bg-warning-50';
      case 'normal':
        return 'border-l-primary-500 bg-primary-50';
      case 'baja':
        return 'border-l-success-500 bg-success-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await apiService.marcarNotificacionComoLeida(id);
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, leida: true } : n)
      );
    } catch (error) {
      console.error('Error marcando notificación como leída:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter(n => !n.leida);
      await Promise.all(
        unreadNotifications.map(n => apiService.marcarNotificacionComoLeida(n.id))
      );
      setNotifications(prev => 
        prev.map(n => ({ ...n, leida: true }))
      );
    } catch (error) {
      console.error('Error marcando todas las notificaciones como leídas:', error);
    }
  };

  return (
    <>
      {/* Botón de notificaciones */}
      <button
        type="button"
        className="relative rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="sr-only">Ver notificaciones</span>
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-error-500 text-xs text-white">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Panel de notificaciones */}
      {isOpen && (
        <div className="absolute right-0 z-50 mt-2 w-80 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Notificaciones</h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-sm text-primary-600 hover:text-primary-500"
                >
                  Marcar todas como leídas
                </button>
              )}
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <Bell className="mx-auto h-8 w-8 text-gray-400" />
                <p className="mt-2 text-sm">No hay notificaciones</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={clsx(
                      'p-4 border-l-4 hover:bg-gray-50 cursor-pointer',
                      getPriorityColor(notification.prioridad),
                      !notification.leida && 'bg-blue-50'
                    )}
                    onClick={() => markAsRead(notification.id)}
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        {getPriorityIcon(notification.prioridad)}
                      </div>
                      <div className="ml-3 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {notification.titulo}
                          </p>
                          {!notification.leida && (
                            <div className="h-2 w-2 rounded-full bg-primary-500" />
                          )}
                        </div>
                        <p className="mt-1 text-sm text-gray-600">
                          {notification.mensaje}
                        </p>
                        <p className="mt-1 text-xs text-gray-500">
                          {new Date(notification.fecha_creacion).toLocaleString('es-ES')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-200">
            <button
              onClick={() => setIsOpen(false)}
              className="w-full text-center text-sm text-primary-600 hover:text-primary-500"
            >
              Ver todas las notificaciones
            </button>
          </div>
        </div>
      )}

      {/* Overlay para cerrar al hacer clic fuera */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};



