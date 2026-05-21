/**
 * Store: Paradas de Planta
 * Cache de paradas. Expone `paradaActiva` para el check-out.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { paradasAPI } from '@/api'

const CACHE_TTL = 120_000 // 2 minutos

export const useParadasStore = defineStore('paradas', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)

  // ── Computed ─────────────────────────────────────────────
  const paradaActiva = computed(() =>
    items.value.find((p) => p.estado === 'Activa') || null,
  )

  const paradasActivas = computed(() =>
    items.value.filter((p) => p.estado === 'Activa'),
  )

  // ── Actions ───────────────────────────────────────────────
  async function fetchAll(force = false) {
    const stale = !lastFetch.value || Date.now() - lastFetch.value > CACHE_TTL
    if (!force && !stale && items.value.length > 0) return

    loading.value = true
    error.value = null
    try {
      const { data } = await paradasAPI.get()
      items.value = data
      lastFetch.value = Date.now()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar paradas'
    } finally {
      loading.value = false
    }
  }

  async function createParada(payload) {
    const { data } = await paradasAPI.create(payload)
    items.value.unshift(data)
    return data
  }

  async function updateParada(id, payload) {
    const { data } = await paradasAPI.update(id, payload)
    const idx = items.value.findIndex((p) => p.id === id)
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
    paradaActiva,
    paradasActivas,
    fetchAll,
    createParada,
    updateParada,
    $reset,
  }
})
