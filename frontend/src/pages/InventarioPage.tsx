import React, { useState, useEffect } from 'react';
import {
  Package,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Settings,
  RefreshCw,
  Plus,
  Filter,
  Download,
  Search,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import { apiService } from '@/services/api';
import { useNotificationContext } from '@/contexts/NotificationContext';
import {
  ResumenInventario,
  EstadisticasInventario,
  MovimientoStock,
  AlertaInventario,
  OrdenReabastecimiento,
  ConfiguracionInventario
} from '@/types';

const InventarioPage: React.FC = () => {
  const [resumen, setResumen] = useState<ResumenInventario | null>(null);
  const [estadisticas, setEstadisticas] = useState<EstadisticasInventario | null>(null);
  const [movimientos, setMovimientos] = useState<MovimientoStock[]>([]);
  const [alertas, setAlertas] = useState<AlertaInventario[]>([]);
  const [ordenes, setOrdenes] = useState<OrdenReabastecimiento[]>([]);
  const [configuraciones, setConfiguraciones] = useState<ConfiguracionInventario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'resumen' | 'movimientos' | 'alertas' | 'ordenes' | 'configuracion'>('resumen');
  const [filtros, setFiltros] = useState({
    fecha_desde: '',
    fecha_hasta: '',
    tipo: '',
    nivel: ''
  });
  const { showToast } = useNotificationContext();

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [resumenData, estadisticasData, movimientosData, alertasData, ordenesData, configuracionesData] = await Promise.all([
        apiService.getResumenInventario(),
        apiService.getEstadisticasInventario(),
        apiService.getMovimientosStock(filtros),
        apiService.getAlertasInventario(filtros),
        apiService.getOrdenesReabastecimiento(filtros),
        apiService.getConfiguracionesInventario(filtros)
      ]);

      setResumen(resumenData);
      setEstadisticas(estadisticasData);
      setMovimientos(movimientosData);
      setAlertas(alertasData);
      setOrdenes(ordenesData);
      setConfiguraciones(configuracionesData);
    } catch (err) {
      console.error('Error cargando datos de inventario:', err);
      setError('Error al cargar los datos del inventario');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filtros]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('es-AR').format(num);
  };

  const getNivelColor = (nivel: string) => {
    switch (nivel) {
      case 'critical':
        return 'text-red-600 bg-red-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'warning':
        return 'text-orange-600 bg-orange-100';
      case 'info':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getTipoColor = (tipo: string) => {
    switch (tipo) {
      case 'IN':
        return 'text-green-600 bg-green-100';
      case 'OUT':
        return 'text-red-600 bg-red-100';
      case 'AJUSTE':
        return 'text-blue-600 bg-blue-100';
      case 'TRANSFERENCIA':
        return 'text-purple-600 bg-purple-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'pendiente':
        return 'text-yellow-600 bg-yellow-100';
      case 'aprobada':
        return 'text-green-600 bg-green-100';
      case 'rechazada':
        return 'text-red-600 bg-red-100';
      case 'completada':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-primary-600" />
          <span className="text-lg text-gray-600">Cargando inventario...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Inventario</h1>
          <p className="text-gray-600">Control avanzado de stock y alertas</p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={loadData}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Actualizar</span>
          </button>
          <button
            onClick={() => {
              // Crear notificación de prueba
              showToast({
                id: Date.now(),
                tipo: 'inventario',
                titulo: 'Alerta de Inventario',
                mensaje: 'Se ha detectado un producto con stock bajo que requiere atención inmediata.',
                prioridad: 'alta',
                leida: false,
                procesada: false,
                fecha_creacion: new Date().toISOString()
              });
            }}
            className="flex items-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
          >
            <AlertTriangle className="h-4 w-4" />
            <span>Probar Alerta</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'resumen', label: 'Resumen', icon: BarChart3 },
            { id: 'movimientos', label: 'Movimientos', icon: TrendingUp },
            { id: 'alertas', label: 'Alertas', icon: AlertTriangle },
            { id: 'ordenes', label: 'Órdenes', icon: Package },
            { id: 'configuracion', label: 'Configuración', icon: Settings }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {tab.id === 'alertas' && alertas.length > 0 && (
                  <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                    {alertas.length}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Contenido de las tabs */}
      {activeTab === 'resumen' && resumen && (
        <div className="space-y-6">
          {/* Métricas principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Productos</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(resumen.total_productos)}</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <Package className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Stock Bajo</p>
                  <p className="text-2xl font-bold text-orange-600">{formatNumber(resumen.productos_stock_bajo)}</p>
                </div>
                <div className="p-3 bg-orange-100 rounded-full">
                  <AlertTriangle className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Valor Total</p>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(resumen.valor_total_inventario)}</p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <BarChart3 className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Alertas Pendientes</p>
                  <p className="text-2xl font-bold text-red-600">{formatNumber(resumen.alertas_pendientes)}</p>
                </div>
                <div className="p-3 bg-red-100 rounded-full">
                  <AlertCircle className="h-6 w-6 text-red-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Gráficos */}
          {estadisticas && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Movimientos por tipo */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Movimientos por Tipo</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(estadisticas.movimientos_por_tipo).map(([tipo, count]) => ({
                          name: tipo,
                          value: count
                        }))}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {Object.entries(estadisticas.movimientos_por_tipo).map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Valor por categoría */}
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Valor por Categoría</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={Object.entries(estadisticas.valor_inventario_por_categoria).map(([categoria, valor]) => ({
                      categoria,
                      valor
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="categoria" />
                      <YAxis />
                      <Tooltip formatter={(value) => [formatCurrency(Number(value)), 'Valor']} />
                      <Bar dataKey="valor" fill="#3B82F6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'movimientos' && (
        <div className="space-y-6">
          {/* Filtros */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Desde</label>
                <input
                  type="date"
                  value={filtros.fecha_desde}
                  onChange={(e) => setFiltros(prev => ({ ...prev, fecha_desde: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Hasta</label>
                <input
                  type="date"
                  value={filtros.fecha_hasta}
                  onChange={(e) => setFiltros(prev => ({ ...prev, fecha_hasta: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                <select
                  value={filtros.tipo}
                  onChange={(e) => setFiltros(prev => ({ ...prev, tipo: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Todos</option>
                  <option value="IN">Entrada</option>
                  <option value="OUT">Salida</option>
                  <option value="AJUSTE">Ajuste</option>
                  <option value="TRANSFERENCIA">Transferencia</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setFiltros({ fecha_desde: '', fecha_hasta: '', tipo: '', nivel: '' })}
                  className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                  Limpiar
                </button>
              </div>
            </div>
          </div>

          {/* Tabla de movimientos */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Movimientos de Stock</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cantidad</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Motivo</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Referencia</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {movimientos.map((movimiento) => (
                    <tr key={movimiento.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(movimiento.fecha).toLocaleDateString('es-AR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTipoColor(movimiento.tipo)}`}>
                          {movimiento.tipo}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatNumber(movimiento.cantidad)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {movimiento.motivo}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {movimiento.referencia || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button className="text-primary-600 hover:text-primary-900">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="text-gray-600 hover:text-gray-900">
                            <Edit className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'alertas' && (
        <div className="space-y-6">
          {/* Filtros */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nivel</label>
                <select
                  value={filtros.nivel}
                  onChange={(e) => setFiltros(prev => ({ ...prev, nivel: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Todos</option>
                  <option value="critical">Crítico</option>
                  <option value="error">Error</option>
                  <option value="warning">Advertencia</option>
                  <option value="info">Info</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setFiltros(prev => ({ ...prev, nivel: '' }))}
                  className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                >
                  Limpiar
                </button>
              </div>
            </div>
          </div>

          {/* Lista de alertas */}
          <div className="space-y-4">
            {alertas.map((alerta) => (
              <div key={alerta.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      {alerta.nivel === 'critical' || alerta.nivel === 'error' ? (
                        <AlertCircle className="h-5 w-5 text-red-500" />
                      ) : alerta.nivel === 'warning' ? (
                        <AlertTriangle className="h-5 w-5 text-orange-500" />
                      ) : (
                        <Clock className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getNivelColor(alerta.nivel)}`}>
                          {alerta.nivel}
                        </span>
                        <span className="text-sm text-gray-500">
                          {new Date(alerta.fecha_creacion).toLocaleDateString('es-AR')}
                        </span>
                      </div>
                      <h4 className="text-lg font-medium text-gray-900 mb-1">{alerta.tipo}</h4>
                      <p className="text-gray-600 mb-2">{alerta.mensaje}</p>
                      {alerta.accion_requerida && (
                        <p className="text-sm text-orange-600 font-medium">
                          Acción requerida: {alerta.accion_requerida}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {!alerta.resuelta && (
                      <button
                        onClick={() => {
                          // Implementar resolución de alerta
                          showToast({
                            id: Date.now(),
                            tipo: 'inventario',
                            titulo: 'Alerta Resuelta',
                            mensaje: 'La alerta ha sido marcada como resuelta.',
                            prioridad: 'normal',
                            leida: false,
                            procesada: false,
                            fecha_creacion: new Date().toISOString()
                          });
                        }}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                      >
                        Resolver
                      </button>
                    )}
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'ordenes' && (
        <div className="space-y-6">
          {/* Acciones */}
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Órdenes de Reabastecimiento</h3>
            <button
              onClick={() => {
                showToast({
                  id: Date.now(),
                  tipo: 'inventario',
                  titulo: 'Nueva Orden',
                  mensaje: 'Se ha generado una nueva orden de reabastecimiento.',
                  prioridad: 'normal',
                  leida: false,
                  procesada: false,
                  fecha_creacion: new Date().toISOString()
                });
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Plus className="h-4 w-4" />
              <span>Nueva Orden</span>
            </button>
          </div>

          {/* Lista de órdenes */}
          <div className="space-y-4">
            {ordenes.map((orden) => (
              <div key={orden.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">{orden.id}</h4>
                      <p className="text-sm text-gray-500">Producto ID: {orden.producto_id}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">Cantidad solicitada</p>
                      <p className="text-lg font-semibold text-gray-900">{formatNumber(orden.cantidad_solicitada)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getEstadoColor(orden.estado)}`}>
                      {orden.estado}
                    </span>
                    <div className="flex items-center space-x-2">
                      {orden.estado === 'pendiente' && (
                        <>
                          <button className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700">
                            Aprobar
                          </button>
                          <button className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700">
                            Rechazar
                          </button>
                        </>
                      )}
                      <button className="p-1 text-gray-400 hover:text-gray-600">
                        <Eye className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'configuracion' && (
        <div className="space-y-6">
          {/* Acciones */}
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Configuraciones de Inventario</h3>
            <button
              onClick={() => {
                showToast({
                  id: Date.now(),
                  tipo: 'inventario',
                  titulo: 'Configuración Actualizada',
                  mensaje: 'La configuración de inventario ha sido actualizada correctamente.',
                  prioridad: 'normal',
                  leida: false,
                  procesada: false,
                  fecha_creacion: new Date().toISOString()
                });
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              <Plus className="h-4 w-4" />
              <span>Nueva Configuración</span>
            </button>
          </div>

          {/* Lista de configuraciones */}
          <div className="space-y-4">
            {configuraciones.map((config) => (
              <div key={config.id} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">{config.id}</h4>
                      <p className="text-sm text-gray-500">Producto ID: {config.producto_id}</p>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <p className="text-sm text-gray-500">Stock Mínimo</p>
                        <p className="text-lg font-semibold text-gray-900">{formatNumber(config.stock_minimo)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Stock Máximo</p>
                        <p className="text-lg font-semibold text-gray-900">{formatNumber(config.stock_maximo)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Punto Reorden</p>
                        <p className="text-lg font-semibold text-gray-900">{formatNumber(config.punto_reorden)}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      config.activo ? 'text-green-600 bg-green-100' : 'text-gray-600 bg-gray-100'
                    }`}>
                      {config.activo ? 'Activo' : 'Inactivo'}
                    </span>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <Edit className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InventarioPage;