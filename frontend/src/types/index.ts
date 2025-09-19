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

export interface ClienteCreate {
  nombre: string;
  email?: string;
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  activo?: boolean;
}

export interface ClienteUpdate {
  nombre?: string;
  email?: string;
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  activo?: boolean;
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

export interface ProveedorCreate {
  nombre: string;
  email?: string;
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  activo?: boolean;
}

export interface ProveedorUpdate {
  nombre?: string;
  email?: string;
  telefono?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  activo?: boolean;
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
  items?: VentaItem[];
}

export interface VentaItem {
  id: number;
  venta_id: number;
  producto_id: number;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
  producto?: Producto;
}

export interface VentaCreate {
  cliente_id: number;
  fecha: string;
  descuento?: number;
  impuestos?: number;
  estado?: string;
  observaciones?: string;
  items: VentaItemCreate[];
}

export interface VentaItemCreate {
  producto_id: number;
  cantidad: number;
  precio_unitario: number;
}

export interface VentaUpdate {
  cliente_id?: number;
  fecha?: string;
  descuento?: number;
  impuestos?: number;
  estado?: string;
  observaciones?: string;
  items?: VentaItemCreate[];
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
  items?: CompraItem[];
}

export interface CompraItem {
  id: number;
  compra_id: number;
  producto_id: number;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
  producto?: Producto;
}

export interface CompraCreate {
  proveedor_id: number;
  fecha: string;
  descuento?: number;
  impuestos?: number;
  estado?: string;
  observaciones?: string;
  items: CompraItemCreate[];
}

export interface CompraItemCreate {
  producto_id: number;
  cantidad: number;
  precio_unitario: number;
}

export interface CompraUpdate {
  proveedor_id?: number;
  fecha?: string;
  descuento?: number;
  impuestos?: number;
  estado?: string;
  observaciones?: string;
  items?: CompraItemCreate[];
}

// Tipos para dashboard
export interface DashboardCompleto {
  resumen_ventas: {
    total_ventas: number;
    total_monto: number;
    promedio_venta: number;
    venta_mayor: number;
    venta_menor: number;
    ventas_hoy: number;
    monto_hoy: number;
  };
  ventas_por_periodo: Array<{
    periodo: string;
    cantidad_ventas: number;
    monto_total: number;
    promedio: number;
  }>;
  productos_mas_vendidos: Array<{
    producto_id: number;
    producto_nombre: string;
    cantidad_vendida: number;
    monto_total: number;
    ventas_count: number;
  }>;
  clientes_top: Array<{
    cliente_id: number;
    cliente_nombre: string;
    cantidad_ventas: number;
    monto_total: number;
    promedio_compra: number;
  }>;
  stock_bajo: Array<{
    producto_id: number;
    producto_nombre: string;
    stock_actual: number;
    stock_minimo: number;
    diferencia: number;
    porcentaje: number;
  }>;
  metricas: {
    ventas_ultimo_mes: number;
    crecimiento_ventas: number;
    productos_activos: number;
    clientes_activos: number;
    ticket_promedio: number;
    conversion_rate: number;
  };
  tendencias: Array<{
    fecha: string;
    ventas: number;
    monto: number;
    crecimiento_diario: number;
  }>;
  ultima_actualizacion: string;
}

export interface EstadisticasVentas {
  resumen: {
    total_ventas: number;
    total_monto: number;
    promedio_venta: number;
    venta_mayor: number;
    venta_menor: number;
    ventas_hoy: number;
    monto_hoy: number;
  };
  productos_destacados: Array<{
    producto_id: number;
    producto_nombre: string;
    cantidad_vendida: number;
    monto_total: number;
    ventas_count: number;
  }>;
  clientes_destacados: Array<{
    cliente_id: number;
    cliente_nombre: string;
    cantidad_ventas: number;
    monto_total: number;
    promedio_compra: number;
  }>;
  tendencias: Array<{
    fecha: string;
    ventas: number;
    monto: number;
    crecimiento_diario: number;
  }>;
  filtros_aplicados: {
    fecha_inicio: string | null;
    fecha_fin: string | null;
  };
}

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
  titulo: string;
  mensaje: string;
  tipo: 'STOCK_BAJO' | 'VENTA_IMPORTANTE' | 'SISTEMA' | 'MANTENIMIENTO' | 'ERROR' | 'INFO' | 'WARNING';
  estado?: 'PENDIENTE' | 'ENVIADA' | 'LEIDA' | 'ARCHIVADA';
  usuario_id?: number;
  entidad_id?: number;
  entidad_tipo?: string;
  fecha_creacion: string;
  fecha_envio?: string;
  fecha_lectura?: string;
  es_urgente?: boolean;
  requiere_accion?: boolean;
  datos_adicionales?: string;
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

// Tipos para inventario
export interface MovimientoStock {
  id: number;
  producto_id: number;
  tipo: 'IN' | 'OUT' | 'AJUSTE' | 'TRANSFERENCIA';
  cantidad: number;
  motivo: string;
  referencia?: string;
  usuario_id?: number;
  fecha: string;
  observaciones?: string;
  producto?: Producto;
  usuario?: User;
}

export interface AlertaInventario {
  id: number;
  producto_id: number;
  tipo: 'stock_bajo' | 'stock_critico' | 'agotado' | 'exceso' | 'vencimiento';
  nivel: 'info' | 'warning' | 'error' | 'critical';
  mensaje: string;
  fecha_creacion: string;
  fecha_resolucion?: string;
  resuelta: boolean;
  producto?: Producto;
}

export interface OrdenReabastecimiento {
  id: number;
  producto_id: number;
  cantidad_solicitada: number;
  cantidad_aprobada?: number;
  estado: 'pendiente' | 'aprobada' | 'rechazada' | 'completada';
  fecha_solicitud: string;
  fecha_aprobacion?: string;
  fecha_completado?: string;
  solicitado_por?: number;
  aprobado_por?: number;
  observaciones?: string;
  producto?: Producto;
  solicitante?: User;
  aprobador?: User;
}

export interface ConfiguracionInventario {
  id: number;
  producto_id: number;
  stock_minimo: number;
  stock_maximo: number;
  punto_reorden: number;
  dias_cobertura: number;
  activo: boolean;
  created_at: string;
  updated_at: string;
  producto?: Producto;
}

export interface ResumenInventario {
  total_productos: number;
  productos_stock_bajo: number;
  productos_stock_critico: number;
  productos_agotados: number;
  alertas_pendientes: number;
  alertas_urgentes: number;
  valor_total_inventario: number;
  movimientos_hoy: number;
  reordenes_pendientes: number;
}

export interface EstadisticasInventario {
  total_productos: number;
  productos_configurados: number;
  alertas_por_tipo: Record<string, number>;
  movimientos_por_tipo: Record<string, number>;
  valor_inventario_por_categoria: Record<string, number>;
  productos_mas_movidos: Array<{
    producto_id: number;
    producto_nombre: string;
    total_movimientos: number;
  }>;
  tendencia_stock: Array<{
    fecha: string;
    total_stock: number;
    valor_total: number;
  }>;
  alertas_resueltas_mes: number;
  tiempo_promedio_resolucion: number;
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

// Tipos para Permisos y Roles
export interface Permission {
  id: number;
  name: string;
  description?: string;
  module: string;
  action: string;
  is_active: boolean;
  created_at: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  permissions: Permission[];
}

export interface UserCreate {
  username: string;
  email?: string;
  password: string;
  role: string;
  is_active: boolean;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  password?: string;
  role?: string;
  is_active?: boolean;
}

export interface UserPermissions {
  user_id: number;
  username: string;
  role: string;
  permissions: Permission[];
  modules_access: string[];
}

export interface RoleCreate {
  name: string;
  description?: string;
  permission_ids: number[];
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  permission_ids?: number[];
  is_active?: boolean;
}










