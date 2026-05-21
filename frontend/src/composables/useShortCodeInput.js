/**
 * useShortCodeInput — Composable de ventanilla de almacén
 *
 * REGLA DE ORO: El input NUNCA pierde el foco.
 * El almacenero opera 100% con teclado. Enter = confirmar, Escape = cancelar.
 *
 * Búsqueda dual: primero por short code exacto, si no hay resultados busca por nombre en catálogo.
 * Los resultados del catálogo vienen con _esSugerencia: true.
 */
import { ref, watch, onMounted, nextTick } from 'vue'
import { inventarioAPI, catalogoAPI } from '@/api'

export function useShortCodeInput({ onResult } = {}) {
  const inputRef = ref(null)
  const query = ref('')
  const results = ref([])
  const loading = ref(false)
  const error = ref(null)
  let debounceTimer = null

  onMounted(() => {
    nextTick(() => _focusInput())
  })

  function refocus() {
    nextTick(() => _focusInput())
  }

  function _focusInput() {
    const el = inputRef.value
    if (!el) return
    const target = el.$el ?? el
    target.focus()
    if (typeof target.select === 'function') target.select()
  }

  // ── Búsqueda dual: short code exacto → nombre catálogo ──
  watch(query, (val) => {
    clearTimeout(debounceTimer)
    error.value = null
    if (!val || val.trim().length < 2) {
      results.value = []
      return
    }
    loading.value = true
    debounceTimer = setTimeout(async () => {
      try {
        const q = val.trim()
        const res = await inventarioAPI.buscar(q)
        if (res.data.length > 0) {
          results.value = res.data
        } else {
          const catRes = await catalogoAPI.search(q)
          if (catRes.data.length > 0) {
            results.value = catRes.data.map((c) => ({
              id: null,
              catalogo_id: c.id,
              estado: 'Ver disponibilidad',
              ubicacion_macro: null,
              ubicacion_fisica: null,
              catalogo: c,
              _esSugerencia: true,
            }))
          } else {
            results.value = []
            error.value = `Sin resultados para "${q}"`
          }
        }
        if (typeof onResult === 'function') onResult(results.value)
      } catch (err) {
        results.value = []
        error.value = err.response?.data?.detail || 'Error al buscar herramienta'
      } finally {
        loading.value = false
      }
    }, 200)
  })

  function reset() {
    clearTimeout(debounceTimer)
    query.value = ''
    results.value = []
    loading.value = false
    error.value = null
    refocus()
  }

  return {
    inputRef,
    query,
    results,
    loading,
    error,
    reset,
    refocus,
  }
}
