/**
 * useDashboardStore — Store del Dashboard Residente
 * Sprint 2: KPIs, gráficos y alertas para Residente/Admin
 *
 * Incluye lastFetch para controlar el refresh automático de 60s.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dashboardAPI } from '@/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const metricas = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastFetch = ref(null)

  // True si los datos tienen más de 60 segundos
  const isStale = computed(() => {
    if (!lastFetch.value) return true
    return Date.now() - lastFetch.value > 60_000
  })

  async function fetchResidente(force = false) {
    if (!force && !isStale.value) return
    loading.value = true
    error.value = null
    try {
      const res = await dashboardAPI.residente()
      metricas.value = res.data
      lastFetch.value = Date.now()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar dashboard'
    } finally {
      loading.value = false
    }
  }

  function reset() {
    metricas.value = null
    lastFetch.value = null
    error.value = null
  }

  return {
    metricas,
    loading,
    error,
    lastFetch,
    isStale,
    fetchResidente,
    reset,
  }
})
