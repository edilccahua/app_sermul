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
        class="sap-icon--outbox text-4xl shrink-0"
        :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
      />
      <div>
        <h1
          class="text-3xl font-bold tracking-wide"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          DESPACHO POR GRUPOS
        </h1>
        <p
          class="text-s mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Entrega de herramientas por grupo
        </p>
        <p
          class="text-[11px] mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span v-if="dm.grupoNombre.value">{{ dm.grupoNombre.value }} · </span>
          {{ dm.items.value.length }} ítem(s) · {{ dm.itemsSeleccionados.value.length }} seleccionados
        </p>
      </div>
    </div>

    <!-- ══ Content (flex column para sticky + scroll) ════════════════════════ -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- ══ STICKY ZONE (top:0, z-index:10) ════════════════════════════════ -->
      <div
        class="shrink-0 px-5 pt-3 space-y-2"
        style="position: sticky; top: 0; z-index: 10; background: var(--sapBackgroundColor);"
      >
        <!-- Message Strip: Error API (compacto) -->
        <Transition name="strip-fade">
          <div
            v-if="dm.errorApi.value"
            class="flex items-start gap-2 p-2.5 border rounded-sm text-xs"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }"
          >
            <span
              class="sap-icon--message-error text-sm shrink-0 mt-px"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            />
            <span class="flex-1"><strong>Error:</strong> {{ dm.errorApi.value }}</span>
            <button
              class="leading-none text-sm"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
              @click="dm.clearError()"
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

            <!-- Fila 2: Buscar inline -->
            <div class="flex items-center gap-2">
              <label
                class="text-sm font-normal shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Buscar:</label>
              <div class="relative flex-1 min-w-0">
                <span
                  class="sap-icon--add-product absolute left-2.5 top-1/2 -translate-y-1/2 text-sm"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                />
                <input
                  ref="inputBusquedaRef"
                  v-model="queryManual"
                  type="text"
                  placeholder="Código o nombre..."
                  autocomplete="off"
                  class="w-full h-9 pl-8 pr-12 text-sm border rounded-sm outline-none font-mono"
                  :style="fieldStyle"
                  @keyup.enter="agregarDesdeBusqueda"
                  @blur="onBlurBusqueda"
                  @focus="onFocusBusqueda"
                >
                <span
                  v-if="buscandoManual"
                  class="sap-icon--refresh animate-spin absolute right-10 top-1/2 -translate-y-1/2 text-sm"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                />
                <span
                  v-if="queryManual"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-sm cursor-pointer"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                  @click="queryManual = ''"
                >✕</span>

                <!-- Dropdown resultados (positioned absolute) -->
                <div
                  v-if="resultadosBusqueda.length && dropdownAbierto"
                  class="absolute z-30 left-0 right-0 top-full mt-1 border rounded-sm shadow-lg max-h-64 overflow-y-auto"
                  :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
                >
                  <button
                    v-for="r in resultadosBusqueda"
                    :key="r.id"
                    class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-black/5 dark:hover:bg-white/5 transition-colors border-b last:border-0"
                    :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                    @mousedown.prevent="agregarDesdeResultado(r)"
                  >
                    <span
                      class="sap-icon--add text-sm shrink-0"
                      :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                    />
                    <code
                      class="font-mono text-xs shrink-0"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >{{ r.codigo_interno }}</code>
                    <span
                      class="text-sm truncate flex-1"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >{{ r.nombre
                    }}</span>
                    <span
                      class="text-xs px-2 py-0.5 rounded-sm shrink-0"
                      :style="r.cant_disponible > 0
                        ? { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }
                        : { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)' }"
                    >{{
                      r.cant_disponible }} disp.</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Error búsqueda manual -->
            <p
              v-if="errorBusquedaManual"
              class="text-xs"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              {{ errorBusquedaManual }}
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
            :disabled="dm.itemsSeleccionados.value.length === 0 || dm.tieneErrores.value || dm.enviando.value"
            class="self-stretch flex items-center justify-center gap-3 px-6 sm:px-8 rounded-sm transition-all"
            :style="dm.itemsSeleccionados.value.length > 0 && !dm.tieneErrores.value
              ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
              : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)', cursor: 'not-allowed' }"
            @click="dialogConfirmacion = true"
          >
            <span
              v-if="dm.enviando.value"
              class="sap-icon--refresh animate-spin text-2xl shrink-0"
            />
            <span
              v-else
              class="sap-icon--paper-plane text-2xl shrink-0"
            />

            <div class="flex flex-col items-start text-left">
              <span class="text-sm sm:text-base leading-tight font-bold tracking-wide">CONFIRMAR ENTREGA</span>
              <span class="text-xs font-mono opacity-90 mt-0.5">
                [ {{ dm.itemsSeleccionados.value.length }} ] ítems listos
              </span>
            </div>
          </button>
        </div>

        <!-- TABLE HEADER (checkbox al final) -->
        <div
          class="border rounded-sm"
          :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
        >
          <div
            class="grid items-center px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wide border-b"
            style="grid-template-columns: 2.5rem 5rem 1fr 5rem 1fr 3rem 3rem;"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
          >
            <span class="text-center">#</span>
            <span class="text-center">Stock</span>
            <span>Herramienta</span>
            <span class="text-center">Cant.</span>
            <span class="text-center">Observ.</span>
            <span class="text-center">Ori.</span>
            <span class="flex justify-center">☑</span>
          </div>
        </div>
      </div>

      <!-- ══ TABLE BODY (scrollable) ════════════════════════════════════════ -->
      <div
        class="flex-1 overflow-y-auto px-5 pb-4"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
        style="margin-top: 0.5rem;"
      >
        <div
          v-for="(item, idx) in dm.items.value"
          :key="item.catalogo_id"
          class="grid items-center px-3 py-2 border-b transition-colors hover-sap-table-row"
          :class="{ 'is-error': item._error, 'is-selected': item.seleccionado }"
          style="grid-template-columns: 2.5rem 5rem 1fr 5rem 1fr 3rem 3rem;"
          :style="{
            borderColor: 'var(--sapList_BorderColor)',
            background: item._error
              ? 'var(--sapErrorBackground)'
              : item.seleccionado
                ? 'var(--sapList_SelectionBackgroundColor)'
                : 'transparent',
          }"
        >
          <!-- Columna 0: Numeración -->
          <span
            class="text-center text-xs font-mono"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >{{ idx + 1
          }}</span>

          <!-- Columna 1: Stock LED -->
          <div class="text-center">
            <span
              v-if="item.cant_disponible >= item.cantidad"
              class="text-xs px-1.5 py-0.5 rounded-sm border font-medium inline-block"
              :style="{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }"
            >{{
              item.cant_disponible }} disp.</span>
            <span
              v-else
              class="text-xs px-1.5 py-0.5 rounded-sm border font-medium inline-block animate-pulse"
              :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
            >Faltan
              {{ item.cantidad - item.cant_disponible }}</span>
          </div>

          <!-- Columna 2: Herramienta (nombre + código) -->
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

          <!-- Columna 3: Cantidad editable -->
          <div class="flex justify-center">
            <input
              v-model.number="item.cantidad"
              type="number"
              :min="1"
              :max="999"
              class="w-16 h-10 text-center text-sm border rounded-sm outline-none font-mono"
              :style="item._error
                ? { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }
                : { background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor, var(--sapTextColor))' }"
              @blur="dm.validarItem(item)"
            >
          </div>

          <!-- Columna 4: Observación editable -->
          <div class="flex justify-center">
            <input
              v-model="item.observacion"
              type="text"
              placeholder="..."
              class="w-full h-10 px-2 text-xs border rounded-sm outline-none"
              :style="fieldStyle"
            >
          </div>

          <!-- Columna 5: Origen badge + Quitar -->
          <div class="flex items-center justify-center gap-1">
            <span
              v-if="item.origen === 'reserva'"
              class="text-[10px] px-1.5 py-0.5 rounded-sm border font-semibold"
              :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }"
              title="De reserva"
            >R</span>
            <button
              v-else
              class="w-8 h-8 flex items-center justify-center rounded-sm transition-colors hover:bg-[var(--sapErrorBackground)]"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
              style="background:transparent"
              title="Quitar ítem manual"
              @click="quitarItem(item)"
            >
              <span class="sap-icon--decline text-xs" />
            </button>
          </div>

          <!-- Columna 6: Checkbox 48px touch (al final) -->
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

        <!-- Empty state -->
        <div
          v-if="dm.items.value.length === 0"
          class="flex flex-col items-center justify-center py-20 text-center"
        >
          <span
            class="sap-icon--outbox text-4xl block mb-3"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          />
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Seleccione un grupo para cargar sus reservas pendientes,<br>
            o busque herramientas para agregar manualmente.
          </p>
        </div>
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
            Confirmar Despacho Masivo
          </DialogTitle>
          <DialogDescription
            class="text-sm mt-3 space-y-2"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            <p>Confirmar entrega de <strong :style="{ color: 'var(--sapTextColor)' }">{{ usuarioLogueado }}</strong></p>
            <p>
              a <strong :style="{ color: 'var(--sapTextColor)' }">{{ dm.grupoNombre.value }}</strong>
              <span v-if="liderNombre"> · Líder: <strong :style="{ color: 'var(--sapTextColor)' }">{{ liderNombre
              }}</strong></span>
            </p>
            <p>
              Se registrarán <strong :style="{ color: 'var(--sapTextColor)' }">{{ dm.itemsSeleccionados.value.length
              }}</strong> movimiento(s) con fecha y hora actual.
            </p>
          </DialogDescription>
        </DialogHeader>

        <!-- Resumen del payload -->
        <div
          class="mt-3 space-y-2 max-h-40 overflow-y-auto border rounded-sm text-xs p-2"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <div
            v-for="item in dm.itemsSeleccionados.value"
            :key="item.catalogo_id"
            class="flex justify-between px-2 py-1 border-b last:border-0"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <span
              class="truncate"
              :style="{ color: 'var(--sapTextColor)' }"
            >{{ item.nombre }}</span>
            <span
              class="font-mono ml-2 shrink-0"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >× {{ item.cantidad
            }}</span>
          </div>
          <p
            v-if="dm.itemsSeleccionados.value.length === 0"
            class="text-center py-2"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            No hay items seleccionados.
          </p>
        </div>

        <!-- Advertencia si hay items con stock insuficiente (bloquean CONFIRMAR) -->
        <div
          v-if="dm.tieneErrores.value"
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
            Hay herramientas con stock insuficiente. Ajuste las cantidades antes de confirmar.
          </p>
        </div>

        <DialogFooter class="flex gap-3 mt-4">
          <button
            :disabled="dm.enviando.value"
            class="flex-1 h-10 text-sm border rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
            @click="dialogConfirmacion = false"
          >
            Volver
          </button>
          <button
            :disabled="dm.enviando.value || dm.tieneErrores.value"
            class="flex-1 h-10 text-sm font-semibold rounded-sm flex items-center justify-center gap-2 transition-all"
            :style="{
              background: 'var(--sapButton_Emphasized_Background)',
              color: 'var(--sapButton_Emphasized_TextColor)',
              opacity: dm.enviando.value || dm.tieneErrores.value ? '0.6' : '1',
            }"
            @click="confirmarDespacho"
          >
            <span
              v-if="dm.enviando.value"
              class="sap-icon--refresh animate-spin text-sm"
            />
            <span
              v-else
              class="sap-icon--accept text-sm"
            />
            {{ dm.enviando.value ? 'Enviando...' : 'Confirmar Despacho' }}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
  DialogDescription, DialogFooter,
} from '@/components/ui/dialog'
import { useDespachoMasivo } from '@/composables/useDespachoMasivo'
import { useParadasStore } from '@/stores/paradas'
import { useGruposStore } from '@/stores/grupos'
import { useReservasStore } from '@/stores/reservas'
import { useSound } from '@/composables/useSound'
import { useToast } from '@/components/ui/toast'
import { api } from '@/api'

const dm = useDespachoMasivo()
const paradasStore = useParadasStore()
const gruposStore = useGruposStore()
const reservasStore = useReservasStore()
const route = useRoute()
const { playSuccess, playError } = useSound()
const { toast } = useToast()

// ── Estado local ───────────────────────────────────────────────────────────────
const paradaSeleccionadaId = ref(null)
const grupoSeleccionadoId = ref(null)
const dialogConfirmacion = ref(false)
const enviando = ref(false)

// Búsqueda con dropdown
const inputBusquedaRef = ref(null)
const queryManual = ref('')
const buscandoManual = ref(false)
const resultadosBusqueda = ref([])
const errorBusquedaManual = ref(null)
const dropdownAbierto = ref(false)
let debounceTimer = null

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

const liderNombre = computed(() => {
  const g = grupoSeleccionadoInfo.value
  if (!g?.lider) return ''
  return `${g.lider.nombre} ${g.lider.apellido}`
})

const usuarioLogueado = computed(() => {
  // Se obtiene del auth store en runtime
  const stored = localStorage.getItem('usuario')
  if (!stored) return '—'
  try {
    const u = JSON.parse(stored)
    return `${u.nombre} ${u.apellido}`.trim() || u.dni || '—'
  } catch { return '—' }
})

// ── Estilos ────────────────────────────────────────────────────────────────────
const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

// ── Búsqueda con debounce ─────────────────────────────────────────────────────

watch(queryManual, (val) => {
  clearTimeout(debounceTimer)
  errorBusquedaManual.value = null
  if (!val || val.trim().length < 2) {
    resultadosBusqueda.value = []
    return
  }
  buscandoManual.value = true
  debounceTimer = setTimeout(async () => {
    try {
      const q = val.trim()
      const { data } = await api.get('/inventario/buscar', { params: { short_code: q } })
      // Filtrar solo items con stock disponible
      resultadosBusqueda.value = (data || []).filter(m => m.cant_disponible > 0)
      dropdownAbierto.value = true
    } catch (err) {
      resultadosBusqueda.value = []
      errorBusquedaManual.value = err.response?.data?.detail || 'Error al buscar'
    } finally {
      buscandoManual.value = false
    }
  }, 250)
})

function onFocusBusqueda() {
  if (resultadosBusqueda.value.length > 0) dropdownAbierto.value = true
}

function onBlurBusqueda() {
  // Cerrar dropdown después de un pequeño delay para permitir click
  setTimeout(() => { dropdownAbierto.value = false }, 200)
}

function agregarDesdeResultado(material) {
  dm.agregarItemManual(material)
  queryManual.value = ''
  resultadosBusqueda.value = []
  dropdownAbierto.value = false
  toast({ title: `✓ ${material.nombre} añadido`, variant: 'success' })
}

function agregarDesdeBusqueda() {
  const q = queryManual.value.trim()
  if (!q) return
  if (resultadosBusqueda.value.length === 1) {
    agregarDesdeResultado(resultadosBusqueda.value[0])
    return
  }
  if (resultadosBusqueda.value.length > 1) {
    // Multiple resultados - dejar que el usuario elija del dropdown
    return
  }
  // Sin resultados, intentar búsqueda exacta
  buscarYAgregarDirecto(q)
}

async function buscarYAgregarDirecto(q) {
  buscandoManual.value = true
  errorBusquedaManual.value = null
  try {
    const { data } = await api.get('/inventario/buscar', { params: { short_code: q } })
    const conStock = (data || []).filter(m => m.cant_disponible > 0)
    if (conStock.length === 0) {
      errorBusquedaManual.value = `"${q}": sin stock disponible o no encontrado.`
      return
    }
    agregarDesdeResultado(conStock[0])
  } catch (err) {
    errorBusquedaManual.value = err.response?.data?.detail || 'Material no encontrado.'
  } finally {
    buscandoManual.value = false
  }
}

function quitarItem(item) {
  dm.quitarItem(item.catalogo_id)
}

// ── Selectores ─────────────────────────────────────────────────────────────────

function onParadaChange() {
  grupoSeleccionadoId.value = null
  dm.resetear()
}

async function onGrupoChange() {
  if (!grupoSeleccionadoId.value || !paradaSeleccionadaId.value) return
  const grupo = grupoSeleccionadoInfo.value
  if (!grupo) return
  const parada = paradaSeleccionada.value
  if (!parada) return

  // Reset items y cargar prelista
  dm.resetear()

  try {
    await reservasStore.fetchAll({
      grupo_id: grupo.id,
    })
    const reserva = reservasStore.items.find(r => r.estado === 'Pendiente' || r.estado === 'Aprobada') ?? null
    const prelista = reserva?.detalles ?? []

    dm.inicializar({
      grupoId: grupo.id,
      paradaId: parada.id,
      grupoNombre: `GRUPO ${grupo.codigo} — ${grupo.nombre}`,
      paradaNombre: parada.nombre,
      prelista,
      reservaId: reserva?.id ?? null,
    })
  } catch (e) {
    toast({ title: 'Error al cargar reservas', description: e.message, variant: 'destructive' })
  }
}

// ── Confirmación ────────────────────────────────────────────────────────────────

async function confirmarDespacho() {
  enviando.value = true
  try {
    await dm.ejecutarDespacho()
    dialogConfirmacion.value = false
    playSuccess()
    toast({
      title: '✓ Despacho masivo exitoso',
      description: dm.resultado.value?.mensaje,
      variant: 'success',
    })
    // Reset completo
    paradaSeleccionadaId.value = null
    grupoSeleccionadoId.value = null
    dm.resetear()
  } catch (err) {
    dialogConfirmacion.value = false
    playError()
  } finally {
    enviando.value = false
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────────

onMounted(async () => {
  await Promise.all([
    paradasStore.fetchAll(),
    gruposStore.fetchAll(),
  ])
  
  if (route.query.parada_id && route.query.grupo_id) {
    paradaSeleccionadaId.value = Number(route.query.parada_id)
    grupoSeleccionadoId.value = Number(route.query.grupo_id)
    await onGrupoChange()
  } else {
    // Default a última parada activa
    const activa = paradasStore.items.find(p => p.estado === 'Activa')
    paradaSeleccionadaId.value = activa?.id ?? paradasStore.items[0]?.id ?? null
    dm.resetear()
  }
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
