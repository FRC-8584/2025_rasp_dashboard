import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "localhost",
    port: 3000
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/colors" as *;`
      }
    }
  },
  resolve: {
    alias: {
      "@": "/src"
    }
  },
})
