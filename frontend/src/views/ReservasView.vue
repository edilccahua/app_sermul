<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Dynamic Page Header + Filter Bar -->
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3 mb-4">
        <span
          class="sap-icon--list text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Reservas
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Gestión del workflow: Pendiente → Aprobada → Despachada
          </p>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2">
          <label
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >Estado:</label>
          <select
            v-model="filtros.estado"
            class="h-8 border px-2 text-xs rounded-sm"
            :style="selectStyle"
          >
            <option value="">
              Todos
            </option>
            <option value="Pendiente">
              Pendiente
            </option>
            <option value="Aprobada">
              Aprobada
            </option>
            <option value="Rechazada">
              Rechazada
            </option>
            <option value="Despachada">
              Despachada
            </option>
            <option value="Cancelada">
              Cancelada
            </option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <label
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >Parada:</label>
          <select
            v-model="filtros.parada_id"
            class="h-8 border px-2 text-xs rounded-sm"
            :style="selectStyle"
          >
            <option
              v-for="p in paradasStore.items"
              :key="p.id"
              :value="p.id"
            >
              {{ p.codigo }} - {{ p.nombre }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table Toolbar -->
    <div
      class="flex items-center gap-3 px-6 py-2 border-b shrink-0"
      :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <span
        class="text-sm font-medium"
        :style="{ color: 'var(--sapTextColor)' }"
      >
        Reservas ({{ reservasStore.items.length }})
      </span>
      <router-link
        to="/app/reservas/crear"
        class="ml-auto flex items-center gap-1.5 h-8 px-3 text-xs font-medium rounded-sm"
        :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
      >
        <span class="sap-icon--add-product" /> Nueva Reserva
      </router-link>
    </div>

    <!-- Tabla Compact -->
    <div class="flex-1 overflow-auto">
      <div
        v-if="reservasStore.loading"
        class="flex items-center justify-center py-8"
      >
        <span
          class="sap-icon--refresh animate-spin text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
      </div>
      <table
        v-else
        class="w-full text-xs border-collapse"
      >
        <thead>
          <tr :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)' }">
            <th
              v-for="col in columnas"
              :key="col"
              class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              {{ col }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in reservasStore.items"
            :key="r.id"
            class="border-b hover:bg-muted/20 transition-colors"
            :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
          >
            <td class="px-4 py-1.5">
              <code
                class="font-mono"
                :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
              >{{ r.codigo_reserva }}</code>
            </td>
            <td class="px-4 py-1.5">
              {{ r.grupo?.nombre ?? '—' }}
            </td>
            <td
              class="px-4 py-1.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ r.parada?.nombre ?? '—' }}
            </td>
            <td class="px-4 py-1.5">
              <span
                class="px-2 py-0.5 rounded-sm border text-xs font-medium"
                :style="estadoBadgeStyle(r.estado)"
              >
                {{ r.estado }}
              </span>
            </td>
            <td
              class="px-4 py-1.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ r.turno }}
            </td>
            <td
              class="px-4 py-1.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ r.fecha_programada ? new Date(r.fecha_programada).toLocaleDateString('es-PE') : '—' }}
            </td>
            <td class="px-4 py-1.5 text-center">
              {{ r.detalles?.length ?? '—' }}
            </td>
            <!-- Acciones según estado -->
            <td class="px-4 py-1.5">
              <div class="flex items-center gap-1">
                <!-- Pendiente -->
                <template v-if="r.estado === 'Pendiente'">
                  <button
                    class="h-6 px-2 text-xs rounded-sm border transition-colors"
                    :style="{ background: 'var(--sapButton_Accept_Background)', color: 'var(--sapButton_Accept_TextColor)', border: 'none' }"
                    @click="aprobar(r.id)"
                  >
                    <span class="sap-icon--accept" />
                  </button>
                  <button
                    class="h-6 px-2 text-xs rounded-sm border transition-colors"
                    :style="{ background: 'var(--sapButton_Reject_Background)', color: 'var(--sapButton_Reject_TextColor)', border: 'none' }"
                    @click="abrirRechazar(r)"
                  >
                    <span class="sap-icon--decline" />
                  </button>
                </template>
                <!-- Aprobada -->
                <router-link
                  v-if="r.estado === 'Aprobada'"
                  :to="`/app/reservas/despachar/${r.id}`"
                  class="h-6 px-2 text-xs rounded-sm font-medium transition-colors"
                  :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
                >
                  Despachar
                </router-link>
                <!-- Rechazada: mostrar motivo -->
                <span
                  v-if="r.estado === 'Rechazada' && r.motivo_rechazo"
                  class="text-xs truncate max-w-[120px]"
                  :style="{ color: 'var(--sapNegativeTextColor)' }"
                  :title="r.motivo_rechazo"
                >
                  {{ r.motivo_rechazo }}
                </span>
              </div>
            </td>
          </tr>
          <tr v-if="!reservasStore.loading && !reservasStore.items.length">
            <td
              colspan="8"
              class="px-4 py-8 text-center text-xs"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              No hay reservas con los filtros seleccionados.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Dialog Rechazar -->
    <div
      v-if="dialogRechazar"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.4)"
    >
      <div
        class="w-full max-w-md rounded-sm border shadow-xl"
        :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow2)' }"
      >
        <div
          class="px-5 py-4 border-b flex items-center gap-2"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <span
            class="sap-icon--decline"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          />
          <h2
            class="text-base font-semibold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Rechazar Reserva
          </h2>
        </div>
        <div class="p-5 space-y-3">
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Reserva <code class="font-mono">{{ reservaARechazar?.codigo }}</code>
          </p>
          <div class="space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Motivo de rechazo *:</label>
            <textarea
              v-model="motivoRechazo"
              rows="3"
              placeholder="Indica el motivo del rechazo..."
              class="w-full border px-3 py-2 text-sm rounded-sm resize-none focus:outline-none"
              :style="{ background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor)' }"
            />
          </div>
        </div>
        <div
          class="flex gap-3 px-5 py-4 border-t"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <button
            class="flex-1 h-9 text-sm border rounded-sm"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
            @click="dialogRechazar = false"
          >
            Cancelar
          </button>
          <button
            :disabled="!motivoRechazo.trim() || rechazando"
            class="flex-1 h-9 text-sm font-medium rounded-sm"
            :style="{ background: 'var(--sapButton_Reject_Background)', color: 'var(--sapButton_Reject_TextColor)', border: 'none' }"
            @click="confirmarRechazo"
          >
            <span
              v-if="rechazando"
              class="sap-icon--refresh animate-spin mr-1"
            />
            Rechazar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useReservasStore } from '@/stores/reservas'
import { useParadasStore } from '@/stores/paradas'
import { useToast } from '@/components/ui/toast'

const reservasStore = useReservasStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

const columnas = ['Código', 'Grupo', 'Parada', 'Estado', 'Turno', 'Fecha', 'Ítems', 'Acciones']
const filtros = reactive({ estado: '', parada_id: '' })

async function aplicarFiltros() {
  const params = {}
  if (filtros.estado) params.estado = filtros.estado
  if (filtros.parada_id) params.parada_id = filtros.parada_id
  await reservasStore.fetchAll(params)
}

watch(filtros, () => {
  aplicarFiltros()
}, { deep: true })

async function aprobar(id) {
  try {
    await reservasStore.aprobar(id)
    toast({ title: '✓ Reserva aprobada', variant: 'success' })
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail, variant: 'error' })
  }
}

// Dialog Rechazar
const dialogRechazar = ref(false)
const reservaARechazar = ref(null)
const motivoRechazo = ref('')
const rechazando = ref(false)

function abrirRechazar(r) {
  reservaARechazar.value = r
  motivoRechazo.value = ''
  dialogRechazar.value = true
}

async function confirmarRechazo() {
  if (!motivoRechazo.value.trim() || rechazando.value) return
  rechazando.value = true
  try {
    await reservasStore.rechazar(reservaARechazar.value.id, motivoRechazo.value.trim())
    toast({ title: '✓ Reserva rechazada', variant: 'success' })
    dialogRechazar.value = false
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail, variant: 'error' })
  } finally {
    rechazando.value = false
  }
}

function estadoBadgeStyle(estado) {
  return {
    Pendiente:  { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
    Aprobada:   { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
    Rechazada:  { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' },
    Despachada: { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' },
    Cancelada:  { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
  }[estado] ?? {}
}

const selectStyle = { background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor)' }

onMounted(async () => {
  await paradasStore.fetchAll()
  if (paradasStore.items.length > 0) {
    filtros.parada_id = paradasStore.items[paradasStore.items.length - 1].id
  }
  // The watch on filtros will trigger aplicarFiltros automatically
  if (!filtros.parada_id) {
    await reservasStore.fetchAll()
  }
})
</script>
