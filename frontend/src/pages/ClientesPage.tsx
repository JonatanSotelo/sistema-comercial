import React from 'react';
import { Users, Plus, Search, Download } from 'lucide-react';

export const ClientesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestiona tu base de clientes
          </p>
        </div>
        <button className="btn-primary btn-md">
          <Plus className="h-4 w-4 mr-2" />
          Nuevo Cliente
        </button>
      </div>

      <div className="card">
        <div className="card-content">
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Gestión de Clientes</h3>
            <p className="mt-1 text-sm text-gray-500">
              Funcionalidad en desarrollo
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};



