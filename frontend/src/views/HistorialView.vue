<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center gap-3">
      <ClockIcon class="w-7 h-7 text-primary" />
      <h1 class="text-2xl font-bold">Historial de Movimientos</h1>
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
        <ArrowPathIcon :class="['w-4 h-4', loading && 'animate-spin']" />
        Buscar
      </button>
    </div>

    <!-- Tabla -->
    <div class="rounded-md border border-border overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-muted-foreground">
        <ArrowPathIcon class="w-6 h-6 mx-auto mb-2 animate-spin" />Cargando historial...
      </div>
      <table v-else class="w-full caption-bottom text-sm">
        <thead class="border-b border-border">
          <tr>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Fecha / Hora</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Tipo</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Herramienta</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Estado</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Observaciones</th>
          </tr>
        </thead>
        <tbody class="[&_tr:last-child]:border-0">
          <tr v-for="m in movimientos" :key="m.id"
            class="border-b border-border hover:bg-muted/20 transition-colors">
            <td class="px-3 py-3 text-xs text-muted-foreground whitespace-nowrap">
              {{ formatTs(m.timestamp) }}
            </td>
            <td class="px-3 py-3">
              <span :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', badgeTipo(m.tipo_movimiento)]">
                {{ m.tipo_movimiento }}
              </span>
            </td>
            <td class="px-3 py-3 text-sm">
              <span v-if="m.inventario_fisico_id" class="text-muted-foreground">#{{ m.inventario_fisico_id }}</span>
              <span v-else class="text-muted-foreground">—</span>
            </td>
            <td class="px-3 py-3 text-xs text-muted-foreground">
              <span v-if="m.estado_origen || m.estado_destino">
                {{ m.estado_origen || '?' }} → {{ m.estado_destino || '?' }}
              </span>
              <span v-else>—</span>
            </td>
            <td class="px-3 py-3 text-xs text-muted-foreground max-w-[200px] truncate">
              {{ m.observaciones || '—' }}
            </td>
          </tr>
          <tr v-if="movimientos.length === 0">
            <td colspan="5" class="px-3 py-8 text-center text-muted-foreground">
              No hay movimientos con esos filtros
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { historialAPI } from '@/api'
import { ClockIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const movimientos = ref([])
const loading = ref(false)

const filtros = ref({ tipo: '', fecha_desde: '', fecha_hasta: '' })

const tipos = ['Entrega','Devolucion','Perdida','Paso_Mantenimiento','Retorno_Mantenimiento','Baja','Ajuste_Inventario','Recepcion_Mina','Salida_Ciudad','Ingreso_Compra']

function badgeTipo(tipo) {
  const map = {
    Entrega: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
    Devolucion: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
    Perdida: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
    Baja: 'bg-slate-500/15 text-slate-400 border border-slate-500/30',
    Paso_Mantenimiento: 'bg-violet-500/15 text-violet-400 border border-violet-500/30',
    Retorno_Mantenimiento: 'bg-teal-500/15 text-teal-400 border border-teal-500/30',
    Recepcion_Mina: 'bg-sky-500/15 text-sky-400 border border-sky-500/30',
  }
  return map[tipo] || 'bg-muted text-muted-foreground'
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
</script>
