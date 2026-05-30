<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Loading -->
    <template v-if="loading">
      <div class="flex-1 flex items-center justify-center">
        <span
          class="sap-icon--refresh animate-spin text-3xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
      </div>
    </template>

    <!-- Error -->
    <template v-else-if="error">
      <div class="flex-1 flex items-center justify-center p-6">
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
            @click="$router.push('/app/paradas')"
          >
            ← Volver a Paradas
          </button>
        </div>
      </div>
    </template>

    <!-- ══ Object Page ════════════════════════════════════════════════════════ -->
    <template v-else>
      <!-- ── Object Page Header ─────────────────────────────────────────── -->
      <div
        class="px-6 py-4 border-b shrink-0"
        :style="{ background: 'var(--sapObjectHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
      >
        <button
          class="h-8 px-3 text-xs border rounded-sm flex items-center gap-1 mb-2"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="$router.push('/app/paradas')"
        >
          <span class="sap-icon--nav-back" /> Volver
        </button>
        <h1 class="text-2xl">
          [{{ parada.codigo }}] <span class="font-bold">{{ parada.nombre }}</span>
        </h1>
        <div class="flex gap-4 mt-2 text-sm">
          <span>Inicio: {{ parada.fecha_inicio }}</span>
          <span>Fin: {{ parada.fecha_fin || '—' }}</span>
          <span
            class="px-2 py-0.5 rounded-sm border text-xs font-medium"
            :style="estadoBadgeStyle(parada.estado)"
          >{{ parada.estado }}</span>
        </div>
      </div>

      <!-- ── Anchor Bar ──────────────────────────────────────────────────── -->
      <div
        class="border-b shrink-0 flex gap-0 px-6"
        :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'var(--sapObjectHeader_Background)' }"
      >
        <button
          v-for="t in tabs"
          :key="t.key"
          class="px-4 py-3 text-sm font-medium border-b-2 transition-all"
          :style="tabActivo === t.key
            ? { color: 'var(--sapButton_Emphasized_Background)', borderBottomColor: 'var(--sapButton_Emphasized_Background)' }
            : { color: 'var(--sapContent_LabelColor)', borderBottomColor: 'transparent' }"
          @click="tabActivo = t.key"
        >
          {{ t.label }}
        </button>
      </div>

      <!-- ── Tab Content ─────────────────────────────────────────────────── -->
      <div class="flex-1 overflow-auto p-6 space-y-4">

        <!-- ─── TAB: Cuadrillas ─────────────────────────────────────────── -->
        <div v-if="tabActivo === 'cuadrillas'">
          <div
            v-if="!grupos.length"
            class="text-sm text-center py-8"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            No hay cuadrillas asignadas a esta parada.
          </div>

          <!-- Un bloque (Object Page Section) por grupo -->
          <div
            v-for="g in grupos"
            :key="g.id"
            class="border overflow-hidden rounded-sm"
            :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
          >
            <!-- Section Header: Facets del grupo (líder + supervisores) -->
            <div
              class="px-4 pt-4 pb-3 border-b"
              :style="{ background: 'var(--sapObjectHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              <div class="flex items-start justify-between gap-4 flex-wrap">
                <!-- Título grupo -->
                <div class="flex items-center gap-2">
                  <span
                    class="sap-icon--group text-lg"
                    :style="{ color: 'var(--sapContent_IconColor)' }"
                  />
                  <router-link
                    :to="`/app/grupos/${g.id}`"
                    class="font-semibold text-sm hover:underline transition-colors"
                    :style="{ color: 'var(--sapLinkColor, var(--sapTextColor))' }"
                  >
                    GRUPO {{ g.codigo }} — {{ g.nombre }}
                  </router-link>
                  <span
                    v-if="g.circuito_area"
                    class="text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >· {{ g.circuito_area }}</span>
                </div>
                <!-- Facets clave -->
                <div class="flex flex-wrap gap-6">
                  <!-- Líder -->
                  <div
                    v-if="getLider(g.integrantes)"
                    class="flex flex-col"
                  >
                    <span
                      class="text-[10px] font-medium uppercase tracking-wide"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >Líder</span>
                    <span
                      class="text-xs font-semibold"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >
                      {{ getLider(g.integrantes)?.usuario.nombre }}
                      {{ getLider(g.integrantes)?.usuario.apellido }}
                    </span>
                  </div>
                  <!-- Supervisores -->
                  <div
                    v-for="sup in getSupervisores(g.integrantes)"
                    :key="sup.usuario.id"
                    class="flex flex-col"
                  >
                    <span
                      class="text-[10px] font-medium uppercase tracking-wide"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      {{ sup.usuario.rol?.codigo === 'SUP_MEC' ? 'Sup. Op.' : 'Sup. SSOMA' }}
                    </span>
                    <span
                      class="text-xs font-semibold"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >
                      {{ sup.usuario.nombre }} {{ sup.usuario.apellido }}
                    </span>
                  </div>
                  <!-- Contador integrantes -->
                  <div class="flex flex-col">
                    <span
                      class="text-[10px] font-medium uppercase tracking-wide"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >Integrantes</span>
                    <span
                      class="text-xs font-semibold"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >{{ g.integrantes?.length ?? 0 }}</span>
                  </div>
                </div>
              </div>

              <!-- Segmented Buttons (sub-tabs por grupo) -->
              <div class="flex gap-0 mt-3 border rounded-sm overflow-hidden w-fit"
                   :style="{ borderColor: 'var(--sapButton_BorderColor)' }"
              >
                <button
                  class="h-7 px-4 text-xs font-medium transition-colors"
                  :style="getSubTab(g.id) === 'integrantes'
                    ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
                    : { background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)' }"
                  @click="setSubTab(g.id, 'integrantes')"
                >
                  <span class="sap-icon--employee mr-1 text-xs" />
                  Integrantes ({{ g.integrantes?.length ?? 0 }})
                </button>
                <button
                  class="h-7 px-4 text-xs font-medium transition-colors border-l"
                  :style="getSubTab(g.id) === 'herramientas'
                    ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', borderColor: 'var(--sapButton_Emphasized_Background)' }
                    : { background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
                  @click="setSubTab(g.id, 'herramientas'); cargarHerramientas(g.id)"
                >
                  <span class="sap-icon--wrench mr-1 text-xs" />
                  Herramientas
                </button>
              </div>
            </div>

            <!-- Sub-tab: Integrantes ──────────────────────────────────────── -->
            <div v-if="getSubTab(g.id) === 'integrantes'">
              <table class="w-full text-sm">
                <thead>
                  <tr
                    :style="{
                      background: 'var(--sapList_HeaderBackground)',
                      borderBottom: '1px solid var(--sapList_BorderColor)',
                    }"
                  >
                    <th
                      class="h-8 px-3 text-left text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      DNI
                    </th>
                    <th
                      class="h-8 px-3 text-left text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Nombre Completo
                    </th>
                    <th
                      class="h-8 px-3 text-left text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Rol
                    </th>
                    <th
                      class="h-8 px-3 text-left text-xs font-semibold hidden md:table-cell"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Especialidad
                    </th>
                  </tr>
                </thead>
                <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
                  <tr
                    v-for="int in getIntegrantesOrdenados(g.integrantes)"
                    :key="int.id"
                    class="border-b transition-colors hover:bg-black/5"
                    :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                  >
                    <td
                      class="px-3 py-1.5 font-mono text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      {{ int.usuario.dni }}
                    </td>
                    <td class="px-3 py-1.5">
                      <div class="flex items-center gap-2">
                        <router-link
                          :to="`/app/personal/${int.usuario.id}`"
                          class="font-medium hover:underline transition-colors"
                          :style="{ color: 'var(--sapLinkColor, var(--sapTextColor))' }"
                        >
                          {{ int.usuario.nombre }} {{ int.usuario.apellido }}
                        </router-link>
                        <span
                          v-if="int.es_lider_frente"
                          class="inline-flex items-center text-[10px] px-1.5 py-0.5 rounded-sm font-semibold"
                          :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }"
                        >
                          <span class="sap-icon--favorite mr-0.5 text-[10px]" /> Líder
                        </span>
                      </div>
                    </td>
                    <td
                      class="px-3 py-1.5 text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      {{ rolLabel(int) }}
                    </td>
                    <td
                      class="px-3 py-1.5 text-xs hidden md:table-cell"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      {{ int.usuario.especialidad?.nombre ?? '—' }}
                    </td>
                  </tr>
                  <tr v-if="!g.integrantes?.length">
                    <td
                      colspan="4"
                      class="py-6 text-center text-sm"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Sin integrantes registrados.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Sub-tab: Herramientas ─────────────────────────────────────── -->
            <div v-if="getSubTab(g.id) === 'herramientas'">
              <!-- Loading herramientas del grupo -->
              <div
                v-if="herramientasMap[g.id]?.loading"
                class="py-10 text-center"
                :style="{ background: 'var(--sapGroup_ContentBackground)' }"
              >
                <span
                  class="sap-icon--refresh animate-spin text-2xl block mb-2"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p
                  class="text-xs"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Cargando inventario...
                </p>
              </div>

              <table
                v-else
                class="w-full text-sm"
              >
                <thead>
                  <tr
                    :style="{
                      background: 'var(--sapList_HeaderBackground)',
                      borderBottom: '1px solid var(--sapList_BorderColor)',
                    }"
                  >
                    <th
                      class="h-8 px-3 text-left text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Código
                    </th>
                    <th
                      class="h-8 px-3 text-left text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Herramienta
                    </th>
                    <th
                      class="h-8 px-3 text-center text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Prestado
                    </th>
                    <th
                      class="h-8 px-3 text-center text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Devuelto
                    </th>
                    <th
                      class="h-8 px-3 text-center text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Perdido
                    </th>
                    <th
                      class="h-8 px-3 text-center text-xs font-semibold"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Falta
                    </th>
                  </tr>
                </thead>
                <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
                  <tr
                    v-for="herr in herramientasMap[g.id]?.items ?? []"
                    :key="herr.catalogo_id"
                    class="border-b transition-colors hover:bg-black/5"
                    :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                  >
                    <td
                      class="px-3 py-1.5 font-mono text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      {{ herr.codigo_interno }}
                    </td>
                    <td
                      class="px-3 py-1.5 font-medium"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >
                      {{ herr.nombre }}
                    </td>
                    <td class="px-3 py-1.5 text-center">
                      <span
                        class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-semibold"
                        :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)' }"
                      >{{ herr.prestado }}</span>
                    </td>
                    <td class="px-3 py-1.5 text-center">
                      <span
                        class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-semibold"
                        :style="{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                      >{{ herr.devuelto }}</span>
                    </td>
                    <td class="px-3 py-1.5 text-center">
                      <span
                        class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-semibold"
                        :style="herr.perdido > 0
                          ? { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)' }
                          : { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                      >{{ herr.perdido }}</span>
                    </td>
                    <td class="px-3 py-1.5 text-center">
                      <span
                        class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-bold"
                        :style="herr.falta > 0
                          ? { background: 'var(--sapCriticalBackground)', color: 'var(--sapCriticalTextColor)' }
                          : { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                      >{{ herr.falta }}</span>
                    </td>
                  </tr>

                  <!-- Empty -->
                  <tr v-if="!herramientasMap[g.id]?.loading && !(herramientasMap[g.id]?.items ?? []).length">
                    <td
                      colspan="6"
                      class="py-8 text-center"
                    >
                      <span
                        class="sap-icon--accept text-2xl block mb-1"
                        :style="{ color: 'var(--sapPositiveTextColor)' }"
                      />
                      <p
                        class="text-xs"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      >
                        Sin herramientas asignadas a este grupo.
                      </p>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ─── TAB: Nómina ────────────────────────────────────────────── -->
        <div v-if="tabActivo === 'nomina'">
          <div
            class="text-sm text-center py-4"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Nómina completa (próximamente)
          </div>
        </div>

        <!-- ─── TAB: Información ──────────────────────────────────────── -->
        <div v-if="tabActivo === 'info'">
          <div
            class="p-4 rounded-sm border max-w-xl"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <p
              class="text-sm font-semibold mb-4"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              Información de la Parada
            </p>
            <div class="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Código:</span>
              <span class="font-semibold font-mono">{{ parada.codigo }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Nombre:</span>
              <span class="font-semibold">{{ parada.nombre }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Inicio:</span>
              <span class="font-semibold">{{ parada.fecha_inicio }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Fin:</span>
              <span class="font-semibold">{{ parada.fecha_fin || '—' }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Empresa Contratista:</span>
              <span class="font-semibold">{{ parada.empresa_contratista || 'SERMUL EIRL' }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Gerencia del Contrato:</span>
              <span class="font-semibold">{{ parada.gerencia_contrato || '—' }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Responsable CMA:</span>
              <span class="font-semibold">{{ parada.responsable_cma || '—' }}</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Ubicación:</span>
              <span class="font-semibold">{{ parada.ubicacion || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- ─── TAB: Cierre ────────────────────────────────────────────── -->
        <div v-if="tabActivo === 'cierre'">
          <div v-if="parada.estado === 'Activa'">
            <router-link
              :to="`/app/paradas/${parada.id}/cierre`"
              class="inline-flex items-center gap-2 h-10 px-6 rounded-sm text-sm font-semibold"
              :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }"
            >
              <span class="sap-icon--stop" /> Ir al Cierre de Parada
            </router-link>
          </div>
          <div
            v-else
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            La parada no está activa. No es posible realizar un cierre.
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { paradasAPI, gruposAPI } from '@/api'

const route  = useRoute()
const loading = ref(true)
const error   = ref(null)
const parada  = ref(null)
const grupos  = ref([])

const tabActivo = ref('cuadrillas')
const tabs = [
  { key: 'cuadrillas', label: 'Cuadrillas' },
  { key: 'nomina',     label: 'Nómina' },
  { key: 'info',       label: 'Información' },
  { key: 'cierre',     label: 'Cierre' },
]

// Sub-tab activo por grupo: { [grupoId]: 'integrantes' | 'herramientas' }
const subTabs = reactive({})
const getSubTab = (gid) => subTabs[gid] ?? 'integrantes'
const setSubTab = (gid, tab) => { subTabs[gid] = tab }

// Herramientas cargadas por grupo: { [grupoId]: { loading, items[] } }
const herramientasMap = reactive({})

async function cargarHerramientas(grupoId) {
  if (herramientasMap[grupoId]?.items) return // ya cargado, no repetir
  herramientasMap[grupoId] = { loading: true, items: null }
  try {
    const { data } = await gruposAPI.herramientasEnUsoGrupo(grupoId)
    herramientasMap[grupoId].items = data.herramientas ?? []
  } catch {
    herramientasMap[grupoId].items = []
  } finally {
    herramientasMap[grupoId].loading = false
  }
}

// ── Helpers de integrantes ──────────────────────────────────────────────────
const getLider = (integrantes) =>
  integrantes?.find(i => i.es_lider_frente) ?? null

const getSupervisores = (integrantes) =>
  integrantes?.filter(i => ['SUP_MEC', 'SUP_SSOMA'].includes(i.usuario.rol?.codigo)) ?? []

const ORDEN_ROL = { SUP_MEC: 0, SUP_SSOMA: 1 }

const getIntegrantesOrdenados = (integrantes) => {
  if (!integrantes) return []
  return [...integrantes].sort((a, b) => {
    const rolA = a.usuario.rol?.codigo
    const rolB = b.usuario.rol?.codigo
    const oA = ORDEN_ROL[rolA] ?? (a.es_lider_frente ? 2 : 3)
    const oB = ORDEN_ROL[rolB] ?? (b.es_lider_frente ? 2 : 3)
    return oA - oB
  })
}

function rolLabel(integrante) {
  const cod = integrante.usuario.rol?.codigo
  if (cod === 'SUP_MEC')   return 'Sup. Operaciones'
  if (cod === 'SUP_SSOMA') return 'Sup. SSOMA'
  if (integrante.es_lider_frente) return 'Líder de Frente'
  return integrante.usuario.especialidad?.nombre ?? 'Técnico'
}

// ── Estado Badge ────────────────────────────────────────────────────────────
const estadoBadgeStyle = (estado) => {
  const map = {
    Activa:     { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)',   borderColor: 'var(--sapSuccessBorderColor)' },
    Pendiente:  { background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalTextColor)',   borderColor: 'var(--sapWarningBorderColor)' },
    Finalizada: { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
  }
  return map[estado] ?? { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' }
}

// ── onMounted ───────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const { data: paradaData } = await paradasAPI.getById(route.params.id)
    parada.value = paradaData
    const { data: gruposData } = await gruposAPI.get({ parada_id: route.params.id })
    grupos.value = gruposData
  } catch (err) {
    error.value = 'Error al cargar los datos de la parada'
  } finally {
    loading.value = false
  }
})
</script>
