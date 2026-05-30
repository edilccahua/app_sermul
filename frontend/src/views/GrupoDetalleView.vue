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
          @click="$router.push('/app/grupos')"
        >
          ← Volver a Grupos
        </button>
      </div>
    </div>

    <!-- ══ Object Page Content ════════════════════════════════════════════════ -->
    <template v-else>
      <!-- ── Object Page Header ──────────────────────────────────────────── -->
      <div
        class="px-6 pt-4 pb-5 border-b shrink-0 flex flex-col gap-4"
        :style="{ background: 'var(--sapObjectHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
      >
        <!-- Breadcrumb + Title -->
        <div>
          <button
            class="h-8 px-3 text-xs flex items-center gap-1 mb-3 transition-colors rounded-sm hover:bg-black/5"
            :style="{ background: 'transparent', color: 'var(--sapButton_TextColor)', borderColor: 'transparent' }"
            @click="$router.push('/app/grupos')"
          >
            <span class="sap-icon--nav-back" /> Volver a Grupos
          </button>

          <div class="flex items-start gap-4">
            <span
              class="sap-icon--group text-4xl mt-1"
              :style="{ color: 'var(--sapContent_IconColor)' }"
            />
            <div>
              <h1
                class="text-2xl font-bold mb-1"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                GRUPO {{ grupo.codigo }} — {{ grupo.nombre }}
              </h1>
              <div class="flex flex-wrap gap-4 text-sm">
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">
                  <span class="sap-icon--calendar mr-1" />{{ grupo.parada?.codigo ?? '—' }}
                </span>
                <span
                  v-if="grupo.circuito_area"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  <span class="sap-icon--functional-location mr-1" />{{ grupo.circuito_area }}
                </span>
                <span
                  v-if="grupo.descripcion"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  <span class="sap-icon--hint mr-1" />{{ grupo.descripcion }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Facets: Líder + Supervisores -->
        <div class="flex flex-wrap gap-8 mt-2 pl-14">
          <!-- Líder -->
          <div
            v-if="lider"
            class="flex flex-col"
          >
            <span
              class="text-xs mb-0.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Líder de Frente</span>
            <span
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              {{ lider.usuario.nombre }} {{ lider.usuario.apellido }}
            </span>
            <span
              class="text-xs"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >{{ lider.usuario.dni }}</span>
          </div>

          <!-- Supervisores -->
          <div
            v-for="sup in supervisores"
            :key="sup.usuario.id"
            class="flex flex-col"
          >
            <span
              class="text-xs mb-0.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ sup.usuario.rol?.codigo === 'SUP_MEC' ? 'Sup. Operaciones' : 'Sup. SSOMA' }}
            </span>
            <span
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              {{ sup.usuario.nombre }} {{ sup.usuario.apellido }}
            </span>
            <span
              class="text-xs"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >{{ sup.usuario.dni }}</span>
          </div>
        </div>
      </div>

      <!-- ── Anchor Bar (Tabs) ────────────────────────────────────────────── -->
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

      <!-- ── Tab Content ──────────────────────────────────────────────────── -->
      <div class="flex-1 overflow-auto p-6">

        <!-- TAB: Integrantes ──────────────────────────────────────────────── -->
        <div v-if="tabActivo === 'integrantes'">
          <div
            class="border overflow-hidden rounded-sm"
            :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
          >
            <!-- Toolbar -->
            <div
              class="h-10 px-4 border-b flex items-center gap-2"
              :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              <span
                class="text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Integrantes
                <span
                  class="font-semibold"
                  :style="{ color: 'var(--sapTextColor)' }"
                >({{ todosIntegrantes.length }})</span>
              </span>
            </div>

            <!-- Compact Table -->
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
                    class="h-8 px-3 text-left text-xs font-semibold"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    Especialidad
                  </th>
                  <th
                    class="h-8 px-3 text-left text-xs font-semibold"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    Ingreso
                  </th>
                </tr>
              </thead>
              <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
                <tr
                  v-for="int in todosIntegrantes"
                  :key="int.id"
                  class="border-b transition-colors hover:bg-black/5"
                  :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                >
                  <!-- DNI -->
                  <td
                    class="px-3 py-1.5 font-mono text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    {{ int.usuario.dni }}
                  </td>
                  <!-- Nombre -->
                  <td class="px-3 py-1.5">
                    <div class="flex items-center gap-2">
                      <router-link
                        :to="`/app/personal/${int.usuario.id}`"
                        class="font-medium hover:underline transition-colors"
                        :style="{ color: 'var(--sapLinkColor, var(--sapTextColor))' }"
                      >
                        {{ int.usuario.nombre }} {{ int.usuario.apellido }}
                      </router-link>
                      <!-- Badge líder -->
                      <span
                        v-if="int.es_lider_frente"
                        class="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-sm font-semibold"
                        :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }"
                      >
                        <span class="sap-icon--favorite text-[10px]" /> Líder
                      </span>
                    </div>
                  </td>
                  <!-- Rol -->
                  <td
                    class="px-3 py-1.5 text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    {{ rolLabel(int) }}
                  </td>
                  <!-- Especialidad -->
                  <td
                    class="px-3 py-1.5 text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    {{ int.usuario.especialidad?.nombre ?? '—' }}
                  </td>
                  <!-- Ingreso -->
                  <td
                    class="px-3 py-1.5 font-mono text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    {{ formatDate(int.fecha_ingreso) }}
                  </td>
                </tr>

                <!-- Empty state -->
                <tr v-if="todosIntegrantes.length === 0">
                  <td
                    colspan="5"
                    class="py-10 text-center"
                  >
                    <span
                      class="sap-icon--employee text-3xl block mb-2"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    />
                    <p
                      class="text-sm"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      No hay integrantes registrados en este grupo.
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- TAB: Herramientas ─────────────────────────────────────────────── -->
        <div v-if="tabActivo === 'herramientas'">
          <div
            class="border overflow-hidden rounded-sm"
            :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
          >
            <!-- Toolbar -->
            <div
              class="h-10 px-4 border-b flex items-center gap-2"
              :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              <span
                class="text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Herramientas
                <span
                  class="font-semibold"
                  :style="{ color: 'var(--sapTextColor)' }"
                >({{ herramientas.length }})</span>
              </span>
              <div class="ml-auto">
                <span
                  v-if="herramientas.some(h => h.falta > 0)"
                  class="inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-sm"
                  :style="{ background: 'var(--sapCriticalBackground)', color: 'var(--sapCriticalTextColor)' }"
                >
                  <span class="sap-icon--alert" />
                  Hay herramientas sin devolver
                </span>
                <span
                  v-else-if="herramientas.length > 0"
                  class="inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-sm"
                  :style="{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                >
                  <span class="sap-icon--accept" />
                  Todo devuelto
                </span>
              </div>
            </div>

            <!-- Loading -->
            <div
              v-if="herramientasLoading"
              class="py-12 text-center"
              :style="{ background: 'var(--sapGroup_ContentBackground)' }"
            >
              <span
                class="sap-icon--refresh animate-spin text-3xl block mb-3"
                :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
              />
              <p
                class="text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Cargando inventario...
              </p>
            </div>

            <!-- Compact Table -->
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
                  v-for="herr in herramientas"
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
                  <!-- Prestado -->
                  <td class="px-3 py-1.5 text-center">
                    <span
                      class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-semibold"
                      :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)' }"
                    >
                      {{ herr.prestado }}
                    </span>
                  </td>
                  <!-- Devuelto -->
                  <td class="px-3 py-1.5 text-center">
                    <span
                      class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-semibold"
                      :style="{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                    >
                      {{ herr.devuelto }}
                    </span>
                  </td>
                  <!-- Perdido -->
                  <td class="px-3 py-1.5 text-center">
                    <span
                      class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-semibold"
                      :style="herr.perdido > 0
                        ? { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)' }
                        : { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                    >
                      {{ herr.perdido }}
                    </span>
                  </td>
                  <!-- Falta -->
                  <td class="px-3 py-1.5 text-center">
                    <span
                      class="inline-flex items-center justify-center w-7 h-5 rounded-sm text-xs font-bold"
                      :style="herr.falta > 0
                        ? { background: 'var(--sapCriticalBackground)', color: 'var(--sapCriticalTextColor)' }
                        : { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }"
                    >
                      {{ herr.falta }}
                    </span>
                  </td>
                </tr>

                <!-- Empty state -->
                <tr v-if="!herramientasLoading && herramientas.length === 0">
                  <td
                    colspan="6"
                    class="py-10 text-center"
                  >
                    <span
                      class="sap-icon--accept text-3xl block mb-2"
                      :style="{ color: 'var(--sapPositiveTextColor)' }"
                    />
                    <p
                      class="text-sm font-semibold"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >
                      Sin herramientas asignadas
                    </p>
                    <p
                      class="text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Este grupo no tiene movimientos de herramientas registrados.
                    </p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { gruposAPI } from '@/api'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const grupo = ref(null)

const tabActivo = ref('integrantes')
const tabs = [
  { key: 'integrantes', label: 'Integrantes' },
  { key: 'herramientas', label: 'Herramientas' },
]

const herramientasLoading = ref(false)
const herramientas = ref([])

// ── Computed: Facets cabecera ────────────────────────────────────────────────
const lider = computed(() =>
  grupo.value?.integrantes?.find(i => i.es_lider_frente) ?? null
)

const supervisores = computed(() =>
  grupo.value?.integrantes?.filter(
    i => ['SUP_MEC', 'SUP_SSOMA'].includes(i.usuario.rol?.codigo)
  ) ?? []
)

// ── Orden: SUP_MEC → SUP_SSOMA → Líder → Técnicos ───────────────────────────
const ORDEN_ROL = { SUP_MEC: 0, SUP_SSOMA: 1 }

const todosIntegrantes = computed(() => {
  if (!grupo.value?.integrantes) return []
  return [...grupo.value.integrantes].sort((a, b) => {
    const rolA = a.usuario.rol?.codigo
    const rolB = b.usuario.rol?.codigo
    // SUP_MEC y SUP_SSOMA van primero
    const oA = ORDEN_ROL[rolA] ?? (a.es_lider_frente ? 2 : 3)
    const oB = ORDEN_ROL[rolB] ?? (b.es_lider_frente ? 2 : 3)
    return oA - oB
  })
})

// Etiqueta legible por rol + flag líder
function rolLabel(integrante) {
  const cod = integrante.usuario.rol?.codigo
  if (cod === 'SUP_MEC')   return 'Sup. Operaciones'
  if (cod === 'SUP_SSOMA') return 'Sup. SSOMA'
  if (integrante.es_lider_frente) return 'Líder de Frente'
  return integrante.usuario.especialidad?.nombre ?? 'Técnico'
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-PE')
}

onMounted(async () => {
  try {
    const { data } = await gruposAPI.getById(route.params.id)
    grupo.value = data

    // Cargar herramientas en paralelo
    herramientasLoading.value = true
    try {
      const { data: hData } = await gruposAPI.herramientasEnUsoGrupo(route.params.id)
      herramientas.value = hData.herramientas ?? []
    } catch (hErr) {
      console.error('Error al cargar herramientas del grupo', hErr)
      herramientas.value = []
    } finally {
      herramientasLoading.value = false
    }
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Error al cargar el grupo'
  } finally {
    loading.value = false
  }
})
</script>
