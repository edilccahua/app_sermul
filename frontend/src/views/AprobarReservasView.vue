<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--approvals text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Aprobar Reservas
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Reservas pendientes de aprobación
          </p>
        </div>
        <span
          v-if="pendientes.length"
          class="ml-auto text-sm px-2 py-0.5 rounded-full font-bold"
          :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)' }"
        >{{ pendientes.length }}</span>
      </div>
    </div>

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
              class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Código
            </th>
            <th
              class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Grupo
            </th>
            <th
              class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Parada
            </th>
            <th
              class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Turno
            </th>
            <th
              class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Fecha
            </th>
            <th
              class="px-4 py-1.5 text-center font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Ítems
            </th>
            <th
              class="px-4 py-1.5 text-right font-semibold uppercase tracking-wide border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              Acciones
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="r in pendientes"
            :key="r.id"
            class="border-b transition-all"
            :class="{ 'opacity-0 pointer-events-none': procesados.has(r.id) }"
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
              {{ r.parada ? r.parada.codigo + ' - ' + r.parada.nombre : '—' }}
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
            <td class="px-4 py-1.5">
              <div class="flex items-center justify-end gap-2">
                <button
                  class="h-7 px-3 text-xs font-medium rounded-sm transition-colors flex items-center gap-1"
                  :style="{ background: 'var(--sapButton_Accept_Background)', color: 'var(--sapButton_Accept_TextColor)', border: 'none' }"
                  @click="aprobar(r.id)"
                >
                  <span class="sap-icon--accept" /> Aprobar
                </button>
                <button
                  class="h-7 px-3 text-xs font-medium rounded-sm transition-colors flex items-center gap-1"
                  :style="{ background: 'var(--sapButton_Reject_Background)', color: 'var(--sapButton_Reject_TextColor)', border: 'none' }"
                  @click="abrirRechazar(r)"
                >
                  <span class="sap-icon--decline" /> Rechazar
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!pendientes.length">
            <td
              colspan="7"
              class="px-4 py-8 text-center text-xs"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              <span
                class="sap-icon--accept block text-3xl mb-2"
                :style="{ color: 'var(--sapPositiveTextColor)' }"
              />
              No hay reservas pendientes de aprobación.
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
            Reserva <code class="font-mono">{{ reservaARechazar?.codigo }}</code> — {{ reservaARechazar?.grupo?.nombre }}
          </p>
          <div class="space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Motivo *:</label>
            <textarea
              v-model="motivoRechazo"
              rows="3"
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
import { ref, computed, onMounted } from 'vue'
import { useReservasStore } from '@/stores/reservas'
import { useToast } from '@/components/ui/toast'

const reservasStore = useReservasStore()
const { toast } = useToast()
const procesados = ref(new Set())
const dialogRechazar = ref(false)
const reservaARechazar = ref(null)
const motivoRechazo = ref('')
const rechazando = ref(false)

const pendientes = computed(() =>
  reservasStore.items.filter((r) => r.estado === 'Pendiente' && !procesados.value.has(r.id))
)

async function aprobar(id) {
  try {
    await reservasStore.aprobar(id)
    procesados.value.add(id)
    toast({ title: '✓ Reserva aprobada', variant: 'success' })
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail, variant: 'error' })
  }
}

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
    procesados.value.add(reservaARechazar.value.id)
    toast({ title: '✓ Reserva rechazada', variant: 'success' })
    dialogRechazar.value = false
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail, variant: 'error' })
  } finally {
    rechazando.value = false
  }
}

onMounted(() => reservasStore.fetchAll({ estado: 'Pendiente' }))
</script>
