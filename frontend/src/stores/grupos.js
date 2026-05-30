/**
 * useGruposStore — Store de Grupos de Trabajo
 * Sprint 2: CRUD completo + gestión de integrantes
 *
 * Caché simple: si items ya está cargado y no se fuerza refresh,
 * no vuelve a llamar al backend.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { gruposAPI } from '@/api'

export const useGruposStore = defineStore('grupos', () => {
  const items = ref([])
  const grupoActual = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchAll(params = {}, force = false) {
    // Caché simple: si ya hay datos y no se fuerza, no volvemos a pedir
    if (items.value.length > 0 && !force && Object.keys(params).length === 0) return
    loading.value = true
    error.value = null
    try {
      const res = await gruposAPI.get(params)
      items.value = res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar grupos'
    } finally {
      loading.value = false
    }
  }

  async function fetchById(id) {
    loading.value = true
    error.value = null
    try {
      const res = await gruposAPI.getById(id)
      grupoActual.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar grupo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function create(data) {
    const res = await gruposAPI.create(data)
    items.value.unshift(res.data)
    return res.data
  }

  async function update(id, data) {
    const res = await gruposAPI.update(id, data)
    const idx = items.value.findIndex((g) => g.id === id)
    if (idx !== -1) items.value[idx] = res.data
    if (grupoActual.value?.id === id) grupoActual.value = res.data
    return res.data
  }

  async function addIntegrante(grupoId, usuarioId, esLiderFrente = false) {
    await gruposAPI.addIntegrante(grupoId, { usuario_id: usuarioId, es_lider_frente: esLiderFrente })
    if (grupoActual.value?.id === grupoId) {
      await fetchById(grupoId)
    }
  }

  async function removeIntegrante(grupoId, usuarioId) {
    await gruposAPI.removeIntegrante(grupoId, usuarioId)
    if (grupoActual.value?.id === grupoId) {
      await fetchById(grupoId)
    }
  }

  function reset() {
    items.value = []
    grupoActual.value = null
    error.value = null
  }

  return {
    items,
    grupoActual,
    loading,
    error,
    fetchAll,
    fetchById,
    create,
    update,
    addIntegrante,
    removeIntegrante,
    reset,
  }
})
