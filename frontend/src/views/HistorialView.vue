<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background, var(--sapGroup_ContentBackground))', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3 mb-4">
        <span
          class="sap-icon--history text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Historial de Movimientos
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Registro de auditoría del inventario
          </p>
        </div>
      </div>

      <!-- Filtros -->
      <div class="flex gap-3 flex-wrap items-center">
        <!-- Búsqueda con debounce -->
        <div class="relative min-w-[250px]">
          <span
            class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          />
          <input
            v-model="filtros.search"
            type="text"
            placeholder="Buscar por nombre, código..."
            class="h-9 w-full pl-9 pr-3 text-sm rounded-sm outline-none border"
            :style="fieldStyle"
          >
        </div>

        <select
          v-model="filtros.tipo"
          class="h-9 px-3 text-sm rounded-sm outline-none border"
          :style="fieldStyle"
        >
          <option value="">
            Todos los tipos
          </option>
          <option
            v-for="t in tipos"
            :key="t"
            :value="t"
          >
            {{ t.replace('_', ' ') }}
          </option>
        </select>

        <input
          v-model="filtros.fecha_desde"
          type="date"
          class="h-9 px-3 text-sm rounded-sm outline-none border"
          :style="fieldStyle"
        >
        <span
          class="text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >→</span>
        <input
          v-model="filtros.fecha_hasta"
          type="date"
          class="h-9 px-3 text-sm rounded-sm outline-none border"
          :style="fieldStyle"
        >
        
        <span
          v-if="loading"
          class="sap-icon--refresh animate-spin text-lg ml-2"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
      </div>
    </div>

    <!-- Tabla -->
    <div class="flex-1 overflow-auto p-4 md:p-6">
      <div
        class="border rounded-sm overflow-hidden"
        :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
      >
        <table class="w-full caption-bottom text-sm">
          <thead
            class="border-b"
            :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <tr>
              <th class="h-9 px-4 text-left font-semibold text-xs uppercase tracking-wide">
                ID Ticket
              </th>
              <th class="h-9 px-4 text-left font-semibold text-xs uppercase tracking-wide">
                Fecha / Hora
              </th>
              <th class="h-9 px-4 text-left font-semibold text-xs uppercase tracking-wide">
                Tipo
              </th>
              <th class="h-9 px-4 text-center font-semibold text-xs uppercase tracking-wide">
                Cant.
              </th>
              <th class="h-9 px-4 text-left font-semibold text-xs uppercase tracking-wide">
                Herramienta
              </th>
              <th class="h-9 px-4 text-left font-semibold text-xs uppercase tracking-wide">
                Estado
              </th>
              <th class="h-9 px-4 text-left font-semibold text-xs uppercase tracking-wide">
                Observación
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="m in movimientos"
              :key="m.id"
              class="border-b transition-colors hover:bg-muted/20 last:border-0"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              <td class="px-4 py-2 font-mono text-xs">
                <router-link
                  :to="`/app/historial/${m.id}`"
                  class="font-medium hover:underline transition-colors"
                  :style="{ color: 'var(--sapLinkColor)' }"
                >
                  #{{ m.id.substring(0, 8) }}
                </router-link>
              </td>
              <td
                class="px-4 py-2 text-xs font-mono"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ formatTs(m.timestamp) }}
              </td>
              <td class="px-4 py-2">
                <span
                  class="font-semibold text-xs uppercase"
                  :style="{ color: badgeStyle(m.tipo_movimiento).color }"
                >
                  {{ m.tipo_movimiento.replace('_', ' ') }}
                </span>
              </td>
              <td
                class="px-4 py-2 text-center text-sm font-semibold"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                {{ m.cantidad ?? '—' }}
              </td>
              <td class="px-4 py-2 text-sm">
                <template v-if="m.catalogo">
                  <router-link
                    :to="`/app/herramienta/${m.catalogo.id}`"
                    class="font-medium hover:underline"
                    :style="{ color: 'var(--sapLinkColor)' }"
                  >
                    <code class="font-mono text-xs mr-1">{{ m.catalogo.codigo_interno }}</code>
                    {{ m.catalogo.nombre }}
                  </router-link>
                </template>
                <span
                  v-else
                  class="text-xs"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >—</span>
              </td>
              <td
                class="px-4 py-2 text-xs"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                {{ estadoDisplay(m) }}
              </td>
              <td
                class="px-4 py-2 text-xs truncate max-w-[200px]"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ m.observacion_entrega || m.observacion_recepcion || m.observaciones || '—' }}
              </td>
            </tr>
            <tr v-if="movimientos.length === 0 && !loading">
              <td
                colspan="6"
                class="px-4 py-12 text-center text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                No hay movimientos con los filtros aplicados
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Paginación UI -->
        <div
          class="border-t px-4 py-2 flex items-center justify-between"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <span
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Mostrando {{ movimientos.length ? offset + 1 : 0 }} - {{ Math.min(offset + limit, total) }} de {{ total }} registros
          </span>
          <div class="flex items-center gap-2">
            <button
              :disabled="offset === 0 || loading"
              class="px-3 h-7 text-xs border rounded-sm transition-colors disabled:opacity-50"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="cambiarPagina(-1)"
            >
              ◀ Anterior
            </button>
            <button
              :disabled="offset + limit >= total || loading"
              class="px-3 h-7 text-xs border rounded-sm transition-colors disabled:opacity-50"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="cambiarPagina(1)"
            >
              Siguiente ▶
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { historialAPI } from '@/api'

const movimientos = ref([])
const loading = ref(false)
const total = ref(0)
const offset = ref(0)
const limit = 50

const filtros = ref({ search: '', tipo: '', fecha_desde: '', fecha_hasta: '' })

// Selector restringido a 6 tipos exactos
const tipos = ['Entrega', 'Devolucion', 'Perdida', 'Paso_Mantenimiento', 'Ajuste_Inventario', 'Baja']

const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

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

function formatTs(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' }) + ' ' +
    d.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

async function cargar() {
  loading.value = true
  try {
    const params = {
      offset: offset.value,
      limit,
    }
    if (filtros.value.search) params.search = filtros.value.search
    if (filtros.value.tipo) params.tipo = filtros.value.tipo
    if (filtros.value.fecha_desde) params.fecha_desde = filtros.value.fecha_desde
    if (filtros.value.fecha_hasta) params.fecha_hasta = filtros.value.fecha_hasta
    
    const { data } = await historialAPI.get(params)
    // Se adapta por si la API retorna { items, total } o una lista plana temporal
    if (data && data.items) {
      movimientos.value = data.items
      total.value = data.total
    } else if (Array.isArray(data)) {
      movimientos.value = data
      total.value = data.length
    }
  } catch (e) {
    movimientos.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function cambiarPagina(delta) {
  offset.value += delta * limit
  cargar()
}

onMounted(cargar)

// Debounce para búsqueda (Corrección B)
let timeout = null
watch(filtros, () => {
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    offset.value = 0 // Reiniciar a página 1 al cambiar filtros
    cargar()
  }, 300)
}, { deep: true })
</script>

<style scoped>
input:focus, select:focus {
  outline: 2px solid var(--sapField_Hover_BorderColor, var(--sapButton_Emphasized_Background));
  outline-offset: -1px;
}
</style>
