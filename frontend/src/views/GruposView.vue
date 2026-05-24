<template>
  <div class="h-full flex flex-col" :style="{ background: 'var(--sapBackgroundColor)' }">

    <!-- Dynamic Page Header -->
    <div class="px-6 py-4 border-b shrink-0" :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }">
      <div class="flex items-center gap-3">
        <span class="sap-icon--group text-2xl" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
        <div>
          <h1 class="text-xl font-bold" :style="{ color: 'var(--sapTextColor)' }">Grupos de Trabajo</h1>
          <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">
            Gestión de grupos, integrantes y asignaciones por parada
          </p>
        </div>
      </div>

      <!-- Filter Bar -->
      <div class="flex items-center gap-3 mt-4 flex-wrap">
        <div class="flex items-center gap-2">
          <label class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Parada:</label>
          <select v-model="filtroParadaId" class="h-8 border px-2 text-xs rounded-sm" :style="selectStyle">
            <option :value="null">Todas las paradas</option>
            <option v-for="p in paradasStore.items" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Estado:</label>
          <select v-model="filtroEstado" class="h-8 border px-2 text-xs rounded-sm" :style="selectStyle">
            <option value="">Todos</option>
            <option value="Activo">Activo</option>
            <option value="Inactivo">Inactivo</option>
            <option value="Finalizado">Finalizado</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table Toolbar -->
    <div class="flex items-center gap-3 px-6 py-2 border-b shrink-0" :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }">
      <span class="text-sm font-medium" :style="{ color: 'var(--sapTextColor)' }">
        Grupos ({{ gruposStore.items.length }})
      </span>
      <div class="ml-auto flex gap-2">
        <router-link to="/app/grupos/importar"
          class="flex items-center gap-1.5 h-8 px-3 text-xs border rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }">
          <span class="sap-icon--excel-attachment" /> Importar Excel
        </router-link>
        <button @click="abrirCrear"
          class="flex items-center gap-1.5 h-8 px-3 text-xs font-medium rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }">
          <span class="sap-icon--add" /> Crear Grupo
        </button>
      </div>
    </div>

    <!-- Tabla Compact -->
    <div class="flex-1 overflow-auto">
      <div v-if="gruposStore.loading" class="flex items-center justify-center py-8">
        <span class="sap-icon--refresh animate-spin text-2xl" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
      </div>
      <table v-else class="w-full text-xs border-collapse">
        <thead>
          <tr :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)' }">
            <th class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">Código</th>
            <th class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">Nombre</th>
            <th class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">Parada</th>
            <th class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">Líder</th>
            <th class="px-4 py-1.5 text-left font-semibold uppercase tracking-wide border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">Estado</th>
            <th class="px-4 py-1.5 text-right font-semibold uppercase tracking-wide border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="grupo in gruposStore.items" :key="grupo.id">
            <!-- Fila principal -->
            <tr
              @click="toggleExpand(grupo.id)"
              class="cursor-pointer transition-colors border-b hover:bg-muted/20"
              :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
            >
              <td class="px-4 py-1.5">
                <code class="font-mono text-xs" :style="{ color: 'var(--sapButton_Emphasized_Background)' }">{{ grupo.codigo }}</code>
              </td>
              <td class="px-4 py-1.5 font-medium">{{ grupo.nombre }}</td>
              <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ grupo.parada?.nombre ?? '—' }}</td>
              <td class="px-4 py-1.5" :style="{ color: 'var(--sapContent_LabelColor)' }">
                {{ grupo.lider ? `${grupo.lider.nombre} ${grupo.lider.apellido}` : '—' }}
              </td>
              <td class="px-4 py-1.5">
                <span class="text-xs px-2 py-0.5 rounded-sm border font-medium" :style="estadoBadgeStyle(grupo.estado)">
                  {{ grupo.estado }}
                </span>
              </td>
              <td class="px-4 py-1.5 text-right">
                <div class="flex items-center justify-end gap-2">
                  <span class="text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
                    <span class="sap-icon--chevron-down" v-if="expandido !== grupo.id" />
                    <span class="sap-icon--chevron-up" v-else />
                  </span>
                  <button
                    @click.stop="abrirEditar(grupo)"
                    class="h-6 px-2 text-xs border rounded-sm transition-colors"
                    :style="{ background: 'transparent', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
                  >
                    <span class="sap-icon--edit" />
                  </button>
                </div>
              </td>
            </tr>
            <!-- Fila expandida: integrantes -->
            <tr v-if="expandido === grupo.id" :key="'exp-' + grupo.id">
              <td colspan="6" class="px-8 py-3" :style="{ background: 'var(--sapInformationBackground)' }">
                <div v-if="loadingIntegrantes" class="text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
                  Cargando integrantes...
                </div>
                <div v-else>
                  <div class="flex items-center gap-2 mb-2">
                    <p class="text-xs font-semibold uppercase tracking-wide" :style="{ color: 'var(--sapContent_LabelColor)' }">
                      Integrantes ({{ grupoDetalle?.integrantes?.length ?? 0 }})
                    </p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="int in grupoDetalle?.integrantes ?? []"
                      :key="int.id"
                      class="inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-sm border"
                      :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                    >
                      <span class="sap-icon--employee text-xs" />
                      {{ int.nombre }} {{ int.apellido }}
                      <button
                        @click="quitarIntegrante(grupo.id, int.id)"
                        class="ml-1 hover:text-red-500 transition-colors"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      >
                        <span class="sap-icon--decline text-xs" />
                      </button>
                    </span>
                    <p
                      v-if="!grupoDetalle?.integrantes?.length"
                      class="text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >Sin integrantes aún.</p>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          <tr v-if="!gruposStore.loading && !gruposStore.items.length">
            <td colspan="6" class="px-4 py-8 text-center text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
              No hay grupos con los filtros seleccionados.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Dialog Crear/Editar -->
    <div v-if="dialogOpen" class="fixed inset-0 z-50 flex items-center justify-center" style="background: rgba(0,0,0,0.4)">
      <div class="w-full max-w-lg rounded-sm border shadow-xl" :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow2)' }">
        <!-- Dialog Header -->
        <div class="flex items-center gap-2 px-5 py-4 border-b" :style="{ borderColor: 'var(--sapList_BorderColor)' }">
          <span class="sap-icon--group" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
          <h2 class="text-base font-semibold" :style="{ color: 'var(--sapTextColor)' }">
            {{ editando ? 'Editar Grupo' : 'Crear Grupo' }}
          </h2>
          <button @click="dialogOpen = false" class="ml-auto" :style="{ color: 'var(--sapContent_LabelColor)' }">
            <span class="sap-icon--decline" />
          </button>
        </div>
        <!-- Dialog Body -->
        <div class="p-5 grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Código *:</label>
            <input v-model="form.codigo" class="h-9 w-full border px-3 text-sm rounded-sm" :style="inputStyle" placeholder="GRP-XXX" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Nombre *:</label>
            <input v-model="form.nombre" class="h-9 w-full border px-3 text-sm rounded-sm" :style="inputStyle" />
          </div>
          <div class="space-y-1">
            <label class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Parada:</label>
            <select v-model="form.parada_id" class="h-9 w-full border px-3 text-sm rounded-sm" :style="selectStyle">
              <option value="">Sin parada</option>
              <option v-for="p in paradasStore.items" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>
          <div class="space-y-1">
            <label class="text-xs font-normal" :style="{ color: 'var(--sapContent_LabelColor)' }">Estado:</label>
            <select v-model="form.estado" class="h-9 w-full border px-3 text-sm rounded-sm" :style="selectStyle">
              <option value="Activo">Activo</option>
              <option value="Inactivo">Inactivo</option>
              <option value="Finalizado">Finalizado</option>
            </select>
          </div>
          <div v-if="errorForm" class="col-span-2 flex items-center gap-2 p-3 rounded-sm border"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }">
            <span class="sap-icon--message-error" :style="{ color: 'var(--sapNegativeTextColor)' }" />
            <p class="text-xs" :style="{ color: 'var(--sapNegativeTextColor)' }">{{ errorForm }}</p>
          </div>
        </div>
        <!-- Dialog Footer -->
        <div class="flex gap-3 px-5 py-4 border-t" :style="{ borderColor: 'var(--sapList_BorderColor)' }">
          <button @click="dialogOpen = false" class="flex-1 h-9 text-sm border rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }">
            Cancelar
          </button>
          <button @click="guardar" :disabled="guardando" class="flex-1 h-9 text-sm font-medium rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }">
            <span v-if="guardando" class="sap-icon--refresh animate-spin mr-1" />
            {{ editando ? 'Guardar Cambios' : 'Crear Grupo' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useGruposStore } from '@/stores/grupos'
import { useParadasStore } from '@/stores/paradas'
import { useToast } from '@/components/ui/toast'

const gruposStore = useGruposStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

// Filtros
const filtroParadaId = ref('')
const filtroEstado = ref('')

async function aplicarFiltros() {
  const params = {}
  if (filtroParadaId.value) params.parada_id = filtroParadaId.value
  if (filtroEstado.value) params.estado = filtroEstado.value
  await gruposStore.fetchAll(params, true)
}

watch([filtroParadaId, filtroEstado], () => {
  aplicarFiltros()
})

// Expandir integrantes
const expandido = ref(null)
const grupoDetalle = ref(null)
const loadingIntegrantes = ref(false)

async function toggleExpand(id) {
  if (expandido.value === id) {
    expandido.value = null
    return
  }
  expandido.value = id
  loadingIntegrantes.value = true
  try {
    grupoDetalle.value = await gruposStore.fetchById(id)
  } finally {
    loadingIntegrantes.value = false
  }
}

async function quitarIntegrante(grupoId, usuarioId) {
  await gruposStore.removeIntegrante(grupoId, usuarioId)
  grupoDetalle.value = gruposStore.grupoActual
  toast({ title: 'Integrante removido', variant: 'success' })
}

// Dialog Crear/Editar
const dialogOpen = ref(false)
const editando = ref(null)
const guardando = ref(false)
const errorForm = ref(null)
const form = reactive({ codigo: '', nombre: '', parada_id: '', estado: 'Activo' })

function abrirCrear() {
  editando.value = null
  form.codigo = ''
  form.nombre = ''
  form.parada_id = ''
  form.estado = 'Activo'
  errorForm.value = null
  dialogOpen.value = true
}

function abrirEditar(grupo) {
  editando.value = grupo.id
  form.codigo = grupo.codigo
  form.nombre = grupo.nombre
  form.parada_id = grupo.parada_id ?? ''
  form.estado = grupo.estado
  errorForm.value = null
  dialogOpen.value = true
}

async function guardar() {
  if (!form.codigo.trim() || !form.nombre.trim()) {
    errorForm.value = 'Código y Nombre son obligatorios.'
    return
  }
  guardando.value = true
  errorForm.value = null
  try {
    const payload = {
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      parada_id: form.parada_id || null,
      estado: form.estado,
    }
    if (editando.value) {
      await gruposStore.update(editando.value, payload)
      toast({ title: 'Grupo actualizado', variant: 'success' })
    } else {
      await gruposStore.create(payload)
      toast({ title: 'Grupo creado', variant: 'success' })
    }
    dialogOpen.value = false
  } catch (err) {
    errorForm.value = err.response?.data?.detail || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

// Estilos compartidos
const estadoBadgeStyle = (estado) => {
  const map = {
    Activo:     { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' },
    Inactivo:   { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
    Finalizado: { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
  }
  return map[estado] ?? map['Inactivo']
}

const selectStyle = {
  background: 'var(--sapField_Background)',
  borderColor: 'var(--sapField_BorderColor)',
  color: 'var(--sapField_TextColor)',
}
const inputStyle = {
  background: 'var(--sapField_Background)',
  borderColor: 'var(--sapField_BorderColor)',
  color: 'var(--sapField_TextColor)',
}

onMounted(async () => {
  await paradasStore.fetchAll()
  if (paradasStore.items.length > 0) {
    const activa = paradasStore.items.find(p => p.estado === 'Activa')
    filtroParadaId.value = activa?.id ?? paradasStore.items[0].id
  }
})
</script>
