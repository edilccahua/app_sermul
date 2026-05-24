/**
 * useReservasStore — Store de Reservas
 * Sprint 2: Workflow completo Pendiente → Aprobada → Despachada / Rechazada
 *
 * Sin caché: los estados cambian frecuentemente (aprobar, rechazar, despachar).
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reservasAPI } from '@/api'

export const useReservasStore = defineStore('reservas', () => {
  const items = ref([])
  const reservaActual = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchAll(params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await reservasAPI.get(params)
      items.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar reservas'
    } finally {
      loading.value = false
    }
  }

  async function fetchById(id) {
    loading.value = true
    error.value = null
    try {
      const res = await reservasAPI.getById(id)
      reservaActual.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar reserva'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function create(data) {
    const res = await reservasAPI.create(data)
    items.value.unshift(res.data)
    return res.data
  }

  // Actualiza el item en la lista local tras cambio de estado
  function _actualizarEnLista(reservaActualizada) {
    const idx = items.value.findIndex((r) => r.id === reservaActualizada.id)
    if (idx !== -1) items.value[idx] = reservaActualizada
    if (reservaActual.value?.id === reservaActualizada.id) {
      reservaActual.value = reservaActualizada
    }
  }

  async function aprobar(id) {
    const res = await reservasAPI.aprobar(id)
    _actualizarEnLista(res.data)
    return res.data
  }

  async function rechazar(id, motivo) {
    const res = await reservasAPI.rechazar(id, motivo)
    _actualizarEnLista(res.data)
    return res.data
  }

  async function despachar(id, itemsIds = null) {
    const payload = itemsIds ? { items_ids: itemsIds } : {}
    const res = await reservasAPI.despachar(id, payload)
    _actualizarEnLista(res.data)
    return res.data
  }

  function reset() {
    items.value = []
    reservaActual.value = null
    error.value = null
  }

  return {
    items,
    reservaActual,
    loading,
    error,
    fetchAll,
    fetchById,
    create,
    aprobar,
    rechazar,
    despachar,
    reset,
  }
})
