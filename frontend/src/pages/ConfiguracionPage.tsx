import React from 'react';
import { Settings, User, Bell, Shield } from 'lucide-react';

export const ConfiguracionPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
        <p className="mt-1 text-sm text-gray-500">
          Configura tu cuenta y preferencias
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <User className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Perfil de Usuario</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="text-center py-8">
              <User className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">
                Configuración de perfil en desarrollo
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <Bell className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Notificaciones</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="text-center py-8">
              <Bell className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">
                Configuración de notificaciones en desarrollo
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <Shield className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Seguridad</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="text-center py-8">
              <Shield className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">
                Configuración de seguridad en desarrollo
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="flex items-center">
              <Settings className="h-5 w-5 text-primary-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Sistema</h3>
            </div>
          </div>
          <div className="card-content">
            <div className="text-center py-8">
              <Settings className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">
                Configuración del sistema en desarrollo
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};














