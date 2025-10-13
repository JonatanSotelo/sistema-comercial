import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Package, 
  DollarSign, 
  AlertTriangle,
  RefreshCw,
  Bell,
  ShoppingCart,
  TrendingDown,
  Activity
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';
import { api } from '@/lib/api';
import { useNotificationContext } from '@/contexts/NotificationContext';
import { DashboardCompleto, EstadisticasVentas, Notificacion } from '@/types';

const DashboardPage: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardCompleto | null>(null);
  const [estadisticasVentas, setEstadisticasVentas] = useState<EstadisticasVentas | null>(null);
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const { showToast } = useNotificationContext();

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [dashboard, ventas, notifs] = await Promise.all([
        api('/dashboard/completo'),
        api('/dashboard/ventas/estadisticas'),
        api('/notificaciones/?per_page=10')
      ]);
      
      setDashboardData(dashboard);
      setEstadisticasVentas(ventas);
      setNotificaciones(notifs);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Error cargando dashboard:', err);
      setError('Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    
    // Actualizar cada 30 segundos
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

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

  const getGrowthColor = (growth: number) => {
    if (growth > 0) return 'text-green-600';
    if (growth < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getGrowthIcon = (growth: number) => {
    if (growth > 0) return <TrendingUp className="h-4 w-4" />;
    if (growth < 0) return <TrendingDown className="h-4 w-4" />;
    return <Activity className="h-4 w-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-6 w-6 animate-spin text-primary-600" />
          <span className="text-lg text-gray-600">Cargando dashboard...</span>
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
            onClick={loadDashboardData}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) return null;

  // Datos para gráficos
  const ventasPorPeriodo = dashboardData.ventas_por_periodo.map(item => ({
    periodo: new Date(item.periodo).toLocaleDateString('es-AR', { month: 'short', day: 'numeric' }),
    ventas: item.cantidad_ventas,
    monto: item.monto_total
  }));

  const productosMasVendidos = dashboardData.productos_mas_vendidos.slice(0, 5).map(item => ({
    name: item.producto_nombre,
    value: item.cantidad_vendida,
    monto: item.monto_total
  }));

  const clientesTop = dashboardData.clientes_top.slice(0, 5).map(item => ({
    name: item.cliente_nombre,
    ventas: item.cantidad_ventas,
    monto: item.monto_total
  }));

  const tendencias = dashboardData.tendencias.map(item => ({
    fecha: new Date(item.fecha).toLocaleDateString('es-AR', { month: 'short', day: 'numeric' }),
    ventas: item.ventas,
    monto: item.monto,
    crecimiento: item.crecimiento_diario
  }));

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Ejecutivo</h1>
          <p className="text-gray-600">
            Última actualización: {lastUpdate.toLocaleTimeString('es-AR')}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={loadDashboardData}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Actualizar</span>
          </button>
          <button
            onClick={() => {
              // Crear notificación de prueba
              const testNotification: Notificacion = {
                id: Date.now(),
                tipo: 'test',
                titulo: 'Notificación de Prueba',
                mensaje: 'Esta es una notificación de prueba del sistema de notificaciones.',
                prioridad: 'normal',
                leida: false,
                procesada: false,
                fecha_creacion: new Date().toISOString()
              };
              showToast(testNotification);
            }}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Bell className="h-4 w-4" />
            <span>Probar Notificación</span>
          </button>
        </div>
      </div>

      {/* Métricas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Ventas */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Ventas</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(dashboardData.resumen_ventas.total_ventas)}
              </p>
              <p className="text-sm text-gray-500">
                Hoy: {formatNumber(dashboardData.resumen_ventas.ventas_hoy)}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <ShoppingCart className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        {/* Total Monto */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Facturado</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(dashboardData.resumen_ventas.total_monto)}
              </p>
              <p className="text-sm text-gray-500">
                Hoy: {formatCurrency(dashboardData.resumen_ventas.monto_hoy)}
              </p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        {/* Ticket Promedio */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ticket Promedio</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(dashboardData.resumen_ventas.promedio_venta)}
              </p>
              <div className="flex items-center space-x-1 mt-1">
                {getGrowthIcon(dashboardData.metricas.crecimiento_ventas)}
                <span className={`text-sm ${getGrowthColor(dashboardData.metricas.crecimiento_ventas)}`}>
                  {dashboardData.metricas.crecimiento_ventas > 0 ? '+' : ''}{dashboardData.metricas.crecimiento_ventas}%
                </span>
              </div>
            </div>
            <div className="p-3 bg-yellow-100 rounded-full">
              <BarChart3 className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        {/* Clientes Activos */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Clientes Activos</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(dashboardData.metricas.clientes_activos)}
              </p>
              <p className="text-sm text-gray-500">
                Productos: {formatNumber(dashboardData.metricas.productos_activos)}
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos principales */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de ventas por período */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ventas por Período</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={ventasPorPeriodo}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="periodo" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'monto' ? formatCurrency(Number(value)) : formatNumber(Number(value)),
                    name === 'monto' ? 'Monto' : 'Ventas'
                  ]}
                />
                <Area 
                  type="monotone" 
                  dataKey="monto" 
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Productos más vendidos */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Productos Más Vendidos</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={productosMasVendidos} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip 
                  formatter={(value) => [formatNumber(Number(value)), 'Cantidad']}
                />
                <Bar dataKey="value" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Tendencias y clientes top */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendencias de crecimiento */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tendencias de Crecimiento</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={tendencias}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="fecha" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'monto' ? formatCurrency(Number(value)) : formatNumber(Number(value)),
                    name === 'monto' ? 'Monto' : 'Ventas'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="ventas" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="monto" 
                  stroke="#10B981" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Clientes top */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Clientes</h3>
          <div className="space-y-4">
            {clientesTop.map((cliente, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-medium text-primary-600">{index + 1}</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{cliente.name}</p>
                    <p className="text-sm text-gray-500">{cliente.ventas} ventas</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{formatCurrency(cliente.monto)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alertas de stock bajo */}
      {dashboardData.stock_bajo.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            <h3 className="text-lg font-semibold text-gray-900">Alertas de Stock Bajo</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {dashboardData.stock_bajo.map((item, index) => (
              <div key={index} className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{item.producto_nombre}</p>
                    <p className="text-sm text-gray-600">
                      Stock: {item.stock_actual} / {item.stock_minimo}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-orange-600">
                      {item.porcentaje}%
                    </p>
                    <p className="text-xs text-gray-500">
                      Faltan: {Math.abs(item.diferencia)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notificaciones recientes */}
      {notificaciones.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Notificaciones Recientes</h3>
          <div className="space-y-3">
            {notificaciones.map((notif) => (
              <div key={notif.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  notif.prioridad === 'urgente' ? 'bg-red-500' :
                  notif.prioridad === 'alta' ? 'bg-orange-500' :
                  notif.prioridad === 'normal' ? 'bg-blue-500' : 'bg-gray-500'
                }`} />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{notif.titulo}</p>
                  <p className="text-sm text-gray-600">{notif.mensaje}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(notif.fecha_creacion).toLocaleString('es-AR')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;