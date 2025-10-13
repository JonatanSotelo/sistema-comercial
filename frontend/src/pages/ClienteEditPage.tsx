import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, X } from 'lucide-react';
import { Cliente, ClienteUpdate } from '@/types';
import { api } from '@/lib/api';

export const ClienteEditPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState<Cliente | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<ClienteUpdate>({
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
    activo: true
  });

  useEffect(() => {
    if (id) {
      loadCliente(parseInt(id));
    }
  }, [id]);

  const loadCliente = async (clienteId: number) => {
    try {
      setLoading(true);
      const clienteData = await api(`/clientes/${clienteId}`);
      setCliente(clienteData);
      setFormData({
        nombre: clienteData.nombre,
        email: clienteData.email || '',
        telefono: clienteData.telefono || '',
        direccion: clienteData.direccion || '',
        activo: clienteData.activo
      });
    } catch (err) {
      setError('Error al cargar el cliente');
      console.error('Error loading cliente:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cliente) return;

    try {
      setSaving(true);
      await api(`/clientes/${cliente.id}`, {
        method: 'PATCH',
        body: JSON.stringify(formData)
      });
      navigate(`/clientes/${cliente.id}`);
    } catch (err) {
      setError('Error al actualizar el cliente');
      console.error('Error updating cliente:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !cliente) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
        <p className="text-gray-500 mb-4">{error || 'No se pudo cargar el cliente.'}</p>
        <button
          onClick={() => navigate('/clientes')}
          className="btn-primary btn-md"
        >
          Volver a Clientes
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
            onClick={() => navigate(`/clientes/${cliente.id}`)}
            className="p-2 text-gray-400 hover:text-gray-600"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Editar Cliente</h1>
            <p className="text-sm text-gray-500">{cliente.nombre}</p>
          </div>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => navigate(`/clientes/${cliente.id}`)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <X className="h-4 w-4 mr-2" />
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Formulario */}
      <div className="bg-white shadow rounded-lg">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Nombre */}
            <div className="md:col-span-2">
              <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-2">
                Nombre *
              </label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                required
                value={formData.nombre}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Teléfono */}
            <div>
              <label htmlFor="telefono" className="block text-sm font-medium text-gray-700 mb-2">
                Teléfono
              </label>
              <input
                type="tel"
                id="telefono"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Dirección */}
            <div className="md:col-span-2">
              <label htmlFor="direccion" className="block text-sm font-medium text-gray-700 mb-2">
                Dirección
              </label>
              <textarea
                id="direccion"
                name="direccion"
                rows={3}
                value={formData.direccion}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Estado */}
            <div className="md:col-span-2">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="activo"
                  name="activo"
                  checked={formData.activo}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="activo" className="ml-2 block text-sm text-gray-900">
                  Cliente activo
                </label>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};




