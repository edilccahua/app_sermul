import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Roles permitidos por sección (mapeo a permisos backend)
const PUEDEN_ALMACEN = ['RESIDENTE', 'ADMIN', 'ALMACENERO']
const PUEDEN_GRUPOS = ['RESIDENTE', 'ADMIN', 'ALMACENERO']
const PUEDEN_PERSONAL = ['RESIDENTE', 'ADMIN']

function guardRol(rolesPermitidos) {
  return (to, from, next) => {
    const auth = useAuthStore()
    if (!rolesPermitidos.includes(auth.rolCodigo)) return next('/app/dashboard')
    next()
  }
}

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
      // ── GENERAL ────────────────────────────────────────────────────────────
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
        path: 'catalogo/crear',
        name: 'CatalogoCrear',
        component: () => import('@/views/MaterialFormView.vue'),
      },
      {
        path: 'catalogo/editar/:id',
        name: 'CatalogoEditar',
        component: () => import('@/views/MaterialFormView.vue'),
      },
      {
        path: 'herramienta/:id',
        name: 'HerramientaDetalle',
        component: () => import('@/views/HerramientaDetalleView.vue'),
      },
      {
        path: 'stock',
        name: 'Stock',
        component: () => import('@/views/StockView.vue'),
      },
      {
        path: 'inventario',
        redirect: '/app/stock',
      },
      {
        path: 'historial',
        name: 'Historial',
        component: () => import('@/views/HistorialView.vue'),
      },
      {
        path: 'historial/:id',
        name: 'historial-detalle',
        component: () => import('@/views/HistorialDetalleView.vue'),
      },
      {
        path: 'mi-grupo',
        name: 'MiGrupo',
        component: () => import('@/views/MiGrupoView.vue'),
      },
      {
        path: 'perfil',
        name: 'Perfil',
        component: () => import('@/views/PerfilView.vue'),
      },

      // ── ALMACÉN ────────────────────────────────────────────────────────────
      {
        path: 'almacen/solicitudes', //antiguo solicitudes
        name: 'Solicitudes',
        component: () => import('@/views/SolicitudesView.vue'),
        beforeEnter: guardRol(PUEDEN_ALMACEN),
      },
      {
        path: 'almacen/solicitud-crear',
        name: 'CrearSolicitud',
        component: () => import('@/views/CrearReservaView.vue'),
        beforeEnter: guardRol(PUEDEN_ALMACEN),
      },
      {
        path: 'almacen/salida',
        name: 'CheckOut',
        component: () => import('@/views/PrestamoSalidaView.vue'),
        beforeEnter: guardRol(PUEDEN_ALMACEN),
      },
      {
        path: 'almacen/entrada',
        name: 'CheckIn',
        component: () => import('@/views/PrestamoEntradaView.vue'),
        beforeEnter: guardRol(PUEDEN_ALMACEN),
      },
      {
        path: 'almacen/despacho-masivo',
        name: 'DespachoMasivo',
        component: () => import('@/views/DespachoMasivoView.vue'),
        beforeEnter: guardRol(PUEDEN_ALMACEN),
      },
      {
        path: 'almacen/devolucion-masiva',
        name: 'DevolucionMasiva',
        component: () => import('@/views/DevolucionMasivoView.vue'),
        beforeEnter: guardRol(PUEDEN_ALMACEN),
      },

      // ── GESTIÓN ────────────────────────────────────────────────────────────
      {
        path: 'personal',
        name: 'Personal',
        component: () => import('@/views/PersonalView.vue'),
        beforeEnter: guardRol(PUEDEN_PERSONAL),
      },
      {
        path: 'personal/:id',
        name: 'PersonalDetalle',
        component: () => import('@/views/PerfilView.vue'),
      },
      {
        path: 'grupos',
        name: 'Grupos',
        component: () => import('@/views/GruposView.vue'),
        beforeEnter: guardRol(PUEDEN_GRUPOS),
      },
      {
        path: 'grupos/:id',
        name: 'GrupoDetalle',
        component: () => import('@/views/GrupoDetalleView.vue'),
      },
      {
        path: 'grupos/importar',
        name: 'ImportarGrupos',
        component: () => import('@/views/ImportarGruposView.vue'),
        beforeEnter: guardRol(PUEDEN_GRUPOS),
      },
      {
        path: 'paradas',
        name: 'Paradas',
        component: () => import('@/views/ParadasView.vue'),
      },
      {
        path: 'paradas/:id',
        name: 'ParadaDetalle',
        component: () => import('@/views/ParadaDetalleView.vue'),
      },
      {
        path: 'paradas/:id/cierre',
        name: 'CierreParada',
        component: () => import('@/views/CierreParadaView.vue'),
      },
      {
        path: 'reportes',
        name: 'Reportes',
        component: () => import('@/views/ReportesView.vue'),
      },
      {
        path: 'about',
        name: 'About',
        component: () => import('@/views/AboutView.vue'),
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
  }
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
