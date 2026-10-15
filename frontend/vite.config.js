import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The browser only talks to Vite (port 5173); Vite forwards /api to FastAPI.
    // Same origin as production, so no CORS and the session cookie just works.
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
