<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center gap-3">
      <span class="sap-icon--history w-7 h-7 flex items-center justify-center text-[var(--sapButton_Emphasized_Background)]" />
      <h1 class="text-xl font-bold">Historial de Movimientos</h1>
      <span class="text-sm text-muted-foreground ml-auto">{{ movimientos.length }} registros</span>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3 flex-wrap items-center">
      <select v-model="filtros.tipo"
        class="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
        <option value="">Todos los tipos</option>
        <option v-for="t in tipos" :key="t" :value="t">{{ t }}</option>
      </select>
      <input v-model="filtros.fecha_desde" type="date"
        class="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
      <span class="text-muted-foreground text-sm">→</span>
      <input v-model="filtros.fecha_hasta" type="date"
        class="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
      <button @click="cargar"
        class="inline-flex items-center gap-1.5 rounded-md bg-primary px-4 h-9 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors">
        <span :class="['sap-icon--refresh w-4 h-4 flex items-center justify-center', loading && 'animate-spin']" />
        Buscar
      </button>
    </div>

    <!-- Table Toolbar -->
    <div class="flex items-center justify-between text-sm text-[var(--sapContent_LabelColor)]">
      <span>Movimientos ({{ movimientos.length }})</span>
    </div>

    <!-- Tabla -->
    <div class="rounded-md border border-border overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-muted-foreground">
        <span class="sap-icon--refresh w-6 h-6 flex items-center justify-center mx-auto mb-2 animate-spin" />Cargando historial...
      </div>
      <table v-else class="w-full caption-bottom text-sm">
        <thead class="border-b border-border">
          <tr>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Fecha / Hora</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Tipo</th>
            <th class="h-8 px-2 text-center font-medium text-muted-foreground text-xs">Cant.</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Herramienta</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Estado</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Observación</th>
          </tr>
        </thead>
        <tbody class="[&_tr:last-child]:border-0">
          <tr v-for="m in movimientos" :key="m.id"
            class="border-b border-border hover:bg-muted/20 transition-colors cursor-default">
            <td class="px-2 py-1.5 text-xs text-muted-foreground whitespace-nowrap">
              {{ formatTs(m.timestamp) }}
            </td>
            <td class="px-2 py-1.5">
              <span :class="['inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', badgeTipo(m.tipo_movimiento)]">
                {{ m.tipo_movimiento }}
              </span>
            </td>
            <td class="px-2 py-1.5 text-center text-sm font-semibold" :style="{ color: 'var(--sapTextColor)' }">
              {{ m.cantidad ?? '—' }}
            </td>
            <td class="px-2 py-1.5 text-sm">
              <template v-if="m.catalogo">
                <router-link :to="`/app/herramienta/${m.catalogo.id}`"
                  class="text-[var(--sapLinkColor)] hover:underline font-medium">
                  <code class="font-mono text-xs">{{ m.catalogo.codigo_interno }}</code>
                </router-link>
                <span class="mx-1 text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">—</span>
                <router-link :to="`/app/herramienta/${m.catalogo.id}`"
                  class="text-[var(--sapLinkColor)] hover:underline text-xs">
                  {{ m.catalogo.nombre }}
                </router-link>
              </template>
              <span v-else class="text-xs text-muted-foreground">—</span>
            </td>
            <td class="px-2 py-1.5 text-xs" :style="{ color: 'var(--sapTextColor)' }">
              {{ estadoDisplay(m) }}
            </td>
            <td class="px-2 py-1.5 text-xs text-muted-foreground max-w-[200px] truncate">
              {{ m.observacion_entrega || m.observacion_recepcion || m.observaciones || '—' }}
            </td>
          </tr>
          <tr v-if="movimientos.length === 0">
            <td colspan="6" class="px-3 py-6 text-center text-muted-foreground">
              No hay movimientos con esos filtros
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { historialAPI } from '@/api'


const movimientos = ref([])
const loading = ref(false)

const filtros = ref({ tipo: '', fecha_desde: '', fecha_hasta: '' })

const tipos = ['Entrega','Devolucion','Perdida','Paso_Mantenimiento','Retorno_Mantenimiento','Baja','Ajuste_Inventario','Recepcion_Mina','Salida_Ciudad','Ingreso_Compra']

function badgeTipo(tipo) {
  const map = {
    Entrega: 'bg-[var(--sapInformationBackground)] text-[var(--sapInformationTextColor)] border border-[var(--sapInformationBorderColor)]',
    Devolucion: 'bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)] border border-[var(--sapSuccessBorderColor)]',
    Perdida: 'bg-[var(--sapErrorBackground)] text-[var(--sapNegativeTextColor)] border border-[var(--sapErrorBorderColor)]',
    Baja: 'bg-[var(--sapNeutralBackground)] text-[var(--sapNeutralTextColor)] border border-[var(--sapNeutralBorderColor)]',
    Paso_Mantenimiento: 'bg-[var(--sapInformationBackground)] text-[var(--sapInformationTextColor)] border border-[var(--sapInformationBorderColor)]',
    Retorno_Mantenimiento: 'bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)] border border-[var(--sapSuccessBorderColor)]',
    Recepcion_Mina: 'bg-[var(--sapInformationBackground)] text-[var(--sapInformationTextColor)] border border-[var(--sapInformationBorderColor)]',
  }
  return map[tipo] || 'bg-muted text-muted-foreground'
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
    Retorno_Mantenimiento: 'Malog. → Disp.',
    Ajuste_Inventario: 'Ajuste',
    Recepcion_Mina: '→ Mina',
    Salida_Ciudad: 'Ciudad →',
    Ingreso_Compra: 'Compra →',
  }
  return map[m.tipo_movimiento] || m.tipo_movimiento
}

function formatTs(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: 'short' }) + ' ' +
    d.toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
}

async function cargar() {
  loading.value = true
  try {
    const params = {}
    if (filtros.value.tipo) params.tipo = filtros.value.tipo
    if (filtros.value.fecha_desde) params.fecha_desde = filtros.value.fecha_desde
    if (filtros.value.fecha_hasta) params.fecha_hasta = filtros.value.fecha_hasta
    const { data } = await historialAPI.get(params)
    movimientos.value = data
  } catch (e) {
    movimientos.value = []
  } finally {
    loading.value = false
  }
}

onMounted(cargar)

// Auto-búsqueda al cambiar cualquier filtro (debounce 300ms)
let timeout = null
watch(filtros, () => {
  clearTimeout(timeout)
  timeout = setTimeout(cargar, 300)
}, { deep: true })
</script>
