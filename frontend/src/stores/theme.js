import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const mode = ref(localStorage.getItem('sermul-theme') || 'light')

  function init() {
    applyTheme()
  }

  function toggle() {
    mode.value = mode.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('sermul-theme', mode.value)
    applyTheme()
  }

  function applyTheme() {
    const html = document.documentElement
    if (mode.value === 'dark') {
      html.classList.add('sap-horizon-dark')
    } else {
      html.classList.remove('sap-horizon-dark')
    }
  }

  return { mode, init, toggle }
})
