import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import { Layout } from '@/components/Layout';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import ProductosPage from '@/pages/ProductosPage';
import ClientesPage from '@/pages/ClientesPage';
import ClienteForm from '@/pages/ClienteForm';
import ProveedoresPage from '@/pages/ProveedoresPage';
import ProveedorForm from '@/pages/ProveedorForm';
import VentasPage from '@/pages/VentasPage';
import ComprasPage from '@/pages/ComprasPage';
import VentaForm from '@/pages/VentaForm';
import CompraForm from '@/pages/CompraForm';
import ProductoForm from '@/pages/ProductoForm';
import InventarioPage from '@/pages/InventarioPage';
import { MetricasPage } from '@/pages/MetricasPage';
import { ReportesPage } from '@/pages/ReportesPage';
import { ConfiguracionPage } from '@/pages/ConfiguracionPage';
import UsuariosPage from '@/pages/UsuariosPage';
import UsuarioForm from '@/pages/UsuarioForm';
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
                      <Navigate to="/productos" replace />
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
                path="/productos/new"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProductoForm mode="create" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/productos/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProductoForm mode="view" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/productos/:id/edit"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProductoForm mode="edit" />
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
                      <ClienteForm />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clientes/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ClienteForm mode="view" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/clientes/:id/editar"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ClienteForm mode="edit" />
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
                      <ProveedorForm />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/proveedores/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProveedorForm mode="view" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/proveedores/:id/editar"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <ProveedorForm mode="edit" />
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
                path="/ventas/new"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <VentaForm mode="create" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ventas/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <VentaForm mode="view" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/ventas/:id/edit"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <VentaForm mode="edit" />
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
                path="/compras/new"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <CompraForm mode="create" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/compras/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <CompraForm mode="view" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/compras/:id/edit"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <CompraForm mode="edit" />
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
                path="/usuarios/nuevo"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <UsuarioForm mode="create" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/usuarios/:id"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <UsuarioForm mode="view" />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/usuarios/:id/editar"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <UsuarioForm mode="edit" />
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
              <Route path="*" element={<Navigate to="/productos" replace />} />
            </Routes>
            </div>
          </Router>
        </NotificationProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;










