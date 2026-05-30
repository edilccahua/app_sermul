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
          DEVOLUCIÓN INDIVIDUAL — Entrada
        </h1>
        <p
          class="text-s mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Recepción directa por DNI
        </p>
        <p
          class="text-[11px] mt-0.5"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span v-if="usuarioReceptor">{{ usuarioReceptor.nombre }} {{ usuarioReceptor.apellido }} · </span>
          {{ itemsADevolver.length }} ítem(s) listos para devolver
        </p>
      </div>
    </div>

    <!-- ══ Content ════════════════════════ -->
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
          <!-- ══ COLUMNA IZQUIERDA: DNI e Info ══ -->
          <div class="flex-1 min-w-0 flex flex-col sm:flex-row gap-3 items-start sm:items-center">
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
              <span class="text-[var(--sapContent_LabelColor)] italic text-xs truncate">Busque un usuario por DNI para ver sus herramientas prestadas</span>
            </div>
          </div>

          <!-- ══ COLUMNA CENTRAL: Spinner ══ -->
          <div class="shrink-0 flex items-center justify-center px-4">
            <span
              v-if="cargandoHerramientas"
              class="sap-icon--refresh animate-spin text-2xl"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            />
          </div>

          <!-- ══ COLUMNA DERECHA: Botón self-stretch ══ -->
          <button
            :disabled="!puedeConfirmar"
            class="self-stretch flex items-center justify-center gap-3 px-6 sm:px-8 rounded-sm transition-all"
            :style="puedeConfirmar
              ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
              : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)', cursor: 'not-allowed' }"
            @click="confirmarDevolucion"
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
                [ {{ itemsADevolver.length }} ] ítems a devolver
              </span>
            </div>
          </button>
        </div>

        <!-- TABLE HEADER -->
        <div
          class="border rounded-sm mt-3"
          :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
        >
          <div
            class="grid items-center px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wide border-b"
            style="grid-template-columns: 2.5rem 5rem 1fr 5rem 8rem 1fr;"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
          >
            <span class="text-center">#</span>
            <span class="text-center">En Posesión</span>
            <span>Herramienta</span>
            <span class="text-center">A Devolver</span>
            <span class="text-center">Estado</span>
            <span class="text-center">Observación</span>
          </div>
        </div>
      </div>

      <!-- ══ TABLE BODY ════════════════════════════════════════ -->
      <div
        class="flex-1 overflow-y-auto px-5 pb-4"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
        style="margin-top: 0.5rem;"
      >
        <div
          v-for="(item, idx) in herramientasUsuario"
          :key="item.catalogo_id"
          class="grid items-center px-3 py-2 border-b transition-colors"
          :class="{ 'is-error': item.cantidad_devuelta > item.cantidad_en_posesion || (item.estado === 'Malograda' && !item.observacion) }"
          style="grid-template-columns: 2.5rem 5rem 1fr 5rem 8rem 1fr;"
          :style="{
            borderColor: 'var(--sapList_BorderColor)',
            background: hoverTableIndex === idx
              ? 'var(--sapList_SelectionBackgroundColor)'
              : (item.cantidad_devuelta > item.cantidad_en_posesion || (item.estado === 'Malograda' && !item.observacion)
                ? 'var(--sapErrorBackground)'
                : (item.cantidad_devuelta > 0 ? 'var(--sapList_SelectionBackgroundColor)' : 'transparent')),
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
              class="text-xs px-1.5 py-0.5 rounded-sm border font-medium inline-block"
              :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }"
            >{{ item.cantidad_en_posesion }} un.</span>
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
            <p
              v-if="item.fecha_ultimo_prestamo"
              class="text-[10px] truncate mt-0.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Prestado: {{ new Date(item.fecha_ultimo_prestamo).toLocaleDateString() }}
            </p>
          </div>

          <div class="flex justify-center">
            <input
              v-model.number="item.cantidad_devuelta"
              type="number"
              :min="0"
              :max="item.cantidad_en_posesion"
              class="w-16 h-10 text-center text-sm border rounded-sm outline-none font-mono"
              :style="item.cantidad_devuelta > item.cantidad_en_posesion
                ? { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }
                : { background: 'var(--sapField_Background)', borderColor: 'var(--sapField_BorderColor)', color: 'var(--sapField_TextColor, var(--sapTextColor))' }"
            >
          </div>

          <div class="flex justify-center px-2">
            <select
              v-model="item.estado"
              :disabled="item.cantidad_devuelta === 0"
              class="w-full h-10 px-2 text-xs border rounded-sm outline-none"
              :style="fieldStyle"
            >
              <option value="Operativa">
                Operativa
              </option>
              <option value="Malograda">
                Malograda
              </option>
              <option value="Perdida">
                Perdida
              </option>
            </select>
          </div>

          <div class="flex justify-center px-2">
            <input
              v-model="item.observacion"
              type="text"
              :placeholder="item.estado === 'Malograda' ? 'Obligatorio...' : 'Opcional...'"
              :disabled="item.cantidad_devuelta === 0"
              class="w-full h-10 px-2 text-xs border rounded-sm outline-none"
              :style="item.estado === 'Malograda' && !item.observacion
                ? { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }
                : fieldStyle"
            >
          </div>
        </div>

        <div
          v-if="herramientasUsuario.length === 0 && usuarioReceptor"
          class="flex flex-col items-center justify-center py-20 text-center"
        >
          <span
            class="sap-icon--sys-enter text-4xl block mb-3"
            :style="{ color: 'var(--sapPositiveTextColor)' }"
          />
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Este usuario no tiene herramientas prestadas a título personal.
          </p>
        </div>
        <div
          v-else-if="!usuarioReceptor"
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
            Busque un DNI para ver las herramientas.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { prestamoPersonalAPI, usuariosAPI } from '@/api'
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

// Herramientas
const cargandoHerramientas = ref(false)
const herramientasUsuario = ref([])
const enviando = ref(false)

// ── Computed ───────────────────────────────────────────────────────────────
const itemsADevolver = computed(() => herramientasUsuario.value.filter(i => i.cantidad_devuelta > 0))

const tieneErrores = computed(() => {
  return itemsADevolver.value.some(i => 
    i.cantidad_devuelta > i.cantidad_en_posesion ||
    (i.estado === 'Malograda' && !i.observacion?.trim())
  )
})

const puedeConfirmar = computed(() => itemsADevolver.value.length > 0 && !tieneErrores.value && !enviando.value)

const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

// ── Métodos: DNI y Carga ───────────────────────────────────────────────────
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
  herramientasUsuario.value = []
  errorGlobal.value = null
  cargarHerramientas(usuario.id)
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
  herramientasUsuario.value = []
  
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

async function cargarHerramientas(usuarioId) {
  cargandoHerramientas.value = true
  try {
    const { data } = await prestamoPersonalAPI.herramientas(usuarioId)
    // Inicializar propiedades reactivas
    herramientasUsuario.value = data.map(item => ({
      ...item,
      cantidad_devuelta: 0,
      estado: 'Operativa',
      observacion: ''
    }))
  } catch (err) {
    errorGlobal.value = "Error al cargar herramientas del usuario."
  } finally {
    cargandoHerramientas.value = false
  }
}

// ── Métodos: Confirmar ─────────────────────────────────────────────────────
async function confirmarDevolucion() {
  if (!puedeConfirmar.value) return
  enviando.value = true
  errorGlobal.value = null

  try {
    const payload = {
      usuario_receptor_id: usuarioReceptor.value.id,
      items: itemsADevolver.value.map(i => ({
        catalogo_id: i.catalogo_id,
        cantidad_devuelta: i.cantidad_devuelta,
        estado: i.estado,
        observacion: i.observacion || null,
      }))
    }
    
    const { data } = await prestamoPersonalAPI.entrada(payload)
    playSuccess()
    toast({
      title: '✓ Devolución exitosa',
      description: data.mensaje,
      variant: 'success',
    })
    
    // Recargar la tabla con el nuevo estado del usuario
    await cargarHerramientas(usuarioReceptor.value.id)
  } catch (err) {
    playError()
    errorGlobal.value = err.response?.data?.detail || 'Error interno del servidor al procesar la devolución'
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
