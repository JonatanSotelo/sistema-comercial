import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { 
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: true,           // equivale a 0.0.0.0
    port: 3000,
    strictPort: true,
    watch: { usePolling: true }, // Docker/WSL
    proxy: {
      // ajustá el path según tu backend (ej.: '/api')
      '/auth': { target: 'http://backend:8000', changeOrigin: true }
    }
  },
  preview: { host: true, port: 3000 }
})