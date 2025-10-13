import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { Notificacion } from '@/types';
import { useAuth } from '@/contexts/AuthContext';

export const useNotifications = () => {
  const { user } = useAuth();
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const loadNotificaciones = useCallback(async () => {
    if (!user) {
      setNotificaciones([]);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      const data = await api('/notificaciones?per_page=100');
      setNotificaciones(data);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error cargando notificaciones:', err);
      setError('Error al cargar notificaciones');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const marcarComoLeida = useCallback(async (id: number) => {
    try {
      await api(`/notificaciones/${id}/leer`, { method: 'PATCH' });
      setNotificaciones(prev =>
        prev.map(notif =>
          notif.id === id
            ? { ...notif, estado: 'LEIDA', fecha_lectura: new Date().toISOString() }
            : notif
        )
      );
    } catch (err) {
      console.error('Error marcando notificación como leída:', err);
    }
  }, []);

  const marcarTodasComoLeidas = useCallback(async () => {
    try {
      await api('/notificaciones/marcar-todas-leidas', { method: 'PATCH' });
      setNotificaciones(prev =>
        prev.map(notif => ({
          ...notif,
          estado: 'LEIDA',
          fecha_lectura: new Date().toISOString()
        }))
      );
    } catch (err) {
      console.error('Error marcando todas como leídas:', err);
    }
  }, []);

  const eliminarNotificacion = useCallback((id: number) => {
    setNotificaciones(prev => prev.filter(notif => notif.id !== id));
  }, []);

  const agregarNotificacion = useCallback((notificacion: Notificacion) => {
    setNotificaciones(prev => [notificacion, ...prev]);
  }, []);

  // Cargar notificaciones al montar el componente
  useEffect(() => {
    loadNotificaciones();
  }, [loadNotificaciones]);

  // Actualizar notificaciones cada 30 segundos solo si el usuario está autenticado
  useEffect(() => {
    if (!user) return;
    
    const interval = setInterval(loadNotificaciones, 30000);
    return () => clearInterval(interval);
  }, [loadNotificaciones, user]);

  // Estadísticas
  const unreadCount = notificaciones.filter(notif => notif.estado !== 'LEIDA').length;
  const urgentCount = notificaciones.filter(notif => notif.es_urgente === true).length;
  const recentCount = notificaciones.filter(notif => {
    const fecha = new Date(notif.fecha_creacion);
    const ahora = new Date();
    const diffHours = (ahora.getTime() - fecha.getTime()) / (1000 * 60 * 60);
    return diffHours <= 24; // Últimas 24 horas
  }).length;

  return {
    notificaciones,
    loading,
    error,
    lastUpdate,
    unreadCount,
    urgentCount,
    recentCount,
    loadNotificaciones,
    marcarComoLeida,
    marcarTodasComoLeidas,
    eliminarNotificacion,
    agregarNotificacion,
  };
};