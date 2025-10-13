import React, { useState, useEffect } from 'react';
import { X, Package, TrendingUp, TrendingDown, RotateCcw, ArrowRightLeft } from 'lucide-react';
import { api } from '@/lib/api';
import { MovimientoStock, Producto } from '@/types';

interface MovimientoStockModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const MovimientoStockModal: React.FC<MovimientoStockModalProps> = ({
  isOpen,
  onClose,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    producto_id: '',
    tipo: 'IN' as 'IN' | 'OUT' | 'AJUSTE' | 'TRANSFERENCIA',
    cantidad: '',
    motivo: '',
    referencia: '',
    observaciones: ''
  });
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadProductos();
    }
  }, [isOpen]);

  const loadProductos = async () => {
    try {
      const response = await api('/productos?per_page=100');
      setProductos(response.items || response.data || response);
    } catch (err) {
      console.error('Error cargando productos:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await api('/movimientos-stock', {
        method: 'POST',
        body: JSON.stringify({
          ...formData,
          cantidad: parseFloat(formData.cantidad),
          producto_id: parseInt(formData.producto_id)
        })
      });
      
      onSuccess();
      onClose();
      resetForm();
    } catch (err) {
      console.error('Error creando movimiento:', err);
      setError('Error al crear el movimiento de stock');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      producto_id: '',
      tipo: 'IN',
      cantidad: '',
      motivo: '',
      referencia: '',
      observaciones: ''
    });
    setError(null);
  };

  const getTipoIcon = (tipo: string) => {
    switch (tipo) {
      case 'IN': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'OUT': return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'AJUSTE': return <RotateCcw className="h-4 w-4 text-blue-600" />;
      case 'TRANSFERENCIA': return <ArrowRightLeft className="h-4 w-4 text-purple-600" />;
      default: return <Package className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'IN': return 'text-green-600 bg-green-100';
      case 'OUT': return 'text-red-600 bg-red-100';
      case 'AJUSTE': return 'text-blue-600 bg-blue-100';
      case 'TRANSFERENCIA': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Package className="h-5 w-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">Nuevo Movimiento de Stock</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Producto */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Producto *
            </label>
            <select
              value={formData.producto_id}
              onChange={(e) => setFormData({ ...formData, producto_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="">Seleccionar producto</option>
              {productos.map((producto) => (
                <option key={producto.id} value={producto.id}>
                  {producto.nombre} - Stock: {producto.stock}
                </option>
              ))}
            </select>
          </div>

          {/* Tipo de movimiento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Movimiento *
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { value: 'IN', label: 'Entrada', icon: TrendingUp },
                { value: 'OUT', label: 'Salida', icon: TrendingDown },
                { value: 'AJUSTE', label: 'Ajuste', icon: RotateCcw },
                { value: 'TRANSFERENCIA', label: 'Transferencia', icon: ArrowRightLeft }
              ].map((tipo) => {
                const Icon = tipo.icon;
                return (
                  <button
                    key={tipo.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, tipo: tipo.value as any })}
                    className={`flex items-center space-x-2 p-3 rounded-md border-2 transition-colors ${
                      formData.tipo === tipo.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="text-sm font-medium">{tipo.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Cantidad */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cantidad *
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.cantidad}
                onChange={(e) => setFormData({ ...formData, cantidad: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="0.00"
                required
              />
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <span className={`text-sm font-medium ${getTipoColor(formData.tipo)}`}>
                  {formData.tipo === 'IN' ? '+' : formData.tipo === 'OUT' ? '-' : '±'}
                </span>
              </div>
            </div>
          </div>

          {/* Motivo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Motivo *
            </label>
            <select
              value={formData.motivo}
              onChange={(e) => setFormData({ ...formData, motivo: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="">Seleccionar motivo</option>
              {formData.tipo === 'IN' && (
                <>
                  <option value="Compra">Compra</option>
                  <option value="Devolución">Devolución</option>
                  <option value="Transferencia entrada">Transferencia entrada</option>
                  <option value="Ajuste positivo">Ajuste positivo</option>
                </>
              )}
              {formData.tipo === 'OUT' && (
                <>
                  <option value="Venta">Venta</option>
                  <option value="Transferencia salida">Transferencia salida</option>
                  <option value="Pérdida">Pérdida</option>
                  <option value="Ajuste negativo">Ajuste negativo</option>
                </>
              )}
              {formData.tipo === 'AJUSTE' && (
                <>
                  <option value="Inventario físico">Inventario físico</option>
                  <option value="Corrección de error">Corrección de error</option>
                  <option value="Reclasificación">Reclasificación</option>
                </>
              )}
              {formData.tipo === 'TRANSFERENCIA' && (
                <>
                  <option value="Entre sucursales">Entre sucursales</option>
                  <option value="Entre almacenes">Entre almacenes</option>
                  <option value="Préstamo">Préstamo</option>
                </>
              )}
            </select>
          </div>

          {/* Referencia */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Referencia
            </label>
            <input
              type="text"
              value={formData.referencia}
              onChange={(e) => setFormData({ ...formData, referencia: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Número de factura, orden, etc."
            />
          </div>

          {/* Observaciones */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Observaciones
            </label>
            <textarea
              value={formData.observaciones}
              onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              rows={3}
              placeholder="Notas adicionales..."
            />
          </div>

          {/* Botones */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Creando...' : 'Crear Movimiento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};







