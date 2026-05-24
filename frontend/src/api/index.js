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
  updateStock: (id, field, delta) =>
    api.put(`/catalogo/${id}/stock`, null, { params: { field, delta } }),
}

// ─── Inventario (StockResponse) ────────────────────────────────────────────────
// GET /api/inventario/                   → lista con filtros opcionales
// GET /api/inventario/buscar?short_code= → búsqueda por short code (devuelve StockResponse[])
export const inventarioAPI = {
  get: (params = {}) => api.get('/inventario/', { params }),
  buscar: (shortCode) => api.get('/inventario/buscar', { params: { short_code: shortCode } }),
}

// ─── Check-in / Check-out ──────────────────────────────────────────────────────
// POST /api/inventario/check-out → { catalogo_id, cantidad, grupo_id, parada_id, observacion_entrega? }
//   Respuesta plana: { movimiento_id, tipo, catalogo_id, cantidad, mensaje }
//
// POST /api/inventario/check-in  → { catalogo_id, cant_buen_estado, cant_malograda, observacion_recepcion?, descripcion_dano? }
//   Respuesta plana: { movimiento_id, tipo, catalogo_id, cantidad, mensaje }
export const almacenAPI = {
  checkOut: (data) => api.post('/inventario/check-out', data),
  checkIn: (data) => api.post('/inventario/check-in', data),
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
// GET    /api/grupos/                         → lista (filtros: ?parada_id=&estado=)
// GET    /api/grupos/:id                      → detalle con integrantes
// POST   /api/grupos/                         → crear
// PUT    /api/grupos/:id                      → editar
// POST   /api/grupos/importar-excel           → upload .xlsx + parada_id (Form)
// POST   /api/grupos/:id/integrantes          → agregar integrante
// DELETE /api/grupos/:id/integrantes/:uid     → remover integrante
export const gruposAPI = {
  get: (params = {}) => api.get('/grupos/', { params }),
  getById: (id) => api.get(`/grupos/${id}`),
  create: (data) => api.post('/grupos/', data),
  update: (id, data) => api.put(`/grupos/${id}`, data),
  importExcel: (formData) =>
    api.post('/grupos/importar-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  addIntegrante: (id, data) => api.post(`/grupos/${id}/integrantes`, data),
  removeIntegrante: (id, usuarioId) =>
    api.delete(`/grupos/${id}/integrantes/${usuarioId}`),
}

// ─── Reservas ──────────────────────────────────────────────────────────────────
// GET  /api/reservas/              → lista (filtros: ?grupo_id=&estado=&parada_id=)
// GET  /api/reservas/:id           → detalle con items + disponibilidad
// POST /api/reservas/              → crear (requiere CREAR_RESERVA)
// PUT  /api/reservas/:id           → editar (solo estado Pendiente)
// POST /api/reservas/:id/aprobar   → aprobar (requiere APROBAR_RESERVA)
// POST /api/reservas/:id/rechazar  → rechazar con motivo (requiere APROBAR_RESERVA)
// POST /api/reservas/:id/despachar → despachar (requiere CHECK_OUT)
export const reservasAPI = {
  get: (params = {}) => api.get('/reservas/', { params }),
  getById: (id) => api.get(`/reservas/${id}`),
  create: (data) => api.post('/reservas/', data),
  update: (id, data) => api.put(`/reservas/${id}`, data),
  aprobar: (id) => api.post(`/reservas/${id}/aprobar`),
  rechazar: (id, motivo) => api.post(`/reservas/${id}/rechazar`, { motivo }),
  despachar: (id, itemsIds) =>
    api.post(`/reservas/${id}/despachar`, { items_ids: itemsIds }),
}

// ─── Dashboards ────────────────────────────────────────────────────────────────
// GET /api/dashboards/residente → KPIs gerenciales + gráficos + alertas
//   Permiso: VER_DASHBOARD_COMPLETO
export const dashboardAPI = {
  residente: () => api.get('/dashboards/residente'),
}

export default api
