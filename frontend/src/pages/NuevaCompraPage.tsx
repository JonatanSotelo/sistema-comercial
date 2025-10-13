import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { CompraCreate, CompraItemCreate, Producto } from '@/types';

export const NuevaCompraPage: React.FC = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState<CompraItemCreate[]>([]);
  const [productos, setProductos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(false);
  const [newItem, setNewItem] = useState<CompraItemCreate>({
    producto_id: 0,
    cantidad: 0,
    costo_unitario: 0
  });

  const { register, handleSubmit, formState: { isSubmitting } } = useForm({
    defaultValues: {
      proveedor_id: 0,
      fecha: new Date().toISOString().slice(0, 10),
      observaciones: '',
    }
  });

  // Cargar productos al montar el componente
  useEffect(() => {
    const loadProductos = async () => {
      try {
        setLoading(true);
        const response = await api('/productos');
        setProductos(response.items || response.data || response);
      } catch (error) {
        console.error('Error cargando productos:', error);
        alert('Error al cargar la lista de productos');
      } finally {
        setLoading(false);
      }
    };

    loadProductos();
  }, []);

  const addItem = () => {
    if (newItem.producto_id > 0 && newItem.cantidad > 0 && newItem.costo_unitario > 0) {
      // Validar que el producto exista
      const producto = productos.find(p => p.id === newItem.producto_id);
      if (!producto) {
        alert('Producto no encontrado');
        return;
      }

      // Validar que no se haya agregado ya este producto
      if (items.some(item => item.producto_id === newItem.producto_id)) {
        alert('Este producto ya fue agregado. Modifique la cantidad en la lista de items.');
        return;
      }

      setItems([...items, { ...newItem }]);
      setNewItem({ producto_id: 0, cantidad: 0, costo_unitario: 0 });
    } else {
      alert('Complete todos los campos del item');
    }
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const onSubmit = async (data: any) => {
    if (items.length === 0) {
      alert('Debe agregar al menos un item');
      return;
    }

    try {
      const compraData: CompraCreate = {
        proveedor_id: Number(data.proveedor_id),
        fecha: data.fecha,
        observaciones: data.observaciones,
        items: items.map(item => ({
          ...item,
          cantidad: Number(item.cantidad),
          costo_unitario: Number(item.costo_unitario)
        }))
      };
      
      console.log('Enviando datos de compra:', compraData);
      console.log('Items:', items);
      
      await api('/compras', {
        method: 'POST',
        body: JSON.stringify(compraData)
      });
      navigate('/compras');
    } catch (e) {
      console.error('Error creando compra', e);
      console.error('Error details:', e.response?.data);
      alert('No se pudo crear la compra: ' + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Nueva Compra</h1>
      
      {/* Información básica */}
      <div className="card">
        <div className="card-content">
          <h2 className="text-lg font-semibold mb-4">Información de la Compra</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Proveedor ID</label>
                <input type="number" className="input" {...register('proveedor_id', { required: true, valueAsNumber: true })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Fecha</label>
                <input type="date" className="input" {...register('fecha', { required: true })} />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1">Observaciones</label>
                <textarea className="input" rows={3} {...register('observaciones')} />
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Items de la compra */}
      <div className="card">
        <div className="card-content">
          <h2 className="text-lg font-semibold mb-4">Items de la Compra</h2>
          
          {/* Formulario para agregar items */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium mb-1">Producto</label>
              <select 
                className="input" 
                value={newItem.producto_id}
                onChange={(e) => setNewItem({...newItem, producto_id: Number(e.target.value)})}
              >
                <option value={0}>Seleccionar producto...</option>
                {productos.map(producto => (
                  <option key={producto.id} value={producto.id}>
                    {producto.nombre} - Stock: {producto.stock} - Precio: ${producto.precio}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Cantidad</label>
              <input 
                type="number" 
                step="0.01"
                className="input" 
                value={newItem.cantidad}
                onChange={(e) => setNewItem({...newItem, cantidad: Number(e.target.value)})}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Costo Unitario</label>
              <input 
                type="number" 
                step="0.01"
                className="input" 
                value={newItem.costo_unitario}
                onChange={(e) => setNewItem({...newItem, costo_unitario: Number(e.target.value)})}
              />
            </div>
            <div className="flex items-end">
              <button type="button" className="btn-primary" onClick={addItem}>
                Agregar Item
              </button>
            </div>
          </div>

          {/* Lista de items */}
          {items.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-medium">Items agregados:</h3>
              {items.map((item, index) => {
                const producto = productos.find(p => p.id === item.producto_id);
                return (
                  <div key={index} className="flex items-center justify-between p-3 bg-white border rounded-lg">
                    <div className="flex space-x-4">
                      <span>Producto: {producto?.nombre || `ID: ${item.producto_id}`}</span>
                      <span>Cantidad: {item.cantidad}</span>
                      <span>Costo: ${item.costo_unitario}</span>
                      <span>Subtotal: ${(item.cantidad * item.costo_unitario).toFixed(2)}</span>
                    </div>
                    <button 
                      type="button" 
                      className="text-red-600 hover:text-red-800"
                      onClick={() => removeItem(index)}
                    >
                      Eliminar
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {/* Botones de acción */}
          <div className="flex justify-end gap-2 mt-6">
            <button type="button" className="btn-outline" onClick={() => navigate('/compras')}>
              Cancelar
            </button>
            <button 
              type="button" 
              className="btn-primary" 
              onClick={handleSubmit(onSubmit)}
              disabled={isSubmitting || items.length === 0}
            >
              {isSubmitting ? 'Guardando...' : 'Guardar Compra'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NuevaCompraPage;

