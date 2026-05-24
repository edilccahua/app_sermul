import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/',
    redirect: '/app/dashboard',
  },
  {
    path: '/app',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardResidenteView.vue'),
      },
      {
        path: 'catalogo',
        name: 'Catalogo',
        component: () => import('@/views/CatalogoView.vue'),
      },
      {
        path: 'stock',
        name: 'Stock',
        component: () => import('@/views/StockView.vue'),
      },
      {
        path: 'inventario',
        redirect: 'stock',
      },
      {
        path: 'paradas',
        name: 'Paradas',
        component: () => import('@/views/ParadasView.vue'),
      },
      {
        path: 'historial',
        name: 'Historial',
        component: () => import('@/views/HistorialView.vue'),
      },
      // ── Sprint 2: Almacén Full-Page ──────────────────────────────────────────
      {
        path: 'almacen/salida',
        name: 'CheckOut',
        component: () => import('@/views/CheckOutView.vue'),
      },
      {
        path: 'almacen/entrada',
        name: 'CheckIn',
        component: () => import('@/views/CheckInView.vue'),
      },
      // ── Sprint 2: Herramienta Detalle ────────────────────────────────────────
      {
        path: 'herramienta/:id',
        name: 'HerramientaDetalle',
        component: () => import('@/views/HerramientaDetalleView.vue'),
      },
      // ── Sprint 2: Grupos ─────────────────────────────────────────────────────
      {
        path: 'grupos',
        name: 'Grupos',
        component: () => import('@/views/GruposView.vue'),
      },
      {
        path: 'grupos/importar',
        name: 'ImportarGrupos',
        component: () => import('@/views/ImportarGruposView.vue'),
      },
      // ── Sprint 2: Reservas ───────────────────────────────────────────────────
      {
        path: 'reservas',
        name: 'Reservas',
        component: () => import('@/views/ReservasView.vue'),
      },
      {
        path: 'reservas/crear',
        name: 'CrearReserva',
        component: () => import('@/views/CrearReservaView.vue'),
      },
      {
        path: 'reservas/aprobar',
        name: 'AprobarReservas',
        component: () => import('@/views/AprobarReservasView.vue'),
      },
      {
        path: 'reservas/despachar/:id',
        name: 'DespacharReserva',
        component: () => import('@/views/DespacharReservaView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ path: '/app/dashboard' })
  } else {
    next()
  }
})

export default router
