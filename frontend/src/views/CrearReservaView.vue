<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Header -->
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3">
        <router-link
          to="/app/almacen/solicitudes"
          class="h-8 w-8 flex items-center justify-center rounded-sm hover:bg-muted/30"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span class="sap-icon--nav-back" />
        </router-link>
        <span
          class="sap-icon--add-product text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Nueva Reserva
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Solicitar herramientas para una parada
          </p>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-3xl mx-auto space-y-4">
        <!-- Message Strip de alertas de stock -->
        <div
          v-if="alertasStock.length"
          class="flex items-start gap-2 p-3 rounded-sm border"
          :style="{ background: 'var(--sapWarningBackground)', borderColor: 'var(--sapWarningBorderColor)' }"
        >
          <span
            class="sap-icon--message-warning shrink-0 mt-0.5"
            :style="{ color: 'var(--sapCriticalColor)' }"
          />
          <div>
            <p
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              Alertas de stock:
            </p>
            <ul class="mt-1 space-y-0.5">
              <li
                v-for="(a, i) in alertasStock"
                :key="i"
                class="text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                • {{ a }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Message Strip de Bloqueo 1-a-1 -->
        <div
          v-if="grupoBloqueado"
          class="flex items-start gap-2 p-3 rounded-sm border"
          :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
        >
          <span
            class="sap-icon--message-error shrink-0 mt-0.5"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          />
          <div>
            <p
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              No se puede crear la reserva
            </p>
            <p
              class="text-xs mt-1"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              Este grupo ya tiene una solicitud pendiente o aprobada en curso. Solo se permite 1 activa.
            </p>
          </div>
        </div>

        <!-- Datos de la reserva -->
        <div
          class="p-5 rounded-sm border"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2
            class="text-sm font-semibold mb-4"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Datos de la Reserva
          </h2>
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label
                class="text-xs font-normal"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Parada *:</label>
              <select
                v-model="form.parada_id"
                class="h-9 w-full border px-3 text-sm rounded-sm"
                :style="inputStyle"
                @change="onParadaChange"
              >
                <option value="">
                  Seleccionar...
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
            <div class="space-y-1">
              <label
                class="text-xs font-normal"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Grupo *:</label>
              <select
                v-model="form.grupo_id"
                :disabled="!form.parada_id || esLider"
                class="h-9 w-full border px-3 text-sm rounded-sm"
                :style="inputStyle"
                @change="onGrupoChangeLocal"
              >
                <option value="">
                  Seleccionar...
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
          </div>
        </div>

        <!-- Carrito de herramientas -->
        <div
          class="p-5 rounded-sm border"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2
            class="text-sm font-semibold mb-3"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Herramientas Solicitadas
          </h2>

          <!-- Input búsqueda -->
          <div class="flex gap-2 mb-4">
            <div class="relative flex-1">
              <span
                class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              />
              <input
                ref="inputRef"
                v-model="query"
                placeholder="Buscar por código o nombre..."
                class="h-9 w-full border pl-9 pr-3 text-sm font-mono rounded-sm focus:outline-none"
                :style="inputStyle"
                @keyup.enter="agregarDelQuery"
              >
            </div>
          </div>

          <!-- Dropdown de resultados -->
          <div
            v-if="resultadosBusqueda.length && query.length >= 2"
            class="mb-3 rounded-sm border overflow-hidden"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <button
              v-for="r in resultadosBusqueda.slice(0, 5)"
              :key="r.id"
              class="w-full flex items-center gap-3 px-3 py-2 text-xs text-left hover:bg-muted/20 border-b last:border-0 transition-colors"
              :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
              @mousedown.prevent="agregarAlCarrito(r)"
            >
              <code
                class="font-mono"
                :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
              >{{ r.codigo_interno }}</code>
              <span class="flex-1 truncate">{{ r.nombre }}</span>
              <span
                class="shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >+ Agregar</span>
            </button>
          </div>

          <!-- Tabla carrito -->
          <div
            v-if="carrito.length"
            class="rounded-sm border overflow-hidden"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <div
              class="grid grid-cols-12 gap-2 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide border-b"
              :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
            >
              <span class="col-span-3">Código</span>
              <span class="col-span-4">Herramienta</span>
              <span class="col-span-2 text-center">Cantidad</span>
              <span class="col-span-2 text-center">Disponible</span>
              <span class="col-span-1" />
            </div>
            <div
              v-for="(item, i) in carrito"
              :key="item.catalogo_id"
              class="grid grid-cols-12 gap-2 items-center px-3 py-1.5 border-b last:border-0 text-xs"
              :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
            >
              <code
                class="col-span-3 font-mono"
                :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
              >{{ item.codigo_interno }}</code>
              <span class="col-span-4 truncate">{{ item.nombre }}</span>
              <div class="col-span-2 flex items-center justify-center">
                <input
                  v-model.number="item.cantidad"
                  type="number"
                  min="1"
                  class="h-7 w-16 border text-center text-xs rounded-sm focus:outline-none"
                  :style="inputStyle"
                >
              </div>
              <div class="col-span-2 text-center">
                <span
                  class="px-1.5 py-0.5 rounded-sm border text-xs"
                  :style="item.disponible > 0
                    ? { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
                    : { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
                >
                  {{ item.disponible > 0 ? item.disponible : 'Agotado' }}
                </span>
              </div>
              <button
                class="col-span-1 flex items-center justify-center"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
                @click="carrito.splice(i, 1)"
              >
                <span class="sap-icon--decline" />
              </button>
            </div>
          </div>

          <p
            v-else
            class="text-xs text-center py-4"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Busca y agrega herramientas al carrito.
          </p>
        </div>

        <!-- Error API -->
        <div
          v-if="errorApi"
          class="flex items-start gap-2 p-3 rounded-sm border"
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

        <!-- Footer -->
        <div class="flex gap-3 pb-6">
          <router-link
            to="/app/almacen/solicitudes"
            class="flex-1 h-12 flex items-center justify-center text-sm border rounded-sm"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          >
            Cancelar
          </router-link>
          <button
            :disabled="!puedeCrear || creando"
            class="flex-2 h-12 px-8 text-sm font-medium rounded-sm transition-colors"
            :style="puedeCrear && !creando
              ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }
              : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }"
            @click="crearReserva"
          >
            <span
              v-if="creando"
              class="flex items-center gap-2"
            ><span class="sap-icon--refresh animate-spin" /> Creando...</span>
            <span v-else>✓ Crear Reserva</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReservasStore } from '@/stores/reservas'
import { useGruposStore } from '@/stores/grupos'
import { useParadasStore } from '@/stores/paradas'
import { catalogoAPI, api } from '@/api'
import { useToast } from '@/components/ui/toast'

const router = useRouter()
const reservasStore = useReservasStore()
const gruposStore = useGruposStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

const form = reactive({ parada_id: '', grupo_id: '' })
const carrito = ref([])
const query = ref('')
const inputRef = ref(null)
const resultadosBusqueda = ref([])
const creando = ref(false)
const errorApi = ref(null)
const alertasStock = ref([])
const grupoBloqueado = ref(false)
const esLider = ref(false)
let debounceTimer = null

const gruposFiltrados = computed(() =>
  gruposStore.items.filter((g) => !form.parada_id || g.parada_id == form.parada_id)
)

const puedeCrear = computed(() =>
  form.parada_id && form.grupo_id && carrito.value.length > 0 && !grupoBloqueado.value
)

async function onParadaChange() {
  if (!esLider.value) form.grupo_id = ''
  if (form.parada_id) {
    await gruposStore.fetchAll({ parada_id: form.parada_id, estado: 'Activo' }, true)
    
    if (esLider.value) {
      const stored = localStorage.getItem('usuario')
      if (stored) {
        const u = JSON.parse(stored)
        const miGrupo = gruposStore.items.find(g => g.lider_id === u.id)
        if (miGrupo) {
          form.grupo_id = miGrupo.id
          await onGrupoChangeLocal()
        }
      }
    }
  }
}

async function onGrupoChangeLocal() {
  if (!form.grupo_id) {
    grupoBloqueado.value = false
    return
  }
  try {
    const { data: pendientes } = await api.get('/reservas/', { params: { grupo_id: form.grupo_id, estado: 'Pendiente' } })
    const { data: aprobadas } = await api.get('/reservas/', { params: { grupo_id: form.grupo_id, estado: 'Aprobada' } })
    grupoBloqueado.value = pendientes.length > 0 || aprobadas.length > 0
  } catch(e) {
    console.error(e)
  }
}

watch(query, (val) => {
  clearTimeout(debounceTimer)
  if (!val || val.trim().length < 2) { resultadosBusqueda.value = []; return }
  debounceTimer = setTimeout(async () => {
    try {
      const { data } = await catalogoAPI.search(val.trim())
      resultadosBusqueda.value = data
    } catch { resultadosBusqueda.value = [] }
  }, 200)
})

async function agregarAlCarrito(catalogo) {
  const itemExistente = carrito.value.find((i) => i.catalogo_id === catalogo.id)
  if (itemExistente) {
    itemExistente.cantidad++
    query.value = ''
    resultadosBusqueda.value = []
    return
  }
  // Obtener disponibilidad
  const { data: stock } = await catalogoAPI.getById(catalogo.id).catch(() => ({ data: null }))
  carrito.value.push({
    catalogo_id: catalogo.id,
    codigo_interno: catalogo.codigo_interno,
    nombre: catalogo.nombre,
    cantidad: 1,
    disponible: stock?.cant_disponible ?? 0,
  })
  query.value = ''
  resultadosBusqueda.value = []
}

function agregarDelQuery() {
  if (resultadosBusqueda.value.length > 0) {
    agregarAlCarrito(resultadosBusqueda.value[0])
  }
}

async function crearReserva() {
  if (!puedeCrear.value || creando.value) return
  creando.value = true
  errorApi.value = null
  alertasStock.value = []
  try {
    const payload = {
      parada_id: Number(form.parada_id),
      grupo_id: Number(form.grupo_id),
      turno: null,
      fecha_programada: new Date().toISOString().split('T')[0],
      items: carrito.value.map((i) => ({ catalogo_id: i.catalogo_id, cantidad: i.cantidad })),
    }
    const reserva = await reservasStore.create(payload)
    if (reserva.alertas_stock?.length) {
      alertasStock.value = reserva.alertas_stock
    }
    toast({ title: '✓ Reserva creada', description: `Código: ${reserva.codigo_reserva}`, variant: 'success' })
    router.push('/app/almacen/solicitudes')
  } catch (err) {
    console.error('Error al crear reserva:', err)
    if (Array.isArray(err.response?.data?.detail)) {
      errorApi.value = err.response.data.detail.map(e => `${e.loc[e.loc.length-1]}: ${e.msg}`).join(', ')
    } else {
      errorApi.value = err.response?.data?.detail || 'Error al crear la reserva'
    }
  } finally {
    creando.value = false
  }
}

const inputStyle = {
  background: 'var(--sapField_Background)',
  borderColor: 'var(--sapField_BorderColor)',
  color: 'var(--sapField_TextColor)',
}

onMounted(async () => {
  inputRef.value?.focus()
  
  const stored = localStorage.getItem('usuario')
  if (stored) {
    const u = JSON.parse(stored)
    if (u.rol_id === 6 || (u.rol && u.rol.codigo === 'LIDER_MEC')) {
      esLider.value = true
    }
  }

  await Promise.all([paradasStore.fetchAll(), gruposStore.fetchAll()])
  if (paradasStore.items.length > 0 && !form.parada_id) {
    const activa = paradasStore.items.find(p => p.estado === 'Activa')
    form.parada_id = activa?.id || paradasStore.items[paradasStore.items.length - 1].id
    await onParadaChange()
  }
})
</script>
