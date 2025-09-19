import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  X,
  Volume2,
  VolumeX
} from 'lucide-react';
import { Notificacion } from '@/types';
import { clsx } from 'clsx';

interface NotificationToastProps {
  notificacion: Notificacion;
  onClose: () => void;
  onMarkAsRead: (id: number) => void;
  soundEnabled?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export const NotificationToast: React.FC<NotificationToastProps> = ({
  notificacion,
  onClose,
  onMarkAsRead,
  soundEnabled = true,
  position = 'top-right'
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);
  const [soundPlayed, setSoundPlayed] = useState(false);

  useEffect(() => {
    // Mostrar la notificación con animación
    const timer = setTimeout(() => setIsVisible(true), 100);

    // Auto-cerrar después de 5 segundos
    const autoCloseTimer = setTimeout(() => {
      handleClose();
    }, 5000);

    // Reproducir sonido si está habilitado
    if (soundEnabled && !soundPlayed) {
      playNotificationSound();
      setSoundPlayed(true);
    }

    return () => {
      clearTimeout(timer);
      clearTimeout(autoCloseTimer);
    };
  }, [soundEnabled, soundPlayed]);

  const playNotificationSound = () => {
    try {
      // Crear un audio context para generar un sonido de notificación
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);

      gainNode.gain.setValueAtTime(0, audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.1, audioContext.currentTime + 0.01);
      gainNode.gain.linearRampToValueAtTime(0, audioContext.currentTime + 0.3);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
    } catch (error) {
      console.log('No se pudo reproducir el sonido de notificación');
    }
  };

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onClose();
    }, 300);
  };

  const handleMarkAsRead = () => {
    onMarkAsRead(notificacion.id);
    handleClose();
  };

  const getPriorityIcon = (prioridad: string) => {
    switch (prioridad) {
      case 'urgente':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'alta':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'normal':
        return <Info className="h-5 w-5 text-blue-500" />;
      case 'baja':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <Info className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPriorityColor = (prioridad: string) => {
    switch (prioridad) {
      case 'urgente':
        return 'border-l-red-500 bg-red-50 shadow-red-100';
      case 'alta':
        return 'border-l-orange-500 bg-orange-50 shadow-orange-100';
      case 'normal':
        return 'border-l-blue-500 bg-blue-50 shadow-blue-100';
      case 'baja':
        return 'border-l-green-500 bg-green-50 shadow-green-100';
      default:
        return 'border-l-gray-500 bg-gray-50 shadow-gray-100';
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4';
      case 'top-right':
        return 'top-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'bottom-right':
        return 'bottom-4 right-4';
      default:
        return 'top-4 right-4';
    }
  };

  if (!isVisible) return null;

  return (
    <div
      className={clsx(
        'fixed z-50 w-80 max-w-sm transform transition-all duration-300 ease-in-out',
        getPositionClasses(),
        isLeaving ? 'opacity-0 scale-95 translate-y-2' : 'opacity-100 scale-100 translate-y-0'
      )}
    >
      <div
        className={clsx(
          'border-l-4 rounded-lg shadow-lg p-4 cursor-pointer hover:shadow-xl transition-shadow',
          getPriorityColor(notificacion.prioridad)
        )}
        onClick={handleMarkAsRead}
      >
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {getPriorityIcon(notificacion.prioridad)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-900 truncate">
                {notificacion.titulo}
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleClose();
                }}
                className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {notificacion.mensaje}
            </p>
            {notificacion.accion_requerida && (
              <p className="text-xs text-orange-600 mt-1 font-medium">
                {notificacion.accion_requerida}
              </p>
            )}
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-gray-500">
                {new Date(notificacion.fecha_creacion).toLocaleTimeString('es-AR', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
              <div className="flex items-center space-x-2">
                <span className={clsx(
                  'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                  notificacion.prioridad === 'urgente' ? 'bg-red-100 text-red-800' :
                  notificacion.prioridad === 'alta' ? 'bg-orange-100 text-orange-800' :
                  notificacion.prioridad === 'normal' ? 'bg-blue-100 text-blue-800' :
                  'bg-green-100 text-green-800'
                )}>
                  {notificacion.prioridad}
                </span>
                {!notificacion.leida && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};