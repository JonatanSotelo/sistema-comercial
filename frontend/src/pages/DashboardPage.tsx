import React from 'react';
import { useQuery } from 'react-query';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Package, 
  ShoppingCart, 
  DollarSign,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Calendar
} from 'lucide-react';
import apiService from '@/services/api';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { MetricCard } from '@/components/MetricCard';
import { ChartCard } from '@/components/ChartCard';
import { AlertCard } from '@/components/AlertCard';
import { RecentActivity } from '@/components/RecentActivity';

export const DashboardPage: React.FC = () => {
  // Obtener datos del dashboard
  const { data: dashboardData, isLoading: isLoadingDashboard } = useQuery(
    'dashboard-executive',
    () => apiService.getDashboardEjecutivo(),
    {
      refetchInterval: 30000, // Refrescar cada 30 segundos
    }
  );

  const { data: dashboardStats, isLoading: isLoadingStats } = useQuery(
    'dashboard-stats',
    () => apiService.getDashboard(),
    {
      refetchInterval: 60000, // Refrescar cada minuto
    }
  );

  if (isLoadingDashboard || isLoadingStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Cargando dashboard..." />
      </div>
    );
  }

  const data = dashboardData || {
    ingresos_mes: 0,
    ingresos_anio: 0,
    crecimiento_ingresos: 0,
    margen_bruto: 0,
    margen_neto: 0,
    ventas_mes: 0,
    clientes_activos: 0,
    productos_vendidos: 0,
    ticket_promedio: 0,
    crecimiento_ventas: 0,
    crecimiento_clientes: 0,
    alertas_criticas: [],
    alertas_importantes: [],
    tendencia_ingresos: 'estable',
    tendencia_ventas: 'estable',
    tendencia_clientes: 'estable',
    recomendaciones: [],
    fecha_actualizacion: new Date().toISOString(),
  };

  const stats = dashboardStats || {
    total_ventas: 0,
    total_compras: 0,
    total_clientes: 0,
    total_proveedores: 0,
    total_productos: 0,
    ventas_mes_actual: 0,
    compras_mes_actual: 0,
    clientes_nuevos_mes: 0,
    productos_agotados: 0,
    ticket_promedio: 0,
    margen_promedio: 0,
  };

  // Métricas principales
  const mainMetrics = [
    {
      title: 'Ingresos del Mes',
      value: `$${data.ingresos_mes.toLocaleString()}`,
      change: data.crecimiento_ingresos,
      changeLabel: 'vs mes anterior',
      icon: DollarSign,
      color: 'primary',
      trend: data.tendencia_ingresos,
    },
    {
      title: 'Ventas del Mes',
      value: data.ventas_mes.toLocaleString(),
      change: data.crecimiento_ventas,
      changeLabel: 'vs mes anterior',
      icon: ShoppingCart,
      color: 'success',
      trend: data.tendencia_ventas,
    },
    {
      title: 'Clientes Activos',
      value: data.clientes_activos.toLocaleString(),
      change: data.crecimiento_clientes,
      changeLabel: 'vs mes anterior',
      icon: Users,
      color: 'warning',
      trend: data.tendencia_clientes,
    },
    {
      title: 'Ticket Promedio',
      value: `$${data.ticket_promedio.toLocaleString()}`,
      change: 0,
      changeLabel: 'promedio mensual',
      icon: BarChart3,
      color: 'gray',
      trend: 'estable',
    },
  ];

  // Métricas secundarias
  const secondaryMetrics = [
    {
      title: 'Productos Vendidos',
      value: data.productos_vendidos.toLocaleString(),
      icon: Package,
      color: 'success',
    },
    {
      title: 'Margen Bruto',
      value: `${data.margen_bruto}%`,
      icon: TrendingUp,
      color: 'primary',
    },
    {
      title: 'Margen Neto',
      value: `${data.margen_neto}%`,
      icon: TrendingDown,
      color: 'warning',
    },
    {
      title: 'Ingresos Anuales',
      value: `$${data.ingresos_anio.toLocaleString()}`,
      icon: Calendar,
      color: 'gray',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Resumen general del negocio - Última actualización: {new Date(data.fecha_actualizacion).toLocaleString('es-ES')}
        </p>
      </div>

      {/* Alertas críticas */}
      {data.alertas_criticas && data.alertas_criticas.length > 0 && (
        <div className="space-y-2">
          {data.alertas_criticas.map((alerta, index) => (
            <AlertCard
              key={index}
              type="error"
              title={alerta.titulo || 'Alerta Crítica'}
              message={alerta.mensaje}
              icon={AlertTriangle}
            />
          ))}
        </div>
      )}

      {/* Métricas principales */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {mainMetrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            changeLabel={metric.changeLabel}
            icon={metric.icon}
            color={metric.color as any}
            trend={metric.trend as any}
          />
        ))}
      </div>

      {/* Métricas secundarias */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {secondaryMetrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            icon={metric.icon}
            color={metric.color as any}
            compact
          />
        ))}
      </div>

      {/* Gráficos y análisis */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Gráfico de ventas */}
        <ChartCard
          title="Ventas por Mes"
          subtitle="Últimos 6 meses"
          icon={BarChart3}
        >
          <div className="h-64 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2">Gráfico de ventas</p>
              <p className="text-sm">Los datos se cargarán próximamente</p>
            </div>
          </div>
        </ChartCard>

        {/* Gráfico de clientes */}
        <ChartCard
          title="Crecimiento de Clientes"
          subtitle="Tendencia mensual"
          icon={Users}
        >
          <div className="h-64 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Users className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2">Gráfico de clientes</p>
              <p className="text-sm">Los datos se cargarán próximamente</p>
            </div>
          </div>
        </ChartCard>
      </div>

      {/* Alertas importantes y recomendaciones */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Alertas importantes */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Alertas Importantes</h3>
          {data.alertas_importantes && data.alertas_importantes.length > 0 ? (
            <div className="space-y-2">
              {data.alertas_importantes.map((alerta, index) => (
                <AlertCard
                  key={index}
                  type="warning"
                  title={alerta.titulo || 'Alerta Importante'}
                  message={alerta.mensaje}
                  icon={AlertTriangle}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2">No hay alertas importantes</p>
            </div>
          )}
        </div>

        {/* Recomendaciones */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Recomendaciones</h3>
          {data.recomendaciones && data.recomendaciones.length > 0 ? (
            <div className="space-y-2">
              {data.recomendaciones.map((recomendacion, index) => (
                <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex">
                    <CheckCircle className="h-5 w-5 text-blue-500 mt-0.5" />
                    <p className="ml-2 text-sm text-blue-800">{recomendacion}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2">No hay recomendaciones disponibles</p>
            </div>
          )}
        </div>
      </div>

      {/* Actividad reciente */}
      <RecentActivity />
    </div>
  );
};



