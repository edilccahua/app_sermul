<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Loading -->
    <div
      v-if="loading"
      class="flex-1 flex items-center justify-center"
    >
      <span
        class="sap-icon--refresh animate-spin text-3xl"
        :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
      />
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="flex-1 flex items-center justify-center p-6"
    >
      <div
        class="p-6 rounded-sm border text-center space-y-3"
        :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
      >
        <span
          class="sap-icon--message-error text-3xl block"
          :style="{ color: 'var(--sapNegativeTextColor)' }"
        />
        <p
          class="text-sm"
          :style="{ color: 'var(--sapNegativeTextColor)' }"
        >
          {{ error }}
        </p>
        <button
          class="h-8 px-4 text-xs border rounded-sm"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="$router.push('/app/historial')"
        >
          ← Volver a Historial
        </button>
      </div>
    </div>

    <!-- ══ Object Page Content ════════════════════════════════════════════════ -->
    <template v-else-if="movimiento">
      <!-- ── Object Page Header ──────────────────────────────────────────── -->
      <div
        class="px-6 pt-4 pb-5 border-b shrink-0 flex flex-col gap-4"
        :style="{ background: 'var(--sapObjectHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
      >
        <!-- Breadcrumb -->
        <div>
          <button
            class="h-8 px-3 text-xs flex items-center gap-1 mb-3 transition-colors rounded-sm hover:bg-black/5"
            :style="{ background: 'transparent', color: 'var(--sapButton_TextColor)', borderColor: 'transparent' }"
            @click="$router.push('/app/historial')"
          >
            <span class="sap-icon--nav-back" /> Volver a Historial
          </button>

          <!-- Título principal -->
          <div class="flex items-start gap-4">
            <span
              class="sap-icon--history text-4xl mt-1"
              :style="{ color: 'var(--sapContent_IconColor)' }"
            />
            <div>
              <div class="flex items-center gap-3 mb-1">
                <h1
                  class="text-2xl font-bold font-mono"
                  :style="{ color: 'var(--sapTextColor)' }"
                >
                  TICKET #{{ ticketCorto }}
                </h1>
                <span
                  class="inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-bold uppercase border"
                  :style="badgeStyle(movimiento.tipo_movimiento)"
                >
                  {{ movimiento.tipo_movimiento.replace('_', ' ') }}
                </span>
              </div>
              <div class="flex flex-wrap gap-4 text-sm">
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">
                  <span class="sap-icon--date-time mr-1" />Registrado el {{ fechaLarga }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Facets (Key Information en Cabecera) -->
        <div class="flex flex-wrap gap-12 mt-2 pl-14">
          <!-- Activo -->
          <div class="flex flex-col">
            <span
              class="text-xs mb-0.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Herramienta Asignada</span>
            <router-link
              v-if="movimiento.catalogo"
              :to="`/app/herramienta/${movimiento.catalogo.id}`"
              class="text-sm font-semibold hover:underline"
              :style="{ color: 'var(--sapLinkColor)' }"
            >
              {{ movimiento.catalogo.codigo_interno }} — {{ movimiento.catalogo.nombre }}
            </router-link>
            <span
              v-else
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >—</span>
          </div>

          <!-- Parada -->
          <div class="flex flex-col">
            <span
              class="text-xs mb-0.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Parada Operativa</span>
            <router-link
              v-if="movimiento.parada"
              :to="`/app/paradas/${movimiento.parada.id}`"
              class="text-sm font-semibold hover:underline"
              :style="{ color: 'var(--sapLinkColor)' }"
            >
              {{ movimiento.parada.codigo }} — {{ movimiento.parada.nombre }}
            </router-link>
            <span
              v-else
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >—</span>
          </div>

          <!-- Cantidad y Estado -->
          <div class="flex flex-col">
            <span
              class="text-xs mb-0.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Cantidad / Transición</span>
            <span
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              {{ movimiento.cantidad }} unid. ({{ estadoDisplay(movimiento) }})
            </span>
          </div>
        </div>
      </div>

      <!-- ── Anchor Bar (Pestañas) ──────────────────────────────────────── -->
      <div
        class="border-b shrink-0 flex gap-0 px-6"
        :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'var(--sapObjectHeader_Background)' }"
      >
        <button
          class="h-10 px-4 text-sm font-semibold border-b-2 transition-colors relative top-[1px]"
          :style="{ 
            color: 'var(--sapTextColor)', 
            borderColor: 'var(--sapSelectedColor, var(--sapButton_Emphasized_Background))' 
          }"
        >
          Información General
        </button>
      </div>

      <!-- ── Contenido de Pestaña (Secciones) ───────────────────────────── -->
      <div class="flex-1 overflow-auto p-6">
        
        <!-- Tarjeta Blanca Central Fiori -->
        <div
          class="max-w-5xl rounded-sm border p-6 flex flex-col gap-8"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <!-- Sección: Contexto Organizacional -->
          <div>
            <h2
              class="text-base font-bold mb-4"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              Contexto Operativo
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <!-- Label izquierda en escritorio, arriba en movil -->
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Cuadrilla / Grupo Destino:</span>
                <router-link
                  v-if="movimiento.grupo_destino"
                  :to="`/app/grupos/${movimiento.grupo_destino.id}`"
                  class="text-sm font-medium hover:underline"
                  :style="{ color: 'var(--sapLinkColor)' }"
                >
                  {{ movimiento.grupo_destino.codigo }} — {{ movimiento.grupo_destino.nombre }}
                </router-link>
                <span v-else class="text-sm" :style="{ color: 'var(--sapTextColor)' }">—</span>
              </div>
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Área / Circuito:</span>
                <span class="text-sm" :style="{ color: 'var(--sapTextColor)' }">
                  {{ movimiento.grupo_destino?.circuito_area || '—' }}
                </span>
              </div>
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Reserva Asociada:</span>
                <span class="text-sm font-mono" :style="{ color: 'var(--sapTextColor)' }">
                  {{ movimiento.reserva_id ? `#${movimiento.reserva_id}` : 'Movimiento Directo' }}
                </span>
              </div>
            </div>
          </div>

          <hr :style="{ borderColor: 'var(--sapList_BorderColor)' }">

          <!-- Sección: Responsables -->
          <div>
            <h2
              class="text-base font-bold mb-4"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              Responsabilidad de Transacción
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Ejecutado por (Sistema):</span>
                <div v-if="movimiento.usuario_ejecuta">
                  <span class="text-sm block" :style="{ color: 'var(--sapTextColor)' }">
                    {{ movimiento.usuario_ejecuta.nombre }} {{ movimiento.usuario_ejecuta.apellido }}
                  </span>
                  <span class="text-xs block font-mono mt-0.5" :style="{ color: 'var(--sapContent_LabelColor)' }">
                    DNI: {{ movimiento.usuario_ejecuta.dni }}
                  </span>
                </div>
                <span v-else class="text-sm" :style="{ color: 'var(--sapTextColor)' }">Sistema Automático</span>
              </div>

              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Entregador / Receptor Físico:</span>
                <div v-if="movimiento.usuario_receptor">
                  <span class="text-sm block" :style="{ color: 'var(--sapTextColor)' }">
                    {{ movimiento.usuario_receptor.nombre }} {{ movimiento.usuario_receptor.apellido }}
                  </span>
                  <span class="text-xs block font-mono mt-0.5" :style="{ color: 'var(--sapContent_LabelColor)' }">
                    DNI: {{ movimiento.usuario_receptor.dni }}
                  </span>
                </div>
                <span v-else class="text-sm" :style="{ color: 'var(--sapTextColor)' }">—</span>
              </div>
            </div>
          </div>

          <hr :style="{ borderColor: 'var(--sapList_BorderColor)' }">

          <!-- Sección: Observaciones -->
          <div>
            <h2
              class="text-base font-bold mb-4"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              Observaciones Registradas
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Nota de Entrega:</span>
                <p class="text-sm whitespace-pre-wrap" :style="{ color: 'var(--sapTextColor)' }">
                  {{ movimiento.observacion_entrega || '—' }}
                </p>
              </div>
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Nota de Devolución:</span>
                <p class="text-sm whitespace-pre-wrap" :style="{ color: 'var(--sapTextColor)' }">
                  {{ movimiento.observacion_recepcion || '—' }}
                </p>
              </div>
              <div class="flex flex-col">
                <span class="text-xs mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Nota de Ajuste/Baja:</span>
                <p class="text-sm whitespace-pre-wrap" :style="{ color: 'var(--sapTextColor)' }">
                  {{ movimiento.observaciones || '—' }}
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { historialAPI } from '@/api'

const route = useRoute()
const movimiento = ref(null)
const loading = ref(true)
const error = ref(null)

const ticketCorto = computed(() => {
  return movimiento.value?.id ? movimiento.value.id.substring(0, 8) : '...'
})

const fechaLarga = computed(() => {
  if (!movimiento.value?.timestamp) return '...'
  const d = new Date(movimiento.value.timestamp)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'long', year: 'numeric' }) + ' a las ' +
         d.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
})

function badgeStyle(tipo) {
  const map = {
    Entrega: { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
    Devolucion: { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' },
    Perdida: { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' },
    Paso_Mantenimiento: { background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalColor)', borderColor: 'var(--sapWarningBorderColor)' },
    Ajuste_Inventario: { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
    Baja: { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
  }
  return map[tipo] || { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' }
}

function estadoDisplay(m) {
  if (m.estado_origen || m.estado_destino) {
    return `${m.estado_origen || '?'} → ${m.estado_destino || '?'}`
  }
  const map = {
    Entrega: 'Disp. → En Uso',
    Devolucion: 'En Uso → Disp.',
    Paso_Mantenimiento: 'En Uso → Malog.',
    Perdida: 'En Uso → Perdida',
    Baja: '→ Baja',
    Ajuste_Inventario: 'Ajuste',
  }
  return map[m.tipo_movimiento] || m.tipo_movimiento
}

onMounted(async () => {
  try {
    const id = route.params.id
    const { data } = await historialAPI.getById(id)
    movimiento.value = data
  } catch (err) {
    error.value = 'No se pudo cargar la información del ticket. Es posible que no exista o el servicio esté caído.'
  } finally {
    loading.value = false
  }
})
</script>
