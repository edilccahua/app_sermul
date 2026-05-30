<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center gap-3">
      <span class="sap-icon--stop w-7 h-7 flex items-center justify-center text-[var(--sapButton_Reject_Background)]" />
      <h1 class="text-xl font-bold">
        Cierre y Reconciliación de Parada
      </h1>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-12 text-center text-[var(--sapContent_LabelColor)]">
      <span class="sap-icon--refresh w-8 h-8 flex items-center justify-center mx-auto mb-3 animate-spin" />
      Iniciando cierre y calculando herramientas pendientes...
    </div>

    <!-- Error State -->
    <div v-else-if="error"
      class="bg-[var(--sapErrorBackground)] border border-[var(--sapErrorBorderColor)] text-[var(--sapNegativeTextColor)] p-6 rounded-sm flex flex-col items-center gap-4 text-center">
      <span class="sap-icon--message-error text-3xl" />
      <div>
        <h3 class="font-bold text-lg mb-1">
          Error al procesar el cierre
        </h3>
        <p class="text-sm mb-4">
          {{ error }}
        </p>
        <button
          class="inline-flex items-center gap-2 rounded-sm border border-[var(--sapButton_BorderColor)] bg-[var(--sapButton_Background)] px-4 py-2 text-sm text-[var(--sapButton_TextColor)] hover:bg-[var(--sapButton_Hover_Background)] transition-colors"
          @click="$router.push('/app/paradas')">
          Volver a Paradas
        </button>
      </div>
    </div>

    <!-- Success State (No pendientes) -->
    <div v-else-if="!hayPendientes && cerradoConExito"
      class="bg-[var(--sapSuccessBackground)] border border-[var(--sapSuccessBorderColor)] text-[var(--sapPositiveTextColor)] p-6 rounded-sm flex flex-col items-center gap-4 text-center">
      <span class="sap-icon--accept text-4xl" />
      <div>
        <h3 class="font-bold text-lg mb-1">
          Parada Cerrada Exitosamente
        </h3>
        <p class="text-sm mb-4">
          No hay herramientas pendientes de devolución. La parada ha sido finalizada correctamente.
        </p>
        <button
          class="inline-flex items-center justify-center rounded-sm bg-[var(--sapButton_Emphasized_Background)] px-6 py-2 text-sm font-medium text-[var(--sapButton_Emphasized_TextColor)] hover:bg-[var(--sapButton_Emphasized_Hover_Background)] transition-colors"
          @click="$router.push('/app/paradas')">
          Entendido, volver a la lista
        </button>
      </div>
    </div>

    <!-- Reconciliación (Hay pendientes) -->
    <div v-else class="space-y-6">
      <div
        class="bg-[var(--sapInformationBackground)] border border-[var(--sapInformationBorderColor)] text-[var(--sapInformationTextColor)] p-4 rounded-sm flex items-start gap-3 text-sm">
        <span class="sap-icon--message-information shrink-0 mt-0.5 text-lg" />
        <div>
          <strong class="block mb-1">Atención: Hay herramientas pendientes</strong>
          Faltan devolver <strong>{{ pendientesOriginales.length }}</strong> herramientas.<br>
          <strong>Continuidad:</strong> Se esperar 3 dias a la devolucion de las herramientas a travez de devoluciones y
          recepcion. o pasar a estado de <strong>Perdida</strong> las herramientas.
        </div>
      </div>

      <div class="bg-card border border-border rounded-sm shadow-[var(--sapContent_Shadow0)] overflow-hidden">
        <div class="bg-[var(--sapList_HeaderBackground)] border-b border-border px-4 py-2">
          <h2 class="font-bold text-sm" :style="{ color: 'var(--sapTextColor)' }">
            Herramientas Pendientes ({{ pendientes.length }})
          </h2>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm border-collapse">
            <thead class="border-b"
              :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'var(--sapList_HeaderBackground)' }">
              <tr>
                <th class="px-3 py-2 font-semibold whitespace-nowrap text-xs" :style="{ color: 'var(--sapTextColor)' }">
                  Estado</th>
                <th class="px-3 py-2 font-semibold whitespace-nowrap text-xs" :style="{ color: 'var(--sapTextColor)' }">
                  Código / Nombre</th>
                <th class="px-3 py-2 font-semibold whitespace-nowrap text-xs text-center"
                  :style="{ color: 'var(--sapTextColor)' }">Falta</th>
                <th class="px-3 py-2 font-semibold whitespace-nowrap text-xs text-center"
                  :style="{ color: 'var(--sapTextColor)' }">Continuar (3d)</th>
                <th class="px-3 py-2 font-semibold whitespace-nowrap text-xs text-center"
                  :style="{ color: 'var(--sapTextColor)' }">Pérdida</th>
              </tr>
            </thead>
            <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
              <tr v-for="item in pendientes" :key="item.catalogo_id" class="border-b transition-colors hover-sap-list"
                :style="{ borderColor: 'var(--sapList_BorderColor)' }">
                <!-- Status Indicator -->
                <td class="px-3 py-2 w-12 text-center">
                  <span :class="[
                    'inline-block w-3 h-3 rounded-full',
                    (item.cantPerdida + item.cantContinuidad) === item.cantidad_pendiente
                      ? 'bg-[var(--sapPositiveTextColor)]'
                      : 'bg-[var(--sapCriticalColor)] animate-pulse'
                  ]" />
                </td>

                <!-- Tool Info -->
                <td class="px-3 py-2">
                  <div class="font-mono text-xs mb-0.5" :style="{ color: 'var(--sapContent_LabelColor)' }">
                    {{ item.codigo_interno }}
                  </div>
                  <div class="font-semibold text-sm" :style="{ color: 'var(--sapTextColor)' }">
                    {{ item.nombre }}
                  </div>
                </td>

                <!-- Pendiente Target -->
                <td class="px-3 py-2 text-center font-bold text-base" :style="{ color: 'var(--sapTextColor)' }">
                  {{ item.cantidad_pendiente }}
                </td>

                <!-- Continuar Input -->
                <td class="px-3 py-2 w-32">
                  <div class="flex flex-col items-center">
                    <input v-model.number="item.cantContinuidad" type="number" min="0" :max="item.cantidad_pendiente"
                      class="w-full h-8 text-center border rounded-sm outline-none transition-colors" :style="{
                        background: 'var(--sapField_Background)',
                        color: 'var(--sapInformationTextColor)',
                        borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
                        fontWeight: '600'
                      }" @input="onContinuidadChange(item)">
                  </div>
                </td>

                <!-- Perdida Input -->
                <td class="px-3 py-2 w-32">
                  <div class="flex flex-col items-center">
                    <input v-model.number="item.cantPerdida" type="number" min="0" :max="item.cantidad_pendiente"
                      class="w-full h-8 text-center border rounded-sm outline-none transition-colors" :style="{
                        background: 'var(--sapErrorBackground)',
                        color: 'var(--sapNegativeTextColor)',
                        borderColor: 'var(--sapErrorBorderColor)',
                        fontWeight: '600'
                      }" @input="onPerdidaChange(item)">
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Action Bar Inferior (Fiori Sticky Footer Toolbar) -->
      <div
        class="sticky bottom-0 z-10 border-t shrink-0 px-6 py-3 flex items-center justify-end gap-3 shadow-[0_-4px_10px_rgba(0,0,0,0.05)]"
        :style="{ background: 'var(--sapBackgroundColor)', borderColor: 'var(--sapList_BorderColor)' }">
        <div class="mr-auto text-sm">
          <span v-if="allBalanced" class="flex items-center gap-2 font-semibold"
            :style="{ color: 'var(--sapPositiveTextColor)' }">
            <span class="sap-icon--accept" /> Todas las herramientas cuadradas.
          </span>
          <span v-else class="flex items-center gap-2 font-semibold" :style="{ color: 'var(--sapCriticalColor)' }">
            <span class="sap-icon--alert" /> Faltan cuadrar cantidades.
          </span>
        </div>

        <!-- Standard Button: Cancelar -->
        <button type="button"
          class="h-10 px-6 text-sm font-medium border rounded-sm transition-colors hover-sap-selection"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="$router.push('/app/paradas')">
          Cancelar
        </button>

        <!-- Emphasized Button: Guardar -->
        <button :disabled="!allBalanced || procesando"
          class="h-10 px-8 text-sm font-semibold rounded-sm transition-opacity flex items-center gap-2 shadow-sm"
          :style="{
            background: 'var(--sapButton_Emphasized_Background)',
            color: 'var(--sapButton_Emphasized_TextColor)',
            opacity: (!allBalanced || procesando) ? '0.6' : '1',
          }" @click="confirmarReconciliacion">
          <span v-if="procesando" class="sap-icon--refresh animate-spin" />
          <span v-else class="sap-icon--accept" />
          {{ procesando ? 'Procesando...' : 'Confirmar y Finalizar Parada' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { paradasAPI } from '@/api'
import { useToast } from '@/components/ui/toast'

const route = useRoute()
const router = useRouter()
const { toast } = useToast()

const paradaId = route.params.id
const loading = ref(true)
const procesando = ref(false)
const error = ref(null)

const pendientesOriginales = ref([])
const pendientes = ref([])
const cerradoConExito = ref(false)
const hayPendientes = computed(() => pendientes.value.length > 0)

function onContinuidadChange(item) {
  let val = Number(item.cantContinuidad) || 0
  val = Math.max(0, Math.min(val, item.cantidad_pendiente))
  item.cantContinuidad = val
  item.cantPerdida = item.cantidad_pendiente - val
}

function onPerdidaChange(item) {
  let val = Number(item.cantPerdida) || 0
  val = Math.max(0, Math.min(val, item.cantidad_pendiente))
  item.cantPerdida = val
  item.cantContinuidad = item.cantidad_pendiente - val
}

const allBalanced = computed(() => {
  if (pendientes.value.length === 0) return false
  return pendientes.value.every(item =>
    (item.cantPerdida || 0) + (item.cantContinuidad || 0) === item.cantidad_pendiente
  )
})

async function iniciarCierre() {
  if (!paradaId) return
  loading.value = true
  try {
    const { data } = await paradasAPI.simularCierre(paradaId)

    // Si no hay pendientes y la llamada fue exitosa (no arrojó error), 
    // significa que la parada se puede cerrar directamente, pero requiere confirmación
    if (!data.pendientes || data.pendientes.length === 0) {
      toast({ title: '✓ Simulación correcta. Sin pendientes.' })
      pendientesOriginales.value = []
      pendientes.value = []
      cerradoConExito.value = true
    } else {
      pendientesOriginales.value = data.pendientes
      pendientes.value = pendientesOriginales.value.map(p => ({
        ...p,
        cantContinuidad: 0,
        cantPerdida: 0
      }))
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error al comunicarse con el servidor.'
  } finally {
    loading.value = false
  }
}

async function confirmarReconciliacion() {
  if (!allBalanced.value) return

  const confirmacion = confirm('¿Estás seguro de finalizar la parada con estas resoluciones? Esta acción es irreversible.')
  if (!confirmacion) return

  procesando.value = true
  const payload = { resoluciones: [] }

  for (const item of pendientes.value) {
    if (item.cantPerdida > 0) {
      payload.resoluciones.push({ catalogo_id: item.catalogo_id, accion: 'Perdida', cantidad: item.cantPerdida })
    }
    if (item.cantContinuidad > 0) {
      payload.resoluciones.push({ catalogo_id: item.catalogo_id, accion: 'Continuidad', cantidad: item.cantContinuidad })
    }
  }

  try {
    await paradasAPI.resolverPendiente(paradaId, payload.resoluciones)
    toast({ title: 'Parada Finalizada', description: 'Todos los pendientes han sido resueltos exitosamente.', variant: 'success' })
    router.push('/app/paradas')
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail || 'No se pudo resolver los pendientes.', variant: 'error' })
  } finally {
    procesando.value = false
  }
}

onMounted(() => {
  iniciarCierre()
})
</script>
