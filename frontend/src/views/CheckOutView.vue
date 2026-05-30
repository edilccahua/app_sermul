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
          class="sap-icon--outbox text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Almacén — Salida de Herramientas
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Entrega de herramientas por grupo o despacho de reservas
          </p>
        </div>
      </div>

      <!-- Stepper visual -->
      <div class="flex items-center gap-2 mt-4">
        <template
          v-for="(step, idx) in pasos"
          :key="step.key"
        >
          <div class="flex items-center gap-2">
            <div
              class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all"
              :style="pasoActivo === idx
                ? { background: 'var(--sapButton_Emphasized_Background)', borderColor: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
                : idx < pasoActivo
                  ? { background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)', color: 'var(--sapPositiveTextColor)' }
                  : { background: 'transparent', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
            >
              <span
                v-if="idx < pasoActivo"
                class="sap-icon--accept text-xs"
              />
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <span
              class="text-sm font-medium hidden sm:block"
              :style="{ color: pasoActivo === idx ? 'var(--sapTextColor)' : 'var(--sapContent_LabelColor)' }"
            >{{ step.label }}</span>
          </div>
          <div
            v-if="idx < pasos.length - 1"
            class="flex-1 h-px mx-1"
            :style="{ background: 'var(--sapList_BorderColor)' }"
          />
        </template>
      </div>
    </div>

    <!-- ── Content Area ─────────────────────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto p-6">
      <!-- Sin parada activa → alerta bloqueante -->
      <div
        v-if="!paradasStore.paradaActiva"
        class="flex items-start gap-3 p-4 border rounded-sm mb-6"
        :style="{ background: 'var(--sapWarningBackground)', borderColor: 'var(--sapWarningBorderColor)' }"
      >
        <span
          class="sap-icon--message-warning text-xl shrink-0"
          :style="{ color: 'var(--sapCriticalColor)' }"
        />
        <div>
          <p
            class="font-semibold text-sm"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Sin parada activa
          </p>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Crea una parada en estado "Activa" antes de realizar entregas.
          </p>
        </div>
      </div>

      <!-- ═══ PASO 1: Seleccionar Grupo ═══════════════════════════════════ -->
      <div
        v-if="pasoActivo === 0"
        class="max-w-xl"
      >
        <div
          class="p-6 rounded-sm border"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2
            class="text-base font-semibold mb-4"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            ¿Para qué grupo es la entrega?
          </h2>

          <div class="space-y-4">
            <div class="space-y-1.5">
              <label
                class="text-sm font-normal flex items-center gap-1"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                <span class="sap-icon--group text-xs" /> Grupo de Trabajo *:
              </label>
              <select
                v-model="grupoSeleccionado"
                :disabled="!paradasStore.paradaActiva || loadingGrupos"
                class="h-12 w-full border px-3 text-sm focus:outline-none focus:ring-1 rounded-sm transition-colors"
                :style="{
                  background: 'var(--sapField_Background)',
                  borderColor: 'var(--sapField_BorderColor)',
                  color: 'var(--sapField_TextColor)',
                  'focus-ring-color': 'var(--sapButton_Emphasized_Background)',
                }"
              >
                <option value="">
                  Seleccionar grupo activo...
                </option>
                <option
                  v-for="g in gruposDisponibles"
                  :key="g.id"
                  :value="g"
                >
                  GRUPO {{ g.codigo }} — {{ g.nombre }}
                  <template v-if="g.lider">
                    · Líder: {{ g.lider.nombre }} {{ g.lider.apellido }}
                  </template>
                </option>
              </select>
              <p
                v-if="loadingGrupos"
                class="text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Cargando grupos...
              </p>
            </div>

            <!-- Info del grupo seleccionado -->
            <div
              v-if="grupoSeleccionado"
              class="p-3 rounded-sm border"
              :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }"
            >
              <div class="flex items-center gap-2 mb-2">
                <span
                  class="sap-icon--group text-sm"
                  :style="{ color: 'var(--sapInformationTextColor)' }"
                />
                <p
                  class="text-sm font-semibold"
                  :style="{ color: 'var(--sapTextColor)' }"
                >
                  {{ grupoSeleccionado.codigo }} — {{ grupoSeleccionado.nombre }}
                </p>
              </div>
              <div class="grid grid-cols-2 gap-1 text-xs">
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">Líder:</span>
                <span :style="{ color: 'var(--sapTextColor)' }">
                  {{ grupoSeleccionado.lider ? `${grupoSeleccionado.lider.nombre} ${grupoSeleccionado.lider.apellido}` : 'Sin asignar' }}
                </span>
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">Parada:</span>
                <span :style="{ color: 'var(--sapTextColor)' }">{{ paradasStore.paradaActiva?.nombre }}</span>
              </div>
            </div>

            <button
              :disabled="!grupoSeleccionado || !paradasStore.paradaActiva"
              class="w-full h-12 text-sm font-medium rounded-sm transition-colors"
              :style="grupoSeleccionado && paradasStore.paradaActiva
                ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }
                : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }"
              @click="siguientePaso"
            >
              Continuar →
            </button>
          </div>
        </div>
      </div>

      <!-- ═══ PASO 2: Checklist de Reserva o Entrega Libre ═══════════════ -->
      <div
        v-else-if="pasoActivo === 1"
        class="space-y-4"
      >
        <!-- Cargando reservas -->
        <div
          v-if="loadingReservas"
          class="flex items-center gap-2 py-4"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span class="sap-icon--refresh animate-spin" />
          <span class="text-sm">Verificando reservas del grupo...</span>
        </div>

        <!-- ── MODO CHECKLIST (hay reserva) ── -->
        <template v-else-if="reservaActiva">
          <div
            class="p-4 rounded-sm border"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <div class="flex items-center gap-2 mb-1">
              <span
                class="sap-icon--approvals"
                :style="{ color: 'var(--sapInformationTextColor)' }"
              />
              <p
                class="text-sm font-semibold"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                Reserva encontrada: {{ reservaActiva.codigo }}
              </p>
              <span
                class="ml-auto text-xs px-2 py-0.5 rounded-sm border font-medium"
                :style="estadoBadgeStyle(reservaActiva.estado)"
              >{{ reservaActiva.estado }}</span>
            </div>
            <p
              class="text-xs"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Turno {{ reservaActiva.turno }} · {{ formatFecha(reservaActiva.fecha_programada) }}
            </p>
          </div>

          <!-- Tabla checklist -->
          <div
            class="rounded-sm border overflow-hidden"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <div
              class="flex items-center gap-3 px-4 py-2 border-b text-xs font-semibold uppercase tracking-wide"
              :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
            >
              <input
                type="checkbox"
                :checked="todosSeleccionados"
                class="rounded-sm"
                @change="toggleTodos"
              >
              <span class="flex-1">Herramienta</span>
              <span class="w-24 text-center">Solicitado</span>
              <span class="w-24 text-center">Disponible</span>
            </div>
            <div
              v-for="item in reservaActiva.detalles"
              :key="item.id"
              class="flex items-center gap-3 px-4 py-3 border-b last:border-0 transition-colors"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
              :class="{ 'opacity-50': item.cantidad_disponible === 0 }"
            >
              <input
                v-model="itemsSeleccionados"
                type="checkbox"
                :value="item.id"
                :disabled="item.cantidad_disponible === 0"
                class="rounded-sm"
              >
              <div class="flex-1 min-w-0">
                <p
                  class="text-sm font-medium"
                  :style="{ color: 'var(--sapTextColor)' }"
                >
                  {{ item.catalogo?.nombre }}
                </p>
                <code
                  class="text-xs font-mono"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  {{ item.catalogo?.codigo_interno }}
                </code>
              </div>
              <span
                class="w-24 text-center text-sm"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                {{ item.cantidad }}
              </span>
              <span
                class="w-24 text-center text-xs px-2 py-0.5 rounded-sm border font-medium"
                :style="item.cantidad_disponible > 0
                  ? { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
                  : { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
              >
                {{ item.cantidad_disponible > 0 ? item.cantidad_disponible : 'Agotado' }}
              </span>
            </div>
          </div>

          <!-- Acciones checklist -->
          <div class="flex gap-3">
            <button
              class="flex-1 h-12 text-sm border rounded-sm transition-colors"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="pasoActivo = 0"
            >
              ← Volver
            </button>
            <button
              :disabled="itemsSeleccionados.length === 0 || despachando"
              class="flex-2 h-12 px-8 text-sm font-medium rounded-sm transition-colors"
              :style="itemsSeleccionados.length > 0 && !despachando
                ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }
                : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }"
              @click="despacharReserva"
            >
              <span
                v-if="despachando"
                class="flex items-center gap-2"
              >
                <span class="sap-icon--refresh animate-spin" /> Despachando...
              </span>
              <span v-else>✓ Despachar Seleccionados ({{ itemsSeleccionados.length }})</span>
            </button>
          </div>
        </template>

        <!-- ── MODO ENTREGA LIBRE (sin reserva) ── -->
        <template v-else>
          <div
            class="p-4 rounded-sm border"
            :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }"
          >
            <div class="flex items-center gap-2">
              <span
                class="sap-icon--message-information"
                :style="{ color: 'var(--sapInformationTextColor)' }"
              />
              <p
                class="text-sm"
                :style="{ color: 'var(--sapInformationTextColor)' }"
              >
                No hay reservas activas para este grupo. Modo entrega directa.
              </p>
            </div>
          </div>

          <!-- Input short code con auto-foco -->
          <div
            class="p-6 rounded-sm border"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <div class="space-y-3">
              <div
                v-show="!materialSeleccionado"
                class="space-y-1.5"
              >
                <label
                  class="text-sm font-normal"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Short Code *:
                </label>
                <div class="relative">
                  <span
                    class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center"
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
                    @keyup.enter="buscarPorEnter"
                  >
                  <span
                    v-if="loading"
                    class="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    <span
                      class="sap-icon--refresh w-4 h-4 flex items-center justify-center animate-spin"
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

              <!-- Resultados de búsqueda (materiales con stock) -->
              <div
                v-if="!materialSeleccionado && resultadosReales.length > 0"
                class="space-y-2"
              >
                <p
                  class="text-xs font-medium uppercase tracking-wide"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  {{ resultadosReales.length }} material{{ resultadosReales.length > 1 ? 'es' : '' }} con stock
                </p>
                <div
                  class="rounded-sm border overflow-hidden"
                  :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                >
                  <button
                    v-for="m in resultadosReales"
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
                      <div class="flex items-center gap-2 mt-0.5">
                        <code
                          class="font-mono text-xs"
                          :style="{ color: 'var(--sapContent_LabelColor)' }"
                        >
                          {{ m.codigo_interno }}
                        </code>
                      </div>
                    </div>
                    <div class="shrink-0 text-right">
                      <span
                        class="block text-xs px-2 py-0.5 rounded-sm border font-medium"
                        :style="{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }"
                      >
                        {{ m.cant_disponible }} dispon.
                      </span>
                    </div>
                  </button>
                </div>
              </div>

              <!-- Tarjeta del material seleccionado -->
              <div
                v-if="materialSeleccionado"
                class="p-4 rounded-sm border space-y-3 relative"
                :style="{ background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)' }"
              >
                <button
                  class="absolute top-3 right-3 flex items-center justify-center w-6 h-6 rounded-sm transition-colors"
                  :style="{ color: 'var(--sapNegativeTextColor)' }"
                  title="Deseleccionar"
                  @click="deseleccionarMaterial"
                >
                  <span class="sap-icon--decline text-sm" />
                </button>
                <div class="flex items-center gap-2">
                  <span
                    class="sap-icon--product"
                    :style="{ color: 'var(--sapPositiveTextColor)' }"
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
                  <span :style="{ color: 'var(--sapContent_LabelColor)' }">Disponible:</span>
                  <span
                    class="font-semibold"
                    :style="{ color: 'var(--sapPositiveTextColor)' }"
                  >{{ materialSeleccionado.cant_disponible }} unidades</span>
                  <span :style="{ color: 'var(--sapContent_LabelColor)' }">Costo reposición:</span>
                  <span :style="{ color: 'var(--sapTextColor)' }">S/. {{ materialSeleccionado.costo_reposicion?.toFixed(2) || '--' }}</span>
                </div>

                <!-- Input cantidad -->
                <div class="space-y-1.5">
                  <label
                    class="text-sm font-normal"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >Cantidad a entregar *:</label>
                  <input
                    v-model.number="cantidadEntrega"
                    type="number"
                    :min="1"
                    :max="materialSeleccionado.cant_disponible"
                    class="w-24 h-12 border px-3 text-sm rounded-sm focus:outline-none focus:ring-1"
                    :style="{
                      background: 'var(--sapField_Background)',
                      borderColor: 'var(--sapField_BorderColor)',
                      color: 'var(--sapField_TextColor)',
                    }"
                  >
                  <p
                    v-if="cantidadEntrega > materialSeleccionado.cant_disponible"
                    class="text-xs"
                    :style="{ color: 'var(--sapNegativeTextColor)' }"
                  >
                    Máximo {{ materialSeleccionado.cant_disponible }} unidades
                  </p>
                </div>

                <!-- Observación -->
                <div class="space-y-1.5">
                  <label
                    class="text-sm font-normal"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >Observación de entrega:</label>
                  <textarea
                    v-model="observacionEntrega"
                    placeholder="ej: entregado con cable de repuesto"
                    rows="2"
                    class="w-full border px-3 py-2 text-sm rounded-sm focus:outline-none focus:ring-1 resize-none"
                    :style="{
                      background: 'var(--sapField_Background)',
                      borderColor: 'var(--sapField_BorderColor)',
                      color: 'var(--sapField_TextColor)',
                    }"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Acciones entrega libre -->
          <div class="flex gap-3">
            <button
              class="flex-1 h-12 text-sm border rounded-sm transition-colors"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="pasoActivo = 0"
            >
              ← Volver
            </button>
            <button
              :disabled="!materialSeleccionado || confirmando"
              class="flex-2 h-12 px-8 text-sm font-medium rounded-sm transition-colors"
              :style="materialSeleccionado && !confirmando
                ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }
                : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }"
              @click="confirmarEntregaDirecta"
            >
              <span
                v-if="confirmando"
                class="flex items-center gap-2"
              >
                <span class="sap-icon--refresh animate-spin" /> Entregando...
              </span>
              <span v-else>✓ Confirmar Entrega <kbd class="ml-1 text-xs opacity-70">Enter</kbd></span>
            </button>
          </div>
        </template>
      </div>

      <!-- ═══ PASO 3: Confirmación ═════════════════════════════════════════ -->
      <div
        v-else-if="pasoActivo === 2"
        class="max-w-xl"
      >
        <div
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
            ¡Entrega registrada!
          </h2>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            La operación se completó exitosamente para el grupo
            <strong :style="{ color: 'var(--sapTextColor)' }">{{ grupoSeleccionado?.nombre }}</strong>.
          </p>
          <button
            class="w-full h-12 text-sm font-medium rounded-sm border transition-colors"
            :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
            @click="resetOperacion"
          >
            <span class="sap-icon--refresh mr-2" /> Nueva Operación
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useParadasStore } from '@/stores/paradas'
import { useGruposStore } from '@/stores/grupos'
import { useReservasStore } from '@/stores/reservas'
import { useInventarioStore } from '@/stores/inventario'
import { useShortCodeInput } from '@/composables/useShortCodeInput'
import { useSound } from '@/composables/useSound'
import { useToast } from '@/components/ui/toast'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

const paradasStore = useParadasStore()
const gruposStore = useGruposStore()
const reservasStore = useReservasStore()
const inventarioStore = useInventarioStore()
const { playSuccess, playError } = useSound()
const { toast } = useToast()

// ── Estado del stepper ─────────────────────────────────────────────────────────
const pasos = [
  { key: 'grupo',   label: '1. Seleccionar Grupo' },
  { key: 'entrega', label: '2. Verificar y Entregar' },
  { key: 'ok',      label: '3. Confirmación' },
]
const pasoActivo = ref(0)

// ── Estado Paso 1 ──────────────────────────────────────────────────────────────
const grupoSeleccionado = ref(null)
const loadingGrupos = ref(false)
const gruposDisponibles = computed(() => gruposStore.items)

// ── Estado Paso 2 ──────────────────────────────────────────────────────────────
const loadingReservas = ref(false)
const reservaActiva = ref(null)
const itemsSeleccionados = ref([])
const despachando = ref(false)
const confirmando = ref(false)

// Short code input (modo entrega libre)
const { inputRef, query, results, loading, error, reset: resetInput, refocus } = useShortCodeInput()
const materialSeleccionado = ref(null)
const cantidadEntrega = ref(1)
const observacionEntrega = ref('')
const resultadosReales = computed(() => results.value.filter((r) => !r._esSugerencia))

// ── Helpers ────────────────────────────────────────────────────────────────────
function estadoBadgeStyle(estado) {
  const map = {
    Pendiente: { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
    Aprobada:  { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
    Despachada:{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' },
    Rechazada: { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' },
  }
  return map[estado] ?? map['Pendiente']
}

const todosSeleccionados = computed(() =>
  reservaActiva.value?.detalles?.length > 0 &&
  itemsSeleccionados.value.length === reservaActiva.value.detalles.filter((i) => i.cantidad_disponible > 0).length
)

function toggleTodos() {
  if (todosSeleccionados.value) {
    itemsSeleccionados.value = []
  } else {
    itemsSeleccionados.value = (reservaActiva.value?.detalles ?? [])
      .filter((i) => i.cantidad_disponible > 0)
      .map((i) => i.id)
  }
}

function formatFecha(fecha) {
  if (!fecha) return '—'
  return format(new Date(fecha), "d 'de' MMMM yyyy", { locale: es })
}

// ── Paso 1: continuar ──────────────────────────────────────────────────────────
async function siguientePaso() {
  if (!grupoSeleccionado.value || !paradasStore.paradaActiva) return
  pasoActivo.value = 1
  loadingReservas.value = true
  try {
    // Buscar reservas Pendientes o Aprobadas para este grupo
    await reservasStore.fetchAll({
      grupo_id: grupoSeleccionado.value.id,
      estado: 'Pendiente,Aprobada',
    })
    // Tomamos la primera reserva activa si existe
    reservaActiva.value = reservasStore.items.length > 0 ? reservasStore.items[0] : null
    if (reservaActiva.value) {
      // Pre-seleccionar todos los ítems disponibles
      itemsSeleccionados.value = (reservaActiva.value.detalles ?? [])
        .filter((i) => i.cantidad_disponible > 0)
        .map((i) => i.id)
    } else {
      // Modo entrega libre: foco en el input
      nextTick(() => refocus())
    }
  } catch {
    reservaActiva.value = null
    nextTick(() => refocus())
  } finally {
    loadingReservas.value = false
  }
}

// ── Paso 2a: despachar reserva ─────────────────────────────────────────────────
async function despacharReserva() {
  if (!reservaActiva.value || itemsSeleccionados.value.length === 0 || despachando.value) return
  despachando.value = true
  try {
    await reservasStore.despachar(reservaActiva.value.id, itemsSeleccionados.value)
    playSuccess()
    toast({ title: '✓ Reserva despachada', description: `${itemsSeleccionados.value.length} ítem(s) entregados`, variant: 'success' })
    pasoActivo.value = 2
  } catch (err) {
    playError()
    toast({ title: 'Error al despachar', description: err.response?.data?.detail || 'Error desconocido', variant: 'error' })
  } finally {
    despachando.value = false
  }
}

// ── Paso 2b: confirmar entrega directa ─────────────────────────────────────────
async function confirmarEntregaDirecta() {
  if (!materialSeleccionado.value || !grupoSeleccionado.value || confirmando.value) return
  if (cantidadEntrega.value < 1 || cantidadEntrega.value > materialSeleccionado.value.cant_disponible) {
    error.value = `Cantidad inválida (máx: ${materialSeleccionado.value.cant_disponible})`
    return
  }
  confirmando.value = true
  error.value = null
  try {
    const response = await inventarioStore.checkOut({
      catalogo_id: materialSeleccionado.value.id,
      cantidad: cantidadEntrega.value,
      grupo_id: grupoSeleccionado.value.id,
      parada_id: paradasStore.paradaActiva.id,
      observacion_entrega: observacionEntrega.value || undefined,
    })
    playSuccess()
    toast({
      title: '✓ Herramienta entregada',
      description: response.mensaje || `${materialSeleccionado.value.nombre} → ${grupoSeleccionado.value.nombre}`,
      variant: 'success',
    })
    pasoActivo.value = 2
  } catch (err) {
    playError()
    toast({ title: 'Error en entrega', description: err.response?.data?.detail || 'Sin stock disponible', variant: 'error' })
    nextTick(() => refocus())
  } finally {
    confirmando.value = false
  }
}

function buscarPorEnter() {
  if (materialSeleccionado.value) {
    confirmarEntregaDirecta()
  }
}

function seleccionarMaterial(m) {
  materialSeleccionado.value = m
  cantidadEntrega.value = 1
  observacionEntrega.value = ''
}

function deseleccionarMaterial() {
  materialSeleccionado.value = null
  cantidadEntrega.value = 1
  observacionEntrega.value = ''
  nextTick(() => refocus())
}

function handleKeydown(e) {
  if (e.key === 'Escape' && materialSeleccionado.value) {
    deseleccionarMaterial()
  }
}

// ── Paso 3: reset ──────────────────────────────────────────────────────────────
function resetOperacion() {
  pasoActivo.value = 0
  grupoSeleccionado.value = null
  reservaActiva.value = null
  itemsSeleccionados.value = []
  materialSeleccionado.value = null
  cantidadEntrega.value = 1
  observacionEntrega.value = ''
  resetInput()
}

// ── Init ───────────────────────────────────────────────────────────────────────
onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  await Promise.all([
    paradasStore.fetchAll(),
    gruposStore.fetchAll({ estado: 'Activo' }, true),
  ])
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
