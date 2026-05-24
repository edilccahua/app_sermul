<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="w-[420px] sm:w-[500px] flex flex-col" @open-auto-focus.prevent>
      <SheetHeader class="pb-4 border-b border-border">
        <SheetTitle class="flex items-center gap-2">
          <span class="sap-icon--sys-back w-5 h-5 flex items-center justify-center text-[var(--sapButton_Emphasized_Background)]" />
          Check-Out — Entrega de Herramienta
        </SheetTitle>
        <SheetDescription>
          Digita el short code y presiona <kbd class="px-1 py-0.5 text-xs bg-muted rounded border border-border">Enter</kbd>
        </SheetDescription>
      </SheetHeader>

      <div class="flex-1 overflow-y-auto py-5 space-y-5">
        <!-- ① INPUT SHORT CODE — Auto-foco permanente -->
        <div class="space-y-1.5">
          <label class="text-sm font-normal text-[var(--sapContent_LabelColor)]">Short Code *:</label>
          <div class="relative">
            <span class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center text-[var(--sapContent_LabelColor)]" />
            <input
              ref="inputRef"
              v-model="query"
              placeholder="ej: HER-001 — Enter para buscar"
              class="flex h-11 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary transition-all"
              @keyup.enter="buscarPorEnter"
              @keyup.escape="resetSheet"
              autocomplete="off"
              autofocus
            />
            <span v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
              <span class="sap-icon--refresh w-4 h-4 flex items-center justify-center animate-spin text-[var(--sapContent_LabelColor)]" />
            </span>
          </div>
          <!-- Error de búsqueda -->
          <p v-if="error" class="text-xs text-[var(--sapNegativeTextColor)] flex items-center gap-1">
                          <span class="sap-icon--warning w-3.5 h-3.5 flex items-center justify-center" />{{ error }}
          </p>
        </div>

        <!-- ② RESULTADOS: unidades en inventario -->
        <div v-if="resultadosReales.length > 0" class="space-y-2">
          <p class="text-xs text-muted-foreground font-medium uppercase tracking-wide">
            {{ resultadosReales.length }} unidad{{ resultadosReales.length > 1 ? 'es' : '' }} en inventario
          </p>
          <div class="rounded-md border border-border overflow-hidden">
            <button
              v-for="u in resultadosReales"
              :key="'inv-'+u.id"
              @click="seleccionarUnidad(u)"
              :class="[
                'w-full flex items-start gap-3 px-4 py-3 text-left transition-colors border-b border-border last:border-0',
                unidadSeleccionada?.id === u.id
                  ? 'bg-primary/10 border-l-2 border-l-primary'
                  : 'hover:bg-muted/30',
              ]"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium">{{ u.catalogo?.nombre }}</p>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="font-mono text-xs text-muted-foreground">{{ u.catalogo?.codigo_interno }}</span>
                  <span class="text-xs text-muted-foreground">·</span>
                  <span class="text-xs text-muted-foreground">{{ u.ubicacion_fisica || 'Sin ubicación' }}</span>
                </div>
              </div>
              <span :class="['shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium mt-0.5',
                u.estado === 'Disponible' ? 'bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)] border border-[var(--sapSuccessBorderColor)]' : 'bg-muted text-muted-foreground']">
                {{ u.estado }}
              </span>
            </button>
          </div>
        </div>

        <!-- ②b SUGERENCIAS: resultados del catálogo sin stock inmediato -->
        <div v-if="sugerencias.length > 0" class="space-y-2">
          <p class="text-xs text-[var(--sapWarningColor)] font-medium uppercase tracking-wide">
            {{ sugerencias.length }} coincidencia{{ sugerencias.length > 1 ? 's' : '' }} en catálogo
          </p>
          <div           class="rounded-md border border-[var(--sapWarningBorderColor)] overflow-hidden">
            <button
              v-for="s in sugerencias"
              :key="'sug-'+s.catalogo_id"
              @click="buscarPorSugerencia(s)"
              class="w-full flex items-start gap-3 px-4 py-3 text-left transition-colors border-b border-border last:border-0 hover:bg-[var(--sapWarningBackground)]"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium">{{ s.catalogo?.nombre }}</p>
                <div class="flex items-center gap-2 mt-0.5">
                  <code class="font-mono text-xs text-primary">{{ s.catalogo?.codigo_interno }}</code>
                  <span class="text-xs text-[var(--sapWarningColor)]">· Ver disponibilidad →</span>
                </div>
              </div>
              <span class="shrink-0 inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-[var(--sapWarningBackground)] text-[var(--sapWarningColor)] border border-[var(--sapWarningBorderColor)] mt-0.5">
                Catálogo
              </span>
            </button>
          </div>
        </div>

        <p v-if="resultadosReales.length > 1" class="text-xs text-muted-foreground">
          Se asignará la primera unidad disponible al confirmar
        </p>

        <!-- ③ DETALLES DE HERRAMIENTA seleccionada -->
        <div v-if="unidadSeleccionada"           class="rounded-lg border border-[var(--sapInformationBorderColor)] bg-[var(--sapInformationBackground)] p-4 space-y-3">
          <div class="flex items-center gap-2">
            <span class="sap-icon--accept w-4 h-4 flex items-center justify-center text-[var(--sapButton_Emphasized_Background)]" />
            <p class="text-sm font-semibold">{{ unidadSeleccionada.catalogo?.nombre }}</p>
          </div>
          <div class="grid grid-cols-2 gap-1.5 text-xs">
            <span class="text-muted-foreground">Short code:</span>
            <code class="font-mono">{{ unidadSeleccionada.catalogo?.codigo_interno }}</code>
            <span class="text-muted-foreground">Estado actual:</span>
            <span class="text-[var(--sapPositiveTextColor)]">{{ unidadSeleccionada.estado }}</span>
            <span class="text-muted-foreground">Costo reposición:</span>
            <span>S/. {{ unidadSeleccionada.catalogo?.costo_reposicion?.toFixed(2) || '—' }}</span>
          </div>
        </div>

        <!-- ④ GRUPO + PARADA -->
        <div v-if="unidadSeleccionada" class="space-y-4">
          <div class="space-y-1.5">
            <label class="text-sm font-normal text-[var(--sapContent_LabelColor)]">Parada Activa *:</label>
            <div v-if="paradasStore.paradaActiva"
              class="h-9 w-full rounded-md border border-border bg-muted/30 px-3 text-sm flex items-center gap-2">
              <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)] border border-[var(--sapSuccessBorderColor)]">Activa</span>
              <span>{{ paradasStore.paradaActiva.nombre }}</span>
            </div>
            <p v-else class="text-xs text-[var(--sapWarningColor)] flex items-center gap-1">
            <span class="sap-icon--warning w-3.5 h-3.5 flex items-center justify-center" />
              No hay parada activa. Crea una en Gestión de Paradas.
            </p>
          </div>

          <!-- GRUPO — workaround: seed GRP-001 mientras Sprint 2 implementa /api/grupos -->
          <div class="space-y-1.5">
            <label class="text-sm font-normal text-[var(--sapContent_LabelColor)]">Grupo de Destino *:</label>
            <select v-model="grupoId"
              class="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
              <option value="">Seleccionar grupo...</option>
              <option :value="1">GRP-001 — Grupo A · Molino SAG</option>
            </select>
            <p class="text-xs text-muted-foreground">
              ⚠ Grupos disponibles en Sprint 2. Por ahora usa el grupo semilla.
            </p>
          </div>
        </div>
      </div>

      <!-- Footer con acciones — teclado friendly -->
      <SheetFooter class="pt-4 border-t border-border gap-3">
        <button
          @click="resetSheet"
          class="flex-1 rounded-sm border border-[var(--sapButton_BorderColor)] bg-[var(--sapButton_Background)] px-4 py-2.5 text-sm text-[var(--sapButton_TextColor)] hover:bg-[var(--sapButton_Hover_Background)] transition-colors min-h-[48px]"
        >
          Cancelar <kbd class="ml-1 text-xs opacity-50">Esc</kbd>
        </button>
        <button
          @click="confirmarCheckOut"
          :disabled="!puedeConfirmar || confirmando"
          :class="[
            'flex-1 rounded-md px-4 py-2.5 text-sm font-medium transition-colors min-h-[48px]',
            puedeConfirmar && !confirmando
              ? 'bg-[var(--sapButton_Accept_Background)] hover:bg-[var(--sapButton_Accept_Hover_Background)] text-[var(--sapButton_Accept_TextColor)]'
              : 'bg-muted text-muted-foreground cursor-not-allowed opacity-50',
          ]"
        >
          <span v-if="confirmando" class="flex items-center justify-center gap-2">
            <span class="sap-icon--refresh w-4 h-4 flex items-center justify-center animate-spin" />Entregando...
          </span>
          <span v-else>
            ✓ Confirmar Entrega <kbd class="ml-1 text-xs opacity-70">Enter</kbd>
          </span>
        </button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { useShortCodeInput } from '@/composables/useShortCodeInput'
import { useInventarioStore } from '@/stores/inventario'
import { useParadasStore } from '@/stores/paradas'
import { useToast } from '@/components/ui/toast'


const props = defineProps({
  open: { type: Boolean, default: false },
  initialCode: { type: String, default: '' },
})
const emit = defineEmits(['update:open', 'update:initialCode'])

const inventarioStore = useInventarioStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

const { inputRef, query, results, loading, error, reset } = useShortCodeInput()

const unidadSeleccionada = ref(null)
const grupoId = ref('')
const confirmando = ref(false)

// Auto-seleccionar la primera unidad real (no sugerencia) al buscar
watch(results, (val) => {
  const itemsReales = val.filter((u) => !u._esSugerencia)
  if (itemsReales.length === 1) {
    unidadSeleccionada.value = itemsReales[0]
  } else {
    unidadSeleccionada.value = null
  }
})

// Al abrir el sheet: cargar paradas, inyectar código inicial y forzar foco
watch(() => props.open, async (val) => {
  if (val) {
    reset()
    unidadSeleccionada.value = null
    grupoId.value = ''
    confirmando.value = false
    await paradasStore.fetchAll()
    if (props.initialCode) {
      query.value = props.initialCode
    }
    nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
  }
})

// Si la barra superior envía un código mientras el sheet ya está abierto
watch(() => props.initialCode, (val) => {
  if (val && props.open) {
    reset()
    query.value = val
  }
})

const resultadosReales = computed(() =>
  results.value.filter((u) => !u._esSugerencia),
)
const sugerencias = computed(() =>
  results.value.filter((u) => u._esSugerencia),
)

const puedeConfirmar = computed(() =>
  unidadSeleccionada.value &&
  grupoId.value &&
  paradasStore.paradaActiva,
)

// Enter en el input busca; si ya hay resultado confirmado puede confirmar
function buscarPorEnter() {
  if (puedeConfirmar.value) {
    confirmarCheckOut()
  }
}

function buscarPorSugerencia(s) {
  unidadSeleccionada.value = null
  query.value = s.catalogo.codigo_interno
  nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
}

function seleccionarUnidad(u) {
  unidadSeleccionada.value = u
  nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
}

async function confirmarCheckOut() {
  if (!puedeConfirmar.value || confirmando.value) return
  confirmando.value = true
  try {
    await inventarioStore.checkOut({
      short_code: unidadSeleccionada.value.catalogo.codigo_interno,
      grupo_id: Number(grupoId.value),
      parada_id: paradasStore.paradaActiva.id,
    })
    // ✅ Toast verde de éxito
    toast({
      title: '✓ Herramienta entregada',
      description: `${unidadSeleccionada.value.catalogo?.nombre} → GRP-00${grupoId.value}`,
      variant: 'success',
    })
    resetSheet(false)
    emit('update:initialCode', '')
    // Foco inmediato para siguiente operación
    nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
  } catch (err) {
    const msg = err.response?.data?.detail || 'Sin stock disponible'
    // ❌ Toast rojo de error
    toast({ title: 'Error en check-out', description: msg, variant: 'error' })
    nextTick(() => inputRef.value?.focus?.() ?? inputRef.value?.$el?.focus())
  } finally {
    confirmando.value = false
  }
}

function resetSheet(cerrar = true) {
  reset()
  unidadSeleccionada.value = null
  grupoId.value = ''
  confirmando.value = false
  if (cerrar) {
    emit('update:open', false)
    emit('update:initialCode', '')
  }
}
</script>
