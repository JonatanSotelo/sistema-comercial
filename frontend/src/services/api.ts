import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  AuthResponse, 
  Metrica, 
  Medicion, 
  Alerta, 
  ReporteFinanciero,
  Producto,
  Cliente,
  Proveedor,
  Venta,
  Compra,
  DashboardData,
  DashboardCompleto,
  EstadisticasVentas,
  Notificacion,
  MovimientoStock,
  AlertaInventario,
  OrdenReabastecimiento,
  ConfiguracionInventario,
  ResumenInventario,
  EstadisticasInventario,
  ApiResponse,
  PaginatedResponse,
  FiltrosBase,
  FiltrosMetricas,
  FiltrosProductos,
  FiltrosClientes,
  FiltrosVentas,
  Permission,
  Role,
  UserCreate,
  UserUpdate,
  UserPermissions,
  RoleCreate,
  RoleUpdate
} from '@/types';

// Configuración base de la API
const isDev = (import.meta as any).env?.DEV ?? true;
const API_BASE_URL = isDev
  ? 'http://localhost:8000'
  : ((import.meta as any).env?.VITE_API_URL || (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8000');

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token de autenticación
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Interceptor para manejar respuestas y errores
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expirado, limpiar localStorage y redirigir al login
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Métodos de autenticación
  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const response = await this.api.post('/auth/login', { username, password });
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    role?: string;
  }): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/users/me');
    return response.data;
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  // Métodos para métricas
  async getMetricas(filtros?: FiltrosMetricas): Promise<PaginatedResponse<Metrica>> {
    const response: AxiosResponse<Metrica[]> = await this.api.get('/metricas-rendimiento/', {
      params: filtros,
    });
    
    return {
      data: response.data,
      total: response.data.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(response.data.length / (filtros?.per_page || 100)),
    };
  }

  async getMetrica(id: number): Promise<Metrica> {
    const response: AxiosResponse<Metrica> = await this.api.get(`/metricas-rendimiento/${id}`);
    return response.data;
  }

  async createMetrica(metrica: Partial<Metrica>): Promise<Metrica> {
    const response: AxiosResponse<Metrica> = await this.api.post('/metricas-rendimiento/', metrica);
    return response.data;
  }

  async updateMetrica(id: number, metrica: Partial<Metrica>): Promise<Metrica> {
    const response: AxiosResponse<Metrica> = await this.api.put(`/metricas-rendimiento/${id}`, metrica);
    return response.data;
  }

  async deleteMetrica(id: number): Promise<void> {
    await this.api.delete(`/metricas-rendimiento/${id}`);
  }

  async calcularMetrica(id: number, params?: {
    fecha_medicion?: string;
    periodo_desde?: string;
    periodo_hasta?: string;
  }): Promise<Medicion> {
    const response: AxiosResponse<Medicion> = await this.api.post(
      `/metricas-rendimiento/${id}/mediciones`,
      null,
      { params }
    );
    return response.data;
  }

  async getMediciones(id: number, filtros?: FiltrosBase): Promise<Medicion[]> {
    const response: AxiosResponse<Medicion[]> = await this.api.get(
      `/metricas-rendimiento/${id}/mediciones`,
      { params: filtros }
    );
    return response.data;
  }

  async getAlertas(id: number, filtros?: FiltrosBase): Promise<Alerta[]> {
    const response: AxiosResponse<Alerta[]> = await this.api.get(
      `/metricas-rendimiento/${id}/alertas`,
      { params: filtros }
    );
    return response.data;
  }

  async createAlerta(metricaId: number, alerta: Partial<Alerta>): Promise<Alerta> {
    const response: AxiosResponse<Alerta> = await this.api.post(
      `/metricas-rendimiento/${metricaId}/alertas`,
      alerta
    );
    return response.data;
  }

  // Métodos para dashboard
  async getDashboardCompleto(): Promise<DashboardCompleto> {
    const response: AxiosResponse<DashboardCompleto> = await this.api.get('/dashboard/completo');
    return response.data;
  }

  async getEstadisticasVentas(): Promise<EstadisticasVentas> {
    const response: AxiosResponse<EstadisticasVentas> = await this.api.get('/dashboard/ventas/estadisticas');
    return response.data;
  }

  async getProductosMasVendidos(): Promise<any[]> {
    const response: AxiosResponse<any[]> = await this.api.get('/dashboard/productos/mas-vendidos');
    return response.data;
  }

  async getClientesTop(): Promise<any[]> {
    const response: AxiosResponse<any[]> = await this.api.get('/dashboard/clientes/top');
    return response.data;
  }

  async getStockBajo(): Promise<any[]> {
    const response: AxiosResponse<any[]> = await this.api.get('/dashboard/stock/bajo');
    return response.data;
  }

  async getTendencias(): Promise<any[]> {
    const response: AxiosResponse<any[]> = await this.api.get('/dashboard/tendencias');
    return response.data;
  }

  async getDashboardEjecutivo(): Promise<DashboardData> {
    const response: AxiosResponse<DashboardData> = await this.api.get('/metricas-rendimiento/dashboard-ejecutivo');
    return response.data;
  }

  // Métodos para productos
  async getProductos(filtros?: FiltrosProductos): Promise<PaginatedResponse<Producto>> {
    // Adaptar filtros del frontend a los esperados por el backend
    const params: Record<string, any> = {};
    if (filtros?.page != null) params.page = filtros.page;
    if (filtros?.per_page != null) params.size = filtros.per_page; // backend espera 'size'
    if (filtros?.search) params.search = filtros.search;
    if (filtros?.sort_by) {
      const dir = filtros.sort_order === 'desc' ? '-' : '';
      params.sort = `${dir}${filtros.sort_by}`; // backend espera 'sort'
    }
    if (filtros?.categoria) params.categoria = filtros.categoria;
    if (filtros?.activo != null) params.activo = filtros.activo;
    if (filtros?.precio_min != null) params.precio_min = filtros.precio_min;
    if (filtros?.precio_max != null) params.precio_max = filtros.precio_max;
    if (filtros?.stock_min != null) params.stock_min = filtros.stock_min;

    const response = await this.api.get('/productos/', { params });
    const body = response.data as any;

    // El backend puede devolver lista simple o paginado con { items, total, page, size }
    if (Array.isArray(body)) {
      const per = filtros?.per_page || body.length || 100;
      return {
        data: body,
        total: body.length,
        page: filtros?.page || 1,
        per_page: per,
        total_pages: Math.max(1, Math.ceil(body.length / per)),
      };
    }

    const items = Array.isArray(body?.items) ? body.items : [];
    const total = body?.total ?? items.length;
    const page = body?.page ?? filtros?.page ?? 1;
    const size = body?.size ?? (filtros?.per_page ?? (items.length || 100));
    return {
      data: items,
      total,
      page,
      per_page: size,
      total_pages: Math.max(1, Math.ceil(total / (size || 1))),
    };
  }

  async getProducto(id: number): Promise<Producto> {
    const response: AxiosResponse<Producto> = await this.api.get(`/productos/${id}`);
    return response.data;
  }

  async createProducto(producto: Partial<Producto>): Promise<Producto> {
    const response: AxiosResponse<Producto> = await this.api.post('/productos/', producto);
    return response.data;
  }

  async updateProducto(id: number, producto: Partial<Producto>): Promise<Producto> {
    const response: AxiosResponse<Producto> = await this.api.put(`/productos/${id}`, producto);
    return response.data;
  }

  async deleteProducto(id: number): Promise<void> {
    await this.api.delete(`/productos/${id}`);
  }

  // Métodos para clientes
  async getClientes(filtros?: FiltrosClientes): Promise<PaginatedResponse<Cliente>> {
    const response: AxiosResponse<Cliente[]> = await this.api.get('/clientes/', {
      params: filtros,
    });
    
    return {
      data: response.data,
      total: response.data.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(response.data.length / (filtros?.per_page || 100)),
    };
  }

  async getClienteById(id: number): Promise<Cliente> {
    const response = await this.api.get<Cliente>(`/clientes/${id}`);
    return response.data;
  }

  async getCliente(id: number): Promise<Cliente> {
    const response: AxiosResponse<Cliente> = await this.api.get(`/clientes/${id}`);
    return response.data;
  }

  async createCliente(cliente: Partial<Cliente>): Promise<Cliente> {
    const response: AxiosResponse<Cliente> = await this.api.post('/clientes/', cliente);
    return response.data;
  }

  async updateCliente(id: number, cliente: Partial<Cliente>): Promise<Cliente> {
    const response: AxiosResponse<Cliente> = await this.api.put(`/clientes/${id}`, cliente);
    return response.data;
  }

  async deleteCliente(id: number): Promise<void> {
    await this.api.delete(`/clientes/${id}`);
  }

  // Métodos para proveedores
  async getProveedores(filtros?: FiltrosBase): Promise<PaginatedResponse<Proveedor>> {
    const response: AxiosResponse<Proveedor[]> = await this.api.get('/proveedores/', {
      params: filtros,
    });
    
    return {
      data: response.data,
      total: response.data.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(response.data.length / (filtros?.per_page || 100)),
    };
  }

  async getProveedorById(id: number): Promise<Proveedor> {
    const response = await this.api.get<Proveedor>(`/proveedores/${id}`);
    return response.data;
  }

  async getProveedor(id: number): Promise<Proveedor> {
    const response: AxiosResponse<Proveedor> = await this.api.get(`/proveedores/${id}`);
    return response.data;
  }

  async createProveedor(proveedor: Partial<Proveedor>): Promise<Proveedor> {
    const response: AxiosResponse<Proveedor> = await this.api.post('/proveedores/', proveedor);
    return response.data;
  }

  async updateProveedor(id: number, proveedor: Partial<Proveedor>): Promise<Proveedor> {
    const response: AxiosResponse<Proveedor> = await this.api.put(`/proveedores/${id}`, proveedor);
    return response.data;
  }

  async deleteProveedor(id: number): Promise<void> {
    await this.api.delete(`/proveedores/${id}`);
  }

  // Métodos para ventas
  async getVentas(filtros?: FiltrosVentas): Promise<PaginatedResponse<Venta>> {
    const response: AxiosResponse<Venta[]> = await this.api.get('/ventas/', {
      params: filtros,
    });
    
    // El backend devuelve directamente un array de ventas
    const ventas = Array.isArray(response.data) ? response.data : [];
    
    return {
      data: ventas,
      total: ventas.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(ventas.length / (filtros?.per_page || 100)),
    };
  }

  async getVentaById(id: number): Promise<Venta> {
    const response = await this.api.get<Venta>(`/ventas/${id}`);
    return response.data;
  }

  async getVenta(id: number): Promise<Venta> {
    const response: AxiosResponse<Venta> = await this.api.get(`/ventas/${id}`);
    return response.data;
  }

  async createVenta(venta: Partial<Venta>): Promise<Venta> {
    const response: AxiosResponse<Venta> = await this.api.post('/ventas/', venta);
    return response.data;
  }

  async updateVenta(id: number, venta: Partial<Venta>): Promise<Venta> {
    const response: AxiosResponse<Venta> = await this.api.put(`/ventas/${id}`, venta);
    return response.data;
  }

  async deleteVenta(id: number): Promise<void> {
    await this.api.delete(`/ventas/${id}`);
  }

  // Métodos para compras
  async getCompras(filtros?: FiltrosBase): Promise<PaginatedResponse<Compra>> {
    const response: AxiosResponse<Compra[]> = await this.api.get('/compras/', {
      params: filtros,
    });
    
    // El backend devuelve directamente un array de compras
    const compras = Array.isArray(response.data) ? response.data : [];
    
    return {
      data: compras,
      total: compras.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(compras.length / (filtros?.per_page || 100)),
    };
  }

  async getCompraById(id: number): Promise<Compra> {
    const response = await this.api.get<Compra>(`/compras/${id}`);
    return response.data;
  }

  async getCompra(id: number): Promise<Compra> {
    const response: AxiosResponse<Compra> = await this.api.get(`/compras/${id}`);
    return response.data;
  }

  async createCompra(compra: Partial<Compra>): Promise<Compra> {
    const response: AxiosResponse<Compra> = await this.api.post('/compras/', compra);
    return response.data;
  }

  async updateCompra(id: number, compra: Partial<Compra>): Promise<Compra> {
    const response: AxiosResponse<Compra> = await this.api.put(`/compras/${id}`, compra);
    return response.data;
  }

  async deleteCompra(id: number): Promise<void> {
    await this.api.delete(`/compras/${id}`);
  }

  // Métodos para reportes financieros
  async getReportesFinancieros(filtros?: FiltrosBase): Promise<PaginatedResponse<ReporteFinanciero>> {
    const response: AxiosResponse<ReporteFinanciero[]> = await this.api.get('/reportes-financieros/', {
      params: filtros,
    });
    
    return {
      data: response.data,
      total: response.data.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(response.data.length / (filtros?.per_page || 100)),
    };
  }

  async getReporteFinanciero(id: number): Promise<ReporteFinanciero> {
    const response: AxiosResponse<ReporteFinanciero> = await this.api.get(`/reportes-financieros/${id}`);
    return response.data;
  }

  async createReporteFinanciero(reporte: Partial<ReporteFinanciero>): Promise<ReporteFinanciero> {
    const response: AxiosResponse<ReporteFinanciero> = await this.api.post('/reportes-financieros/', reporte);
    return response.data;
  }

  // Métodos para dashboard
  async getDashboard(): Promise<DashboardData> {
    // Compatibilidad: usar el endpoint vigente del backend
    const response: AxiosResponse<DashboardData> = await this.api.get('/metricas-rendimiento/dashboard-ejecutivo');
    return response.data;
  }

  // Métodos para notificaciones
  async getNotificaciones(filtros?: FiltrosBase): Promise<Notificacion[]> {
    const response: AxiosResponse<Notificacion[]> = await this.api.get('/notificaciones', {
      params: filtros,
    });
    return response.data;
  }

  async getNotificacionesPendientes(): Promise<Notificacion[]> {
    const response: AxiosResponse<Notificacion[]> = await this.api.get('/notificaciones/pendientes');
    return response.data;
  }

  async getNotificacionesUrgentes(): Promise<Notificacion[]> {
    const response: AxiosResponse<Notificacion[]> = await this.api.get('/notificaciones/urgentes');
    return response.data;
  }

  async marcarNotificacionComoLeida(id: number): Promise<void> {
    await this.api.patch(`/notificaciones/${id}/leer`);
  }

  async marcarTodasComoLeidas(): Promise<void> {
    await this.api.patch('/notificaciones/bulk/leer');
  }

  // Métodos para exportación
  async exportarDatos(endpoint: string, formato: string, filtros?: any): Promise<Blob> {
    const response = await this.api.get(endpoint, {
      params: { ...filtros, formato },
      responseType: 'blob',
    });
    return response.data;
  }

  // Método para obtener tipos disponibles
  async getTiposDisponibles(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/metricas-rendimiento/tipos-disponibles');
    return response.data;
  }

  // Métodos para inventario
  async getResumenInventario(): Promise<ResumenInventario> {
    const response: AxiosResponse<ResumenInventario> = await this.api.get('/inventario/resumen');
    return response.data;
  }

  async getEstadisticasInventario(): Promise<EstadisticasInventario> {
    const response: AxiosResponse<EstadisticasInventario> = await this.api.get('/inventario/estadisticas');
    return response.data;
  }

  async getMovimientosStock(filtros?: FiltrosBase): Promise<MovimientoStock[]> {
    const response: AxiosResponse<MovimientoStock[]> = await this.api.get('/inventario/movimientos', {
      params: filtros,
    });
    return response.data;
  }

  async createMovimientoStock(movimiento: Partial<MovimientoStock>): Promise<MovimientoStock> {
    const response: AxiosResponse<MovimientoStock> = await this.api.post('/inventario/movimientos', movimiento);
    return response.data;
  }

  async getAlertasInventario(filtros?: FiltrosBase): Promise<AlertaInventario[]> {
    const response: AxiosResponse<AlertaInventario[]> = await this.api.get('/inventario/alertas', {
      params: filtros,
    });
    return response.data;
  }

  async getAlertasPendientes(): Promise<AlertaInventario[]> {
    const response: AxiosResponse<AlertaInventario[]> = await this.api.get('/inventario/alertas/pendientes');
    return response.data;
  }

  async getAlertasUrgentes(): Promise<AlertaInventario[]> {
    const response: AxiosResponse<AlertaInventario[]> = await this.api.get('/inventario/alertas/urgentes');
    return response.data;
  }

  async resolverAlerta(alertaId: number): Promise<void> {
    await this.api.patch(`/inventario/alertas/${alertaId}/resolver`);
  }

  async getOrdenesReabastecimiento(filtros?: FiltrosBase): Promise<OrdenReabastecimiento[]> {
    const response: AxiosResponse<OrdenReabastecimiento[]> = await this.api.get('/inventario/reordenes', {
      params: filtros,
    });
    return response.data;
  }

  async createOrdenReabastecimiento(orden: Partial<OrdenReabastecimiento>): Promise<OrdenReabastecimiento> {
    const response: AxiosResponse<OrdenReabastecimiento> = await this.api.post('/inventario/generar-reorden', orden);
    return response.data;
  }

  async aprobarOrdenReabastecimiento(ordenId: number): Promise<void> {
    await this.api.patch(`/inventario/reordenes/${ordenId}/aprobar`);
  }

  async rechazarOrdenReabastecimiento(ordenId: number): Promise<void> {
    await this.api.patch(`/inventario/reordenes/${ordenId}/rechazar`);
  }

  async getConfiguracionesInventario(filtros?: FiltrosBase): Promise<ConfiguracionInventario[]> {
    const response: AxiosResponse<ConfiguracionInventario[]> = await this.api.get('/inventario/configuraciones', {
      params: filtros,
    });
    return response.data;
  }

  async createConfiguracionInventario(config: Partial<ConfiguracionInventario>): Promise<ConfiguracionInventario> {
    const response: AxiosResponse<ConfiguracionInventario> = await this.api.post('/inventario/configuraciones', config);
    return response.data;
  }

  async updateConfiguracionInventario(configId: number, config: Partial<ConfiguracionInventario>): Promise<ConfiguracionInventario> {
    const response: AxiosResponse<ConfiguracionInventario> = await this.api.put(`/inventario/configuraciones/${configId}`, config);
    return response.data;
  }

  async procesarAlertas(): Promise<void> {
    await this.api.post('/inventario/procesar-alertas');
  }

  // ==================== GESTIÓN DE USUARIOS ====================
  
  async getUsers(): Promise<User[]> {
    const response = await this.api.get<User[]>('/users/');
    return response.data;
  }

  async getUserById(userId: number): Promise<User> {
    const response = await this.api.get<User>(`/users/${userId}`);
    return response.data;
  }

  async createUser(userData: UserCreate): Promise<User> {
    const response = await this.api.post<User>('/users/', userData);
    return response.data;
  }

  async updateUser(userId: number, userData: UserUpdate): Promise<User> {
    const response = await this.api.put<User>(`/users/${userId}`, userData);
    return response.data;
  }

  async deleteUser(userId: number): Promise<void> {
    await this.api.delete(`/users/${userId}`);
  }


  // ==================== GESTIÓN DE PERMISOS ====================
  
  async getPermissions(): Promise<Permission[]> {
    const response = await this.api.get<Permission[]>('/permisos/permissions');
    return response.data;
  }

  async getPermissionsByModule(module: string): Promise<Permission[]> {
    const response = await this.api.get<Permission[]>(`/permisos/permissions/module/${module}`);
    return response.data;
  }

  async createPermission(permissionData: Omit<Permission, 'id' | 'created_at'>): Promise<Permission> {
    const response = await this.api.post<Permission>('/permisos/permissions', permissionData);
    return response.data;
  }

  async updatePermission(permissionId: number, permissionData: Partial<Permission>): Promise<Permission> {
    const response = await this.api.put<Permission>(`/permisos/permissions/${permissionId}`, permissionData);
    return response.data;
  }

  async deletePermission(permissionId: number): Promise<void> {
    await this.api.delete(`/permisos/permissions/${permissionId}`);
  }

  // ==================== GESTIÓN DE ROLES ====================
  
  async getRoles(): Promise<Role[]> {
    const response = await this.api.get<Role[]>('/permisos/roles');
    return response.data;
  }

  async createRole(roleData: RoleCreate): Promise<Role> {
    const response = await this.api.post<Role>('/permisos/roles', roleData);
    return response.data;
  }

  async updateRole(roleId: number, roleData: RoleUpdate): Promise<Role> {
    const response = await this.api.put<Role>(`/permisos/roles/${roleId}`, roleData);
    return response.data;
  }

  async deleteRole(roleId: number): Promise<void> {
    await this.api.delete(`/permisos/roles/${roleId}`);
  }

  // ==================== VERIFICACIÓN DE PERMISOS ====================
  
  async getUserPermissions(userId: number): Promise<UserPermissions> {
    const response = await this.api.get<UserPermissions>(`/permisos/user/${userId}/permissions`);
    return response.data;
  }

  async checkPermission(permissionName: string): Promise<{ permission: string; has_permission: boolean; user_role: string }> {
    const response = await this.api.get(`/permisos/check/${permissionName}`);
    return response.data;
  }

  async initializeDefaultPermissions(): Promise<{ message: string }> {
    const response = await this.api.post('/permisos/initialize');
    return response.data;
  }
}

// Instancia singleton del servicio API
export const apiService = new ApiService();
export default apiService;










