import { defineConfig } from "vite"

export default defineConfig({
  base: "",                       // <-- CLAVE: rutas relativas dentro del iframe
  server: { port: 5173, strictPort: true },
  build: {
    outDir: "dist",
    sourcemap: false
  }
})