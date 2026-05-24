/**
 * Store: Catálogo de Materiales
 * Cache en memoria con TTL de 60 segundos.
 * Evita requests repetidos mientras el usuario navega entre vistas.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { catalogoAPI } from '@/api'

const CACHE_TTL = 60_000 // 60 segundos

export const useCatalogoStore = defineStore('catalogo', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)

  // ── Getters computados ────────────────────────────────────
  function getById(id) {
    return items.value.find((i) => i.id === id) || null
  }

  function getByCodigoInterno(codigo) {
    return items.value.find(
      (i) => i.codigo_interno.toLowerCase() === codigo.toLowerCase(),
    ) || null
  }

  // ── Actions ───────────────────────────────────────────────
  async function fetchAll(force = false) {
    const stale = !lastFetch.value || Date.now() - lastFetch.value > CACHE_TTL
    if (!force && !stale && items.value.length > 0) return

    loading.value = true
    error.value = null
    try {
      const { data } = await catalogoAPI.get()
      items.value = data
      lastFetch.value = Date.now()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar catálogo'
    } finally {
      loading.value = false
    }
  }

  async function createMaterial(payload) {
    const { data } = await catalogoAPI.create(payload)
    items.value.push(data)
    return data
  }

  async function updateMaterial(id, payload) {
    const { data } = await catalogoAPI.update(id, payload)
    const idx = items.value.findIndex((i) => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  async function updateStock(id, field, delta) {
    const { data } = await catalogoAPI.updateStock(id, field, delta)
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  function $reset() {
    items.value = []
    loading.value = false
    error.value = null
    lastFetch.value = null
  }

  return {
    items,
    loading,
    error,
    getById,
    getByCodigoInterno,
    fetchAll,
    createMaterial,
    updateMaterial,
    updateStock,
    $reset,
  }
})
