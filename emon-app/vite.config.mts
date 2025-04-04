import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  //envDir: "/media/tepochtli/zino/Dev/python/mano8_repo/emon_tools/",
  server: {
    host: 'localhost',
    port: 5173,
  },
  base: "http://localhost:5173",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  esbuild: {
    drop: mode === 'production' ? ['console', 'debugger'] : [],
  },
  test: {
    globals: true,             // Enables global variables like describe, it, and expect
    environment: 'jsdom',      // Use jsdom to simulate a browser environment
    setupFiles: './src/setupTests.ts', // Optional: A setup file for extending matchers, etc.
    // You can also add include/exclude settings if needed:
    include: ['**/*.{test,spec}.{ts,tsx}'],
  },
}))
