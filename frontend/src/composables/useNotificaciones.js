import { ref, computed } from 'vue'

// ─── Tipos de notificación disponibles ───────────────────────────────────────
// 'error'   → sap-icon--message-error    | var(--sapErrorBackground)
// 'warning' → sap-icon--message-warning  | var(--sapCriticalBackground)
// 'success' → sap-icon--message-success  | var(--sapSuccessBackground)
// 'info'    → sap-icon--message-information | var(--sapInformationBackground)

const ICONOS_NIVEL = {
  error: 'sap-icon--message-error',
  warning: 'sap-icon--message-warning',
  success: 'sap-icon--message-success',
  info: 'sap-icon--message-information',
}

const ESTILOS_NIVEL = {
  error: {
    background: 'var(--sapErrorBackground)',
    borderColor: 'var(--sapErrorBorderColor)',
    color: 'var(--sapNegativeTextColor)',
    iconColor: 'var(--sapNegativeColor)',
  },
  warning: {
    background: 'var(--sapCriticalBackground)',
    borderColor: 'var(--sapCriticalBorderColor)',
    color: 'var(--sapCriticalColor)',
    iconColor: 'var(--sapCriticalColor)',
  },
  success: {
    background: 'var(--sapSuccessBackground)',
    borderColor: 'var(--sapSuccessBorderColor)',
    color: 'var(--sapPositiveTextColor)',
    iconColor: 'var(--sapPositiveColor)',
  },
  info: {
    background: 'var(--sapInformationBackground)',
    borderColor: 'var(--sapInformationBorderColor)',
    color: 'var(--sapInformationTextColor)',
    iconColor: 'var(--sapInformationColor)',
  },
}

// ─── Estado global singleton (compartido entre todas las instancias) ──────────
const notificaciones = ref([
  {
    id: 1,
    nivel: 'error',
    titulo: 'Stock crítico detectado',
    mensaje: 'Taladro Neumático Atlas Copco (TALNEU-ATLAS) tiene 0 unidades disponibles.',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(), // hace 5 min
    leida: false,
    ruta: '/app/catalogo',
  },
  {
    id: 2,
    nivel: 'warning',
    titulo: '4 solicitudes pendientes de aprobación',
    mensaje: 'Hay reservas sin despachar del grupo GRP-001 para la Parada PAR-2026-001.',
    timestamp: new Date(Date.now() - 1000 * 60 * 18).toISOString(), // hace 18 min
    leida: false,
    ruta: '/app/almacen/solicitudes',
  },
  {
    id: 3,
    nivel: 'warning',
    titulo: 'Integrante con herramientas activas',
    mensaje: 'Luis Mamani tiene 2 herramientas en uso y fue removido del grupo GRP-003.',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // hace 45 min
    leida: false,
    ruta: '/app/grupos',
  },
  {
    id: 4,
    nivel: 'success',
    titulo: 'Despacho masivo completado',
    mensaje: '12 herramientas despachadas correctamente al grupo Mant. de Molino SAG.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // hace 2h
    leida: false,
    ruta: '/app/almacen/despacho-masivo',
  },
  {
    id: 5,
    nivel: 'info',
    titulo: 'Nuevo grupo importado desde Excel',
    mensaje: 'Se importaron 8 trabajadores al grupo GRP-004 de la Parada PAR-2026-002.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // hace 5h
    leida: true,
    ruta: '/app/grupos',
  },
  {
    id: 6,
    nivel: 'info',
    titulo: 'Parada PAR-2026-001 activa',
    mensaje: 'La parada de planta "Gran Parada Anual 2026" fue activada correctamente.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), // hace 1 día
    leida: true,
    ruta: '/app/paradas',
  },
])

// ─── Composable exportable ────────────────────────────────────────────────────
export function useNotificaciones() {
  // ── Computadas ──────────────────────────────────────────────────────────────
  const noLeidas = computed(() =>
    notificaciones.value.filter((n) => !n.leida)
  )

  const cantidadNoLeidas = computed(() => noLeidas.value.length)

  const tieneNoLeidas = computed(() => cantidadNoLeidas.value > 0)

  // ── Helpers de presentación ─────────────────────────────────────────────────
  /**
   * Devuelve la clase CSS del ícono SAP según el nivel de la notificación.
   * @param {'error'|'warning'|'success'|'info'} nivel
   */
  function iconoPorNivel(nivel) {
    return ICONOS_NIVEL[nivel] ?? ICONOS_NIVEL.info
  }

  /**
   * Devuelve el objeto de estilos CSS para el contenedor de la notificación.
   * @param {'error'|'warning'|'success'|'info'} nivel
   */
  function estiloPorNivel(nivel) {
    return ESTILOS_NIVEL[nivel] ?? ESTILOS_NIVEL.info
  }

  /**
   * Formatea el timestamp relativo (ej. "hace 5 min", "hace 2 h", "ayer").
   * @param {string} isoTimestamp
   */
  function tiempoRelativo(isoTimestamp) {
    const ahora = Date.now()
    const ts = new Date(isoTimestamp).getTime()
    const diff = ahora - ts // en milisegundos

    const minutos = Math.floor(diff / (1000 * 60))
    const horas = Math.floor(diff / (1000 * 60 * 60))
    const dias = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (minutos < 1) return 'Ahora mismo'
    if (minutos < 60) return `Hace ${minutos} min`
    if (horas < 24) return `Hace ${horas} h`
    if (dias === 1) return 'Ayer'
    return `Hace ${dias} días`
  }

  // ── Acciones ────────────────────────────────────────────────────────────────
  /**
   * Marca una notificación específica como leída por su id.
   * @param {number} id
   */
  function marcarComoLeida(id) {
    const n = notificaciones.value.find((item) => item.id === id)
    if (n) n.leida = true
  }

  /**
   * Marca todas las notificaciones como leídas.
   */
  function marcarTodasComoLeidas() {
    notificaciones.value.forEach((n) => {
      n.leida = true
    })
  }

  /**
   * Elimina una notificación de la lista por su id.
   * @param {number} id
   */
  function eliminarNotificacion(id) {
    notificaciones.value = notificaciones.value.filter((n) => n.id !== id)
  }

  /**
   * Agrega una nueva notificación al inicio de la lista (push simulado desde lógica de negocio).
   * @param {{ nivel: string, titulo: string, mensaje: string, ruta?: string }} data
   */
  function agregarNotificacion({ nivel, titulo, mensaje, ruta = null }) {
    const nuevaId = notificaciones.value.length
      ? Math.max(...notificaciones.value.map((n) => n.id)) + 1
      : 1
    notificaciones.value.unshift({
      id: nuevaId,
      nivel,
      titulo,
      mensaje,
      timestamp: new Date().toISOString(),
      leida: false,
      ruta,
    })
  }

  return {
    // Estado
    notificaciones,
    noLeidas,
    cantidadNoLeidas,
    tieneNoLeidas,
    // Helpers
    iconoPorNivel,
    estiloPorNivel,
    tiempoRelativo,
    // Acciones
    marcarComoLeida,
    marcarTodasComoLeidas,
    eliminarNotificacion,
    agregarNotificacion,
  }
}
