<template>
  <div class="h-full flex flex-col" :style="{ background: 'var(--sapBackgroundColor)' }">

    <!-- Dynamic Page Header -->
    <div
      class="px-6 py-4 border-b shrink-0 flex items-center justify-between"
      :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3">
        <span class="sap-icon--home text-2xl" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
        <div>
          <h1 class="text-xl font-bold" :style="{ color: 'var(--sapTextColor)' }">Dashboard Residente</h1>
          <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">
            KPIs en tiempo real · Actualización automática cada 60s
          </p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <!-- Última actualización -->
        <span v-if="dashboardStore.lastFetch" class="text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
          Actualizado: {{ formatHora(dashboardStore.lastFetch) }}
        </span>
        <!-- Botón refresh manual -->
        <button
          @click="dashboardStore.fetchResidente(true)"
          :disabled="dashboardStore.loading"
          class="flex items-center gap-2 h-8 px-3 text-xs border rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
        >
          <span :class="['sap-icon--refresh text-xs', dashboardStore.loading ? 'animate-spin' : '']" />
          Actualizar
        </button>
      </div>
    </div>

    <!-- Loading state -->
    <div
      v-if="dashboardStore.loading && !dashboardStore.metricas"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center space-y-3">
        <span class="sap-icon--refresh text-4xl animate-spin block" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
        <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">Cargando métricas...</p>
      </div>
    </div>

    <!-- Error state -->
    <div
      v-else-if="dashboardStore.error && !dashboardStore.metricas"
      class="flex-1 flex items-center justify-center p-6"
    >
      <div
        class="max-w-md p-6 rounded-sm border text-center space-y-3"
        :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
      >
        <span class="sap-icon--message-error text-3xl block" :style="{ color: 'var(--sapNegativeTextColor)' }" />
        <p class="text-sm" :style="{ color: 'var(--sapNegativeTextColor)' }">{{ dashboardStore.error }}</p>
        <button
          @click="dashboardStore.fetchResidente(true)"
          class="h-9 px-4 text-sm border rounded-sm"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
        >Reintentar</button>
      </div>
    </div>

    <!-- ══ Grid OVP ═══════════════════════════════════════════════════════════ -->
    <div
      v-else-if="m"
      class="flex-1 overflow-y-auto p-4"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">

        <!-- ① SATURACIÓN DE HERRAMIENTAS — Donut gauge semircular -->
        <div class="card-ovp">
          <div class="card-header">
            <span class="sap-icon--status-critical" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
            <p class="card-title">Saturación</p>
            <span
              class="ml-auto text-xs px-2 py-0.5 rounded-sm border font-medium"
              :style="saturacionStyle"
            >{{ saturacionPct }}%</span>
          </div>
          <div class="flex items-center justify-center py-2">
            <div class="w-40 h-40 relative">
              <Doughnut
                v-if="saturacionData"
                :data="saturacionData"
                :options="saturacionOptions"
              />
              <div class="absolute inset-0 flex flex-col items-center justify-center">
                <span class="text-2xl font-bold" :style="{ color: saturacionColor }">{{ saturacionPct }}%</span>
                <span class="text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">En uso</span>
              </div>
            </div>
          </div>
          <div class="flex justify-around text-xs mt-1">
            <span :style="{ color: 'var(--sapContent_LabelColor)' }">
              En uso: <strong :style="{ color: 'var(--sapTextColor)' }">{{ herramientasPorEstado.En_Uso }}</strong>
            </span>
            <span :style="{ color: 'var(--sapContent_LabelColor)' }">
              Disponibles: <strong :style="{ color: 'var(--sapTextColor)' }">{{ herramientasPorEstado.Disponible }}</strong>
            </span>
          </div>
        </div>

        <!-- ② HERRAMIENTAS POR ESTADO — Donut -->
        <div class="card-ovp">
          <div class="card-header">
            <span class="sap-icon--pie-chart" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
            <p class="card-title">Por Estado</p>
          </div>
          <div class="flex items-center justify-center py-2">
            <div class="w-40 h-40">
              <Doughnut v-if="estadosData" :data="estadosData" :options="donutOptions" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-1">
            <template v-for="(val, key) in herramientasPorEstado" :key="key">
              <div class="flex items-center gap-1.5">
                <div class="w-2 h-2 rounded-full" :style="{ background: estadoColor(key) }" />
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">{{ key }}:</span>
                <strong :style="{ color: 'var(--sapTextColor)' }">{{ val }}</strong>
              </div>
            </template>
          </div>
        </div>

        <!-- ③ VALOR TOTAL DE PÉRDIDAS — KPI -->
        <div class="card-ovp flex flex-col justify-center">
          <div class="card-header">
            <span class="sap-icon--money-bills" :style="{ color: 'var(--sapNegativeTextColor)' }" />
            <p class="card-title">Pérdidas Acumuladas</p>
          </div>
          <div class="text-center py-4 space-y-1">
            <p class="text-4xl font-bold" :style="{ color: 'var(--sapNegativeTextColor)' }">
              S/ {{ formatMoney(m.costo_total_perdidas) }}
            </p>
            <p class="text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
              Herramientas Perdidas · Malogradas
            </p>
            <p class="text-lg font-semibold mt-2" :style="{ color: 'var(--sapNegativeTextColor)' }">
              {{ herramientasPorEstado.Perdida }} perdidas ·
              {{ herramientasPorEstado.Malograda }} malogradas
            </p>
          </div>
        </div>

        <!-- ④ TOP RESPONSABLES — Barras Horizontales -->
        <div class="card-ovp md:col-span-2">
          <div class="card-header">
            <span class="sap-icon--group" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
            <p class="card-title">Top Grupos (por herramientas en uso)</p>
          </div>
          <div class="py-2" style="height: 220px">
            <Bar v-if="topGruposData" :data="topGruposData" :options="hBarOptions" />
          </div>
        </div>

        <!-- ⑤ PÉRDIDAS POR PARADA — Barras Verticales -->
        <div class="card-ovp">
          <div class="card-header">
            <span class="sap-icon--bar-chart" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
            <p class="card-title">Pérdidas por Parada (S/)</p>
          </div>
          <div class="py-2" style="height: 180px">
            <Bar v-if="perdidasParadaData" :data="perdidasParadaData" :options="vBarOptions" />
          </div>
        </div>

        <!-- ⑥ DISTRIBUCIÓN POR CATEGORÍA — TODO: Sprint 3 backend endpoint -->
        <!-- <div class="card-ovp">
          <div class="card-header">
            <span class="sap-icon--product" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
            <p class="card-title">Pérdidas por Categoría</p>
          </div>
          <div class="py-2" style="height: 180px">
            <Bar v-if="categoriaData" :data="categoriaData" :options="hBarOptions" />
          </div>
        </div> -->
<!-- ⑦ TOP 10 HERRAMIENTAS — Tabla Compact -->
        <div class="card-ovp md:col-span-2">
          <div class="card-header">
            <span class="sap-icon--list" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
            <p class="card-title">Top 10 Herramientas Más Entregadas</p>
          </div>
          <div class="mt-2 overflow-hidden rounded-sm border" :style="{ borderColor: 'var(--sapList_BorderColor)' }">
            <div
              class="grid grid-cols-12 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide border-b"
              :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
            >
              <span class="col-span-2">#</span>
              <span class="col-span-4">Código</span>
              <span class="col-span-4">Herramienta</span>
              <span class="col-span-2 text-right">Entregas</span>
            </div>
            <div
              v-for="(h, i) in (m.herramientas_mas_usadas ?? []).slice(0, 10)"
              :key="h.catalogo_id"
              class="grid grid-cols-12 px-3 py-1.5 text-xs border-b last:border-0 hover:bg-muted/20 transition-colors"
              :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
            >
              <span class="col-span-2" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ i + 1 }}</span>
              <code class="col-span-4 font-mono" :style="{ color: 'var(--sapButton_Emphasized_Background)' }">{{ h.codigo_interno }}</code>
              <span class="col-span-4 truncate">{{ h.nombre }}</span>
              <span class="col-span-2 text-right font-semibold">{{ h.veces_usada }}</span>
            </div>
            <p
              v-if="!m.herramientas_mas_usadas?.length"
              class="text-xs text-center py-3"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Sin datos aún</p>
          </div>
        </div>

        <!-- ⑧ ALERTAS ACTIVAS -->
        <div class="card-ovp">
          <div class="card-header">
            <span class="sap-icon--message-warning" :style="{ color: 'var(--sapCriticalColor)' }" />
            <p class="card-title">Alertas</p>
            <span
              v-if="alertas.length"
              class="ml-auto text-xs px-2 py-0.5 rounded-full font-bold"
              :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)' }"
            >{{ alertas.length }}</span>
          </div>
          <div class="mt-2 space-y-2">
            <div
              v-for="(alerta, i) in alertas"
              :key="i"
              class="flex items-start gap-2 p-2 rounded-sm border"
              :style="alertaStyle(alerta.nivel)"
            >
              <span :class="['sap-icon--message-warning text-sm shrink-0', alerta.nivel]" />
              <p class="text-xs leading-relaxed" :style="{ color: 'var(--sapTextColor)' }">{{ alerta.mensaje }}</p>
            </div>
            <p
              v-if="!alertas.length"
              class="text-xs text-center py-4"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              <span class="sap-icon--accept block text-2xl mb-1" :style="{ color: 'var(--sapPositiveTextColor)' }" />
              Sin alertas activas
            </p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement, BarElement, CategoryScale,
  LinearScale, Tooltip, Legend,
} from 'chart.js'
import { useDashboardStore } from '@/stores/dashboard'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const dashboardStore = useDashboardStore()
const m = computed(() => dashboardStore.metricas)

// ── Extraer colores SAP para Chart.js (no soporta CSS vars directamente) ─────
function sapColor(varName) {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim()
}

const sapColors = computed(() => ({
  success:  sapColor('--sapPositiveTextColor'),
  info:     sapColor('--sapInformationTextColor'),
  error:    sapColor('--sapNegativeTextColor'),
  warning:  sapColor('--sapCriticalColor'),
  neutral:  sapColor('--sapNeutralTextColor'),
  text:     sapColor('--sapTextColor'),
  label:    sapColor('--sapContent_LabelColor'),
  bg:       sapColor('--sapGroup_ContentBackground'),
  border:   sapColor('--sapList_BorderColor'),
  emphasis: sapColor('--sapButton_Emphasized_Background'),
}))

// ── Objeto herramientas_por_estado (derivado de escalares del backend) ─────────
const herramientasPorEstado = computed(() => ({
  Disponible: m.value?.herramientas_disponibles ?? 0,
  En_Uso: m.value?.herramientas_en_uso ?? 0,
  Malograda: m.value?.herramientas_malogradas ?? 0,
  Perdida: m.value?.herramientas_perdidas ?? 0,
}))

// ── Alertas (derivadas de KPIs del backend) ────────────────────────────────────
const alertas = computed(() => {
  const a = []
  if ((m.value?.reservas_pendientes ?? 0) > 0) a.push({ nivel: 'warning', mensaje: `${m.value.reservas_pendientes} reservas pendientes de aprobación` })
  if ((m.value?.pendientes_cierre ?? 0) > 0) a.push({ nivel: 'error', mensaje: `${m.value.pendientes_cierre} herramientas sin devolver (pendientes de cierre)` })
  if ((m.value?.epps_por_vencer ?? 0) > 0) a.push({ nivel: 'warning', mensaje: `${m.value.epps_por_vencer} EPPs con certificación próxima a vencer` })
  if (m.value?.paradas_activas?.length) m.value.paradas_activas.forEach(p => a.push({ nivel: 'info', mensaje: `Parada activa: ${p.nombre} (${p.codigo})` }))
  return a
})

// ── Card 1: Saturación ────────────────────────────────────────────────────────
const saturacionPct = computed(() => {
  if (!m.value) return 0
  const h = herramientasPorEstado.value
  const total = h.En_Uso + h.Disponible
  if (!total) return 0
  return Math.round((h.En_Uso / total) * 100)
})

const saturacionColor = computed(() => {
  const pct = saturacionPct.value
  if (pct < 60) return sapColor('--sapPositiveTextColor')
  if (pct < 80) return sapColor('--sapCriticalColor')
  return sapColor('--sapNegativeTextColor')
})

const saturacionStyle = computed(() => {
  const pct = saturacionPct.value
  if (pct < 60) return { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
  if (pct < 80) return { background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalColor)', borderColor: 'var(--sapWarningBorderColor)' }
  return { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }
})

const saturacionData = computed(() => {
  if (!m.value) return null
  const h = herramientasPorEstado.value
  return {
    datasets: [{
      data: [h.En_Uso, h.Disponible],
      backgroundColor: [saturacionColor.value, sapColor('--sapList_BorderColor')],
      borderWidth: 0,
    }],
  }
})

const saturacionOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '75%',
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
}

// ── Card 2: Estados ───────────────────────────────────────────────────────────
function estadoColor(estado) {
  return {
    Disponible:   sapColor('--sapPositiveTextColor'),
    En_Uso:       sapColor('--sapInformationTextColor'),
    Malograda:    sapColor('--sapNegativeTextColor'),
    Perdida:      sapColor('--sapNeutralTextColor'),
    Mantenimiento: sapColor('--sapCriticalColor'),
  }[estado] ?? sapColor('--sapNeutralTextColor')
}

const estadosData = computed(() => {
  if (!m.value) return null
  const h = herramientasPorEstado.value
  const entries = Object.entries(h).filter(([, v]) => v > 0)
  return {
    labels: entries.map(([k]) => k),
    datasets: [{
      data: entries.map(([, v]) => v),
      backgroundColor: entries.map(([k]) => estadoColor(k)),
      borderWidth: 0,
    }],
  }
})

const donutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.raw}`,
      },
    },
  },
}

// ── Card 4: Top Grupos ────────────────────────────────────────────────────────
const topGruposData = computed(() => {
  const grupos = m.value?.top_grupos_herramientas ?? []
  return {
    labels: grupos.map((g) => g.nombre_grupo),
    datasets: [{
      label: 'En uso',
      data: grupos.map((g) => g.herramientas_en_uso),
      backgroundColor: sapColor('--sapInformationBackground'),
      borderColor: sapColor('--sapInformationTextColor'),
      borderWidth: 1,
      borderRadius: 2,
    }],
  }
})

const hBarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => ` ${ctx.raw} herramientas` } },
  },
  scales: {
    x: { ticks: { color: sapColors.value.label }, grid: { color: sapColors.value.border } },
    y: { ticks: { color: sapColors.value.label }, grid: { display: false } },
  },
}))

// ── Card 5: Pérdidas por Parada ───────────────────────────────────────────────
const perdidasParadaData = computed(() => {
  const paradas = m.value?.perdidas_por_parada ?? []
  return {
    labels: paradas.map((p) => p.nombre_parada),
    datasets: [{
      label: 'S/ Pérdidas',
      data: paradas.map((p) => p.total_perdido),
      backgroundColor: sapColor('--sapErrorBackground'),
      borderColor: sapColor('--sapNegativeTextColor'),
      borderWidth: 1,
      borderRadius: 2,
    }],
  }
})

const vBarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => ` S/ ${ctx.raw.toFixed(2)}` } },
  },
  scales: {
    x: { ticks: { color: sapColors.value.label }, grid: { display: false } },
    y: { ticks: { color: sapColors.value.label, callback: (v) => `S/ ${v}` }, grid: { color: sapColors.value.border } },
  },
}))

// ── Card 6: Pérdidas por Categoría — TODO: Sprint 3 backend endpoint ──────────
/*
const categoriaData = computed(() => {
  const cats = m.value?.perdidas_por_categoria ?? []
  return {
    labels: cats.map((c) => c.categoria),
    datasets: [{
      label: 'S/ Pérdidas',
      data: cats.map((c) => c.valor_perdido),
      backgroundColor: sapColor('--sapWarningBackground'),
      borderColor: sapColor('--sapCriticalColor'),
      borderWidth: 1,
      borderRadius: 2,
    }],
  }
})
*/

// ── Card 8: Alertas ───────────────────────────────────────────────────────────
function alertaStyle(nivel) {
  if (nivel === 'error') return { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }
  if (nivel === 'warning') return { background: 'var(--sapWarningBackground)', borderColor: 'var(--sapWarningBorderColor)' }
  return { background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatMoney(val) {
  return (val ?? 0).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatHora(ts) {
  return format(new Date(ts), "HH:mm:ss", { locale: es })
}

// ── Refresh automático cada 60s ───────────────────────────────────────────────
let refreshTimer = null
onMounted(async () => {
  await dashboardStore.fetchResidente()
  refreshTimer = setInterval(() => dashboardStore.fetchResidente(), 60_000)
})
onUnmounted(() => clearInterval(refreshTimer))
</script>

<style scoped>
.card-ovp {
  padding: 1rem;
  border-radius: 0.125rem;
  border: 1px solid var(--sapList_BorderColor);
  background: var(--sapGroup_ContentBackground);
  box-shadow: var(--sapContent_Shadow0);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--sapList_BorderColor);
}
.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--sapTextColor);
}
</style>
