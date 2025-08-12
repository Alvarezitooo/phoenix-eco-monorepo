import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      // Proxy API calls vers le backend FastAPI Phoenix Rise
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      },
      // Proxy pour les API Dojo existantes
      '/kaizen': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      },
      '/zazen-session': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})