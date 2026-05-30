<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══ Dynamic Page Header ════════════════════════════════════════════════ -->
    <div
      class="px-6 py-3 border-b shrink-0 flex items-center gap-4"
      :style="{ background: 'var(--sapPageHeader_Background, var(--sapGroup_ContentBackground))', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <span
        class="sap-icon--inbox text-4xl shrink-0"
        :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
      />
      <div>
        <h1
          class="text-3xl font-bold tracking-wide"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          DEVOLUCIÓN POR GRUPOS
        </h1>
        <p
          class="text-s mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Recepción de herramientas por grupo
        </p>
        <p
          class="text-[11px] mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span v-if="dv.grupoNombre.value">{{ dv.grupoNombre.value }} · </span>
          {{ dv.items.value.length }} ítem(s) · {{ dv.itemsSeleccionados.value.length }} seleccionados
        </p>
      </div>
    </div>

    <!-- ══ Content ════════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- ══ STICKY ZONE ════════════════════════════════════════════════════ -->
      <div
        class="shrink-0 px-5 pt-3 space-y-2"
        style="position: sticky; top: 0; z-index: 10; background: var(--sapBackgroundColor);"
      >
        <!-- Message Strip: Error API (compacto) -->
        <Transition name="strip-fade">
          <div
            v-if="dv.errorApi.value"
            class="flex items-start gap-2 p-2.5 border rounded-sm text-xs"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }"
          >
            <span
              class="sap-icon--message-error text-sm shrink-0 mt-px"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            />
            <span class="flex-1"><strong>Error:</strong> {{ dv.errorApi.value }}</span>
            <button
              class="leading-none text-sm"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
              @click="dv.clearError()"
            >
              ×
            </button>
          </div>
        </Transition>

        <!-- ══ MAIN TOOLBAR: 3 columnas (Parada/Buscar | Grupo/Info | Botón) ══ -->
        <div class="flex gap-3 items-stretch">
          <!-- ══ COLUMNA IZQUIERDA: Parada + Buscar ══ -->
          <div class="flex-1 min-w-0 flex flex-col gap-2">
            <!-- Fila 1: Parada inline -->
            <div class="flex items-center gap-2">
              <label
                class="text-sm font-normal shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Parada:</label>
              <select
                v-model="paradaSeleccionadaId"
                class="flex-1 min-w-0 h-9 px-2 text-sm border rounded-sm outline-none"
                :style="fieldStyle"
                @change="onParadaChange"
              >
                <option :value="null">
                  Seleccionar parada...
                </option>
                <option
                  v-for="p in paradasStore.items"
                  :key="p.id"
                  :value="p.id"
                >
                  {{ p.codigo }} - {{ p.nombre }}
                </option>
              </select>
            </div>

            <!-- Fila 2: Buscar inline + contador -->
            <div class="flex items-center gap-2">
              <label
                class="text-sm font-normal shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Buscar:</label>
              <div class="relative flex-1 min-w-0">
                <span
                  class="sap-icon--search absolute left-2.5 top-1/2 -translate-y-1/2 text-sm"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                />
                <input
                  v-model="dv.busquedaLocal.value"
                  type="text"
                  placeholder="Código o nombre..."
                  autocomplete="off"
                  class="w-full h-9 pl-8 pr-8 text-sm border rounded-sm outline-none"
                  :style="fieldStyle"
                >
                <span
                  v-if="dv.busquedaLocal.value"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-sm cursor-pointer"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                  @click="dv.busquedaLocal.value = ''"
                >✕</span>
              </div>
            </div>

            <!-- Contador -->
            <p
              class="text-xs"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ dv.itemsFiltrados.value.length }} de {{ dv.items.value.length }} herramientas
            </p>
          </div>

          <!-- ══ COLUMNA CENTRAL: Grupo + Info Card ══ -->
          <div class="flex-1 min-w-0 flex flex-col gap-2">
            <!-- Fila 1: Grupo inline -->
            <div class="flex items-center gap-2">
              <label
                class="text-sm font-normal shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Grupo:</label>
              <select
                v-model="grupoSeleccionadoId"
                :disabled="!paradaSeleccionadaId"
                class="flex-1 min-w-0 h-9 px-2 text-sm border rounded-sm outline-none"
                :style="fieldStyle"
                @change="onGrupoChange"
              >
                <option :value="null">
                  Seleccionar grupo...
                </option>
                <option
                  v-for="g in gruposFiltrados"
                  :key="g.id"
                  :value="g.id"
                >
                  GRUPO {{ g.codigo }} — {{ g.nombre }}
                </option>
              </select>
            </div>

            <!-- Fila 2: Info Card (misma altura que Buscar) -->
            <div
              v-if="grupoSeleccionadoInfo"
              class="flex items-center gap-2"
            >
              <label class="text-sm font-normal shrink-0 invisible pointer-events-none select-none">Grupo:</label>
              <div
                class="flex-1 min-w-0 h-9 flex items-center gap-2 px-3 text-sm border rounded-sm overflow-hidden"
                :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }"
              >
                <span class="shrink-0 whitespace-nowrap">
                  <span :style="{ color: 'var(--sapContent_LabelColor)' }">Líder:</span>
                  <strong :style="{ color: 'var(--sapTextColor)' }">{{ grupoSeleccionadoInfo.lider?.nombre ?? '—' }} {{
                    grupoSeleccionadoInfo.lider?.apellido?.charAt(0) ?? '' }}.</strong>
                </span>
                <span class="shrink-0 truncate whitespace-nowrap">
                  <span :style="{ color: 'var(--sapContent_LabelColor)' }">Parada:</span>
                  <strong :style="{ color: 'var(--sapTextColor)' }">{{ paradaSeleccionada?.nombre || '—' }}</strong>
                </span>
                <span
                  v-if="grupoSeleccionadoInfo.supervisor"
                  :style="{ color: 'var(--sapList_BorderColor)' }"
                >·</span>
                <span
                  v-if="grupoSeleccionadoInfo.supervisor"
                  class="shrink-0 truncate whitespace-nowrap"
                >
                  <span :style="{ color: 'var(--sapContent_LabelColor)' }">Sup:</span>
                  <strong :style="{ color: 'var(--sapTextColor)' }">{{ grupoSeleccionadoInfo.supervisor.nombre
                  }}</strong>
                </span>
              </div>
            </div>
          </div>

          <!-- ══ COLUMNA DERECHA: Botón self-stretch ══ -->
          <button
            :disabled="dv.itemsSeleccionados.value.length === 0 || dv.tieneErrores.value || dv.enviando.value"
            class="self-stretch flex items-center justify-center gap-3 px-6 sm:px-8 rounded-sm transition-all"
            :style="dv.itemsSeleccionados.value.length > 0 && !dv.tieneErrores.value
              ? { background: 'var(--sapButton_Accept_Background)', color: 'var(--sapButton_Accept_TextColor)' }
              : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)', cursor: 'not-allowed' }"
            @click="dialogConfirmacion = true"
          >
            <span
              v-if="dv.enviando.value"
              class="sap-icon--refresh animate-spin text-2xl shrink-0"
            />
            <span
              v-else
              class="sap-icon--accept text-2xl shrink-0"
            />

            <div class="flex flex-col items-start text-left">
              <span class="text-sm sm:text-base leading-tight font-bold tracking-wide">CONFIRMAR DEVOLUCIÓN</span>
              <span class="text-xs font-mono opacity-90 mt-0.5">
                [ {{ dv.itemsSeleccionados.value.length }} ] ítems listos
              </span>
            </div>
          </button>
        </div>

        <!-- TABLE HEADERS -->
        <div
          class="border rounded-sm"
          :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
        >
          <div
            class="grid items-center px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wide border-b"
            style="grid-template-columns: 2.5rem 1fr 5rem 5rem 8rem 1fr 3rem;"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
          >
            <span class="text-center">#</span>
            <span>Herramienta</span>
            <span class="text-center">Llevó</span>
            <span class="text-center">Devuel.</span>
            <span class="text-center">Estado</span>
            <span class="text-center">Obs.</span>
            <span class="flex justify-center">☑</span>
          </div>
        </div>
      </div>

      <!-- ══ TABLE BODY ════════════════════════════════════════════════════ -->
      <div
        class="flex-1 overflow-y-auto px-5 pb-4"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
        style="margin-top: 0.5rem;"
      >
        <!-- Loading state -->
        <div
          v-if="dv.cargando.value"
          class="flex items-center justify-center py-20"
        >
          <div class="text-center">
            <span
              class="sap-icon--refresh text-4xl animate-spin block mb-3"
              :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
            />
            <p
              class="text-sm"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Cargando herramientas del grupo...
            </p>
          </div>
        </div>

        <!-- Error loading state -->
        <div
          v-else-if="dv.errorCarga.value"
          class="flex items-center justify-center py-20"
        >
          <div class="text-center max-w-sm">
            <span
              class="sap-icon--message-error text-4xl block mb-3"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            />
            <p
              class="text-sm mb-4"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              {{ dv.errorCarga.value }}
            </p>
            <button
              class="h-9 px-4 text-sm border rounded-sm"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="onGrupoChange"
            >
              Reintentar
            </button>
          </div>
        </div>

        <!-- Normal state: rows -->
        <template v-else>
          <div
            v-for="(item, idx) in dv.itemsFiltrados.value"
            :key="item.catalogo_id"
            class="grid items-center px-3 py-2 border-b transition-colors hover-sap-table-row"
            :class="{ 'is-error': item._error, 'is-selected': item.seleccionado }"
            style="grid-template-columns: 2.5rem 1fr 5rem 5rem 8rem 1fr 3rem;"
            :style="{
              borderColor: 'var(--sapList_BorderColor)',
              background: item._error
                ? 'var(--sapErrorBackground)'
                : item.seleccionado
                  ? 'var(--sapList_SelectionBackgroundColor)'
                  : 'transparent',
            }"
          >
            <!-- #: Numeración -->
            <span
              class="text-center text-xs font-mono"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >{{ idx + 1
            }}</span>

            <!-- Herramienta: código + nombre + descripción/marca -->
            <div class="min-w-0 pr-2">
              <p
                class="text-sm font-medium truncate"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                {{ item.nombre }}
              </p>
              <code
                class="text-[10px] font-mono"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >{{ item.codigo_interno }}</code>
              <p
                v-if="item.marca || item.descripcion"
                class="text-[10px] truncate mt-0.5"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ [item.marca, item.descripcion].filter(Boolean).join(' · ') }}
              </p>
            </div>

            <!-- Cant. Prestada: read-only -->
            <div class="text-center">
              <span
                class="text-xs px-1.5 py-0.5 rounded-sm border font-medium"
                :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }"
              >{{
                item.cantidad_en_uso }}</span>
            </div>

            <!-- Cant. a Devolver: input editable -->
            <div class="flex justify-center">
              <input
                v-model.number="item.cantidad_devuelta"
                type="number"
                :min="1"
                :max="item.cantidad_en_uso"
                class="w-16 h-10 text-center text-sm border rounded-sm outline-none font-mono"
                :style="item._error
                  ? { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }
                  : { background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor, var(--sapTextColor))' }"
                @blur="dv.validarItem(item)"
              >
            </div>

            <!-- Estado de Retorno: select inline -->
            <div class="flex justify-center">
              <select
                v-model="item.estado"
                class="h-10 px-2 text-xs border rounded-sm outline-none w-full transition-colors font-medium"
                :style="estadoSelectStyle(item.estado)"
                @change="dv.validarItem(item)"
              >
                <option
                  v-for="opt in ESTADOS_RETORNO"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <!-- Observaciones -->
            <div class="flex justify-center">
              <input
                v-model="item.observacion"
                type="text"
                :placeholder="item.estado === 'MALOGRADO' ? 'Describa daño...' : '...'"
                class="w-full h-10 px-2 text-xs border rounded-sm outline-none"
                :style="fieldStyle"
              >
            </div>

            <!-- Checkbox (al FINAL de fila) 48px -->
            <label
              class="flex items-center justify-center cursor-pointer"
              style="min-height: 48px; min-width: 48px;"
            >
              <input
                type="checkbox"
                class="w-5 h-5 rounded-sm cursor-pointer"
                :style="{ accentColor: 'var(--sapButton_Emphasized_Background)' }"
                :checked="item.seleccionado"
                @change="item.seleccionado = !item.seleccionado"
              >
            </label>
          </div>

          <!-- Empty state (grupo cargado pero sin herramientas) -->
          <div
            v-if="dv.items.value.length === 0"
            class="flex flex-col items-center justify-center py-20 text-center"
          >
            <span
              class="sap-icon--inbox text-4xl block mb-3"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            />
            <p
              class="text-sm"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Seleccione un grupo para cargar sus herramientas en uso.
            </p>
          </div>
        </template>
      </div>
    </div>

    <!-- ══ AlertDialog de confirmación ════════════════════════════════════ -->
    <Dialog v-model:open="dialogConfirmacion">
      <DialogContent
        class="max-w-md"
        :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
      >
        <DialogHeader>
          <DialogTitle
            :style="{ color: 'var(--sapTextColor)' }"
            class="flex items-center gap-2"
          >
            <span
              class="sap-icon--message-warning text-lg"
              :style="{ color: 'var(--sapCriticalColor)' }"
            />
            Confirmar Devolución Masiva
          </DialogTitle>
          <DialogDescription
            class="text-sm mt-3 space-y-2"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            <p>
              Confirmar recepción de <strong :style="{ color: 'var(--sapTextColor)' }">{{ usuarioLogueado }}</strong>
            </p>
            <p>
              de herramientas del grupo <strong :style="{ color: 'var(--sapTextColor)' }">{{ dv.grupoNombre.value
              }}</strong>
            </p>
            <p>Las herramientas malogradas o perdidas generarán un reporte.</p>
          </DialogDescription>
        </DialogHeader>

        <!-- Resumen por estado -->
        <div
          class="mt-3 space-y-2 max-h-40 overflow-y-auto border rounded-sm text-xs p-2"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <div
            v-for="(cant, estado) in resumenPorEstado"
            :key="estado"
            class="flex items-center justify-between px-2 py-1 border-b last:border-0"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <span :style="{ color: 'var(--sapTextColor)' }">{{ ESTADOS_RETORNO.find(e => e.value === estado)?.label ||
              estado }}</span>
            <span
              class="font-semibold"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >{{ cant }} ítem(s)</span>
          </div>
          <p
            v-if="dv.itemsSeleccionados.value.length === 0"
            class="text-center py-2"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            No hay ítems seleccionados.
          </p>
        </div>

        <!-- Advertencia errores de validación -->
        <div
          v-if="dv.tieneErrores.value"
          class="flex items-start gap-2 p-3 border rounded-sm mt-3"
          :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
        >
          <span
            class="sap-icon--message-error text-base shrink-0"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          />
          <p
            class="text-xs"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          >
            Hay herramientas con cantidad devuelta mayor a la prestada. Ajuste antes de confirmar.
          </p>
        </div>

        <DialogFooter class="flex gap-3 mt-4">
          <button
            :disabled="dv.enviando.value"
            class="flex-1 h-10 text-sm border rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
            @click="dialogConfirmacion = false"
          >
            Volver
          </button>
          <button
            :disabled="dv.enviando.value || dv.tieneErrores.value"
            class="flex-1 h-10 text-sm font-semibold rounded-sm flex items-center justify-center gap-2 transition-all"
            :style="{
              background: 'var(--sapButton_Accept_Background, var(--sapButton_Emphasized_Background))',
              color: 'var(--sapButton_Accept_TextColor, var(--sapButton_Emphasized_TextColor))',
              opacity: dv.enviando.value || dv.tieneErrores.value ? '0.6' : '1',
            }"
            @click="confirmarDevolucion"
          >
            <span
              v-if="dv.enviando.value"
              class="sap-icon--refresh animate-spin text-sm"
            />
            <span
              v-else
              class="sap-icon--accept text-sm"
            />
            {{ dv.enviando.value ? 'Registrando...' : 'Confirmar Devolución' }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogFooter,
} from '@/components/ui/dialog'
import { useDevolucionMasivo, ESTADOS_RETORNO } from '@/composables/useDevolucionMasivo'
import { useParadasStore } from '@/stores/paradas'
import { useGruposStore } from '@/stores/grupos'
import { useSound } from '@/composables/useSound'
import { useToast } from '@/components/ui/toast'

const dv = useDevolucionMasivo()
const paradasStore = useParadasStore()
const gruposStore = useGruposStore()
const { playSuccess, playError } = useSound()
const { toast } = useToast()

// ── Estado local ───────────────────────────────────────────────────────────────
const paradaSeleccionadaId = ref(null)
const grupoSeleccionadoId = ref(null)
const dialogConfirmacion = ref(false)

// ── Computed ───────────────────────────────────────────────────────────────────

const gruposFiltrados = computed(() => {
  if (!paradaSeleccionadaId.value) return []
  return gruposStore.items.filter(g => g.parada_id === paradaSeleccionadaId.value)
})

const paradaSeleccionada = computed(() => {
  if (!paradaSeleccionadaId.value) return null
  return paradasStore.items.find(p => p.id === paradaSeleccionadaId.value) ?? null
})

const grupoSeleccionadoInfo = computed(() => {
  if (!grupoSeleccionadoId.value) return null
  return gruposStore.items.find(g => g.id === grupoSeleccionadoId.value) ?? null
})

const usuarioLogueado = computed(() => {
  const stored = localStorage.getItem('usuario')
  if (!stored) return '—'
  try {
    const u = JSON.parse(stored)
    return `${u.nombre} ${u.apellido}`.trim() || u.dni || '—'
  } catch { return '—' }
})

// Resumen por estado para el diálogo
const resumenPorEstado = computed(() => {
  const grupos = {}
  dv.itemsSeleccionados.value.forEach((item) => {
    grupos[item.estado] = (grupos[item.estado] ?? 0) + 1
  })
  return grupos
})

// ── Estilos ────────────────────────────────────────────────────────────────────
const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

function estadoSelectStyle(estado) {
  if (estado === 'MALOGRADO') {
    return { background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalColor)', borderColor: 'var(--sapWarningBorderColor)' }
  }
  if (estado === 'PERDIDO') {
    return { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }
  }
  return { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
}

// ── Selectores ─────────────────────────────────────────────────────────────────

function onParadaChange() {
  grupoSeleccionadoId.value = null
  dv.resetear()
}

async function onGrupoChange() {
  if (!grupoSeleccionadoId.value || !paradaSeleccionadaId.value) return
  const grupo = grupoSeleccionadoInfo.value
  if (!grupo) return
  const parada = paradaSeleccionada.value
  if (!parada) return

  dv.resetear()
  await dv.cargarHerramientasEnUso(
    grupo.id,
    parada.id,
    `GRUPO ${grupo.codigo} — ${grupo.nombre}`,
    parada.nombre,
  )
}

// ── Confirmación ────────────────────────────────────────────────────────────────

async function confirmarDevolucion() {
  try {
    await dv.ejecutarDevolucion()
    dialogConfirmacion.value = false
    playSuccess()
    toast({
      title: '✓ Devolución masiva registrada',
      description: dv.resultado.value?.mensaje,
      variant: 'success',
    })
    // Reset completo
    paradaSeleccionadaId.value = null
    grupoSeleccionadoId.value = null
    dv.resetear()
  } catch (err) {
    dialogConfirmacion.value = false
    playError()
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([
    paradasStore.fetchAll(),
    gruposStore.fetchAll(),
  ])
  const activa = paradasStore.items.find(p => p.estado === 'Activa')
  paradaSeleccionadaId.value = activa?.id ?? paradasStore.items[0]?.id ?? null
  dv.resetear()
})
</script>

<style scoped>
.strip-fade-enter-active,
.strip-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.strip-fade-enter-from,
.strip-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

input[type="checkbox"] {
  cursor: pointer;
}

input:focus,
select:focus {
  outline: 2px solid var(--sapField_Hover_BorderColor, var(--sapButton_Emphasized_Background));
  outline-offset: -1px;
}

input:disabled,
select:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Remove number input spinners */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>
