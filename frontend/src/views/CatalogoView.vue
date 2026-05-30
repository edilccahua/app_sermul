<template>
  <div
    class="p-6 space-y-4"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══ Dynamic Page Header — List Report ══════════════════════════════════ -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--inventory text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Catálogo de Materiales
          </h1>
          <p
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Gestión del inventario de herramientas y EPPs
          </p>
        </div>
      </div>
      <!-- Emphasized Button (ÚNICO): Nuevo Material → navega a /app/catalogo/crear -->
      <router-link
        v-if="puedeEditar"
        to="/app/catalogo/crear"
        class="inline-flex items-center gap-2 h-9 px-4 text-sm font-semibold rounded-sm transition-colors"
        :style="{
          background: 'var(--sapButton_Emphasized_Background)',
          color: 'var(--sapButton_Emphasized_TextColor)',
        }"
      >
        <span class="sap-icon--add text-sm" />
        Nuevo Material
      </router-link>
    </div>

    <!-- ══ Filter Bar ══════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-3">
      <!-- Búsqueda local -->
      <div class="relative max-w-sm flex-1">
        <span
          class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        />
        <input
          v-model="busqueda"
          type="text"
          placeholder="Buscar por nombre o código interno..."
          class="w-full h-9 pl-9 pr-3 text-sm border rounded-sm outline-none"
          :style="{
            background: 'var(--sapField_Background)',
            color: 'var(--sapField_TextColor, var(--sapTextColor))',
            borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
          }"
        >
      </div>

      <!-- Filtro por tipo -->
      <select
        v-model="filtroTipo"
        class="h-9 px-3 text-sm border rounded-sm outline-none"
        :style="{
          background: 'var(--sapField_Background)',
          color: 'var(--sapField_TextColor, var(--sapTextColor))',
          borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
        }"
      >
        <option value="">
          Todos los tipos
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

      <!-- Botón limpiar filtros -->
      <button
        v-if="busqueda || filtroTipo"
        class="h-9 px-3 text-xs border rounded-sm flex items-center gap-1.5 transition-colors"
        :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
        @click="busqueda = ''; filtroTipo = ''"
      >
        <span class="sap-icon--clear-filter text-xs" />
        Limpiar
      </button>
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
          ({{ itemsFiltrados.length }})
        </span>
        <span
          v-if="busqueda || filtroTipo"
          class="ml-2"
        >
          · Filtro activo
        </span>
      </span>
      <!-- Acciones principales -->
      <div class="flex items-center gap-2">
        <!-- Ghost button: actualizar -->
        <button
          class="flex items-center gap-1.5 h-8 px-3 text-xs transition-colors rounded-sm"
          :style="{ color: 'var(--sapButton_TextColor)' }"
          style="background:transparent"
          :disabled="catalogoStore.loading"
          @click="catalogoStore.fetchAll(true)"
        >
          <span :class="['sap-icon--refresh text-xs', catalogoStore.loading ? 'animate-spin' : '']" />
          Actualizar
        </button>
      </div>
    </div>

    <!-- ══ Tabla (Compact Mode) ════════════════════════════════════════════════ -->
    <div
      class="border overflow-hidden rounded-sm"
      :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
    >
      <!-- Loading state -->
      <div
        v-if="catalogoStore.loading && !catalogoStore.items.length"
        class="py-12 text-center"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
      >
        <span
          class="sap-icon--refresh text-3xl animate-spin block mb-3"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <p
          class="text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Cargando catálogo...
        </p>
      </div>

      <!-- Error state -->
      <div
        v-else-if="catalogoStore.error"
        class="py-8 text-center"
        :style="{ background: 'var(--sapErrorBackground)' }"
      >
        <span
          class="sap-icon--message-error text-2xl block mb-2"
          :style="{ color: 'var(--sapNegativeTextColor)' }"
        />
        <p
          class="text-sm"
          :style="{ color: 'var(--sapNegativeTextColor)' }"
        >
          {{ catalogoStore.error }}
        </p>
      </div>

      <table
        v-else
        class="w-full text-sm"
      >
        <!-- Encabezado (Compact: h-8) -->
        <thead>
          <tr
            :style="{
              background: 'var(--sapList_HeaderBackground)',
              borderBottom: '1px solid var(--sapList_BorderColor)',
            }"
          >
            <th 
              class="h-8 px-3 text-left text-xs font-semibold cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('codigo')"
            >
              <div class="flex items-center gap-1">
                Código Interno
                <span v-if="sortColumn === 'codigo'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left text-xs font-semibold cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('nombre')"
            >
              <div class="flex items-center gap-1">
                Nombre
                <span v-if="sortColumn === 'nombre'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left text-xs font-semibold hidden md:table-cell cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('tipo')"
            >
              <div class="flex items-center gap-1">
                Tipo
                <span v-if="sortColumn === 'tipo'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-left text-xs font-semibold hidden lg:table-cell cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('categoria')"
            >
              <div class="flex items-center gap-1">
                Categoría
                <span v-if="sortColumn === 'categoria'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-right text-xs font-semibold cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('costo')"
            >
              <div class="flex items-center justify-end gap-1">
                Costo (S/.)
                <span v-if="sortColumn === 'costo'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th 
              class="h-8 px-3 text-center text-xs font-semibold cursor-pointer select-none hover:bg-black/5 transition-colors group" 
              :style="{ color: 'var(--sapContent_LabelColor)' }"
              @click="toggleSort('stock')"
            >
              <div class="flex items-center justify-center gap-1">
                Stock
                <span v-if="sortColumn === 'stock'" :class="sortDesc ? 'sap-icon--sort-descending' : 'sap-icon--sort-ascending'" />
              </div>
            </th>
            <th
              v-if="puedeEditar"
              class="h-8 px-3 text-center text-xs font-semibold"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Acciones
            </th>
          </tr>
        </thead>

        <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
          <tr
            v-for="item in itemsFiltrados"
            :key="item.id"
            class="border-b transition-colors hover-sap-list"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          >
            <!-- ─ Código Interno — router-link al detalle (Corrección nav) ─ -->
            <td class="px-3 py-1.5">
              <router-link
                :to="{ name: 'HerramientaDetalle', params: { id: item.id } }"
                class="font-mono text-xs hover:underline transition-colors"
                :style="{ color: 'var(--sapLinkColor)' }"
                :title="`Ver detalle de ${item.codigo_interno}`"
              >
                {{ item.codigo_interno }}
              </router-link>
            </td>

            <!-- ─ Nombre — router-link al detalle ─────────────────────── -->
            <td class="px-3 py-1.5">
              <router-link
                :to="{ name: 'HerramientaDetalle', params: { id: item.id } }"
                class="font-medium text-sm transition-colors hover:underline"
                :style="{ color: 'var(--sapLinkColor)' }"
              >
                {{ item.nombre }}
              </router-link>
              <span
                v-if="item.marca"
                class="block text-[11px] mt-0.5"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >{{ item.marca }}<span v-if="item.modelo"> · {{ item.modelo }}</span></span>
            </td>

            <!-- ─ Tipo ────────────────────────────────────────────────── -->
            <td 
              class="px-3 py-1.5 text-xs hidden md:table-cell"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ tipoLabel(item.tipo_material) }}
            </td>

            <!-- ─ Categoría ───────────────────────────────────────────── -->
            <td
              class="px-3 py-1.5 text-xs hidden lg:table-cell"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              {{ item.categoria?.nombre || '—' }}
            </td>

            <!-- ─ Costo ───────────────────────────────────────────────── -->
            <td
              class="px-3 py-1.5 text-right font-mono text-sm"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              {{ item.costo_reposicion ? `S/ ${item.costo_reposicion.toFixed(2)}` : '—' }}
            </td>

            <!-- ─ Stock (Status Text) ───────────────────────────────── -->
            <td class="px-3 py-1.5 text-center">
              <span
                class="inline-flex items-center gap-1.5 text-xs font-semibold"
                :style="stockBadgeStyle(item)"
              >
                <span
                  :class="stockIcon(item)"
                  class="text-xs"
                />
                {{ stockLabel(item) }}
              </span>
            </td>

            <!-- ─ Acciones (Ghost buttons + Editar navega a form) ─────── -->
            <td
              v-if="puedeEditar"
              class="px-3 py-1.5 text-center"
            >
              <div class="flex items-center justify-center gap-1">
                <!-- Editar → navega a /app/catalogo/editar/:id -->
                <router-link
                  :to="{ name: 'CatalogoEditar', params: { id: item.id } }"
                  class="w-7 h-7 flex items-center justify-center rounded-sm transition-colors hover-sap-selection"
                  :style="{ color: 'var(--sapContent_IconColor)' }"
                  style="background:transparent"
                  title="Editar material"
                >
                  <span class="sap-icon--edit text-sm" />
                </router-link>
              </div>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="!catalogoStore.loading && itemsFiltrados.length === 0">
            <td
              :colspan="puedeEditar ? 7 : 6"
              class="py-10 text-center"
            >
              <span
                class="sap-icon--product text-3xl block mb-2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              />
              <p
                class="text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ busqueda || filtroTipo ? 'No se encontraron materiales con los filtros aplicados.' : 'El catálogo está vacío.' }}
              </p>
              <router-link
                v-if="puedeEditar && !busqueda && !filtroTipo"
                to="/app/catalogo/crear"
                class="inline-flex items-center gap-2 mt-3 h-9 px-4 text-sm rounded-sm"
                :style="{
                  background: 'var(--sapButton_Emphasized_Background)',
                  color: 'var(--sapButton_Emphasized_TextColor)',
                }"
              >
                <span class="sap-icon--add text-xs" />
                Crear primer material
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogoStore } from '@/stores/catalogo'

const authStore = useAuthStore()
const catalogoStore = useCatalogoStore()

// ── Estado ────────────────────────────────────────────────────────────────────
const busqueda = ref('')
const filtroTipo = ref('')
const sortColumn = ref('codigo')
const sortDesc = ref(false)

function toggleSort(col) {
  if (sortColumn.value === col) {
    sortDesc.value = !sortDesc.value
  } else {
    sortColumn.value = col
    sortDesc.value = !['codigo', 'nombre', 'tipo', 'categoria'].includes(col)
  }
}

// ── Permisos ──────────────────────────────────────────────────────────────────
const puedeEditar = computed(() =>
  ['RESIDENTE', 'ADMIN', 'ALMACENERO'].includes(authStore.rolCodigo)
)

// ── Datos filtrados ────────────────────────────────────────────────────────────
const itemsFiltrados = computed(() => {
  let items = catalogoStore.items

  if (filtroTipo.value) {
    items = items.filter((i) => i.tipo_material === filtroTipo.value)
  }

  if (busqueda.value.trim()) {
    const q = busqueda.value.toLowerCase().trim()
    items = items.filter(
      (i) =>
        i.nombre.toLowerCase().includes(q) ||
        i.codigo_interno.toLowerCase().includes(q) ||
        (i.marca ?? '').toLowerCase().includes(q),
    )
  }

  if (sortColumn.value) {
    items.sort((a, b) => {
      let valA = 0; let valB = 0;
      switch (sortColumn.value) {
        case 'codigo': valA = a.codigo_interno || ''; valB = b.codigo_interno || ''; break;
        case 'nombre': valA = a.nombre || ''; valB = b.nombre || ''; break;
        case 'tipo': valA = a.tipo_material || ''; valB = b.tipo_material || ''; break;
        case 'categoria': valA = a.categoria?.nombre || ''; valB = b.categoria?.nombre || ''; break;
        case 'costo': valA = a.costo_reposicion ?? 0; valB = b.costo_reposicion ?? 0; break;
        case 'stock': valA = a.cant_disponible ?? 0; valB = b.cant_disponible ?? 0; break;
      }
      if (typeof valA === 'string') {
        return sortDesc.value ? String(valB).localeCompare(String(valA)) : String(valA).localeCompare(String(valB));
      }
      if (valA > valB) return sortDesc.value ? -1 : 1;
      if (valA < valB) return sortDesc.value ? 1 : -1;
      return 0;
    })
  }

  return items
})

// ── Helpers de presentación ───────────────────────────────────────────────────
const TIPO_LABELS = {
  HERRAMIENTA_DEVOLUTIVA: 'Herr. Devol.',
  EPP_DEVOLUTIVO: 'EPP Dev.',
  EPP_CONSUMIBLE: 'EPP Cons.',
  CONSUMIBLE: 'Consumible',
}

function tipoLabel(tipo) {
  return TIPO_LABELS[tipo] ?? tipo
}

function stockBadgeStyle(item) {
  if (item.cant_disponible > 0) {
    return { color: 'var(--sapPositiveTextColor)' }
  }
  return { color: 'var(--sapNegativeTextColor)' }
}

function stockIcon(item) {
  if (item.cant_disponible > 0) return 'sap-icon--accept'
  return 'sap-icon--decline'
}

function stockLabel(item) {
  return `${item.cant_disponible} disp.`
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(() => catalogoStore.fetchAll())
</script>
