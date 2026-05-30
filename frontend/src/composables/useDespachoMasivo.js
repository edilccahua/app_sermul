/**
 * useDespachoMasivo — Composable para Despacho Masivo
 *
 * Gestiona la prelista (fusión reserva + items manuales) y envía un único
 * payload atómico a POST /api/inventario/check-out-masivo (Corrección A).
 *
 * NO usa Promise.all(items.map(checkOut)) — eso causaba N transacciones.
 * El backend garantiza atomicidad: si 1 falla, rollback de todos.
 */

import { ref, computed, readonly } from 'vue'
import { api } from '@/api'

// ── Estado global del módulo (singleton: comparte estado entre vista y header) ──
const grupoId       = ref(null)      // int: grupo seleccionado
const paradaId      = ref(null)      // int: parada activa
const grupoNombre   = ref('')        // string: para la UI
const paradaNombre  = ref('')        // string: para la UI

// Lista maestra fusionada: reserva pre-seleccionada + adiciones manuales
const items = ref([])
/*
  Estructura de cada item:
  {
    catalogo_id:        int,
    codigo_interno:     string,
    nombre:             string,
    descripcion:        string|null,
    marca:              string|null,
    cant_disponible:    int,       // stock actual leído del backend
    cantidad:           int,       // cantidad que se va a despachar (editable)
    observacion:        string,    // observación de entrega (opcional)
    origen:             'reserva' | 'manual',
    seleccionado:       boolean,   // checkbox de la fila
    _error:             string|null, // error de validación inline (supera stock)
  }
*/

const enviando      = ref(false)
const resultado     = ref(null)   // { procesados, mensaje } — respuesta exitosa
const errorApi      = ref(null)   // string — error global de la API

// ── Computed ──────────────────────────────────────────────────────────────────

/** Items marcados como seleccionados (irán en el payload) */
const itemsSeleccionados = computed(() =>
  items.value.filter((i) => i.seleccionado)
)

/** ¿Todos los ítems válidos están seleccionados? */
const todosSeleccionados = computed(() => {
  const validos = items.value.filter((i) => i.cant_disponible > 0)
  return validos.length > 0 && validos.every((i) => i.seleccionado)
})

/** ¿Hay algún error de validación activo? */
const tieneErrores = computed(() =>
  items.value.some((i) => i._error)
)

/** Payload listo para enviar al backend (Corrección A: único objeto) */
const payloadMasivo = computed(() => ({
  grupo_id:  grupoId.value,
  parada_id: paradaId.value,
  items: itemsSeleccionados.value.map((i) => ({
    catalogo_id:        i.catalogo_id,
    cantidad:           i.cantidad,
    observacion_entrega: i.observacion || null,
  })),
}))

// ── Acciones ──────────────────────────────────────────────────────────────────

/**
 * Inicializa el estado con un grupo/parada y una prelista (de reserva o vacía).
 * Los items de la prelista llegan con `seleccionado: true` por defecto si tienen stock.
 * @param {Object} opts - { grupoId, paradaId, grupoNombre, paradaNombre, prelista }
 * @param {Array}  opts.prelista - Items de la reserva pre-aprobada (puede ser [])
 */
function inicializar({ grupoId: gId, paradaId: pId, grupoNombre: gNom, paradaNombre: pNom, prelista = [] }) {
  grupoId.value     = gId
  paradaId.value    = pId
  grupoNombre.value = gNom
  paradaNombre.value = pNom
  errorApi.value    = null
  resultado.value   = null

  // Mapear prelista a nuestro formato interno — checks inician desmarcados
  items.value = prelista.map((detalle) => ({
    catalogo_id:     detalle.catalogo_id ?? detalle.catalogo?.id,
    codigo_interno:  detalle.catalogo?.codigo_interno ?? detalle.codigo_interno ?? '—',
    nombre:          detalle.catalogo?.nombre ?? detalle.nombre ?? '—',
    descripcion:     detalle.catalogo?.descripcion ?? detalle.descripcion ?? null,
    marca:           detalle.catalogo?.marca ?? detalle.marca ?? null,
    cant_disponible: detalle.cant_disponible ?? detalle.cantidad_disponible ?? 0,
    cantidad:        Math.min(detalle.cantidad ?? 1, detalle.cant_disponible ?? detalle.cantidad_disponible ?? 1),
    observacion:     '',
    origen:          'reserva',
    seleccionado:    false,
    _error:          null,
  }))
}

/**
 * Agrega un item manualmente (desde búsqueda por short code).
 * Si el catalogo_id ya está en la lista, incrementa la cantidad en su lugar.
 * @param {Object} material - { id, codigo_interno, nombre, cant_disponible }
 */
function agregarItemManual(material) {
  const existente = items.value.find((i) => i.catalogo_id === material.id)
  if (existente) {
    // Incrementar cantidad en lugar de duplicar fila
    const nueva = existente.cantidad + 1
    existente.cantidad = Math.min(nueva, material.cant_disponible)
    existente.seleccionado = true
    validarItem(existente)
    return
  }
  items.value.push({
    catalogo_id:     material.id,
    codigo_interno:  material.codigo_interno,
    nombre:          material.nombre,
    descripcion:     material.descripcion ?? null,
    marca:           material.marca ?? null,
    cant_disponible: material.cant_disponible,
    cantidad:        1,
    observacion:     '',
    origen:          'manual',
    seleccionado:    material.cant_disponible > 0,
    _error:          null,
  })
}

/**
 * Elimina un item manual de la lista.
 * Los items de reserva no se eliminan, solo se desmarcan.
 * @param {number} catalogoId
 */
function quitarItem(catalogoId) {
  const idx = items.value.findIndex((i) => i.catalogo_id === catalogoId)
  if (idx === -1) return
  const item = items.value[idx]
  if (item.origen === 'manual') {
    items.value.splice(idx, 1)
  } else {
    item.seleccionado = false
  }
}

/**
 * Valida un item: actualiza _error si la cantidad supera el stock disponible.
 * La reactividad de Vue hace que el checkbox y el input se pinten automáticamente.
 * @param {Object} item - referencia reactiva al item
 */
function validarItem(item) {
  if (item.cantidad < 1) {
    item.cantidad = 1
  }
  if (item.cantidad > item.cant_disponible) {
    item._error = `Máx: ${item.cant_disponible}`
  } else {
    item._error = null
  }
}

/**
 * Cambia el estado del checkbox de todos los ítems válidos.
 */
function toggleTodos() {
  const validos = items.value.filter((i) => i.cant_disponible > 0 && !i._error)
  const todasMarcadas = validos.every((i) => i.seleccionado)
  validos.forEach((i) => { i.seleccionado = !todasMarcadas })
}

/**
 * ── CORRECCIÓN A ──────────────────────────────────────────────────────────────
 * Envía UN ÚNICO request con todo el lote. El backend garantiza atomicidad.
 * NO usar Promise.all(items.map(checkOut)) — cada call sería una transacción
 * separada y podría resultar en éxitos parciales.
 *
 * @returns {Promise<{ procesados: number, mensaje: string }>}
 * @throws  Error con el detail del backend si algo falla
 */
async function ejecutarDespacho() {
  if (itemsSeleccionados.value.length === 0) return
  if (tieneErrores.value) throw new Error('Corrige los errores de validación antes de continuar.')
  if (!grupoId.value || !paradaId.value) throw new Error('Grupo o parada no configurados.')

  enviando.value = true
  errorApi.value = null
  resultado.value = null

  try {
    const { data } = await api.post('/inventario/check-out-masivo', payloadMasivo.value)
    resultado.value = data
    return data
  } catch (err) {
    const detail = err.response?.data?.detail || 'Error inesperado en el despacho masivo.'
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

/** Reset completo del estado del módulo */
function resetear() {
  grupoId.value      = null
  paradaId.value     = null
  grupoNombre.value  = ''
  paradaNombre.value = ''
  items.value        = []
  enviando.value     = false
  resultado.value    = null
  errorApi.value     = null
}

// ── Export ────────────────────────────────────────────────────────────────────
export function useDespachoMasivo() {
  return {
    // Estado (readonly para evitar mutaciones accidentales fuera del composable)
    grupoId:           readonly(grupoId),
    paradaId:          readonly(paradaId),
    grupoNombre:       readonly(grupoNombre),
    paradaNombre:      readonly(paradaNombre),
    items,                   // mutable: la tabla edita cantidad / observacion
    enviando:          readonly(enviando),
    resultado:         readonly(resultado),
    errorApi:          readonly(errorApi),

    // Computed
    itemsSeleccionados,
    todosSeleccionados,
    tieneErrores,
    payloadMasivo,

    // Acciones
    clearError,
    inicializar,
    agregarItemManual,
    quitarItem,
    validarItem,
    toggleTodos,
    ejecutarDespacho,
    resetear,
  }
}
