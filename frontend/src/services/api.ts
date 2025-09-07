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
  ApiResponse,
  PaginatedResponse,
  FiltrosBase,
  FiltrosMetricas,
  FiltrosProductos,
  FiltrosClientes,
  FiltrosVentas
} from '@/types';

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  async login(username: string, password: string): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response: AxiosResponse<AuthResponse> = await this.api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // Guardar token y usuario en localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));

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
    const response: AxiosResponse<User> = await this.api.get('/users/usuarios/me');
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
  async getDashboardEjecutivo(): Promise<DashboardData> {
    const response: AxiosResponse<DashboardData> = await this.api.get('/metricas-rendimiento/dashboard-ejecutivo');
    return response.data;
  }

  // Métodos para productos
  async getProductos(filtros?: FiltrosProductos): Promise<PaginatedResponse<Producto>> {
    const response: AxiosResponse<Producto[]> = await this.api.get('/productos/', {
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
    
    return {
      data: response.data,
      total: response.data.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(response.data.length / (filtros?.per_page || 100)),
    };
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
    
    return {
      data: response.data,
      total: response.data.length,
      page: filtros?.page || 1,
      per_page: filtros?.per_page || 100,
      total_pages: Math.ceil(response.data.length / (filtros?.per_page || 100)),
    };
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
  async getDashboard(): Promise<any> {
    const response: AxiosResponse<any> = await this.api.get('/dashboard/');
    return response.data;
  }

  // Métodos para notificaciones
  async getNotificaciones(filtros?: FiltrosBase): Promise<any[]> {
    const response: AxiosResponse<any[]> = await this.api.get('/notificaciones/', {
      params: filtros,
    });
    return response.data;
  }

  async marcarNotificacionComoLeida(id: number): Promise<void> {
    await this.api.put(`/notificaciones/${id}`, { leida: true });
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
}

// Instancia singleton del servicio API
export const apiService = new ApiService();
export default apiService;



