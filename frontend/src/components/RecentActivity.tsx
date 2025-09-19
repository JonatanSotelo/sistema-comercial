import React from 'react';
import { 
  ShoppingCart, 
  ShoppingBag, 
  UserPlus, 
  Package, 
  TrendingUp, 
  AlertTriangle,
  Clock
} from 'lucide-react';
import { clsx } from 'clsx';

interface ActivityItem {
  id: string;
  type: 'sale' | 'purchase' | 'customer' | 'product' | 'metric' | 'alert';
  title: string;
  description: string;
  timestamp: string;
  value?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
}

export const RecentActivity: React.FC = () => {
  // Datos de ejemplo - en una aplicación real vendrían de la API
  const activities: ActivityItem[] = [
    {
      id: '1',
      type: 'sale',
      title: 'Nueva Venta',
      description: 'Venta #1234 por $1,250.00',
      timestamp: 'Hace 5 minutos',
      value: '+$1,250',
      status: 'success',
    },
    {
      id: '2',
      type: 'customer',
      title: 'Cliente Registrado',
      description: 'Juan Pérez se registró como nuevo cliente',
      timestamp: 'Hace 15 minutos',
      status: 'info',
    },
    {
      id: '3',
      type: 'alert',
      title: 'Stock Bajo',
      description: 'Producto "Laptop Dell" tiene stock bajo',
      timestamp: 'Hace 30 minutos',
      status: 'warning',
    },
    {
      id: '4',
      type: 'purchase',
      title: 'Nueva Compra',
      description: 'Compra #5678 por $850.00',
      timestamp: 'Hace 1 hora',
      value: '-$850',
      status: 'info',
    },
    {
      id: '5',
      type: 'metric',
      title: 'Métrica Actualizada',
      description: 'Ventas mensuales: +12.5% vs mes anterior',
      timestamp: 'Hace 2 horas',
      value: '+12.5%',
      status: 'success',
    },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'sale':
        return <ShoppingCart className="h-4 w-4" />;
      case 'purchase':
        return <ShoppingBag className="h-4 w-4" />;
      case 'customer':
        return <UserPlus className="h-4 w-4" />;
      case 'product':
        return <Package className="h-4 w-4" />;
      case 'metric':
        return <TrendingUp className="h-4 w-4" />;
      case 'alert':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success':
        return 'text-success-600 bg-success-100';
      case 'warning':
        return 'text-warning-600 bg-warning-100';
      case 'error':
        return 'text-error-600 bg-error-100';
      case 'info':
        return 'text-primary-600 bg-primary-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">Actividad Reciente</h3>
        <p className="text-sm text-gray-500">Últimas actividades del sistema</p>
      </div>
      <div className="card-content">
        <div className="flow-root">
          <ul className="-mb-8">
            {activities.map((activity, activityIdx) => (
              <li key={activity.id}>
                <div className="relative pb-8">
                  {activityIdx !== activities.length - 1 ? (
                    <span
                      className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                      aria-hidden="true"
                    />
                  ) : null}
                  <div className="relative flex space-x-3">
                    <div>
                      <span
                        className={clsx(
                          'flex h-8 w-8 items-center justify-center rounded-full',
                          getStatusColor(activity.status)
                        )}
                      >
                        {getActivityIcon(activity.type)}
                      </span>
                    </div>
                    <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {activity.title}
                        </p>
                        <p className="text-sm text-gray-500">
                          {activity.description}
                        </p>
                      </div>
                      <div className="whitespace-nowrap text-right text-sm text-gray-500">
                        <div className="flex items-center space-x-2">
                          {activity.value && (
                            <span
                              className={clsx(
                                'inline-flex items-center rounded-full px-2 py-1 text-xs font-medium',
                                activity.status === 'success' && 'bg-success-100 text-success-800',
                                activity.status === 'warning' && 'bg-warning-100 text-warning-800',
                                activity.status === 'error' && 'bg-error-100 text-error-800',
                                activity.status === 'info' && 'bg-primary-100 text-primary-800',
                                !activity.status && 'bg-gray-100 text-gray-800'
                              )}
                            >
                              {activity.value}
                            </span>
                          )}
                          <span>{activity.timestamp}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="card-footer">
        <button className="text-sm text-primary-600 hover:text-primary-500 font-medium">
          Ver toda la actividad
        </button>
      </div>
    </div>
  );
};














