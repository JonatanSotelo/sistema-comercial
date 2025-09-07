// Tipos base del sistema
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Tipos para métricas y dashboards
export interface Metrica {
  id: number;
  nombre: string;
  codigo: string;
  descripcion?: string;
  tipo_metrica: string;
  categoria: string;
  subcategoria?: string;
  tipo_calculo: string;
  formula?: string;
  unidad_medida?: string;
  decimales: number;
  frecuencia_medicion: string;
  fuente_datos?: string;
  valor_objetivo?: number;
  valor_minimo?: number;
  valor_maximo?: number;
  rango_optimo_inicio?: number;
  rango_optimo_fin?: number;
  color_positivo: string;
  color_negativo: string;
  color_neutro: string;
  icono?: string;
  orden_display: number;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Medicion {
  id: number;
  metrica_id: number;
  fecha_medicion: string;
  periodo_desde?: string;
  periodo_hasta?: string;
  valor_actual: number;
  valor_anterior?: number;
  valor_objetivo?: number;
  valor_historico_promedio?: number;
  variacion_absoluta?: number;
  variacion_porcentual?: number;
  tendencia?: 'creciente' | 'decreciente' | 'estable';
  velocidad_cambio?: number;
  percentil?: number;
  ranking?: number;
  desviacion_estandar?: number;
  fuente_datos?: string;
  observaciones?: string;
  created_at: string;
}

export interface Alerta {
  id: number;
  metrica_id: number;
  nombre: string;
  descripcion?: string;
  tipo_alerta: string;
  estado: 'activa' | 'inactiva' | 'triggered' | 'resuelta' | 'expirada';
  condicion: string;
  umbral_minimo?: number;
  umbral_maximo?: number;
  umbral_porcentaje?: number;
  ventana_tiempo?: number;
  notificar_email: boolean;
  notificar_dashboard: boolean;
  notificar_movil: boolean;
  usuarios_notificar?: number[];
  frecuencia_verificacion: string;
  max_alertas_por_dia: number;
  cooldown_minutos: number;
  total_activaciones: number;
  activaciones_resueltas: number;
  activaciones_pendientes: number;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

// Tipos para reportes financieros
export interface ReporteFinanciero {
  id: number;
  nombre: string;
  tipo: string;
  periodo: string;
  estado: string;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_generacion: string;
  incluir_detalles: boolean;
  incluir_proyecciones: boolean;
  incluir_comparaciones: boolean;
  formato_salida: string;
  descripcion?: string;
  creado_por?: number;
  archivo_ruta?: string;
  tamaño_archivo?: number;
  total_ingresos?: number;
  total_costos?: number;
  total_gastos?: number;
  ganancia_neta?: number;
  margen_bruto?: number;
  margen_neto?: number;
  created_at: string;
  updated_at: string;
}

// Tipos para productos
export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string;
  codigo: string;
  categoria: string;
  precio: number;
  costo: number;
  stock: number;
  stock_minimo: number;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

// Tipos para clientes
export interface Cliente {
  id: number;
  nombre: string;
  email: string;
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

// Tipos para proveedores
export interface Proveedor {
  id: number;
  nombre: string;
  email: string;
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
}

// Tipos para ventas
export interface Venta {
  id: number;
  cliente_id: number;
  fecha: string;
  total: number;
  descuento: number;
  impuestos: number;
  estado: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
  cliente?: Cliente;
}

// Tipos para compras
export interface Compra {
  id: number;
  proveedor_id: number;
  fecha: string;
  total: number;
  descuento: number;
  impuestos: number;
  estado: string;
  observaciones?: string;
  created_at: string;
  updated_at: string;
  proveedor?: Proveedor;
}

// Tipos para dashboard
export interface DashboardData {
  // Métricas principales
  ingresos_mes: number;
  ingresos_anio: number;
  crecimiento_ingresos: number;
  margen_bruto: number;
  margen_neto: number;
  rentabilidad_activos: number;
  
  // Métricas operativas
  ventas_mes: number;
  clientes_activos: number;
  productos_vendidos: number;
  ticket_promedio: number;
  satisfaccion_cliente: number;
  
  // Métricas de crecimiento
  crecimiento_ventas: number;
  crecimiento_clientes: number;
  crecimiento_productos: number;
  penetracion_mercado: number;
  
  // Alertas
  alertas_criticas: Array<{
    tipo: string;
    mensaje: string;
    severidad: string;
  }>;
  alertas_importantes: Array<{
    tipo: string;
    mensaje: string;
    severidad: string;
  }>;
  
  // Tendencias
  tendencia_ingresos: string;
  tendencia_ventas: string;
  tendencia_clientes: string;
  tendencia_rentabilidad: string;
  
  // Recomendaciones
  recomendaciones: string[];
  
  // Metadatos
  fecha_actualizacion: string;
  proxima_actualizacion: string;
}

// Tipos para respuestas de API
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Tipos para filtros
export interface FiltrosBase {
  page?: number;
  per_page?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface FiltrosMetricas extends FiltrosBase {
  tipo_metrica?: string;
  categoria?: string;
  subcategoria?: string;
  frecuencia_medicion?: string;
  activo?: boolean;
}

export interface FiltrosProductos extends FiltrosBase {
  categoria?: string;
  activo?: boolean;
  precio_min?: number;
  precio_max?: number;
  stock_min?: number;
}

export interface FiltrosClientes extends FiltrosBase {
  activo?: boolean;
  ciudad?: string;
}

export interface FiltrosVentas extends FiltrosBase {
  cliente_id?: number;
  fecha_desde?: string;
  fecha_hasta?: string;
  estado?: string;
  total_min?: number;
  total_max?: number;
}

// Tipos para formularios
export interface FormularioBase {
  isSubmitting: boolean;
  errors: Record<string, string>;
}

export interface FormularioLogin extends FormularioBase {
  username: string;
  password: string;
}

export interface FormularioRegistro extends FormularioBase {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface FormularioProducto extends FormularioBase {
  nombre: string;
  descripcion: string;
  codigo: string;
  categoria: string;
  precio: number;
  costo: number;
  stock: number;
  stock_minimo: number;
  activo: boolean;
}

export interface FormularioCliente extends FormularioBase {
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  ciudad: string;
  codigo_postal: string;
  activo: boolean;
}

// Tipos para notificaciones
export interface Notificacion {
  id: number;
  tipo: string;
  titulo: string;
  mensaje: string;
  prioridad: 'baja' | 'normal' | 'alta' | 'urgente';
  leida: boolean;
  procesada: boolean;
  fecha_creacion: string;
  fecha_lectura?: string;
  fecha_procesamiento?: string;
  datos_adicionales?: Record<string, any>;
  accion_requerida?: string;
}

// Tipos para configuración
export interface Configuracion {
  tema: 'light' | 'dark' | 'auto';
  idioma: 'es' | 'en';
  moneda: 'ARS' | 'USD' | 'EUR';
  formato_fecha: string;
  formato_numero: string;
  notificaciones_email: boolean;
  notificaciones_push: boolean;
  notificaciones_dashboard: boolean;
}

// Tipos para estadísticas
export interface EstadisticasGenerales {
  total_ventas: number;
  total_compras: number;
  total_clientes: number;
  total_proveedores: number;
  total_productos: number;
  ventas_mes_actual: number;
  compras_mes_actual: number;
  clientes_nuevos_mes: number;
  productos_agotados: number;
  ticket_promedio: number;
  margen_promedio: number;
}

// Tipos para gráficos
export interface DatosGrafico {
  name: string;
  value: number;
  color?: string;
}

export interface SerieDatos {
  name: string;
  data: Array<{
    x: string | number;
    y: number;
  }>;
  color?: string;
}

// Tipos para exportación
export interface OpcionesExportacion {
  formato: 'pdf' | 'excel' | 'csv' | 'json';
  incluir_graficos: boolean;
  incluir_detalles: boolean;
  incluir_comparaciones: boolean;
  idioma: string;
  moneda: string;
}



