import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider } from '@/contexts/AuthContext';
import { Layout } from '@/components/Layout';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ProductosPage } from '@/pages/ProductosPage';
import { ClientesPage } from '@/pages/ClientesPage';
import { ProveedoresPage } from '@/pages/ProveedoresPage';
import { VentasPage } from '@/pages/VentasPage';
import { ComprasPage } from '@/pages/ComprasPage';
import { MetricasPage } from '@/pages/MetricasPage';
import { ReportesPage } from '@/pages/ReportesPage';
import { ConfiguracionPage } from '@/pages/ConfiguracionPage';
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
              
              {/* Ruta por defecto */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;



