/**
 * useDevolucionMasivo — Composable para Devolución Masiva
 *
 * Carga las herramientas en uso de un grupo desde GET /api/inventario/en-uso/grupo/{id}
 * y construye la lista editable para el check-in masivo.
 *
 * Incluye computed de filtro local (búsqueda sobre los ítems cargados sin re-fetch).
 */

import { ref, computed, readonly } from 'vue'
import { api } from '@/api'

// ── Estado global del módulo ──────────────────────────────────────────────────
const grupoId       = ref(null)
const paradaId      = ref(null)
const grupoNombre   = ref('')
const paradaNombre  = ref('')

// Items cargados del backend (herramientas en uso del grupo)
const items = ref([])
/*
  Estructura de cada item:
  {
    catalogo_id:       int,
    codigo_interno:    string,
    nombre:            string,        (nombre_herramienta en respuesta)
    descripcion:       string|null,
    marca:             string|null,
    costo_reposicion:  float|null,
    cantidad_en_uso:   int,           (cantidad máxima a devolver)
    dias_en_uso:       int,
    ultima_entrega:    string (ISO),

    // Campos editables por el operario
    cantidad_devuelta: int,           (editable, 1..cantidad_en_uso)
    estado:            string,        ('Operativa' | 'Malograda' | 'Perdida')
    observacion:       string,

    // Control de UI
    seleccionado:      boolean,
    _error:            string|null,
  }
*/

// Filtro local de búsqueda (no hace re-fetch)
const busquedaLocal = ref('')

const cargando    = ref(false)
const enviando    = ref(false)
const resultado   = ref(null)   // { procesados, mensaje }
const errorApi    = ref(null)
const errorCarga  = ref(null)

// ── Estados de retorno disponibles ────────────────────────────────────────────
export const ESTADOS_RETORNO = [
  { value: 'Operativa', label: 'Operativa' },
  { value: 'Malograda', label: 'Malograda' },
  { value: 'Perdida',   label: 'Perdida' },
]

// ── Computed ──────────────────────────────────────────────────────────────────

/**
 * Filtro LOCAL sobre los items ya cargados.
 * Busca por nombre o código_interno sin hacer requests adicionales.
 */
const itemsFiltrados = computed(() => {
  if (!busquedaLocal.value.trim()) return items.value
  const q = busquedaLocal.value.toLowerCase().trim()
  return items.value.filter(
    (i) =>
      i.nombre.toLowerCase().includes(q) ||
      i.codigo_interno.toLowerCase().includes(q),
  )
})

/** Items marcados para devolver */
const itemsSeleccionados = computed(() =>
  items.value.filter((i) => i.seleccionado)
)

/** ¿Todos los ítems visibles (filtrados) están seleccionados? */
const todosSeleccionados = computed(() => {
  const visible = itemsFiltrados.value
  return visible.length > 0 && visible.every((i) => i.seleccionado)
})

/** ¿Hay algún error de validación? */
const tieneErrores = computed(() =>
  items.value.some((i) => i._error)
)

/** Payload para POST /api/inventario/check-in-masivo */
const payloadMasivo = computed(() => ({
  grupo_id:  grupoId.value,
  parada_id: paradaId.value,
  items: itemsSeleccionados.value.map((i) => ({
    catalogo_id:       i.catalogo_id,
    cantidad_devuelta: i.cantidad_devuelta,
    estado:            i.estado,
    observacion:       i.observacion || null,
  })),
}))

// ── Acciones ──────────────────────────────────────────────────────────────────

/**
 * Carga la lista de herramientas en uso del grupo desde el backend.
 * GET /api/inventario/en-uso/grupo/{grupo_id}
 */
async function cargarHerramientasEnUso(gId, pId, gNom, pNom) {
  grupoId.value      = gId
  paradaId.value     = pId
  grupoNombre.value  = gNom
  paradaNombre.value = pNom
  busquedaLocal.value = ''
  errorCarga.value   = null
  errorApi.value     = null
  resultado.value    = null

  cargando.value = true
  try {
    const { data } = await api.get(`/inventario/en-uso/grupo/${gId}`)
    // Mapear la respuesta del backend al formato interno de UI
    items.value = data.map((h) => ({
      catalogo_id:       h.catalogo_id,
      codigo_interno:    h.codigo_interno,
      nombre:            h.nombre_herramienta,
      descripcion:       h.descripcion ?? null,
      marca:             h.marca ?? null,
      costo_reposicion:  h.costo_reposicion ?? null,
      cantidad_en_uso:   h.cantidad_en_uso,
      dias_en_uso:       h.dias_en_uso ?? 0,
      ultima_entrega:    h.ultima_entrega ?? null,

      // Campos editables (estado inicial seguro)
      cantidad_devuelta: h.cantidad_en_uso,
      estado:            'Operativa',
      observacion:       '',

      // Control
      seleccionado: false,
      _error:       null,
    }))
  } catch (err) {
    errorCarga.value = err.response?.data?.detail || 'Error al cargar herramientas en uso del grupo.'
    items.value = []
  } finally {
    cargando.value = false
  }
}

/**
 * Valida un item y actualiza su _error.
 * El bloqueo del checkbox se refleja reactivamente en la vista.
 * @param {Object} item
 */
function validarItem(item) {
  if (item.cantidad_devuelta < 1) item.cantidad_devuelta = 1
  if (item.cantidad_devuelta > item.cantidad_en_uso) {
    item._error = `Máx: ${item.cantidad_en_uso}`
  } else {
    item._error = null
  }
}

/** Toggle selección de todos los ítems visibles (filtrados) */
function toggleTodos() {
  const visible  = itemsFiltrados.value.filter((i) => !i._error)
  const todasOn  = visible.every((i) => i.seleccionado)
  visible.forEach((i) => { i.seleccionado = !todasOn })
}

/**
 * Ejecuta el check-in masivo.
 * UN único request al backend — transacción atómica.
 * @returns {Promise<{ procesados, mensaje }>}
 */
async function ejecutarDevolucion() {
  if (itemsSeleccionados.value.length === 0) throw new Error('Selecciona al menos una herramienta.')
  if (tieneErrores.value) throw new Error('Corrige los errores antes de continuar.')

  enviando.value = true
  errorApi.value = null
  resultado.value = null

  try {
    const { data } = await api.post('/inventario/check-in-masivo', payloadMasivo.value)
    resultado.value = data
    return data
  } catch (err) {
    const detail = err.response?.data?.detail || 'Error inesperado en la devolución masiva.'
    errorApi.value = detail
    throw new Error(detail)
  } finally {
    enviando.value = false
  }
}

/** Limpia el error API (mutación interna segura, respeta readonly externo) */
function clearError() {
  errorApi.value = null
}

/** Reset completo */
function resetear() {
  grupoId.value       = null
  paradaId.value      = null
  grupoNombre.value   = ''
  paradaNombre.value  = ''
  items.value         = []
  busquedaLocal.value = ''
  cargando.value      = false
  enviando.value      = false
  resultado.value     = null
  errorApi.value      = null
  errorCarga.value    = null
}

// ── Export ────────────────────────────────────────────────────────────────────
export function useDevolucionMasivo() {
  return {
    // Estado
    grupoId:          readonly(grupoId),
    paradaId:         readonly(paradaId),
    grupoNombre:      readonly(grupoNombre),
    paradaNombre:     readonly(paradaNombre),
    items,
    busquedaLocal,    // mutable: el input de búsqueda escribe aquí
    cargando:         readonly(cargando),
    enviando:         readonly(enviando),
    resultado:        readonly(resultado),
    errorApi:         readonly(errorApi),
    errorCarga:       readonly(errorCarga),

    // Computed
    itemsFiltrados,
    itemsSeleccionados,
    todosSeleccionados,
    tieneErrores,
    payloadMasivo,

    // Acciones
    clearError,
    cargarHerramientasEnUso,
    validarItem,
    toggleTodos,
    ejecutarDevolucion,
    resetear,
  }
}
