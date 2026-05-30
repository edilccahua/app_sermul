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
  const sinStock = ref(false)
  const busquedaTexto = ref('')
  
  const sortColumn = ref('codigo')
  const sortDesc = ref(false)

  const itemsFiltrados = computed(() => {
    let result = items.value
    if (filtroTipo.value) result = result.filter(i => i.tipo_material === filtroTipo.value)
    if (filtroCategoria.value) result = result.filter(i => i.categoria_id === Number(filtroCategoria.value))
    
    if (soloConStock.value && !sinStock.value) {
      result = result.filter(i => (i.cant_disponible ?? 0) > 0)
    } else if (!soloConStock.value && sinStock.value) {
      result = result.filter(i => (i.cant_disponible ?? 0) === 0)
    }
    if (busquedaTexto.value) {
      const q = busquedaTexto.value.toLowerCase()
      result = result.filter(i =>
        i.nombre?.toLowerCase().includes(q) ||
        i.codigo_interno?.toLowerCase().includes(q)
      )
    }

    if (sortColumn.value) {
      result.sort((a, b) => {
        let valA = 0; let valB = 0;
        switch (sortColumn.value) {
          case 'codigo': valA = a.codigo_interno || ''; valB = b.codigo_interno || ''; break;
          case 'nombre': valA = a.nombre || ''; valB = b.nombre || ''; break;
          case 'categoria': valA = a.categoria?.nombre || ''; valB = b.categoria?.nombre || ''; break;
          case 'disponible': valA = a.cant_disponible ?? 0; valB = b.cant_disponible ?? 0; break;
          case 'uso': valA = a.cant_en_uso ?? 0; valB = b.cant_en_uso ?? 0; break;
          case 'malograda': valA = a.cant_malograda ?? 0; valB = b.cant_malograda ?? 0; break;
          case 'perdida': valA = a.cant_perdida ?? 0; valB = b.cant_perdida ?? 0; break;
          case 'total':
            valA = (a.cant_disponible ?? 0) + (a.cant_en_uso ?? 0) + (a.cant_malograda ?? 0) + (a.cant_perdida ?? 0);
            valB = (b.cant_disponible ?? 0) + (b.cant_en_uso ?? 0) + (b.cant_malograda ?? 0) + (b.cant_perdida ?? 0);
            break;
        }
        if (typeof valA === 'string') {
          return sortDesc.value ? String(valB).localeCompare(String(valA)) : String(valA).localeCompare(String(valB));
        }
        if (valA > valB) return sortDesc.value ? -1 : 1;
        if (valA < valB) return sortDesc.value ? 1 : -1;
        return 0;
      })
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

  async function ajustarStock(data) {
    const res = await inventarioAPI.ajustarStock(data)
    const idx = items.value.findIndex(i => i.id === res.data.id)
    if (idx !== -1) {
      items.value[idx] = res.data
    }
    return res.data
  }

  function setFiltroTipo(val) { filtroTipo.value = val }
  function setFiltroCategoria(val) { filtroCategoria.value = val }
  function setSoloConStock(val) { soloConStock.value = val }
  function setSinStock(val) { sinStock.value = val }
  function setBusquedaTexto(val) { busquedaTexto.value = val }

  function toggleSort(col) {
    if (sortColumn.value === col) {
      sortDesc.value = !sortDesc.value
    } else {
      sortColumn.value = col
      sortDesc.value = !['codigo', 'nombre', 'categoria'].includes(col)
    }
  }

  function $reset() {
    items.value = []
    loading.value = false
    error.value = null
    filtroTipo.value = ''
    filtroCategoria.value = ''
    soloConStock.value = false
    sinStock.value = false
    busquedaTexto.value = ''
    sortColumn.value = 'codigo'
    sortDesc.value = false
  }

  return {
    items,
    loading,
    error,
    filtroTipo,
    filtroCategoria,
    soloConStock,
    sinStock,
    busquedaTexto,
    sortColumn,
    sortDesc,
    itemsFiltrados,
    fetchAll,
    buscar,
    checkOut,
    checkIn,
    ajustarStock,
    setFiltroTipo,
    setFiltroCategoria,
    setSoloConStock,
    setSinStock,
    setBusquedaTexto,
    toggleSort,
    $reset,
  }
})
