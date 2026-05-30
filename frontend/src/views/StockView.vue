<template>
  <div
    class="p-6 space-y-4"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--inventory w-7 h-7 flex items-center justify-center text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Stock de Materiales
          </h1>
          <p
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Visión global de unidades físicas
          </p>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3 flex-wrap items-center">
      <select
        v-model="filtroTipo"
        class="h-9 px-3 text-sm border rounded-sm outline-none"
        :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
        @change="inventarioStore.setFiltroTipo(filtroTipo)"
      >
        <option value="">Todos los tipos</option>
        <option value="HERRAMIENTA_DEVOLUTIVA">Herramienta Devolutiva</option>
        <option value="EPP_DEVOLUTIVO">EPP Devolutivo</option>
        <option value="EPP_CONSUMIBLE">EPP Consumible</option>
        <option value="CONSUMIBLE">Consumible</option>
      </select>

      <label
        class="flex items-center gap-2 text-sm cursor-pointer"
        :style="{ color: 'var(--sapContent_LabelColor)' }"
      >
        <input
          v-model="soloConStock"
          type="checkbox"
          class="rounded-sm"
          @change="inventarioStore.setSoloConStock(soloConStock)"
        >
        Solo con stock dispon.
      </label>

      <label
        class="flex items-center gap-2 text-sm cursor-pointer"
        :style="{ color: 'var(--sapContent_LabelColor)' }"
      >
        <input
          v-model="sinStock"
          type="checkbox"
          class="rounded-sm"
          @change="inventarioStore.setSinStock(sinStock)"
        >
        Sin stock
      </label>

      <div class="relative max-w-xs flex-1">
        <span
          class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        />
        <input
          v-model="busquedaTexto"
          placeholder="Buscar por nombre o código..."
          class="flex h-9 w-full pl-9 pr-3 rounded-sm border outline-none text-sm"
          :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor, var(--sapTextColor))', borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))' }"
          @input="inventarioStore.setBusquedaTexto(busquedaTexto)"
        >
      </div>
    </div>

    <!-- ══ Table Toolbar ═══════════════════════════════════════════════════════ -->
    <div class="flex items-center justify-between">
      <span
        class="text-sm"
        :style="{ color: 'var(--sapContent_LabelColor)' }"
      >
        Materiales
        <span
          class="font-semibold"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          ({{ inventarioStore.items.length }})
        </span>
        <span
          v-if="busquedaTexto || filtroTipo || soloConStock || sinStock"
          class="ml-2"
        >
          · Filtro activo
        </span>
      </span>
      <div class="flex items-center gap-2">
        <button
          class="flex items-center gap-1.5 h-8 px-3 text-xs transition-colors rounded-sm"
          :style="{ color: 'var(--sapButton_TextColor)' }"
          style="background:transparent"
          :disabled="inventarioStore.loading"
          @click="inventarioStore.fetchAll()"
        >
          <span :class="['sap-icon--refresh text-xs', inventarioStore.loading ? 'animate-spin' : '']" />
          Actualizar
        </button>
      </div>
    </div>

    <!-- Tabla Compact -->
    <div
      class="border overflow-hidden rounded-sm"
      :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
    >
      <div
        v-if="inventarioStore.loading"
        class="py-12 text-center"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
      >
        <span
          class="sap-icon--refresh text-3xl animate-spin block mb-3"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">Cargando...</p>
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
              @click="inventarioStore.toggleSort('codigo')"
            >
              <div class="flex items-center gap-1">
                Código
                <span 
                  v-if="inventarioStore.sortColumn === 'codigo'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>

            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('nombre')"
            >
              <div class="flex items-center gap-1">
                Nombre
                <span 
                  v-if="inventarioStore.sortColumn === 'nombre'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>

            <th 
              class="h-8 px-3 text-left font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('categoria')"
            >
              <div class="flex items-center gap-1">
                Categoría
                <span 
                  v-if="inventarioStore.sortColumn === 'categoria'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>
            
            <th 
              class="h-8 px-3 text-center font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('disponible')"
            >
              <div class="flex items-center justify-center gap-1">
                Disponible
                <span 
                  v-if="inventarioStore.sortColumn === 'disponible'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>

            <th 
              class="h-8 px-3 text-center font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('uso')"
            >
              <div class="flex items-center justify-center gap-1">
                En Uso
                <span 
                  v-if="inventarioStore.sortColumn === 'uso'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>

            <th 
              class="h-8 px-3 text-center font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('malograda')"
            >
              <div class="flex items-center justify-center gap-1">
                Malogradas
                <span 
                  v-if="inventarioStore.sortColumn === 'malograda'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>

            <th 
              class="h-8 px-3 text-center font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('perdida')"
            >
              <div class="flex items-center justify-center gap-1">
                Perdidas
                <span 
                  v-if="inventarioStore.sortColumn === 'perdida'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>

            <th 
              class="h-8 px-3 text-center font-semibold text-xs cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="inventarioStore.toggleSort('total')"
            >
              <div class="flex items-center justify-center gap-1">
                Total
                <span 
                  v-if="inventarioStore.sortColumn === 'total'" 
                  :class="inventarioStore.sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'"
                />
              </div>
            </th>
            
            <th class="h-8 px-3 text-center font-semibold text-xs w-16" :style="{ color: 'var(--sapContent_LabelColor)' }">Acciones</th>
          </tr>
        </thead>
        <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
          <tr
            v-for="item in inventarioStore.itemsFiltrados"
            :key="item.id"
            class="border-b transition-colors hover-sap-list"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <td class="px-3 py-1.5">
              <router-link
                :to="`/app/herramienta/${item.id}`"
                class="font-mono text-[var(--sapLinkColor)] hover:underline text-xs"
              >
                {{ item.codigo_interno }}
              </router-link>
            </td>
            <td class="px-3 py-1.5">
              <router-link
                :to="`/app/herramienta/${item.id}`"
                class="text-[var(--sapLinkColor)] hover:underline text-sm font-medium"
              >
                {{ item.nombre }}
              </router-link>
            </td>
            <td class="px-3 py-1.5 text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
              {{ item.categoria?.nombre || '—' }}
            </td>
            <td class="px-3 py-1.5 text-center">
              <span
                class="text-sm font-semibold"
                :style="{ color: item.cant_disponible > 0 ? 'var(--sapPositiveTextColor)' : 'var(--sapNegativeTextColor)' }"
              >
                {{ item.cant_disponible ?? 0 }}
              </span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span
                class="text-sm font-semibold"
                :style="{ color: (item.cant_en_uso ?? 0) > 0 ? 'var(--sapTextColor)' : 'var(--sapContent_LabelColor)' }"
              >{{ item.cant_en_uso ?? 0 }}</span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span
                class="text-sm font-semibold"
                :style="{ color: (item.cant_malograda ?? 0) > 0 ? 'var(--sapTextColor)' : 'var(--sapContent_LabelColor)' }"
              >{{ item.cant_malograda ?? 0 }}</span>
            </td>
            <td class="px-3 py-1.5 text-center">
              <span
                class="text-sm font-semibold"
                :style="{ color: (item.cant_perdida ?? 0) > 0 ? 'var(--sapTextColor)' : 'var(--sapContent_LabelColor)' }"
              >{{ item.cant_perdida ?? 0 }}</span>
            </td>
            <td class="px-3 py-1.5 text-center font-mono text-sm" :style="{ color: 'var(--sapTextColor)' }">
              {{ (item.cant_disponible ?? 0) + (item.cant_en_uso ?? 0) + (item.cant_malograda ?? 0) + (item.cant_perdida ?? 0) }}
            </td>
            <td class="px-3 py-1.5 text-center">
              <div class="flex items-center justify-center gap-1">
                <button
                  class="sap-icon--edit transition-colors w-7 h-7 inline-flex items-center justify-center rounded-sm hover-sap-selection"
                  :style="{ color: 'var(--sapContent_IconColor)' }"
                  style="background:transparent"
                  title="Ajustar Stock"
                  @click="abrirModal(item)"
                />
              </div>
            </td>
          </tr>
          <tr v-if="inventarioStore.itemsFiltrados.length === 0">
            <td
              colspan="9"
              class="py-10 text-center"
            >
              <span
                class="sap-icon--inventory text-3xl block mb-2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              />
              <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">Sin materiales con esos filtros</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ── Dialog (Modal) Fiori: Ajuste de Stock ──────────────────────────── -->
    <div
      v-if="modalAbierto"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      @click.self="cerrarModal"
      @keydown.esc="cerrarModal"
    >
      <div
        class="border rounded-sm w-[90%] max-w-lg flex flex-col overflow-hidden"
        :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
      >
        <!-- Modal Header -->
        <div
          class="px-5 py-4 border-b flex items-center justify-between"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2
            class="text-lg font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Ajuste de Stock
          </h2>
          <button
            class="text-xl leading-none hover:opacity-70 transition-opacity"
            :style="{ color: 'var(--sapContent_IconColor)' }"
            @click="cerrarModal"
          >
            ×
          </button>
        </div>

        <!-- Modal Body (Cozy Mode) -->
        <div class="p-5 flex-1 overflow-y-auto space-y-5">
          <!-- Message Strip Error -->
          <div
            v-if="modalError"
            class="p-3 border rounded-sm flex gap-3 text-sm"
            :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapErrorTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
          >
            <span class="sap-icon--message-error mt-0.5" />
            <span>{{ modalError }}</span>
          </div>

          <!-- Info Herramienta -->
          <div>
            <label
              class="block text-xs font-semibold uppercase tracking-wider mb-1"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Material Seleccionado</label>
            <div
              class="p-3 border rounded-sm"
              :style="{ background: 'var(--sapNeutralBackground)', borderColor: 'var(--sapList_BorderColor)' }"
            >
              <div class="font-mono text-sm font-semibold">
                {{ itemSeleccionado?.codigo_interno }}
              </div>
              <div class="text-sm mt-1 truncate">
                {{ itemSeleccionado?.nombre }}
              </div>
              <div
                class="text-xs mt-2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Disp actual: <strong :style="{ color: 'var(--sapTextColor)' }">{{ itemSeleccionado?.cant_disponible }}</strong>
              </div>
            </div>
          </div>

          <!-- Formularios -->
          <form
            id="form-ajuste"
            class="space-y-4"
            @submit.prevent="guardarAjuste"
          >
            <div>
              <label
                class="block text-sm mb-1 font-medium"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Tipo de Ajuste <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:
              </label>
              <select
                v-model="formAjuste.tipo_ajuste"
                required
                class="w-full h-10 px-3 text-sm border rounded-sm outline-none transition-colors"
                :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor)', borderColor: 'var(--sapField_BorderColor)' }"
              >
                <option value="INGRESO_COMPRA">
                  Ingreso por Compra
                </option>
                <option value="PASE_MALOGRADO">
                  Pase a Malogrado / Mantenimiento
                </option>
              </select>
            </div>

            <div>
              <label
                class="block text-sm mb-1 font-medium"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Cantidad <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:
              </label>
              <input
                v-model.number="formAjuste.cantidad"
                type="number"
                min="1"
                required
                class="w-full h-10 px-3 text-sm border rounded-sm outline-none transition-colors"
                :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor)', borderColor: 'var(--sapField_BorderColor)' }"
              >
            </div>

            <div>
              <label
                class="block text-sm mb-1 font-medium"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Motivo / Referencia (Trazabilidad) <span :style="{ color: 'var(--sapNegativeColor)' }">*</span>:
              </label>
              <textarea
                v-model="formAjuste.observaciones"
                required
                rows="3"
                placeholder="Ej. Factura #1234, o Se quemó motor..."
                class="w-full px-3 py-2 text-sm border rounded-sm outline-none transition-colors resize-y"
                :style="{ background: 'var(--sapField_Background)', color: 'var(--sapField_TextColor)', borderColor: 'var(--sapField_BorderColor)' }"
              />
            </div>
          </form>
        </div>

        <!-- Modal Footer -->
        <div
          class="px-5 py-3 border-t flex justify-end gap-3 bg-[var(--sapPageHeader_Background)]"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <button
            type="button"
            class="h-9 px-4 text-sm font-medium border rounded-sm transition-colors"
            :style="{ 
              background: 'transparent',
              color: 'var(--sapButton_TextColor)', 
              borderColor: 'var(--sapButton_BorderColor)'
            }"
            @click="cerrarModal"
          >
            Cancelar
          </button>
          <button
            type="submit"
            form="form-ajuste"
            class="h-9 px-4 text-sm font-semibold rounded-sm transition-opacity flex items-center gap-2"
            :style="{ 
              background: 'var(--sapButton_Emphasized_Background)', 
              color: 'var(--sapButton_Emphasized_TextColor)',
              borderColor: 'var(--sapButton_Emphasized_BorderColor)'
            }"
            :disabled="guardando"
          >
            <span
              v-if="guardando"
              class="sap-icon--refresh animate-spin"
            />
            Guardar Ajuste
          </button>
        </div>
      </div>
    </div>

    <!-- Message Toast Fiori (Bottom Center) -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-8 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-8 opacity-0"
    >
      <div
        v-if="toastExito"
        class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[60] px-6 py-3 rounded-md shadow-lg flex items-center justify-center text-sm font-medium"
        :style="{ background: '#32363a', color: '#ffffff' }"
      >
        {{ toastExito }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useInventarioStore } from '@/stores/inventario'

const inventarioStore = useInventarioStore()

const filtroTipo = ref('')
const soloConStock = ref(false)
const sinStock = ref(false)
const busquedaTexto = ref('')

// -- Modal State --
const modalAbierto = ref(false)
const modalError = ref(null)
const guardando = ref(false)
const itemSeleccionado = ref(null)
const toastExito = ref(null)

const formAjuste = ref({
  tipo_ajuste: 'INGRESO_COMPRA',
  cantidad: 1,
  observaciones: ''
})

onMounted(() => inventarioStore.fetchAll())

function abrirModal(item) {
  itemSeleccionado.value = item
  formAjuste.value = {
    tipo_ajuste: 'INGRESO_COMPRA',
    cantidad: 1,
    observaciones: ''
  }
  modalError.value = null
  modalAbierto.value = true
  nextTick(() => {
    // Focus in modal can be added here if needed
  })
}

function cerrarModal() {
  if (guardando.value) return
  modalAbierto.value = false
  itemSeleccionado.value = null
  formAjuste.value = {
    tipo_ajuste: 'INGRESO_COMPRA',
    cantidad: 1,
    observaciones: ''
  }
}

async function guardarAjuste() {
  if (!formAjuste.value.cantidad || formAjuste.value.cantidad < 1) {
    modalError.value = 'La cantidad debe ser mayor a 0.'
    return
  }
  if (!formAjuste.value.observaciones?.trim()) {
    modalError.value = 'El motivo/referencia es obligatorio para trazabilidad.'
    return
  }

  guardando.value = true
  modalError.value = null

  try {
    await inventarioStore.ajustarStock({
      catalogo_id: itemSeleccionado.value.id,
      ...formAjuste.value
    })
    
    // Liberar lock antes de cerrar para evitar el bug del modal zombie
    guardando.value = false
    cerrarModal()
    
    // Disparar Message Toast Fiori
    toastExito.value = 'Ajuste de stock guardado exitosamente'
    setTimeout(() => { toastExito.value = null }, 3000)
    
  } catch (e) {
    modalError.value = e.response?.data?.detail || e.message || 'Error al guardar el ajuste.'
    guardando.value = false
  }
}
</script>

