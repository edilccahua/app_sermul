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
          PRÉSTAMO INDIVIDUAL — Salida
        </h1>
        <p
          class="text-s mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Préstamo directo por DNI
        </p>
        <p
          class="text-[11px] mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span v-if="usuarioReceptor">{{ usuarioReceptor.nombre }} {{ usuarioReceptor.apellido }} · </span>
          {{ items.length }} ítem(s) listos
        </p>
      </div>
    </div>

    <!-- ══ Content (flex column para sticky + scroll) ════════════════════════ -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- ══ STICKY ZONE ════════════════════════════════ -->
      <div
        class="shrink-0 px-5 pt-3 space-y-2"
        style="position: sticky; top: 0; z-index: 10; background: var(--sapBackgroundColor);"
      >
        <!-- Message Strip: Error -->
        <Transition name="strip-fade">
          <div
            v-if="errorGlobal"
            class="flex items-start gap-2 p-2.5 border rounded-sm text-xs"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }"
          >
            <span
              class="sap-icon--message-error text-sm shrink-0 mt-px"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            />
            <span class="flex-1"><strong>Error:</strong> {{ errorGlobal }}</span>
            <button
              class="leading-none text-sm"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
              @click="errorGlobal = null"
            >
              ×
            </button>
          </div>
        </Transition>

        <!-- ══ MAIN TOOLBAR ══ -->
        <div class="flex gap-3 items-stretch">
          <!-- ══ COLUMNA IZQUIERDA: DNI, Info, Busqueda ══ -->
          <div class="flex-1 min-w-0 flex flex-col gap-3">
            <!-- Fila 1: DNI e Info Card -->
            <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
              <div class="flex items-center gap-2 w-full sm:w-72 shrink-0">
                <label
                  class="text-sm font-normal shrink-0"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >DNI:</label>
                <div class="relative flex-1 min-w-0">
                  <input
                    v-model="dniInput"
                    type="text"
                    placeholder="Buscar por DNI o nombre..."
                    autocomplete="off"
                    class="w-full h-9 px-2 text-sm border rounded-sm outline-none font-mono"
                    :style="fieldStyle"
                    @keyup.enter="buscarUsuarioDirecto"
                    @blur="onBlurBusquedaDni"
                    @focus="onFocusBusquedaDni"
                  >
                  <span
                    v-if="buscandoDni"
                    class="sap-icon--refresh animate-spin absolute right-2 top-1/2 -translate-y-1/2 text-sm"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  />
                  <div
                    v-if="resultadosBusquedaDni.length && dropdownDniAbierto"
                    class="absolute z-40 left-0 right-0 top-full mt-1 border rounded-sm shadow-lg max-h-64 overflow-y-auto"
                    :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
                  >
                    <button
                      v-for="(u, idx) in resultadosBusquedaDni"
                      :key="u.id"
                      class="w-full flex items-center justify-between px-3 py-2 text-left transition-colors border-b last:border-0"
                      :style="{ 
                        borderColor: 'var(--sapList_BorderColor)',
                        background: hoverDniIndex === idx ? 'var(--sapList_SelectionBackgroundColor)' : 'transparent'
                      }"
                      @mouseenter="hoverDniIndex = idx"
                      @mouseleave="hoverDniIndex = -1"
                      @mousedown.prevent="seleccionarUsuarioDni(u)"
                    >
                      <span
                        class="text-sm font-semibold truncate pr-2"
                        :style="{ color: 'var(--sapTextColor)' }"
                      >{{ u.nombre }} {{ u.apellido }}</span>
                      <code
                        class="text-xs shrink-0"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      >{{ u.dni }}</code>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Info Card Usuario -->
              <div
                v-if="usuarioReceptor"
                class="flex-1 min-w-0 flex items-center gap-2 h-9 border rounded-sm px-3 text-sm overflow-hidden"
                :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }"
              >
                <span
                  class="sap-icon--person-placeholder mr-1"
                  :style="{ color: 'var(--sapInformationTextColor)' }"
                />
                <span class="truncate text-[var(--sapTextColor)] font-semibold">{{ usuarioReceptor.nombre }} {{ usuarioReceptor.apellido }}</span>
                <span :style="{ color: 'var(--sapList_BorderColor)' }">&nbsp;·&nbsp;</span>
                <span class="text-[var(--sapContent_LabelColor)] font-mono text-xs">{{ usuarioReceptor.dni }}</span>
                <span :style="{ color: 'var(--sapList_BorderColor)' }">&nbsp;·&nbsp;</span>
                <span class="text-[var(--sapTextColor)] text-xs font-semibold">{{ usuarioReceptor.rol.nombre }}</span>
              </div>
              <div
                v-else
                class="flex-1 min-w-0 flex items-center gap-2 h-9 border rounded-sm px-3 text-sm overflow-hidden"
                :style="{ background: 'var(--sapNeutralBackground)', borderColor: 'var(--sapNeutralBorderColor)' }"
              >
                <span class="text-[var(--sapContent_LabelColor)] italic text-xs truncate">Busque un usuario por DNI para habilitar el préstamo</span>
              </div>
            </div>

            <!-- Fila 2: Buscar Herramienta -->
            <div class="flex flex-col gap-1">
              <div class="flex items-center gap-2">
                <label
                  class="text-sm font-normal shrink-0"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Herramienta:</label>
                <div class="relative flex-1 min-w-0">
                  <span
                    class="sap-icon--add-product absolute left-2.5 top-1/2 -translate-y-1/2 text-sm"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  />
                  <input
                    v-model="queryManual"
                    type="text"
                    placeholder="Código o nombre..."
                    autocomplete="off"
                    :disabled="!usuarioReceptor"
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

                  <div
                    v-if="resultadosBusqueda.length && dropdownAbierto"
                    class="absolute z-30 left-0 right-0 top-full mt-1 border rounded-sm shadow-lg max-h-64 overflow-y-auto"
                    :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
                  >
                    <button
                      v-for="(r, idx) in resultadosBusqueda"
                      :key="r.id"
                      class="w-full flex items-center gap-3 px-4 py-3 text-left transition-colors border-b last:border-0"
                      :style="{ 
                        borderColor: 'var(--sapList_BorderColor)',
                        background: hoverSearchIndex === idx ? 'var(--sapList_SelectionBackgroundColor)' : 'transparent'
                      }"
                      @mouseenter="hoverSearchIndex = idx"
                      @mouseleave="hoverSearchIndex = -1"
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
                      >{{ r.nombre }}</span>
                      <span
                        class="text-xs px-2 py-0.5 rounded-sm shrink-0"
                        :style="r.cant_disponible > 0
                          ? { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)' }
                          : { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)' }"
                      >{{ r.cant_disponible }} disp.</span>
                    </button>
                  </div>
                </div>
              </div>
              <p
                v-if="errorBusquedaManual"
                class="text-xs mt-1"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
              >
                {{ errorBusquedaManual }}
              </p>
            </div>
          </div> <!-- Cierra Columna Izquierda -->

          <!-- ══ COLUMNA DERECHA: Botón self-stretch ══ -->
          <button
            :disabled="!puedeConfirmar"
            class="self-stretch flex items-center justify-center gap-3 px-6 sm:px-8 rounded-sm transition-all"
            :style="puedeConfirmar
              ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
              : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)', cursor: 'not-allowed' }"
            @click="confirmarPrestamo"
          >
            <span
              v-if="enviando"
              class="sap-icon--refresh animate-spin text-2xl shrink-0"
            />
            <span
              v-else
              class="sap-icon--paper-plane text-2xl shrink-0"
            />
            <div class="flex flex-col items-start text-left">
              <span class="text-sm sm:text-base leading-tight font-bold tracking-wide">CONFIRMAR</span>
              <span class="text-xs font-mono opacity-90 mt-0.5">
                [ {{ items.length }} ] ítems listos
              </span>
            </div>
          </button>
        </div> <!-- Cierra Toolbar -->

        <!-- TABLE HEADER -->
        <div
          class="border rounded-sm mt-3"
          :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
        >
          <div
            class="grid items-center px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wide border-b"
            style="grid-template-columns: 2.5rem 5rem 1fr 5rem 1fr 3rem;"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
          >
            <span class="text-center">#</span>
            <span class="text-center">Stock</span>
            <span>Herramienta</span>
            <span class="text-center">Cant.</span>
            <span class="text-center">Observ.</span>
            <span class="text-center">✕</span>
          </div>
        </div>

        <!-- ══ TABLE BODY ════════════════════════════════════════ -->
        <div
          class="flex-1 overflow-y-auto px-5 pb-4"
          :style="{ background: 'var(--sapGroup_ContentBackground)' }"
          style="margin-top: 0.5rem;"
        >
          <div
            v-for="(item, idx) in items"
            :key="item.catalogo_id"
            class="grid items-center px-3 py-2 border-b transition-colors"
            :class="{ 'is-error': item.cantidad > item.cant_disponible }"
            style="grid-template-columns: 2.5rem 5rem 1fr 5rem 1fr 3rem;"
            :style="{
              borderColor: 'var(--sapList_BorderColor)',
              background: hoverTableIndex === idx
                ? 'var(--sapList_SelectionBackgroundColor)'
                : (item.cantidad > item.cant_disponible ? 'var(--sapErrorBackground)' : 'transparent'),
            }"
            @mouseenter="hoverTableIndex = idx"
            @mouseleave="hoverTableIndex = -1"
          >
            <span
              class="text-center text-xs font-mono"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >{{ idx + 1 }}</span>

            <div class="text-center">
              <span
                v-if="item.cant_disponible >= item.cantidad"
                class="text-xs px-1.5 py-0.5 rounded-sm border font-medium inline-block"
                :style="{ background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }"
              >{{ item.cant_disponible }} disp.</span>
              <span
                v-else
                class="text-xs px-1.5 py-0.5 rounded-sm border font-medium inline-block animate-pulse"
                :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
              >Faltan {{ item.cantidad - item.cant_disponible }}</span>
            </div>

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
            </div>

            <div class="flex justify-center">
              <input
                v-model.number="item.cantidad"
                type="number"
                :min="1"
                :max="item.cant_disponible"
                class="w-16 h-10 text-center text-sm border rounded-sm outline-none font-mono"
                :style="item.cantidad > item.cant_disponible
                  ? { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }
                  : { background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor, var(--sapTextColor))' }"
              >
            </div>

            <div class="flex justify-center px-2">
              <input
                v-model="item.observacion_entrega"
                type="text"
                placeholder="..."
                class="w-full h-10 px-2 text-xs border rounded-sm outline-none"
                :style="fieldStyle"
              >
            </div>

            <div class="flex items-center justify-center">
              <button
                class="w-8 h-8 flex items-center justify-center rounded-sm transition-colors hover:bg-[var(--sapErrorBackground)]"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
                style="background:transparent"
                title="Quitar"
                @click="quitarItem(idx)"
              >
                <span class="sap-icon--decline text-xs" />
              </button>
            </div>
          </div>

          <div
            v-if="items.length === 0"
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
              Busque un DNI y luego agregue herramientas a prestar.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { prestamoPersonalAPI, api, usuariosAPI } from '@/api'
import { useToast } from '@/components/ui/toast'
import { useSound } from '@/composables/useSound'

const { toast } = useToast()
const { playSuccess, playError } = useSound()

// ── Estado ─────────────────────────────────────────────────────────────────
const errorGlobal = ref(null)

// DNI y Usuario
const dniInput = ref('')
const buscandoDni = ref(false)
const resultadosBusquedaDni = ref([])
const dropdownDniAbierto = ref(false)
let debounceDniTimer = null
const usuarioReceptor = ref(null)

// Hover State
const hoverTableIndex = ref(-1)
const hoverDniIndex = ref(-1)
const hoverSearchIndex = ref(-1)

// Buscador Herramientas
const queryManual = ref('')
const buscandoManual = ref(false)
const resultadosBusqueda = ref([])
const errorBusquedaManual = ref(null)
const dropdownAbierto = ref(false)
let debounceTimer = null

// Items a prestar
const items = ref([])
const enviando = ref(false)

// ── Computed ───────────────────────────────────────────────────────────────
const tieneErrores = computed(() => items.value.some(i => !i.cantidad || i.cantidad > i.cant_disponible))
const puedeConfirmar = computed(() => usuarioReceptor.value && items.value.length > 0 && !tieneErrores.value && !enviando.value)

const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

// ── Métodos: DNI ───────────────────────────────────────────────────────────
watch(dniInput, (val) => {
  clearTimeout(debounceDniTimer)
  if (!val || val.trim().length < 2) {
    resultadosBusquedaDni.value = []
    dropdownDniAbierto.value = false
    return
  }
  if (usuarioReceptor.value && val === usuarioReceptor.value.dni) {
    resultadosBusquedaDni.value = []
    dropdownDniAbierto.value = false
    return
  }
  buscandoDni.value = true
  debounceDniTimer = setTimeout(async () => {
    try {
      const q = val.trim()
      const { data } = await usuariosAPI.buscar(q)
      resultadosBusquedaDni.value = data || []
      dropdownDniAbierto.value = true
    } catch (err) {
      resultadosBusquedaDni.value = []
    } finally {
      buscandoDni.value = false
    }
  }, 250)
})

function onFocusBusquedaDni() {
  if (resultadosBusquedaDni.value.length > 0) dropdownDniAbierto.value = true
}

function onBlurBusquedaDni() {
  setTimeout(() => { dropdownDniAbierto.value = false }, 200)
}

function seleccionarUsuarioDni(usuario) {
  usuarioReceptor.value = usuario
  dniInput.value = usuario.dni
  resultadosBusquedaDni.value = []
  dropdownDniAbierto.value = false
  items.value = []
  errorGlobal.value = null
}

async function buscarUsuarioDirecto() {
  const q = dniInput.value.trim()
  if (!q) return
  if (resultadosBusquedaDni.value.length === 1) {
    seleccionarUsuarioDni(resultadosBusquedaDni.value[0])
    return
  }
  buscandoDni.value = true
  errorGlobal.value = null
  usuarioReceptor.value = null
  items.value = []
  
  try {
    const { data } = await usuariosAPI.buscar(q)
    if (data && data.length > 0) {
      seleccionarUsuarioDni(data[0])
    } else {
      errorGlobal.value = "DNI o usuario no encontrado en el sistema."
    }
  } catch (err) {
    errorGlobal.value = "Error al consultar usuario."
  } finally {
    buscandoDni.value = false
  }
}

// ── Métodos: Buscar Herramientas ───────────────────────────────────────────
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
  setTimeout(() => { dropdownAbierto.value = false }, 200)
}

function agregarDesdeResultado(material) {
  const existente = items.value.find(i => i.catalogo_id === material.id)
  if (existente) {
    if (existente.cantidad < existente.cant_disponible) existente.cantidad++
  } else {
    items.value.push({
      catalogo_id: material.id,
      nombre: material.nombre,
      codigo_interno: material.codigo_interno,
      cant_disponible: material.cant_disponible,
      cantidad: 1,
      observacion_entrega: '',
    })
  }
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
  // Fallback exacto
  buscarYAgregarDirecto(q)
}

async function buscarYAgregarDirecto(q) {
  buscandoManual.value = true
  errorBusquedaManual.value = null
  try {
    const { data } = await api.get('/inventario/buscar', { params: { short_code: q } })
    const conStock = (data || []).filter(m => m.cant_disponible > 0)
    if (conStock.length === 0) {
      errorBusquedaManual.value = `"${q}": sin stock disponible.`
      return
    }
    agregarDesdeResultado(conStock[0])
  } catch (err) {
    errorBusquedaManual.value = err.response?.data?.detail || 'Material no encontrado.'
  } finally {
    buscandoManual.value = false
  }
}

function quitarItem(idx) {
  items.value.splice(idx, 1)
}

// ── Métodos: Confirmar ─────────────────────────────────────────────────────
async function confirmarPrestamo() {
  if (!puedeConfirmar.value) return
  enviando.value = true
  errorGlobal.value = null

  try {
    const payload = {
      usuario_receptor_id: usuarioReceptor.value.id,
      items: items.value.map(i => ({
        catalogo_id: i.catalogo_id,
        cantidad: i.cantidad,
        observacion_entrega: i.observacion_entrega || null,
      }))
    }
    
    const { data } = await prestamoPersonalAPI.salida(payload)
    playSuccess()
    toast({
      title: '✓ Préstamo exitoso',
      description: data.mensaje,
      variant: 'success',
    })
    
    // Reset
    items.value = []
    usuarioReceptor.value = null
    dniInput.value = ''
  } catch (err) {
    playError()
    errorGlobal.value = err.response?.data?.detail || 'Error interno del servidor al procesar el préstamo'
  } finally {
    enviando.value = false
  }
}
</script>

<style scoped>
.strip-fade-enter-active, .strip-fade-leave-active {
  transition: all 0.2s ease;
}
.strip-fade-enter-from, .strip-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
