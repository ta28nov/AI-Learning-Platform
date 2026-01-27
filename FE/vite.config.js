import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// Cau hinh Vite cho du an JavaScript + CSS thuan
export default defineConfig({
  plugins: [react()],
  
  // Cau hinh duong dan goc
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@services': resolve(__dirname, 'src/services'),
      '@stores': resolve(__dirname, 'src/stores'),
      '@styles': resolve(__dirname, 'src/styles'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@contexts': resolve(__dirname, 'src/contexts')
    }
  },

  // Cau hinh server phat trien
  server: {
    port: 3000,
    host: true,
    open: true
  },

  // Cau hinh build
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          utils: ['axios', 'zustand']
        }
      }
    }
  },

  // Cau hinh CSS
  css: {
    devSourcemap: true
  }
})