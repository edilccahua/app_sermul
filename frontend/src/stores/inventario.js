/**
 * Store: Inventario Físico
 * Cache de unidades físicas con soporte de filtros.
 * Se invalida automáticamente después de un check-in/out.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { inventarioAPI, almacenAPI } from '@/api'

export const useInventarioStore = defineStore('inventario', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)

  // Filtros activos
  const filtroEstado = ref('')
  const filtroUbicacion = ref('')

  // ── Computed ─────────────────────────────────────────────
  const itemsFiltrados = computed(() => {
    return items.value.filter((item) => {
      const matchEstado = !filtroEstado.value || item.estado === filtroEstado.value
      const matchUbicacion =
        !filtroUbicacion.value || item.ubicacion_macro === filtroUbicacion.value
      return matchEstado && matchUbicacion
    })
  })

  const disponiblesEnMina = computed(() =>
    items.value.filter(
      (i) => i.estado === 'Disponible' && i.ubicacion_macro === 'Mina',
    ),
  )

  // ── Actions ───────────────────────────────────────────────
  async function fetchAll(params = {}) {
    loading.value = true
    error.value = null
    try {
      const { data } = await inventarioAPI.get(params)
      items.value = data
      lastFetch.value = Date.now()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar inventario'
    } finally {
      loading.value = false
    }
  }

  /**
   * Busca unidades disponibles en Mina para un short_code.
   * Retorna array de InventarioResponse.
   */
  async function buscarPorShortCode(shortCode) {
    const { data } = await inventarioAPI.buscar(shortCode)
    return data
  }

  /**
   * Ejecuta check-out y refresca el inventario.
   * @returns { movimiento, unidad }
   */
  async function checkOut(payload) {
    const { data } = await almacenAPI.checkOut(payload)
    // Actualizar la unidad en caché
    const idx = items.value.findIndex((i) => i.id === data.unidad.id)
    if (idx !== -1) items.value[idx] = data.unidad
    return data
  }

  /**
   * Ejecuta check-in y refresca el inventario.
   * @returns { movimiento, unidad }
   */
  async function checkIn(payload) {
    const { data } = await almacenAPI.checkIn(payload)
    const idx = items.value.findIndex((i) => i.id === data.unidad.id)
    if (idx !== -1) items.value[idx] = data.unidad
    return data
  }

  async function cambiarUbicacion(id, ubicacionMacro) {
    const { data } = await inventarioAPI.cambiarUbicacion(id, ubicacionMacro)
    const idx = items.value.findIndex((i) => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  function setFiltroEstado(val) { filtroEstado.value = val }
  function setFiltroUbicacion(val) { filtroUbicacion.value = val }

  function $reset() {
    items.value = []
    loading.value = false
    error.value = null
    lastFetch.value = null
    filtroEstado.value = ''
    filtroUbicacion.value = ''
  }

  return {
    items,
    loading,
    error,
    filtroEstado,
    filtroUbicacion,
    itemsFiltrados,
    disponiblesEnMina,
    fetchAll,
    buscarPorShortCode,
    checkOut,
    checkIn,
    cambiarUbicacion,
    setFiltroEstado,
    setFiltroUbicacion,
    $reset,
  }
})
