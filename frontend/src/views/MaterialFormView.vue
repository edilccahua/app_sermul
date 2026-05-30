<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══ Dynamic Page Header (Object Page) ══════════════════════════════════ -->
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background, var(--sapGroup_ContentBackground))', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- Volver -->
          <button
            class="w-8 h-8 flex items-center justify-center rounded-sm transition-colors hover-sap-selection"
            :style="{ color: 'var(--sapContent_IconColor)' }"
            style="background:transparent"
            title="Volver"
            @click="handleVolver"
          >
            <span class="sap-icon--nav-back text-lg" />
          </button>
          <span
            class="sap-icon--inventory text-2xl"
            :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
          />
          <div>
            <h1
              class="text-xl font-bold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              {{ esEdicion ? 'Editar Material' : 'Nuevo Material' }}
            </h1>
            <p
              class="text-sm"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ esEdicion ? `Catálogo / ${form.codigo_interno || '...'}` : 'Catálogo / Crear' }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Badge de estado -->
          <span
            v-if="esEdicion"
            class="text-xs px-2 py-1.5 rounded-sm border font-medium"
            :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }"
          >Modo Edición</span>
        </div>
      </div>
    </div>

    <!-- ══ Content Area ════════════════════════════════════════════════════════ -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-4xl mx-auto w-full">
        <!-- Message Strip: Error global (ej. código duplicado) -->
        <Transition name="strip-fade">
          <div
            v-if="errorGlobal"
            class="flex items-start gap-3 p-3 mb-5 rounded-sm border"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }"
          >
            <span class="sap-icon--message-error text-base shrink-0 mt-0.5" />
            <div class="flex-1 text-sm">
              <strong class="font-semibold block">Error al guardar</strong>
              <span>{{ errorGlobal }}</span>
            </div>
            <button
              class="shrink-0 text-lg leading-none"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
              @click="errorGlobal = null"
            >
              ×
            </button>
          </div>
        </Transition>

        <!-- ── Formulario en 2 columnas (Object Page Grid) ──────────────────── -->
        <form
          class="space-y-6"
          @submit.prevent="guardar"
        >
          <!-- ── BLOQUE 1: Identificación ─────────────────────────────────── -->
          <div
            class="p-5 border rounded-sm"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
          >
            <h2
              class="text-sm font-semibold uppercase tracking-wider mb-4 pb-2 border-b"
              :style="{ color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              Identificación
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <!-- Código Interno -->
              <div class="md:col-span-2">
                <label
                  class="block text-sm mb-1 flex items-center justify-between"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  <span>Código Interno <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:</span>
                  <button
                    v-if="!esEdicion && !editandoCodigo"
                    type="button"
                    class="text-xs font-semibold flex items-center gap-1 hover:opacity-70 transition-opacity"
                    :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                    title="Editar código manualmente"
                    @click="activarEdicionCodigo"
                  >
                    <span class="sap-icon--edit" /> Editar
                  </button>
                </label>
                <div class="relative w-full">
                  <input
                    ref="codigoInlineInput"
                    v-model="form.codigo_interno"
                    type="text"
                    required
                    :disabled="esEdicion || (!editandoCodigo && !esEdicion)"
                    placeholder="Ej: TALAELEC-BOSC"
                    class="w-full h-9 px-3 text-sm border rounded-sm outline-none font-mono transition-colors"
                    :style="{ 
                      background: editandoCodigo || esEdicion ? 'var(--sapField_Background)' : 'var(--sapNeutralBackground)', 
                      color: form.codigo_interno ? 'var(--sapTextColor)' : 'var(--sapContent_DisabledTextColor)',
                      borderColor: errorCodigo ? 'var(--sapErrorBorderColor)' : 'var(--sapList_BorderColor)' 
                    }"
                    @input="errorCodigo = null; errorGlobal = null"
                  >
                  <span
                    v-if="errorCodigo"
                    class="sap-icon--message-error absolute right-2 top-1/2 -translate-y-1/2 text-sm"
                    :style="{ color: 'var(--sapNegativeColor)' }"
                  />
                </div>
                <p
                  v-if="errorCodigo"
                  class="text-xs mt-1"
                  :style="{ color: 'var(--sapNegativeTextColor)' }"
                >
                  {{ errorCodigo }}
                </p>
                <p
                  v-else-if="!esEdicion && !editandoCodigo"
                  class="text-xs mt-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Auto-generado como: <code class="font-mono">NOMBRE(4) + CATEGORIA(4) + "-" + MARCA(4)</code>
                </p>
              </div>

              <!-- Nombre -->
              <div class="md:col-span-2">
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Nombre <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:
                </label>
                <input
                  ref="nombreInputRef"
                  v-model="form.nombre"
                  type="text"
                  required
                  placeholder="Ej: Taladro Neumático Atlas Copco"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                  @input="sugerirCodigo"
                >
              </div>

              <!-- Tipo de Material -->
              <div>
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Tipo de Material <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:
                </label>
                <select
                  v-model="form.tipo_material"
                  required
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                  @change="sugerirCodigo"
                >
                  <option value="">
                    Seleccionar tipo...
                  </option>
                  <option value="HERRAMIENTA_DEVOLUTIVA">
                    Herramienta Devolutiva
                  </option>
                  <option value="EPP_DEVOLUTIVO">
                    EPP Devolutivo
                  </option>
                  <option value="EPP_CONSUMIBLE">
                    EPP Consumible
                  </option>
                  <option value="CONSUMIBLE">
                    Consumible
                  </option>
                </select>
              </div>

              <!-- Categoría -->
              <div>
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Categoría <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:
                </label>
                <select
                  v-model.number="form.categoria_id"
                  required
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                  @change="sugerirCodigo"
                >
                  <option :value="1">
                    Eléctricas
                  </option>
                  <option :value="2">
                    Manuales
                  </option>
                  <option :value="3">
                    Neumáticas
                  </option>
                  <option :value="4">
                    Hidráulicas
                  </option>
                  <option :value="5">
                    Izaje
                  </option>
                  <option :value="6">
                    EPP - Cabeza
                  </option>
                  <option :value="7">
                    EPP - Manos
                  </option>
                  <option :value="8">
                    EPP - Respiratoria
                  </option>
                  <option :value="9">
                    EPP - Altura
                  </option>
                  <option :value="10">
                    Consumibles Generales
                  </option>
                </select>
              </div>


              <!-- Talla (EPP) -->
              <div v-if="form.tipo_material === 'EPP_DEVOLUTIVO' || form.tipo_material === 'EPP_CONSUMIBLE'">
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Talla:</label>
                <input
                  v-model="form.talla"
                  type="text"
                  placeholder="Ej: L, M, 42"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                >
              </div>

              <!-- Vida Útil Días (EPP) -->
              <div v-if="form.tipo_material === 'EPP_DEVOLUTIVO' || form.tipo_material === 'EPP_CONSUMIBLE'">
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Vida Útil (Días):</label>
                <input
                  v-model.number="form.vida_util_dias"
                  type="number"
                  min="0"
                  placeholder="Ej: 180"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                >
              </div>
            </div>
          </div>

          <!-- ── BLOQUE 2: Descripción y Proveedor ────────────────────────── -->
          <div
            class="p-5 border rounded-sm"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
          >
            <h2
              class="text-sm font-semibold uppercase tracking-wider mb-4 pb-2 border-b"
              :style="{ color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              Descripción y Proveedores
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <!-- Marca -->
              <div>
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Marca <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:</label>
                <input
                  v-model="form.marca"
                  type="text"
                  required
                  placeholder="Ej: Bosch, Atlas Copco"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                  @input="sugerirCodigo"
                >
              </div>

              <!-- Modelo -->
              <div>
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Modelo:</label>
                <input
                  v-model="form.modelo"
                  type="text"
                  placeholder="Ej: LBB16, GWS 7-100"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                >
              </div>

              <!-- Proveedor -->
              <div>
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Proveedor:</label>
                <input
                  v-model="form.proveedor"
                  type="text"
                  placeholder="Ej: Ferremax SAC"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none transition-colors"
                  :style="inputStyle()"
                >
              </div>



              <!-- Descripción (full width) -->
              <div class="md:col-span-2">
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Descripción:</label>
                <textarea
                  v-model="form.descripcion"
                  rows="3"
                  placeholder="Descripción detallada del material, especificaciones técnicas..."
                  class="w-full px-3 py-2 text-sm border rounded-sm outline-none transition-colors resize-y"
                  style="min-height: 76px;"
                  :style="inputStyle()"
                />
              </div>
            </div>
          </div>

          <!-- ── BLOQUE 3: Stock e Inventario ─────────────────────────────── -->
          <div
            class="p-5 border rounded-sm"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
          >
            <h2
              class="text-sm font-semibold uppercase tracking-wider mb-4 pb-2 border-b"
              :style="{ color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              Stock e Inventario
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
              <!-- Stock Disponible Inicial (solo en creación) -->
              <div v-if="!esEdicion">
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Stock Inicial:</label>
                <input
                  v-model.number="form.cant_disponible"
                  type="number"
                  min="0"
                  placeholder="0"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none font-mono transition-colors"
                  :style="inputStyle()"
                >
              </div>
              <!-- Costo de reposición -->
              <div>
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Costo Reposición (S/.):</label>
                <input
                  v-model.number="form.costo_reposicion"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none font-mono transition-colors"
                  :style="inputStyle()"
                >
              </div>

              <!-- Stock mínimo (solo en edición) -->
              <div v-if="esEdicion">
                <label
                  class="block text-sm mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Stock Mínimo:</label>
                <input
                  v-model.number="form.stock_minimo"
                  type="number"
                  min="0"
                  placeholder="0"
                  class="w-full h-9 px-3 text-sm border rounded-sm outline-none font-mono transition-colors"
                  :style="inputStyle()"
                >
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- ── Sticky Footer Toolbar (Fiori Standard) ────────────────────────── -->
    <div
      class="sticky bottom-0 z-10 border-t shrink-0 px-6 py-3 flex items-center justify-end gap-3 shadow-[0_-4px_10px_rgba(0,0,0,0.05)]"
      :style="{ background: 'var(--sapBackgroundColor)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <!-- Standard Button: Cancelar -->
      <button
        type="button"
        class="h-10 px-6 text-sm font-medium border rounded-sm transition-colors hover-sap-selection"
        :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
        @click="handleVolver"
      >
        Cancelar
      </button>

      <!-- Emphasized Button (ÚNICO POR VISTA): Guardar -->
      <button
        type="button"
        :disabled="guardando"
        class="h-10 px-8 text-sm font-semibold rounded-sm transition-opacity flex items-center gap-2 shadow-sm"
        :style="{
          background: 'var(--sapButton_Emphasized_Background)',
          color: 'var(--sapButton_Emphasized_TextColor)',
          opacity: guardando ? '0.6' : '1',
        }"
        @click="guardar"
      >
        <span
          v-if="guardando"
          class="sap-icon--refresh text-sm animate-spin"
        />
        <span
          v-else
          class="sap-icon--accept text-sm"
        />
        {{ guardando ? 'Guardando...' : (esEdicion ? 'Guardar Cambios' : 'Crear Material') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCatalogoStore } from '@/stores/catalogo'
import { useToast } from '@/components/ui/toast'

const catalogoStore = useCatalogoStore()
const route = useRoute()
const router = useRouter()

// Refs
const formContainer = ref(null)
const codigoInlineInput = ref(null)
const nombreInputRef = ref(null)
const editandoCodigo = ref(false)
const { toast } = useToast()

// ── Estado ───────────────────────────────────────────────────────────────────
const codigoInputRef = ref(null)
const guardando = ref(false)
const errorGlobal = ref(null)  // Message Strip: error de validación
const errorCodigo = ref(null)  // Error inline en el campo código_interno
// Flag para evitar que sugerirCodigo sobreescriba un código editado manualmente
const codigoManualmenteEditado = ref(false)

// ── Modo: detectar Crear vs Editar desde route.name ──────────────────────────
const esEdicion = computed(() => route.name === 'CatalogoEditar')
const idEdicion = computed(() => esEdicion.value ? parseInt(route.params.id) : null)

// ── Formulario reactivo ───────────────────────────────────────────────────────
const form = ref({
  codigo_interno: '',
  nombre: '',
  tipo_material: '',
  categoria_id: 1,
  descripcion: null,
  marca: null,
  modelo: null,
  proveedor: null,
  costo_reposicion: null,
  cant_disponible: 0,
  stock_minimo: 0,
  talla: null,
  vida_util_dias: null,
})

// ── Estilos de inputs ─────────────────────────────────────────────────────────
function inputStyle() {
  return {
    background: 'var(--sapField_Background)',
    color: 'var(--sapField_TextColor, var(--sapTextColor))',
    borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
  }
}

const codigoInputStyle = computed(() => {
  if (errorCodigo.value) {
    return {
      background: 'var(--sapErrorBackground)',
      color: 'var(--sapNegativeTextColor)',
      borderColor: 'var(--sapErrorBorderColor)',
      borderWidth: '2px',
    }
  }
  if (esEdicion.value) {
    return {
      background: 'var(--sapField_ReadOnly_Background, var(--sapNeutralBackground))',
      color: 'var(--sapContent_LabelColor)',
      borderColor: 'var(--sapList_BorderColor)',
      cursor: 'not-allowed',
    }
  }
  return inputStyle()
})

// ── Short Code Generator ──────────────────────────────────────────────────────
// Genera sugerencia: primeras 4 letras de Nombre + 4 de Categoría + "-" + 4 de Marca
function generarCodigoSugerido() {
  const nombre = form.value.nombre?.trim() ?? ''
  const categoriaId = form.value.categoria_id
  const marca = form.value.marca?.trim() ?? ''

  if (!nombre) return ''

  const categoriasMap = {
    1: 'GENE', 2: 'NEUM', 3: 'ELEC', 4: 'SEGU', 5: 'IZAJ',
    6: 'MANU', 7: 'MEDI', 8: 'SOLD', 9: 'CONS'
  }
  const partNombre = nombre.replace(/\s+/g, '').slice(0, 4).toUpperCase()
  const partCategoria = categoriasMap[categoriaId] || ''
  const partMarca = marca.replace(/\s+/g, '').slice(0, 4).toUpperCase()

  if (partCategoria && partMarca) return `${partNombre}${partCategoria}-${partMarca}`
  if (partCategoria) return `${partNombre}${partCategoria}`
  return partNombre
}

function activarEdicionCodigo() {
  editandoCodigo.value = true
  codigoManualmenteEditado.value = true
  nextTick(() => {
    codigoInlineInput.value?.focus()
  })
}

// Sugiere código automáticamente si no ha sido editado manualmente
function sugerirCodigo() {
  if (esEdicion.value || codigoManualmenteEditado.value) return
  const sugerido = generarCodigoSugerido()
  if (sugerido) {
    form.value.codigo_interno = sugerido
    errorCodigo.value = null
  }
}



// Detectar edición manual del código (el usuario tecleó directo)
watch(() => form.value.codigo_interno, (nuevo, viejo) => {
  // Si el cambio no vino de generarCodigoSugerido, marcar como manual
  const sugerido = generarCodigoSugerido()
  if (nuevo !== sugerido && nuevo !== viejo) {
    codigoManualmenteEditado.value = true
  }
  if (errorCodigo.value) errorCodigo.value = null
  if (errorGlobal.value) errorGlobal.value = null
})

// ── Cargar datos en modo Edición ──────────────────────────────────────────────
async function cargarMaterialEdicion() {
  if (!esEdicion.value || !idEdicion.value) return
  await catalogoStore.fetchAll()
  const material = catalogoStore.getById(idEdicion.value)
  if (!material) {
    toast({ title: 'Material no encontrado', variant: 'destructive' })
    router.push({ name: 'Catalogo' })
    return
  }
  form.value = {
    codigo_interno: material.codigo_interno ?? '',
    nombre: material.nombre ?? '',
    tipo_material: material.tipo_material ?? '',
    categoria_id: material.categoria_id ?? 1,
    descripcion: material.descripcion ?? null,
    marca: material.marca ?? null,
    modelo: material.modelo ?? null,
    proveedor: material.proveedor ?? null,
    costo_reposicion: material.costo_reposicion ?? null,
    fecha_ingreso: material.fecha_ingreso
      ? material.fecha_ingreso.slice(0, 10)  // ISO → YYYY-MM-DD para input date
      : null,
    stock_minimo: material.stock_minimo ?? 0,
    talla: material.talla ?? null,
    vida_util_dias: material.vida_util_dias ?? null,
  }
  codigoManualmenteEditado.value = true // En edición no tocar el código
}

// ── Guardar (Crear / Editar) ──────────────────────────────────────────────────
async function guardar() {
  errorGlobal.value = null
  errorCodigo.value = null
  guardando.value = true

  try {
    if (esEdicion.value) {
      // PUT /api/catalogo/{id}  — payload de edición (sin codigo_interno ni cantidad)
      const payload = {
        nombre: form.value.nombre,
        tipo_material: form.value.tipo_material,
        categoria_id: form.value.categoria_id,
        descripcion: form.value.descripcion || null,
        marca: form.value.marca || null,
        modelo: form.value.modelo || null,
        proveedor: form.value.proveedor || null,
        costo_reposicion: form.value.costo_reposicion ?? null,
        stock_minimo: form.value.stock_minimo ?? 0,
        talla: form.value.talla || null,
        vida_util_dias: form.value.vida_util_dias || null,
      }
      await catalogoStore.updateMaterial(idEdicion.value, payload)
      toast({ title: '✓ Material actualizado correctamente', variant: 'success' })
      router.push({ name: 'HerramientaDetalle', params: { id: idEdicion.value } })
    } else {
      // POST /api/catalogo/  — payload de creación
      const payload = {
        codigo_interno: form.value.codigo_interno.trim().toUpperCase(),
        nombre: form.value.nombre,
        tipo_material: form.value.tipo_material,
        categoria_id: form.value.categoria_id,
        descripcion: form.value.descripcion || null,
        marca: form.value.marca || null,
        modelo: form.value.modelo || null,
        proveedor: form.value.proveedor || null,
        costo_reposicion: form.value.costo_reposicion ?? null,
        cant_disponible: form.value.cant_disponible ?? 0,
        fecha_ingreso: form.value.fecha_ingreso || null,
        talla: form.value.talla || null,
        vida_util_dias: form.value.vida_util_dias || null,
      }
      const creado = await catalogoStore.createMaterial(payload)
      toast({ title: '✓ Material creado exitosamente', variant: 'success' })
      router.push({ name: 'HerramientaDetalle', params: { id: creado.id } })
    }
  } catch (err) {
    const status = err.response?.status
    const detail = err.response?.data?.detail || 'Error inesperado. Intenta nuevamente.'

    if (status === 400 || status === 409) {
      // ── Corrección C: Error 400 de código duplicado ──────────────────────
      // NO navegamos, NO cerramos. Pintamos el input en rojo y mostramos mensaje.
      const esDuplicado =
        detail.toLowerCase().includes('código') ||
        detail.toLowerCase().includes('codigo') ||
        detail.toLowerCase().includes('duplicate') ||
        detail.toLowerCase().includes('ya existe') ||
        detail.toLowerCase().includes('unique')

      if (esDuplicado && !esEdicion.value) {
        errorCodigo.value = detail
        // Hacer foco en el campo con error para que el operario lo corrija
        nextTick(() => codigoInputRef.value?.focus())
      } else {
        errorGlobal.value = detail
      }
    } else if (status === 422) {
      errorGlobal.value = `Datos inválidos: ${detail}`
    } else {
      errorGlobal.value = detail
    }
    // Scroll al tope para ver el Message Strip
    document.querySelector('[data-form-top]')?.scrollIntoView({ behavior: 'smooth' })
  } finally {
    guardando.value = false
  }
}

// ── Navegar hacia atrás con fallback ─────────────────────────────────────────
function handleVolver() {
  if (window.history.length > 2) {
    router.back()
  } else {
    router.push({ name: 'Catalogo' })
  }
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await cargarMaterialEdicion()
  if (!esEdicion.value) {
    nextTick(() => {
      // Auto-foco en nombre al crear (Heads-down Data Entry)
      nombreInputRef.value?.focus()
    })
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

/* Focus ring SAP */
input:focus,
select:focus,
textarea:focus {
  outline: 2px solid var(--sapField_Hover_BorderColor, var(--sapButton_Emphasized_Background));
  outline-offset: -1px;
}

input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
