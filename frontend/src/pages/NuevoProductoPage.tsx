import React from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import apiService from '@/services/api';
import { FormularioProducto } from '@/types';

export const NuevoProductoPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormularioProducto>({
    defaultValues: {
      nombre: '',
      descripcion: '',
      codigo: '',
      categoria: '',
      precio: 0,
      costo: 0,
      stock: 0,
      stock_minimo: 0,
      activo: true,
      isSubmitting: false,
      errors: {},
    } as any
  });

  const onSubmit = async (data: FormularioProducto) => {
    try {
      await apiService.createProducto({
        nombre: data.nombre,
        descripcion: data.descripcion,
        codigo: data.codigo,
        categoria: data.categoria,
        precio: Number(data.precio),
        costo: Number(data.costo),
        stock: Number(data.stock),
        stock_minimo: Number(data.stock_minimo),
        activo: !!data.activo,
      });
      navigate('/productos');
    } catch (e) {
      console.error('Error creando producto', e);
      alert('No se pudo crear el producto');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Nuevo Producto</h1>
      </div>

      <div className="card">
        <div className="card-content">
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input className="input" {...register('nombre', { required: true })} />
              {errors.nombre && <p className="text-sm text-red-600">Requerido</p>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Código</label>
              <input className="input" {...register('codigo', { required: true })} />
              {errors.codigo && <p className="text-sm text-red-600">Requerido</p>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Categoría</label>
              <input className="input" {...register('categoria', { required: true })} />
              {errors.categoria && <p className="text-sm text-red-600">Requerido</p>}
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-1">Descripción</label>
              <textarea className="input" rows={3} {...register('descripcion')} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Precio</label>
              <input type="number" step="0.01" className="input" {...register('precio', { required: true, valueAsNumber: true })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Costo</label>
              <input type="number" step="0.01" className="input" {...register('costo', { required: true, valueAsNumber: true })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Stock</label>
              <input type="number" className="input" {...register('stock', { required: true, valueAsNumber: true })} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Stock mínimo</label>
              <input type="number" className="input" {...register('stock_minimo', { required: true, valueAsNumber: true })} />
            </div>
            <div className="md:col-span-2 flex items-center gap-2">
              <input id="activo" type="checkbox" {...register('activo')} />
              <label htmlFor="activo">Activo</label>
            </div>
            <div className="md:col-span-2 flex justify-end gap-2">
              <button type="button" className="btn-outline" onClick={() => navigate('/productos')}>Cancelar</button>
              <button type="submit" className="btn-primary" disabled={isSubmitting}>Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default NuevoProductoPage;

