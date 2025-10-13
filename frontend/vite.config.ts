import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
// Permite configurar el target del backend via env (útil en Docker)
const backendTarget = process.env.BACKEND_URL || 'http://localhost:8000'

console.log('Backend target:', backendTarget)

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      // Proxy para todas las rutas de la API
      '/auth': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/usuarios': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/productos': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/clientes': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/proveedores': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/compras': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/ventas': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/inventario': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/notificaciones': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/dashboard': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/reportes': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/metricas': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/backup': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/docs': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/openapi.json': {
        target: backendTarget,
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
