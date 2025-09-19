import React, { useState, useEffect, useRef } from 'react';
import {
  Bell,
  X,
  Check,
  AlertTriangle,
  Info,
  CheckCircle,
  AlertCircle,
  Clock,
  Trash2,
  Settings,
  Volume2,
  VolumeX
} from 'lucide-react';
import { apiService } from '@/services/api';
import { Notificacion } from '@/types';
import { clsx } from 'clsx';

interface NotificationsProps {
  isOpen: boolean;
  onClose: () => void;
}

export const Notifications: React.FC<NotificationsProps> = ({ isOpen, onClose }) => {
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [loading, setLoading] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'urgent'>('all');
  const [showSettings, setShowSettings] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const loadNotificaciones = async () => {
    try {
      setLoading(true);
      const data = await apiService.getNotificaciones({ per_page: 50 });
      setNotificaciones(data);
    } catch (error) {
      console.error('Error cargando notificaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadNotificaciones();
    }
  }, [isOpen]);

  // Actualizar notificaciones cada 30 segundos
  useEffect(() => {
    const interval = setInterval(loadNotificaciones, 30000);
    return () => clearInterval(interval);
  }, []);

  const playNotificationSound = () => {
    if (soundEnabled && audioRef.current) {
      audioRef.current.play().catch(console.error);
    }
  };

  const marcarComoLeida = async (id: number) => {
    try {
      await apiService.marcarNotificacionComoLeida(id);
      setNotificaciones(prev =>
        prev.map(notif =>
          notif.id === id ? { ...notif, estado: 'LEIDA', fecha_lectura: new Date().toISOString() } : notif
        )
      );
    } catch (error) {
      console.error('Error marcando notificación como leída:', error);
    }
  };

  const marcarTodasComoLeidas = async () => {
    try {
      await apiService.marcarTodasComoLeidas();
      setNotificaciones(prev =>
        prev.map(notif => ({ ...notif, estado: 'LEIDA', fecha_lectura: new Date().toISOString() }))
      );
    } catch (error) {
      console.error('Error marcando todas como leídas:', error);
    }
  };

  const eliminarNotificacion = async (id: number) => {
    try {
      // Aquí deberías implementar el endpoint de eliminación si existe
      setNotificaciones(prev => prev.filter(notif => notif.id !== id));
    } catch (error) {
      console.error('Error eliminando notificación:', error);
    }
  };

  const getPriorityIcon = (esUrgente: boolean) => {
    if (esUrgente) {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    return <Info className="h-4 w-4 text-blue-500" />;
  };

  const getPriorityColor = (esUrgente: boolean) => {
    if (esUrgente) {
      return 'border-l-red-500 bg-red-50';
    }
    return 'border-l-blue-500 bg-blue-50';
  };

  const filteredNotificaciones = notificaciones.filter(notif => {
    if (filter === 'unread') return notif.estado !== 'LEIDA';
    if (filter === 'urgent') return notif.es_urgente === true;
    return true;
  });

  const unreadCount = notificaciones.filter(notif => notif.estado !== 'LEIDA').length;
  const urgentCount = notificaciones.filter(notif => notif.es_urgente === true).length;

  if (!isOpen) return null;

  return (
    <>
      {/* Audio para notificaciones */}
      <audio ref={audioRef} preload="auto">
        <source src="/sounds/notification.mp3" type="audio/mpeg" />
        <source src="/sounds/notification.wav" type="audio/wav" />
      </audio>

      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Panel de notificaciones */}
      <div className="fixed right-4 top-16 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Bell className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Notificaciones</h3>
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                {unreadCount}
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <Settings className="h-4 w-4" />
            </button>
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Configuración rápida */}
        {showSettings && (
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Sonido</span>
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className="flex items-center space-x-2"
              >
                {soundEnabled ? (
                  <Volume2 className="h-4 w-4 text-green-500" />
                ) : (
                  <VolumeX className="h-4 w-4 text-gray-400" />
                )}
                <span className="text-sm text-gray-600">
                  {soundEnabled ? 'Activado' : 'Desactivado'}
                </span>
              </button>
            </div>
          </div>
        )}

        {/* Filtros */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={clsx(
                'px-3 py-1 text-xs rounded-full',
                filter === 'all'
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
            >
              Todas ({notificaciones.length})
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={clsx(
                'px-3 py-1 text-xs rounded-full',
                filter === 'unread'
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
            >
              No leídas ({unreadCount})
            </button>
            <button
              onClick={() => setFilter('urgent')}
              className={clsx(
                'px-3 py-1 text-xs rounded-full',
                filter === 'urgent'
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
            >
              Urgentes ({urgentCount})
            </button>
          </div>
        </div>

        {/* Acciones */}
        {unreadCount > 0 && (
          <div className="p-4 border-b border-gray-200">
            <button
              onClick={marcarTodasComoLeidas}
              className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700"
            >
              <Check className="h-4 w-4" />
              <span>Marcar todas como leídas</span>
            </button>
          </div>
        )}

        {/* Lista de notificaciones */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            </div>
          ) : filteredNotificaciones.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-gray-500">
              <Bell className="h-12 w-12 text-gray-300 mb-4" />
              <p className="text-sm">No hay notificaciones</p>
              <p className="text-xs text-gray-400">
                {filter === 'unread' ? 'No hay notificaciones sin leer' :
                 filter === 'urgent' ? 'No hay notificaciones urgentes' :
                 'No hay notificaciones disponibles'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredNotificaciones.map((notif) => (
                <div
                  key={notif.id}
                  className={clsx(
                    'p-4 border-l-4 transition-colors hover:bg-gray-50',
                    getPriorityColor(notif.es_urgente || false),
                    notif.estado !== 'LEIDA' && 'bg-blue-50'
                  )}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getPriorityIcon(notif.es_urgente || false)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className={clsx(
                          'text-sm font-medium',
                          notif.estado !== 'LEIDA' ? 'text-gray-900' : 'text-gray-600'
                        )}>
                          {notif.titulo}
                        </p>
                        <div className="flex items-center space-x-1">
                          {notif.estado !== 'LEIDA' && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                          <span className="text-xs text-gray-400">
                            {new Date(notif.fecha_creacion).toLocaleTimeString('es-AR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {notif.mensaje}
                      </p>
                      {notif.accion_requerida && (
                        <p className="text-xs text-orange-600 mt-1 font-medium">
                          Acción requerida: {notif.accion_requerida}
                        </p>
                      )}
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center space-x-2">
                          <span className={clsx(
                            'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                            notif.es_urgente ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
                          )}>
                            {notif.es_urgente ? 'Urgente' : 'Normal'}
                          </span>
                          <span className="text-xs text-gray-400">
                            {new Date(notif.fecha_creacion).toLocaleDateString('es-AR')}
                          </span>
                        </div>
                        <div className="flex items-center space-x-1">
                          {notif.estado !== 'LEIDA' && (
                            <button
                              onClick={() => marcarComoLeida(notif.id)}
                              className="p-1 text-gray-400 hover:text-green-600"
                              title="Marcar como leída"
                            >
                              <Check className="h-3 w-3" />
                            </button>
                          )}
                          <button
                            onClick={() => eliminarNotificacion(notif.id)}
                            className="p-1 text-gray-400 hover:text-red-600"
                            title="Eliminar"
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={loadNotificaciones}
            className="w-full text-sm text-primary-600 hover:text-primary-700"
          >
            Actualizar notificaciones
          </button>
        </div>
      </div>
    </>
  );
};