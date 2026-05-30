<template>
  <div
    class="p-6 space-y-4"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--calendar w-7 h-7 flex items-center justify-center text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Gestión de Paradas
          </h1>
          <p
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Registro y control de mantenimientos
          </p>
        </div>
      </div>
      <button
        v-if="puedeCrear"
        class="inline-flex items-center gap-2 h-9 px-4 text-sm font-semibold rounded-sm transition-colors"
        :style="{
          background: 'var(--sapButton_Emphasized_Background)',
          color: 'var(--sapButton_Emphasized_TextColor)',
        }"
        @click="abrirModal()"
      >
        <span class="sap-icon--add text-sm" />
        Nueva Parada
      </button>
    </div>

    <!-- Table Toolbar -->
    <div class="flex items-center justify-between text-sm">
      <span :style="{ color: 'var(--sapContent_LabelColor)' }">
        Paradas
        <span class="font-semibold" :style="{ color: 'var(--sapTextColor)' }">({{ itemsOrdenados.length }})</span>
      </span>
      <div class="flex items-center gap-2">
        <button
          class="flex items-center gap-1.5 h-8 px-3 text-xs transition-colors rounded-sm"
          :style="{ color: 'var(--sapButton_TextColor)' }"
          style="background:transparent"
          :disabled="paradasStore.loading"
          @click="paradasStore.fetchAll(true)"
        >
          <span :class="['sap-icon--refresh text-xs', paradasStore.loading ? 'animate-spin' : '']" />
          Actualizar
        </button>
      </div>
    </div>

    <div
      class="border overflow-hidden rounded-sm"
      :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
    >
      <div
        v-if="paradasStore.loading"
        class="py-12 text-center"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
      >
        <span
          class="sap-icon--refresh text-3xl animate-spin block mb-3"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">Cargando paradas...</p>
      </div>
      <table
        v-else
        class="w-full caption-bottom text-sm"
      >
        <thead :style="{ background: 'var(--sapList_HeaderBackground)', borderBottom: '1px solid var(--sapList_BorderColor)' }">
          <tr>
            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('codigo')"
            >
              <div class="flex items-center gap-1">
                Código
                <span v-if="sortColumn === 'codigo'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('nombre')"
            >
              <div class="flex items-center gap-1">
                Nombre
                <span v-if="sortColumn === 'nombre'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('inicio')"
            >
              <div class="flex items-center gap-1">
                Inicio
                <span v-if="sortColumn === 'inicio'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('fin')"
            >
              <div class="flex items-center gap-1">
                Fin
                <span v-if="sortColumn === 'fin'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('estado')"
            >
              <div class="flex items-center gap-1">
                Estado
                <span v-if="sortColumn === 'estado'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th
              v-if="tieneAcciones"
              class="h-8 px-3 text-center font-semibold text-xs w-24"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Acciones
            </th>
          </tr>
        </thead>
        <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
          <tr
            v-for="p in itemsOrdenados"
            :key="p.id"
            class="border-b transition-colors hover-sap-list"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <td class="px-3 py-1.5">
              <router-link
                :to="`/app/paradas/${p.id}`"
                class="font-mono text-xs hover:underline"
                :style="{ color: 'var(--sapLinkColor)' }"
              >
                {{ p.codigo }}
              </router-link>
            </td>
            <td class="px-3 py-1.5 font-medium text-sm">
              <router-link
                :to="`/app/paradas/${p.id}`"
                class="hover:underline"
                :style="{ color: 'var(--sapLinkColor)' }"
              >
                {{ p.nombre }}
              </router-link>
            </td>
            <td class="px-3 py-1.5 text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
              {{ formatDate(p.fecha_inicio) }}
            </td>
            <td class="px-3 py-1.5 text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
              {{ p.fecha_fin ? formatDate(p.fecha_fin) : '—' }}
            </td>
            <td class="px-3 py-1.5">
              <span 
                class="inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium border"
                :style="badgeEstadoFiori(p.estado)"
              >
                {{ p.estado }}
              </span>
            </td>
            <td
              v-if="tieneAcciones"
              class="px-3 py-1.5"
            >
              <div class="flex items-center justify-center gap-1">
                <button
                  v-if="puedeCrear"
                  class="sap-icon--edit transition-colors w-7 h-7 inline-flex items-center justify-center rounded-sm hover-sap-selection text-sm"
                  :style="{ color: 'var(--sapContent_IconColor)' }"
                  style="background:transparent"
                  title="Editar parada"
                  @click="abrirModal(p)"
                />
                <router-link
                  v-if="puedeCerrar && p.estado === 'Activa'"
                  :to="`/app/paradas/${p.id}/cierre`"
                  class="sap-icon--flag transition-colors inline-flex items-center justify-center rounded-sm text-xs font-semibold px-2 py-1 ml-1"
                  :style="{ 
                    background: 'var(--sapButton_Reject_Background)', 
                    color: 'var(--sapButton_Reject_TextColor)',
                    border: '1px solid var(--sapButton_Reject_BorderColor)'
                  }"
                  title="Iniciar Cierre de Parada"
                >
                  <span class="ml-1 font-sans">Cerrar</span>
                </router-link>
              </div>
            </td>
          </tr>
          <tr v-if="itemsOrdenados.length === 0">
            <td
              :colspan="tieneAcciones ? 6 : 5"
              class="py-10 text-center"
            >
              <span
                class="sap-icon--calendar text-3xl block mb-2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              />
              <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">No hay paradas registradas</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>


    <!-- Modal (Fiori Dialog) -->
    <div
      v-if="modalAbierto"
      class="fixed inset-0 z-50 flex items-center justify-center"
    >
      <div
        class="absolute inset-0 bg-black/60 backdrop-blur-sm"
        @click="cerrarModal"
      />
      <div 
        class="relative z-10 w-full max-w-md mx-4 rounded-sm border overflow-hidden"
        :style="{ 
          background: 'var(--sapGroup_ContentBackground)', 
          borderColor: 'var(--sapList_BorderColor)', 
          boxShadow: 'var(--sapContent_Shadow2)' 
        }"
      >
        <div 
          class="px-6 py-4 border-b"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2 
            class="text-lg font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            {{ editando ? 'Editar Parada' : 'Nueva Parada' }}
          </h2>
        </div>

        <form
          class="p-6 space-y-4 pt-4"
          @submit.prevent="guardar"
        >
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Código *</label>
            <input
              v-model="form.codigo"
              required
              disabled
              placeholder="Auto-generado: 01-2026"
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none disabled:opacity-50 font-mono"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Nombre *</label>
            <input
              v-model="form.nombre"
              required
              placeholder="ej: Mantenimiento Molino SAG"
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Fecha Inicio *</label>
              <input
                v-model="form.fecha_inicio"
                type="date"
                required
                class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
                :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
              >
            </div>
            <div>
              <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Fecha Fin</label>
              <input
                v-model="form.fecha_fin"
                type="date"
                class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
                :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
              >
            </div>
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Estado</label>
            <select
              v-model="form.estado"
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
              <option value="Planificada">Planificada</option>
              <option value="Activa">Activa</option>
              <option value="Finalizada">Finalizada</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Empresa Contratista</label>
            <input
              v-model="form.empresa_contratista"
              disabled
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none disabled:opacity-70"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Gerencia del Contrato</label>
            <input
              v-model="form.gerencia_contrato"
              placeholder="Mantenimiento Mecánico"
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Responsable CMA</label>
            <input
              v-model="form.responsable_cma"
              placeholder="Luis Cervantes"
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
          </div>
          <div>
            <label class="text-xs font-semibold block mb-1" :style="{ color: 'var(--sapContent_LabelColor)' }">Ubicación</label>
            <select
              v-model="form.ubicacion"
              class="w-full h-9 px-3 text-sm border rounded-sm outline-none"
              :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
            >
              <option value="">Seleccionar ubicación...</option>
              <option value="Antapaccay">Antapaccay</option>
              <option value="Tintaya">Tintaya</option>
            </select>
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="button"
              class="flex-1 rounded-sm border px-4 py-2 text-sm font-semibold transition-colors h-9 flex items-center justify-center"
              :style="{ 
                background: 'var(--sapButton_Background)', 
                color: 'var(--sapButton_TextColor)',
                borderColor: 'var(--sapButton_BorderColor)'
              }"
              @click="cerrarModal"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="guardando"
              class="flex-1 rounded-sm px-4 py-2 text-sm font-semibold transition-colors disabled:opacity-50 h-9 flex items-center justify-center"
              :style="{ 
                background: 'var(--sapButton_Emphasized_Background)', 
                color: 'var(--sapButton_Emphasized_TextColor)' 
              }"
            >
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useParadasStore } from '@/stores/paradas'
import { useToast } from '@/components/ui/toast'


const authStore = useAuthStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

const modalAbierto = ref(false)
const editando = ref(null)
const guardando = ref(false)
const form = ref({ codigo: '', nombre: '', fecha_inicio: '', fecha_fin: '', estado: 'Planificada', empresa_contratista: 'SERMUL EIRL', gerencia_contrato: '', responsable_cma: '', ubicacion: '' })

// ── Estado de Ordenamiento ──────────────────────────────────────────────────
const sortColumn = ref('codigo')
const sortDesc = ref(true)

function toggleSort(col) {
  if (sortColumn.value === col) {
    sortDesc.value = !sortDesc.value
  } else {
    sortColumn.value = col
    sortDesc.value = !['codigo', 'nombre', 'estado'].includes(col)
  }
}

const itemsOrdenados = computed(() => {
  let items = [...paradasStore.items]
  if (sortColumn.value) {
    items.sort((a, b) => {
      let valA = a[sortColumn.value === 'inicio' ? 'fecha_inicio' : sortColumn.value === 'fin' ? 'fecha_fin' : sortColumn.value] || ''
      let valB = b[sortColumn.value === 'inicio' ? 'fecha_inicio' : sortColumn.value === 'fin' ? 'fecha_fin' : sortColumn.value] || ''
      return sortDesc.value ? String(valB).localeCompare(String(valA)) : String(valA).localeCompare(String(valB))
    })
  }
  return items
})

const puedeCrear = computed(() => ['RESIDENTE', 'ADMIN'].includes(authStore.rolCodigo))
const puedeCerrar = computed(() => ['RESIDENTE', 'ADMIN', 'ALMACENERO'].includes(authStore.rolCodigo))
const tieneAcciones = computed(() => puedeCrear.value || puedeCerrar.value)

function badgeEstadoFiori(estado) {
  if (estado === 'Planificada') return { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' }
  if (estado === 'Activa') return { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
  if (estado === 'Finalizada') return { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }
  return { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' }
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' })
}

function abrirModal(p = null) {
  editando.value = p
  form.value = p
    ? { codigo: p.codigo, nombre: p.nombre, fecha_inicio: p.fecha_inicio?.split('T')[0] || '', fecha_fin: p.fecha_fin?.split('T')[0] || '', estado: p.estado, empresa_contratista: p.empresa_contratista || 'SERMUL EIRL', gerencia_contrato: p.gerencia_contrato || '', responsable_cma: p.responsable_cma || '', ubicacion: p.ubicacion || '' }
    : { codigo: '', nombre: '', fecha_inicio: '', fecha_fin: '', estado: 'Planificada', empresa_contratista: 'SERMUL EIRL', gerencia_contrato: '', responsable_cma: '', ubicacion: '' }
  if (!p) generarCodigo()
  modalAbierto.value = true
}

function cerrarModal() { modalAbierto.value = false; editando.value = null }

function generarCodigo() {
  const year = new Date().getFullYear()
  const paradasEsteAno = paradasStore.items.filter(p => p.codigo.endsWith(`-${year}`))
  const nums = paradasEsteAno.map(p => parseInt(p.codigo.split('-')[0])).filter(n => !isNaN(n))
  const next = nums.length > 0 ? Math.max(...nums) + 1 : 1
  form.value.codigo = `${String(next).padStart(2, '0')}-${year}`
}

async function guardar() {
  guardando.value = true
  const payload = { ...form.value, fecha_fin: form.value.fecha_fin || null }
  try {
    if (editando.value) {
      await paradasStore.updateParada(editando.value.id, payload)
      toast({ title: 'Parada actualizada', variant: 'success' })
    } else {
      await paradasStore.createParada(payload)
      toast({ title: 'Parada creada exitosamente', variant: 'success' })
    }
    cerrarModal()
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail || 'Revisa los datos', variant: 'error' })
  } finally { guardando.value = false }
}

onMounted(() => paradasStore.fetchAll(true))
</script>
