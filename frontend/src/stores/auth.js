import { defineStore } from 'pinia'
import { api } from '@/api/index.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    usuario: JSON.parse(localStorage.getItem('usuario') || 'null'),
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    rolCodigo: (state) => state.usuario?.rol_codigo || '',
    nivelJerarquico: (state) => state.usuario?.nivel_jerarquico || 0,
    nombreCompleto: (state) => state.usuario
      ? `${state.usuario.nombre} ${state.usuario.apellido}`
      : '',
  },

  actions: {
    async login(dni, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/auth/login', { dni, password })
        this.token = data.access_token
        this.usuario = data.usuario
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('usuario', JSON.stringify(data.usuario))
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error de conexión'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = null
      this.usuario = null
      this.error = null
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      delete api.defaults.headers.common['Authorization']
    },

    initAuth() {
      if (this.token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    },
  },
})
