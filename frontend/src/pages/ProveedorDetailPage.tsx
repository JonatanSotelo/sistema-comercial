import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Trash2, Phone, Mail, MapPin, Calendar, Building } from 'lucide-react';
import { Proveedor } from '@/types';
import { api } from '@/lib/api';

export const ProveedorDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [proveedor, setProveedor] = useState<Proveedor | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    if (id) {
      loadProveedor(parseInt(id));
    }
  }, [id]);

  const loadProveedor = async (proveedorId: number) => {
    try {
      setLoading(true);
      const proveedorData = await api(`/proveedores/${proveedorId}`);
      setProveedor(proveedorData);
    } catch (err) {
      setError('Error al cargar el proveedor');
      console.error('Error loading proveedor:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!proveedor) return;
    
    try {
      await api(`/proveedores/${proveedor.id}`, { method: 'DELETE' });
      navigate('/proveedores');
    } catch (err) {
      setError('Error al eliminar el proveedor');
      console.error('Error deleting proveedor:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !proveedor) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Proveedor no encontrado</h3>
        <p className="text-gray-500 mb-4">{error || 'El proveedor solicitado no existe.'}</p>
        <button
          onClick={() => navigate('/proveedores')}
          className="btn-primary btn-md"
        >
          Volver a Proveedores
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/proveedores')}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{proveedor.nombre}</h1>
            <p className="text-sm text-gray-500">ID: {proveedor.id}</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => navigate(`/proveedores/${proveedor.id}/editar`)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <Edit className="h-4 w-4 mr-2" />
            Editar
          </button>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="inline-flex items-center px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Eliminar
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Información del proveedor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Información principal */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Información de la Empresa</h3>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="flex items-center">
                <Building className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-500">Nombre</p>
                  <p className="text-sm text-gray-900">{proveedor.nombre}</p>
                </div>
              </div>
              
              {proveedor.email && (
                <div className="flex items-center">
                  <Mail className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Email</p>
                    <p className="text-sm text-gray-900">{proveedor.email}</p>
                  </div>
                </div>
              )}
              
              {proveedor.telefono && (
                <div className="flex items-center">
                  <Phone className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Teléfono</p>
                    <p className="text-sm text-gray-900">{proveedor.telefono}</p>
                  </div>
                </div>
              )}
              
              {proveedor.direccion && (
                <div className="flex items-center">
                  <MapPin className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-500">Dirección</p>
                    <p className="text-sm text-gray-900">{proveedor.direccion}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Información adicional */}
        <div className="space-y-6">
          {/* Estado */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Estado</h3>
            </div>
            <div className="px-6 py-4">
              <div className="flex items-center">
                <div className={`h-3 w-3 rounded-full mr-3 ${
                  proveedor.activo ? 'bg-green-400' : 'bg-red-400'
                }`}></div>
                <span className="text-sm font-medium text-gray-900">
                  {proveedor.activo ? 'Activo' : 'Inactivo'}
                </span>
              </div>
            </div>
          </div>

          {/* Fechas */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Fechas</h3>
            </div>
            <div className="px-6 py-4 space-y-3">
              <div className="flex items-center">
                <Calendar className="h-4 w-4 text-gray-400 mr-3" />
                <div>
                  <p className="text-xs font-medium text-gray-500">Creado</p>
                  <p className="text-sm text-gray-900">
                    {new Date(proveedor.created_at).toLocaleDateString('es-ES')}
                  </p>
                </div>
              </div>
              
              {proveedor.updated_at && (
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 text-gray-400 mr-3" />
                  <div>
                    <p className="text-xs font-medium text-gray-500">Actualizado</p>
                    <p className="text-sm text-gray-900">
                      {new Date(proveedor.updated_at).toLocaleDateString('es-ES')}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal de confirmación de eliminación */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Confirmar eliminación
              </h3>
              <p className="text-sm text-gray-500 mb-6">
                ¿Estás seguro de que quieres eliminar al proveedor "{proveedor.nombre}"? 
                Esta acción no se puede deshacer.
              </p>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleDelete}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};




