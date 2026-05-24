import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { inventarioAPI, almacenAPI } from '@/api'

export const useInventarioStore = defineStore('inventario', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  const filtroTipo = ref('')
  const filtroCategoria = ref('')
  const soloConStock = ref(false)
  const busquedaTexto = ref('')

  const itemsFiltrados = computed(() => {
    let result = items.value
    if (filtroTipo.value) result = result.filter(i => i.tipo_material === filtroTipo.value)
    if (filtroCategoria.value) result = result.filter(i => i.categoria_id === Number(filtroCategoria.value))
    if (soloConStock.value) result = result.filter(i => i.cant_disponible > 0)
    if (busquedaTexto.value) {
      const q = busquedaTexto.value.toLowerCase()
      result = result.filter(i =>
        i.nombre?.toLowerCase().includes(q) ||
        i.codigo_interno?.toLowerCase().includes(q)
      )
    }
    return result
  })

  async function fetchAll(params = {}) {
    loading.value = true
    error.value = null
    try {
      const { data } = await inventarioAPI.get(params)
      items.value = data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al cargar inventario'
    } finally {
      loading.value = false
    }
  }

  async function buscar(shortCode) {
    const { data } = await inventarioAPI.buscar(shortCode)
    return data
  }

  async function checkOut(data) {
    const res = await almacenAPI.checkOut(data)
    return res.data
  }

  async function checkIn(data) {
    const res = await almacenAPI.checkIn(data)
    return res.data
  }

  function setFiltroTipo(val) { filtroTipo.value = val }
  function setFiltroCategoria(val) { filtroCategoria.value = val }
  function setSoloConStock(val) { soloConStock.value = val }
  function setBusquedaTexto(val) { busquedaTexto.value = val }

  function $reset() {
    items.value = []
    loading.value = false
    error.value = null
    filtroTipo.value = ''
    filtroCategoria.value = ''
    soloConStock.value = false
    busquedaTexto.value = ''
  }

  return {
    items,
    loading,
    error,
    filtroTipo,
    filtroCategoria,
    soloConStock,
    busquedaTexto,
    itemsFiltrados,
    fetchAll,
    buscar,
    checkOut,
    checkIn,
    setFiltroTipo,
    setFiltroCategoria,
    setSoloConStock,
    setBusquedaTexto,
    $reset,
  }
})
