import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import { Layout } from '@/components/Layout';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import { ProductosPage } from '@/pages/ProductosPage';
import { NuevoProductoPage } from '@/pages/NuevoProductoPage';
import { ClientesPage } from '@/pages/ClientesPage';
import { NuevoClientePage } from '@/pages/NuevoClientePage';
import { ClienteDetailPage } from '@/pages/ClienteDetailPage';
import { ClienteEditPage } from '@/pages/ClienteEditPage';
import { ProveedoresPage } from '@/pages/ProveedoresPage';
import { NuevoProveedorPage } from '@/pages/NuevoProveedorPage';
import { ProveedorDetailPage } from '@/pages/ProveedorDetailPage';
import { ProveedorEditPage } from '@/pages/ProveedorEditPage';
import { VentasPage } from '@/pages/VentasPage';
import { NuevaVentaPage } from '@/pages/NuevaVentaPage';
import { ComprasPage } from '@/pages/ComprasPage';
import { NuevaCompraPage } from '@/pages/NuevaCompraPage';
import InventarioPage from '@/pages/InventarioPage';
import { MetricasPage } from '@/pages/MetricasPage';
import { ReportesPage } from '@/pages/ReportesPage';
import { ConfiguracionPage } from '@/pages/ConfiguracionPage';
import UsuariosPage from '@/pages/UsuariosPage';
import RolesPage from '@/pages/RolesPage';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import '@/styles/globals.css';

// Configuración de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <NotificationProvider>
          <Router>
            <div className="min-h-screen bg-gray-50">
            <Routes>
              {/* Rutas públicas */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Rutas protegidas */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <DashboardPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <DashboardPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/productos"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProductosPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/productos/nuevo"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <NuevoProductoPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/clientes"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ClientesPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clientes/nuevo"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <NuevoClientePage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clientes/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ClienteDetailPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clientes/:id/editar"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ClienteEditPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/proveedores"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProveedoresPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/proveedores/nuevo"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <NuevoProveedorPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/proveedores/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProveedorDetailPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/proveedores/:id/editar"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProveedorEditPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/ventas"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <VentasPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/ventas/nueva"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <NuevaVentaPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/compras"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ComprasPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/compras/nueva"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <NuevaCompraPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/inventario"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <InventarioPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/metricas"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <MetricasPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/reportes"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ReportesPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/configuracion"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ConfiguracionPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/usuarios"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <UsuariosPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/roles"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <RolesPage />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              
              {/* Ruta por defecto */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
            </div>
          </Router>
        </NotificationProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;










