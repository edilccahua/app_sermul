/**
 * SERMUL — API Service Layer
 * Sprint 1: Catálogo, Inventario, Check-in/out, Paradas, Historial
 *
 * Instancia axios compartida con interceptor de auth.
 * Todos los módulos usan esta misma instancia base.
 */
import axios from 'axios'

// ─── Instancia base ────────────────────────────────────────────────────────────
export const api = axios.create({
  baseURL: '/api',
  timeout: 10_000,
})

// Interceptor de request: inyecta token JWT en cada llamada
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor de response: normaliza errores de auth
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido — limpiar sesión
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

// ─── Catálogo ──────────────────────────────────────────────────────────────────
// GET /api/catalogo          → lista completa de materiales
// GET /api/catalogo/search   → búsqueda por texto libre (q=...)
// GET /api/catalogo/:id      → detalle de un material
// POST /api/catalogo         → crear material (requiere EDITAR_INVENTARIO)
// PUT  /api/catalogo/:id     → editar material (requiere EDITAR_INVENTARIO)
export const catalogoAPI = {
  get: () => api.get('/catalogo/'),
  search: (q) => api.get('/catalogo/search', { params: { q } }),
  getById: (id) => api.get(`/catalogo/${id}`),
  create: (data) => api.post('/catalogo/', data),
  update: (id, data) => api.put(`/catalogo/${id}`, data),
}

// ─── Inventario Físico ─────────────────────────────────────────────────────────
// GET /api/inventario                    → lista con filtros opcionales
// GET /api/inventario/buscar?short_code= → búsqueda por short code (para almacén)
// GET /api/inventario/:id                → detalle de unidad física
// PUT /api/inventario/:id/ubicacion      → cambiar ubicación macro
export const inventarioAPI = {
  get: (params = {}) => api.get('/inventario/', { params }),
  buscar: (shortCode) => api.get('/inventario/buscar', { params: { short_code: shortCode } }),
  getById: (id) => api.get(`/inventario/${id}`),
  cambiarUbicacion: (id, ubicacionMacro) =>
    api.put(`/inventario/${id}/ubicacion`, { ubicacion_macro: ubicacionMacro }),
}

// ─── Check-in / Check-out ──────────────────────────────────────────────────────
// POST /api/inventario/check-out → { short_code, grupo_id, parada_id }
//   Respuesta: { movimiento, unidad }
//   Errores: 400 (sin unidades disponibles), 404 (código/grupo/parada no existe)
//
// POST /api/inventario/check-in  → { inventario_id, buen_estado, dano? }
//   Respuesta: { movimiento, unidad }
//   Errores: 400 (unidad no está En_Uso), 404 (unidad no existe)
export const almacenAPI = {
  checkOut: ({ short_code, grupo_id, parada_id }) =>
    api.post('/inventario/check-out', { short_code, grupo_id, parada_id }),
  checkIn: ({ inventario_id, buen_estado, dano }) =>
    api.post('/inventario/check-in', { inventario_id, buen_estado, dano }),
}

// ─── Paradas ───────────────────────────────────────────────────────────────────
// GET  /api/paradas      → lista completa
// GET  /api/paradas/:id  → detalle
// POST /api/paradas      → crear (requiere CREAR_PARADA: RESIDENTE, ADMIN)
// PUT  /api/paradas/:id  → editar (requiere CREAR_PARADA)
export const paradasAPI = {
  get: () => api.get('/paradas/'),
  getById: (id) => api.get(`/paradas/${id}`),
  create: (data) => api.post('/paradas/', data),
  update: (id, data) => api.put(`/paradas/${id}`, data),
}

// ─── Historial de Movimientos ──────────────────────────────────────────────────
// GET /api/historial → lista con filtros opcionales
//   Query params: parada_id, tipo, fecha_desde, fecha_hasta
//   Máx 500 registros, orden timestamp DESC
export const historialAPI = {
  get: (params = {}) => api.get('/historial/', { params }),
}

// ─── Grupos de Trabajo ─────────────────────────────────────────────────────────
// NOTA: GET /api/grupos NO existe en Sprint 1 (se implementa en Sprint 2).
// Workaround: usar el seed GRP-001 (id=1) para pruebas de check-out.
// Al implementar Sprint 2, reemplazar el workaround en CheckOutSheet.
export const gruposAPI = {
  get: () => api.get('/grupos'),
}

export default api
