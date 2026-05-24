<template>
  <div class="h-full flex flex-col" :style="{ background: 'var(--sapBackgroundColor)' }">

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <span class="sap-icon--refresh animate-spin text-3xl" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
    </div>

    <!-- Error -->
    <div v-else-if="errorCarga" class="flex-1 flex items-center justify-center p-6">
      <div class="p-6 rounded-sm border text-center space-y-3" :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }">
        <span class="sap-icon--message-error text-3xl block" :style="{ color: 'var(--sapNegativeTextColor)' }" />
        <p class="text-sm" :style="{ color: 'var(--sapNegativeTextColor)' }">{{ errorCarga }}</p>
        <button @click="$router.back()" class="h-8 px-4 text-xs border rounded-sm"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }">
          ← Volver
        </button>
      </div>
    </div>

    <!-- Content -->
    <template v-else-if="catalogo">

      <!-- Object Page Header -->
      <div class="px-6 py-5 border-b shrink-0" :style="{ background: 'var(--sapObjectHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }">
        <div class="flex items-start gap-4">
          <!-- Icono tipo -->
          <div class="w-14 h-14 rounded-sm flex items-center justify-center shrink-0 border"
            :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }">
            <span class="sap-icon--product text-2xl" :style="{ color: 'var(--sapInformationTextColor)' }" />
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="text-xl font-bold leading-tight" :style="{ color: 'var(--sapTextColor)' }">{{ catalogo.nombre }}</h1>
            <div class="flex items-center gap-3 mt-1 flex-wrap">
              <code class="font-mono text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ catalogo.codigo_interno }}</code>
              <span class="text-xs px-2 py-0.5 rounded-sm border font-medium"
                :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }">
                {{ catalogo.tipo_material }}
              </span>
              <span v-if="catalogo.categoria" class="text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
                {{ catalogo.categoria?.nombre || '—' }}
              </span>
              <span class="text-sm font-semibold" :style="{ color: 'var(--sapNegativeTextColor)' }">
                S/. {{ catalogo.costo_reposicion?.toFixed(2) ?? '--' }}
              </span>
            </div>
          </div>
          <button @click="$router.back()" class="shrink-0 h-8 px-3 text-xs border rounded-sm flex items-center gap-1"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }">
            <span class="sap-icon--nav-back" /> Volver
          </button>
        </div>
      </div>

      <!-- Anchor Bar (Tabs) -->
      <div class="border-b shrink-0 flex gap-0" :style="{ background: 'var(--sapObjectHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="tabActivo = tab.key"
          class="px-5 py-3 text-sm font-medium border-b-2 transition-all"
          :style="tabActivo === tab.key
            ? { color: 'var(--sapButton_Emphasized_Background)', borderBottomColor: 'var(--sapButton_Emphasized_Background)' }
            : { color: 'var(--sapContent_LabelColor)', borderBottomColor: 'transparent' }"
        >
          <span :class="tab.icon" class="mr-2" />{{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-auto p-6">

        <!-- ① Información General -->
        <div v-if="tabActivo === 'info'" class="max-w-3xl">
          <div class="p-5 rounded-sm border" :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }">
            <div class="grid grid-cols-2 gap-x-8 gap-y-3">
              <div v-for="campo in camposInfo" :key="campo.label" class="space-y-0.5">
                <p class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ campo.label }}:</p>
                <p class="text-sm font-semibold" :style="{ color: 'var(--sapTextColor)' }">
                  <code v-if="campo.mono" class="font-mono">{{ campo.value || '—' }}</code>
                  <span v-else>{{ campo.value || '—' }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- ② Stock — grid 2x2 de contadores -->
        <div v-if="tabActivo === 'unidades'" class="max-w-md">
          <div class="grid grid-cols-2 gap-4 p-4">
            <div class="p-4 rounded-sm border" :style="{ background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)' }">
              <p class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Disponibles:</p>
              <p class="text-2xl font-bold" :style="{ color: 'var(--sapPositiveTextColor)' }">{{ catalogo.cant_disponible ?? 0 }}</p>
            </div>
            <div class="p-4 rounded-sm border" :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }">
              <p class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">En Uso:</p>
              <p class="text-2xl font-bold" :style="{ color: 'var(--sapInformationTextColor)' }">{{ catalogo.cant_en_uso ?? 0 }}</p>
            </div>
            <div class="p-4 rounded-sm border" :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }">
              <p class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Malogradas:</p>
              <p class="text-2xl font-bold" :style="{ color: 'var(--sapNegativeTextColor)' }">{{ catalogo.cant_malograda ?? 0 }}</p>
            </div>
            <div class="p-4 rounded-sm border" :style="{ background: 'var(--sapNeutralBackground)', borderColor: 'var(--sapNeutralBorderColor)' }">
              <p class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Perdidas:</p>
              <p class="text-2xl font-bold" :style="{ color: 'var(--sapNeutralTextColor)' }">{{ catalogo.cant_perdida ?? 0 }}</p>
            </div>
          </div>
        </div>

        <!-- ③ Historial -->
        <div v-if="tabActivo === 'historial'">
          <div v-if="loadingHistorial" class="flex items-center gap-2 py-4" :style="{ color: 'var(--sapContent_LabelColor)' }">
            <span class="sap-icon--refresh animate-spin" /> Cargando historial...
          </div>
          <table v-else class="w-full text-xs border-collapse">
            <thead>
              <tr :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)' }">
                <th v-for="col in ['Tipo', 'Cant.', 'Fecha', 'Parada', 'Grupo', 'Usuario', 'Observación']"
                  :key="col" class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
                  :style="{ borderColor: 'var(--sapList_BorderColor)' }">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="h in historial" :key="h.id" class="border-b hover:bg-muted/20 transition-colors"
                :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }">
                <td class="px-4 py-1.5">
                  <span class="text-xs px-2 py-0.5 rounded-sm border font-medium"
                    :style="h.tipo_movimiento === 'Salida_Ciudad'
                      ? { background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalColor)', borderColor: 'var(--sapWarningBorderColor)' }
                      : { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }">
                    {{ h.tipo_movimiento }}
                  </span>
                </td>
                <td class="px-4 py-1.5 text-center font-semibold" :style="{ color: 'var(--sapTextColor)' }">{{ h.cantidad ?? '—' }}</td>
                <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">
                  {{ new Date(h.timestamp).toLocaleString('es-PE') }}
                </td>
                <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ h.parada?.nombre ?? '—' }}</td>
                <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ h.grupo_destino?.nombre ?? '—' }}</td>
                <td class="px-4 py-1.5">
                  {{ h.usuario_ejecuta ? `${h.usuario_ejecuta.nombre} ${h.usuario_ejecuta.apellido}` : '—' }}
                </td>
                <td class="px-4 py-1.5 text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
                  {{ h.observacion_entrega || h.observacion_recepcion || '—' }}
                </td>
              </tr>
              <tr v-if="!historial.length">
                <td colspan="7" class="px-4 py-6 text-center text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">Sin movimientos registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- ④ Reservas Activas -->
        <div v-if="tabActivo === 'reservas'">
          <div v-if="loadingReservas" class="flex items-center gap-2 py-4" :style="{ color: 'var(--sapContent_LabelColor)' }">
            <span class="sap-icon--refresh animate-spin" /> Cargando reservas...
          </div>
          <p v-else-if="!reservasActivas.length" class="text-xs text-center py-6" :style="{ color: 'var(--sapContent_LabelColor)' }">
            No hay reservas activas para esta herramienta.
          </p>
          <table v-else class="w-full text-xs border-collapse">
            <thead>
              <tr :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)' }">
                <th v-for="col in ['Código', 'Grupo', 'Parada', 'Estado', 'Fecha']"
                  :key="col" class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
                  :style="{ borderColor: 'var(--sapList_BorderColor)' }">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in reservasActivas" :key="r.id" class="border-b hover:bg-muted/20"
                :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }">
                <td class="px-4 py-1.5"><code class="font-mono" :style="{ color: 'var(--sapButton_Emphasized_Background)' }">{{ r.codigo }}</code></td>
                <td class="px-4 py-1.5">{{ r.grupo?.nombre ?? '—' }}</td>
                <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ r.parada?.nombre ?? '—' }}</td>
                <td class="px-4 py-1.5">
                  <span class="text-xs px-2 py-0.5 rounded-sm border font-medium"
                    :style="r.estado === 'Aprobada'
                      ? { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }
                      : { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' }">
                    {{ r.estado }}
                  </span>
                </td>
                <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">
                  {{ r.fecha_programada ? new Date(r.fecha_programada).toLocaleDateString('es-PE') : '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { catalogoAPI, historialAPI, reservasAPI } from '@/api'

const route = useRoute()

const catalogo = ref(null)
const loading = ref(false)
const errorCarga = ref(null)
const tabActivo = ref('info')

const historial = ref([])
const reservasActivas = ref([])
const loadingHistorial = ref(false)
const loadingReservas = ref(false)

const tabs = [
  { key: 'info',      label: 'Información General', icon: 'sap-icon--hint' },
  { key: 'unidades',  label: 'Stock',    icon: 'sap-icon--inventory' },
  { key: 'historial', label: 'Historial',            icon: 'sap-icon--history' },
  { key: 'reservas',  label: 'Reservas Activas',     icon: 'sap-icon--list' },
]

const camposInfo = computed(() => {
  if (!catalogo.value) return []
  const c = catalogo.value
  return [
    { label: 'Código interno', value: c.codigo_interno, mono: true },
    { label: 'Nombre',         value: c.nombre },
    { label: 'Categoría',      value: c.categoria?.nombre || '—' },
    { label: 'Tipo',           value: c.tipo_material },
    { label: 'Costo reposición', value: c.costo_reposicion ? `S/. ${c.costo_reposicion.toFixed(2)}` : '—' },
    { label: 'Moneda',         value: c.moneda },
    { label: 'Marca',          value: c.marca },
    { label: 'Modelo',         value: c.modelo },
    { label: 'Proveedor',      value: c.proveedor },
    { label: 'Descripción',    value: c.descripcion },
  ]
})

// Cargar datos de cada tab según sea necesario
watch(tabActivo, async (tab) => {
  if (tab === 'historial' && !historial.value.length) {
    loadingHistorial.value = true
    try {
      const { data } = await historialAPI.get({ catalogo_id: route.params.id })
      historial.value = data
    } finally {
      loadingHistorial.value = false
    }
  }
  if (tab === 'reservas' && !reservasActivas.value.length) {
    loadingReservas.value = true
    try {
      const { data } = await reservasAPI.get({ estado: 'Pendiente,Aprobada' })
      // Filtrar las que tienen este catalogo_id en sus detalles
      reservasActivas.value = data.filter((r) =>
        r.detalles?.some((d) => d.catalogo_id == route.params.id)
      )
    } finally {
      loadingReservas.value = false
    }
  }
})

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await catalogoAPI.getById(route.params.id)
    catalogo.value = data
  } catch {
    errorCarga.value = 'No se pudo cargar la información de la herramienta.'
  } finally {
    loading.value = false
  }
})
</script>
