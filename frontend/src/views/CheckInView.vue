<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ── Dynamic Page Header ─────────────────────────────────────────────── -->
    <div
      class="px-6 py-4 border-b border-border shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background)' }"
    >
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--inbox text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Almacén — Entrada de Herramientas
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Devolución e inspección visual de herramientas
          </p>
        </div>
      </div>
    </div>

    <!-- ── Content Area ─────────────────────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl mx-auto space-y-4">
        <!-- ── Bloque 1: Búsqueda ─────────────────────────────────────────── -->
        <div
          class="p-6 rounded-sm border"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2
            class="text-base font-semibold mb-4"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Buscar herramienta a devolver
          </h2>
          <div class="space-y-1.5">
            <label
              class="text-sm font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Short Code *:
            </label>
            <div class="relative">
              <span
                class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              />
              <input
                ref="inputRef"
                v-model="query"
                placeholder="ej: TALNE-001 — Enter para buscar"
                class="flex h-12 w-full border pl-9 pr-3 text-sm font-mono focus:outline-none focus:ring-1 rounded-sm transition-all"
                :style="{
                  background: 'var(--sapField_Background)',
                  borderColor: 'var(--sapField_BorderColor)',
                  color: 'var(--sapField_TextColor)',
                }"
                autocomplete="off"
              >
              <span
                v-if="loading"
                class="absolute right-3 top-1/2 -translate-y-1/2"
              >
                <span
                  class="sap-icon--refresh animate-spin"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                />
              </span>
            </div>
            <p
              v-if="error"
              class="text-xs flex items-center gap-1"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              <span class="sap-icon--message-error" /> {{ error }}
            </p>
          </div>

          <!-- Resultados de búsqueda (materiales en uso) -->
          <div
            v-if="resultadosDevolucion.length > 0"
            class="mt-4 space-y-2"
          >
            <p
              class="text-xs font-medium uppercase tracking-wide"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ resultadosDevolucion.length }} material{{ resultadosDevolucion.length > 1 ? 'es' : '' }} en uso
            </p>
            <div
              class="rounded-sm border overflow-hidden"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              <button
                v-for="m in resultadosDevolucion"
                :key="m.id"
                class="w-full flex items-start gap-3 px-4 py-3 text-left transition-colors border-b last:border-0"
                :style="materialSeleccionado?.id === m.id
                  ? { background: 'var(--sapInformationBackground)', borderLeftWidth: '2px', borderLeftColor: 'var(--sapButton_Emphasized_Background)', borderColor: 'var(--sapList_BorderColor)' }
                  : { background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
                @click="seleccionarMaterial(m)"
              >
                <div class="flex-1 min-w-0">
                  <p
                    class="text-sm font-medium"
                    :style="{ color: 'var(--sapTextColor)' }"
                  >
                    {{ m.nombre }}
                  </p>
                  <code
                    class="font-mono text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >{{ m.codigo_interno }}</code>
                </div>
                <span
                  class="shrink-0 text-xs px-2 py-0.5 rounded-sm border font-medium"
                  :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }"
                >{{ m.cant_en_uso }} en uso</span>
              </button>
            </div>
          </div>
        </div>

        <!-- ── Bloque 2: Devolución (aparece al seleccionar material) ── -->
        <div
          v-if="materialSeleccionado"
          class="p-6 rounded-sm border"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <!-- Info del material -->
          <div
            class="p-4 rounded-sm border mb-5"
            :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }"
          >
            <div class="flex items-center gap-2 mb-2">
              <span
                class="sap-icon--product"
                :style="{ color: 'var(--sapInformationTextColor)' }"
              />
              <p
                class="text-sm font-semibold"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                {{ materialSeleccionado.nombre }}
              </p>
            </div>
            <div class="grid grid-cols-2 gap-1 text-xs">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Código:</span>
              <code
                class="font-mono"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ materialSeleccionado.codigo_interno }}</code>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">En uso:</span>
              <span
                class="font-semibold"
                :style="{ color: 'var(--sapInformationTextColor)' }"
              >{{ materialSeleccionado.cant_en_uso }} unidades</span>
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Costo reposición:</span>
              <span :style="{ color: 'var(--sapTextColor)' }">S/. {{ materialSeleccionado.costo_reposicion?.toFixed(2) || '--' }}</span>
            </div>
          </div>

          <h3
            class="text-base font-semibold mb-3"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Devolución
          </h3>
          <p
            class="text-sm mb-4"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Indique cuántas unidades se devuelven y en qué estado
          </p>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div class="space-y-1.5">
              <label
                class="text-sm font-normal"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >En buen estado *:</label>
              <input
                v-model.number="cantBuenEstado"
                type="number"
                :min="0"
                :max="materialSeleccionado.cant_en_uso"
                class="w-full h-12 border px-3 text-sm rounded-sm focus:outline-none focus:ring-1"
                :style="{ background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)', color: 'var(--sapTextColor)' }"
              >
            </div>
            <div class="space-y-1.5">
              <label
                class="text-sm font-normal"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Malogradas *:</label>
              <input
                v-model.number="cantMalograda"
                type="number"
                :min="0"
                :max="materialSeleccionado.cant_en_uso"
                class="w-full h-12 border px-3 text-sm rounded-sm focus:outline-none focus:ring-1"
                :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapTextColor)' }"
              >
            </div>
          </div>

          <p
            v-if="cantBuenEstado + cantMalograda > materialSeleccionado.cant_en_uso"
            class="text-xs mb-3"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          >
            El total ({{ cantBuenEstado + cantMalograda }}) supera las {{ materialSeleccionado.cant_en_uso }} unidades en uso
          </p>

          <!-- Descripción del daño (obligatorio si cantMalograda > 0) -->
          <div
            v-if="cantMalograda > 0"
            class="space-y-1.5 mb-4"
          >
            <label
              class="text-sm font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Descripción del daño *:</label>
            <textarea
              v-model="descripcionDano"
              placeholder="Describa el daño observado..."
              rows="3"
              class="w-full border px-3 py-2 text-sm rounded-sm focus:outline-none focus:ring-1 resize-none"
              :style="{
                background: 'var(--sapField_Background)',
                borderColor: descripcionDano.trim() ? 'var(--sapField_BorderColor)' : 'var(--sapErrorBorderColor)',
                color: 'var(--sapField_TextColor)',
              }"
            />
            <p
              v-if="!descripcionDano.trim() && intentoConfirmar"
              class="text-xs"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              La descripción del daño es obligatoria.
            </p>
          </div>

          <!-- Observación de recepción (opcional) -->
          <div class="space-y-1.5 mb-4">
            <label
              class="text-sm font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Observación de recepción:</label>
            <textarea
              v-model="observacionRecepcion"
              placeholder="ej: devuelto con cable dañado, le falta un perno"
              rows="2"
              class="w-full border px-3 py-2 text-sm rounded-sm focus:outline-none focus:ring-1 resize-none"
              :style="{ background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor)' }"
            />
          </div>

          <!-- Error API -->
          <div
            v-if="errorApi"
            class="flex items-start gap-2 p-3 rounded-sm border mb-4"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
          >
            <span
              class="sap-icon--message-error shrink-0"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            />
            <p
              class="text-sm"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              {{ errorApi }}
            </p>
          </div>

          <!-- Acciones -->
          <div class="flex gap-3">
            <button
              class="flex-1 h-12 text-sm border rounded-sm transition-colors"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="cancelar"
            >
              Cancelar
            </button>
            <button
              :disabled="confirmando"
              class="flex-2 h-12 px-8 text-sm font-medium rounded-sm transition-colors"
              :style="!confirmando
                ? { background: 'var(--sapButton_Accept_Background)', color: 'var(--sapButton_Accept_TextColor)', border: 'none' }
                : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }"
              @click="confirmarCheckIn"
            >
              <span
                v-if="confirmando"
                class="flex items-center gap-2"
              >
                <span class="sap-icon--refresh animate-spin" /> Registrando...
              </span>
              <span v-else>✓ Confirmar Devolución</span>
            </button>
          </div>
        </div>

        <!-- ── Bloque 3: Éxito ─────────────────────────────────────────────── -->
        <div
          v-if="mostrarExito"
          class="p-8 rounded-sm border text-center space-y-4"
          :style="{ background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)' }"
        >
          <span
            class="sap-icon--accept text-5xl block"
            :style="{ color: 'var(--sapPositiveTextColor)' }"
          />
          <h2
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            ¡Devolución registrada!
          </h2>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            La herramienta
            <strong :style="{ color: 'var(--sapTextColor)' }">{{ ultimaHerramienta }}</strong>
            fue recibida correctamente.
          </p>
          <button
            class="w-full h-12 text-sm font-medium rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
            @click="resetOperacion"
          >
            <span class="sap-icon--refresh mr-2" /> Siguiente Devolución
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useInventarioStore } from '@/stores/inventario'
import { useShortCodeInput } from '@/composables/useShortCodeInput'
import { useSound } from '@/composables/useSound'
import { useToast } from '@/components/ui/toast'

const inventarioStore = useInventarioStore()
const { playSuccess, playError } = useSound()
const { toast } = useToast()

const { inputRef, query, results, loading, error, reset: resetInput, refocus } = useShortCodeInput()

const materialSeleccionado = ref(null)
const cantBuenEstado = ref(0)
const cantMalograda = ref(0)
const descripcionDano = ref('')
const observacionRecepcion = ref('')
const confirmando = ref(false)
const intentoConfirmar = ref(false)
const errorApi = ref(null)
const mostrarExito = ref(false)
const ultimaHerramienta = ref('')

// Materiales en uso (que se pueden devolver)
const resultadosDevolucion = computed(() =>
  results.value.filter((r) => !r._esSugerencia && r.cant_en_uso > 0)
)

function seleccionarMaterial(m) {
  materialSeleccionado.value = m
  cantBuenEstado.value = 0
  cantMalograda.value = 0
  descripcionDano.value = ''
  observacionRecepcion.value = ''
  errorApi.value = null
  intentoConfirmar.value = false
}

function cancelar() {
  materialSeleccionado.value = null
  cantBuenEstado.value = 0
  cantMalograda.value = 0
  descripcionDano.value = ''
  observacionRecepcion.value = ''
  errorApi.value = null
  intentoConfirmar.value = false
  resetInput()
}

async function confirmarCheckIn() {
  intentoConfirmar.value = true
  if (cantBuenEstado.value + cantMalograda.value === 0) {
    errorApi.value = 'Debe devolver al menos una unidad'
    return
  }
  if (cantMalograda.value > 0 && !descripcionDano.value.trim()) {
    errorApi.value = 'Describa el daño de las unidades malogradas'
    return
  }
  if (cantBuenEstado.value + cantMalograda.value > materialSeleccionado.value.cant_en_uso) {
    errorApi.value = `Solo puede devolver hasta ${materialSeleccionado.value.cant_en_uso} unidades`
    return
  }

  confirmando.value = true
  errorApi.value = null
  try {
    const response = await inventarioStore.checkIn({
      catalogo_id: materialSeleccionado.value.id,
      cant_buen_estado: cantBuenEstado.value,
      cant_malograda: cantMalograda.value,
      observacion_recepcion: observacionRecepcion.value || undefined,
      descripcion_dano: cantMalograda.value > 0 ? descripcionDano.value.trim() : undefined,
    })
    playSuccess()
    ultimaHerramienta.value = materialSeleccionado.value.nombre ?? ''
    toast({
      title: '✓ Devolución registrada',
      description: response.mensaje || `${ultimaHerramienta.value} recibida correctamente`,
      variant: 'success',
    })
    mostrarExito.value = true
    materialSeleccionado.value = null
  } catch (err) {
    playError()
    errorApi.value = err.response?.data?.detail || 'Error al registrar la devolución'
    nextTick(() => refocus())
  } finally {
    confirmando.value = false
  }
}

function resetOperacion() {
  mostrarExito.value = false
  ultimaHerramienta.value = ''
  cantBuenEstado.value = 0
  cantMalograda.value = 0
  descripcionDano.value = ''
  observacionRecepcion.value = ''
  materialSeleccionado.value = null
  errorApi.value = null
  intentoConfirmar.value = false
  resetInput()
}

onMounted(() => {
  // auto-foco gestionado por useShortCodeInput
})
</script>
