<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="w-[420px] sm:w-[500px] flex flex-col" @open-auto-focus.prevent>
      <SheetHeader class="pb-4 border-b border-border">
        <SheetTitle class="flex items-center gap-2">
          <span class="sap-icon--sys-back w-5 h-5 flex items-center justify-center text-[var(--sapPositiveTextColor)]" />
          Check-In — Devolución de Herramienta
        </SheetTitle>
        <SheetDescription>
          Digita el short code de la herramienta a devolver
        </SheetDescription>
      </SheetHeader>

      <div class="flex-1 overflow-y-auto py-5 space-y-5">
        <!-- ① INPUT SHORT CODE -->
        <div class="space-y-1.5">
          <label class="text-sm font-normal text-[var(--sapContent_LabelColor)]">Short Code *:</label>
          <div class="relative">
            <span class="sap-icon--sys-back absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center text-[var(--sapContent_LabelColor)]" />
            <input
              ref="inputRef"
              v-model="query"
              placeholder="ej: HER-001 — busca unidades En_Uso"
              class="flex h-11 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-[var(--sapSuccessBorderColor)] transition-all"
              @keyup.escape="resetSheet"
              autocomplete="off"
              autofocus
            />
            <span v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
              <span class="sap-icon--refresh w-4 h-4 flex items-center justify-center animate-spin text-[var(--sapContent_LabelColor)]" />
            </span>
          </div>
          <p v-if="error" class="text-xs text-[var(--sapNegativeTextColor)] flex items-center gap-1">
            <span class="sap-icon--warning w-3.5 h-3.5 flex items-center justify-center" />{{ error }}
          </p>
        </div>

        <!-- ② RESULTADOS: unidades En_Uso para devolver -->
        <div v-if="unidadesEnUso.length > 0" class="space-y-2">
          <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">
            Selecciona la unidad a devolver
          </p>
          <div class="rounded-md border border-border overflow-hidden">
            <button
              v-for="u in unidadesEnUso"
              :key="u.id"
              @click="seleccionarUnidad(u)"
              :class="[
                'w-full flex items-start gap-3 px-4 py-3 text-left transition-colors border-b border-border last:border-0',
                unidadSeleccionada?.id === u.id
                  ? 'bg-[var(--sapSuccessBackground)] border-l-2 border-l-[var(--sapSuccessBorderColor)]'
                  : 'hover:bg-muted/30',
              ]"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium">{{ u.catalogo?.nombre }}</p>
                <p class="text-xs text-muted-foreground mt-0.5">
                  Unidad #{{ u.id }} · {{ u.ubicacion_fisica || 'Sin ubicación registrada' }}
                </p>
              </div>
              <span class="shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-[var(--sapInformationBackground)] text-[var(--sapInformationTextColor)] border border-[var(--sapInformationBorderColor)] mt-0.5">
                En Uso
              </span>
            </button>
          </div>
        </div>

        <!-- Mensaje si no hay unidades en uso -->
        <div v-else-if="query.length >= 2 && !loading && unidadesEnUso.length === 0 && results.length === 0"
          class="rounded-lg border border-[var(--sapWarningBorderColor)] bg-[var(--sapWarningBackground)] p-4 text-sm text-[var(--sapWarningColor)]">
          No hay unidades de <code class="font-mono">{{ query }}</code> con estado En_Uso.
        </div>

        <!-- ③ INSPECCIÓN VISUAL — aparece al seleccionar unidad -->
        <div v-if="unidadSeleccionada" class="space-y-4">
          <div class="rounded-lg border border-border bg-card p-4">
            <p class="text-sm font-semibold mb-1">{{ unidadSeleccionada.catalogo?.nombre }}</p>
            <p class="text-xs text-muted-foreground">Unidad #{{ unidadSeleccionada.id }}</p>
          </div>

          <!-- Pregunta de inspección visual -->
          <div class="rounded-lg border border-border p-4 space-y-3">
            <p class="text-sm font-semibold">¿Se devuelve en buen estado?</p>
            <div class="flex gap-3">
              <button
                @click="buenEstado = true; descripcionDano = ''"
                :class="[
                  'flex-1 flex items-center justify-center gap-2 rounded-md border py-3 text-sm font-medium transition-colors min-h-[48px]',
                  buenEstado === true
                    ? 'border-[var(--sapSuccessBorderColor)] bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)]'
                    : 'border-border hover:bg-muted/30',
                ]"
              >
                <span class="sap-icon--accept w-5 h-5 flex items-center justify-center" />
                Sí, buen estado
              </button>
              <button
                @click="buenEstado = false"
                :class="[
                  'flex-1 flex items-center justify-center gap-2 rounded-md border py-3 text-sm font-medium transition-colors min-h-[48px]',
                  buenEstado === false
                    ? 'border-[var(--sapErrorBorderColor)] bg-[var(--sapErrorBackground)] text-[var(--sapNegativeTextColor)]'
                    : 'border-border hover:bg-muted/30',
                ]"
              >
                <span class="sap-icon--decline w-5 h-5 flex items-center justify-center" />
                No — Malograda
              </button>
            </div>

            <!-- Descripción del daño (obligatoria si malograda) -->
            <div v-if="buenEstado === false" class="space-y-1.5">
              <label class="text-sm font-normal text-[var(--sapNegativeTextColor)]">Describe el daño *:</label>
              <textarea
                v-model="descripcionDano"
                placeholder="ej: Piñón ratchet quebrado, cable pelado..."
                rows="3"
                class="flex w-full rounded-md border border-[var(--sapErrorBorderColor)] bg-[var(--sapField_Background)] px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-[var(--sapErrorBorderColor)]"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <SheetFooter class="pt-4 border-t border-border gap-3">
        <button
          @click="resetSheet"
          class="flex-1 rounded-sm border border-[var(--sapButton_BorderColor)] bg-[var(--sapButton_Background)] px-4 py-2.5 text-sm text-[var(--sapButton_TextColor)] hover:bg-[var(--sapButton_Hover_Background)] transition-colors min-h-[48px]"
        >
          Cancelar <kbd class="ml-1 text-xs opacity-50">Esc</kbd>
        </button>
        <button
          @click="confirmarCheckIn"
          :disabled="!puedeConfirmar || confirmando"
          :class="[
            'flex-1 rounded-md px-4 py-2.5 text-sm font-medium transition-colors min-h-[48px]',
            puedeConfirmar && !confirmando
              ? buenEstado
                ? 'bg-[var(--sapButton_Accept_Background)] hover:bg-[var(--sapButton_Accept_Hover_Background)] text-[var(--sapButton_Accept_TextColor)]'
                : 'bg-[var(--sapButton_Reject_Background)] hover:bg-[var(--sapButton_Reject_Hover_Background)] text-[var(--sapButton_Reject_TextColor)]'
              : 'bg-muted text-muted-foreground cursor-not-allowed opacity-50',
          ]"
        >
          <span v-if="confirmando" class="flex items-center justify-center gap-2">
            <span class="sap-icon--refresh w-4 h-4 flex items-center justify-center animate-spin" />Registrando...
          </span>
          <span v-else-if="buenEstado === true">✓ Devolver — Buen Estado</span>
          <span v-else-if="buenEstado === false">⚠ Devolver — Malograda</span>
          <span v-else>Confirmar Devolución</span>
        </button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { useShortCodeInput } from '@/composables/useShortCodeInput'
import { useInventarioStore } from '@/stores/inventario'
import { useToast } from '@/components/ui/toast'


const props = defineProps({ open: { type: Boolean, default: false } })
const emit = defineEmits(['update:open'])

const inventarioStore = useInventarioStore()
const { toast } = useToast()

const { inputRef, query, results, loading, error, reset } = useShortCodeInput()

// El check-in busca unidades En_Uso (la API buscar devuelve todas, filtramos aquí)
const unidadesEnUso = computed(() =>
  results.value.filter((u) => u.estado === 'En_Uso'),
)

const unidadSeleccionada = ref(null)
const buenEstado = ref(null)      // true = buen estado, false = malograda
const descripcionDano = ref('')
const confirmando = ref(false)

// Al buscar: auto-seleccionar si solo hay una en uso
watch(unidadesEnUso, (val) => {
  if (val.length === 1) {
    unidadSeleccionada.value = val[0]
  } else if (val.length === 0) {
    unidadSeleccionada.value = null
  }
})

// Al abrir: resetear y enfocar
watch(() => props.open, (val) => {
  if (val) {
    resetSheet(false)
    nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
  }
})

const puedeConfirmar = computed(() => {
  if (!unidadSeleccionada.value) return false
  if (buenEstado.value === null) return false
  if (buenEstado.value === false && !descripcionDano.value.trim()) return false
  return true
})

function seleccionarUnidad(u) {
  unidadSeleccionada.value = u
  buenEstado.value = null
  descripcionDano.value = ''
  nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
}

async function confirmarCheckIn() {
  if (!puedeConfirmar.value || confirmando.value) return
  confirmando.value = true
  try {
    await inventarioStore.checkIn({
      inventario_id: unidadSeleccionada.value.id,
      buen_estado: buenEstado.value,
      dano: buenEstado.value === false ? descripcionDano.value.trim() : undefined,
    })

    if (buenEstado.value) {
      // ✅ Toast verde — devolución correcta
      toast({
        title: '✓ Herramienta devuelta',
        description: `${unidadSeleccionada.value.catalogo?.nombre} marcada como Disponible`,
        variant: 'success',
      })
    } else {
      // 🔴 Toast rojo/advertencia — devuelta malograda
      toast({
        title: '⚠ Devuelta como Malograda',
        description: `${unidadSeleccionada.value.catalogo?.nombre}: "${descripcionDano.value}"`,
        variant: 'error',
      })
    }

    resetSheet(false)
    nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
  } catch (err) {
    const msg = err.response?.data?.detail || 'Error al registrar devolución'
    toast({ title: 'Error en check-in', description: msg, variant: 'error' })
    nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
  } finally {
    confirmando.value = false
  }
}

function resetSheet(cerrar = true) {
  reset()
  unidadSeleccionada.value = null
  buenEstado.value = null
  descripcionDano.value = ''
  confirmando.value = false
  if (cerrar) emit('update:open', false)
}
</script>
