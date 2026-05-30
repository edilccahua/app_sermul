import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // ── Estado ──────────────────────────────────────────────────────────────────
  // Persiste en localStorage. Valores válidos: 'light' | 'dark'
  const mode = ref(localStorage.getItem('sermul-theme') || 'light')

  // ── Computadas ──────────────────────────────────────────────────────────────
  const isDark = computed(() => mode.value === 'dark')

  const labelTema = computed(() =>
    mode.value === 'dark' ? 'Tema Claro (Morning Horizon)' : 'Tema Oscuro (Evening Horizon)'
  )

  const iconoTema = computed(() =>
    mode.value === 'dark' ? 'sap-icon--light-mode' : 'sap-icon--dark-mode'
  )

  // ── Acciones ────────────────────────────────────────────────────────────────
  /**
   * Inicializa el tema aplicando el estado guardado en localStorage.
   * Debe llamarse en App.vue onMounted para hidratar el DOM correctamente.
   */
  function init() {
    applyTheme()
  }

  /**
   * Alterna entre 'light' y 'dark', persiste en localStorage y aplica en DOM.
   */
  function toggle() {
    mode.value = mode.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('sermul-theme', mode.value)
    applyTheme()
  }

  /**
   * Establece el tema explícitamente.
   * @param {'light'|'dark'} nuevoModo
   */
  function setMode(nuevoModo) {
    if (nuevoModo !== 'light' && nuevoModo !== 'dark') return
    mode.value = nuevoModo
    localStorage.setItem('sermul-theme', nuevoModo)
    applyTheme()
  }

  /**
   * Aplica la clase CSS en <html> usando classList.toggle para máxima compatibilidad.
   * Morning Horizon: sin clase (default de SAP Fundamental Styles).
   * Evening Horizon: clase `sap-horizon-dark` en <html>.
   */
  function applyTheme() {
    const html = document.documentElement
    // classList.toggle(clase, forzar): si isDark → agrega, si no → remueve
    html.classList.toggle('sap-horizon-dark', mode.value === 'dark')
  }

  return {
    // Estado
    mode,
    // Computadas
    isDark,
    labelTema,
    iconoTema,
    // Acciones
    init,
    toggle,
    setMode,
    applyTheme,
  }
})
