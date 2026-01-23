/// <reference types="vitest" />

import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 5173,
    allowedHosts: ["agridao.cloudninjabd.com", "www.agridao.cloudninjabd.com", "frontend"],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/uploads': {
        target: 'http://backend:8000',
        changeOrigin: true,
      }
    },
    headers: {
      'Content-Security-Policy': `
        default-src 'self';
        script-src 'self' 'unsafe-eval' 'unsafe-inline';
        style-src 'self' 'unsafe-inline';
        img-src 'self' data: https:;
        font-src 'self';
        connect-src 'self' http://localhost:* http://127.0.0.1:* http://backend:8000 https: ws: wss:;
        frame-src 'self';
        media-src 'self';
        object-src 'none';
      `.replace(/\s+/g, ' ').trim()
    }
  },
  plugins: [
    react(),
  ].filter(Boolean),
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    include: ['ethers'],
  },
}));
