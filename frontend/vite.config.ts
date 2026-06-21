import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      // Self-destroying: ships a service worker that unregisters any previously
      // installed SW and clears its caches. This kills the stale-cache trap during
      // active development (old app being served after a deploy). Re-enable real
      // offline caching once the app stabilises by removing this flag.
      selfDestroying: true,
      manifest: {
        name: 'SickChill Modern',
        short_name: 'SickChill',
        description: 'Modern, mobile-first TV show automation',
        theme_color: '#0f172a',
        background_color: '#0f172a',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: 'pwa-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512.png', sizes: '512x512', type: 'image/png' },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // Proxy API calls to the backend during dev so there are no CORS hassles.
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true },
    },
  },
  build: {
    // Build straight into the backend's static dir so one container serves both.
    outDir: '../backend/static',
    emptyOutDir: true,
  },
})
