<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center gap-3">
      <span class="sap-icon--inventory w-7 h-7 flex items-center justify-center text-[var(--sapButton_Emphasized_Background)]" />
      <h1 class="text-xl font-bold">Stock de Materiales</h1>
      <span class="text-sm ml-auto" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ inventarioStore.items.length }} materiales</span>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3 flex-wrap items-center">
      <select v-model="filtroTipo" @change="inventarioStore.setFiltroTipo(filtroTipo)"
        class="h-9 rounded-sm border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
        <option value="">Todos los tipos</option>
        <option value="HERRAMIENTA_DEVOLUTIVA">Herramienta Devolutiva</option>
        <option value="EPP_DEVOLUTIVO">EPP Devolutivo</option>
        <option value="EPP_CONSUMIBLE">EPP Consumible</option>
        <option value="CONSUMIBLE">Consumible</option>
      </select>

      <label class="flex items-center gap-2 text-sm cursor-pointer" :style="{ color: 'var(--sapContent_LabelColor)' }">
        <input type="checkbox" v-model="soloConStock" @change="inventarioStore.setSoloConStock(soloConStock)" class="rounded-sm" />
        Solo con stock dispon.
      </label>

      <input v-model="busquedaTexto" @input="inventarioStore.setBusquedaTexto(busquedaTexto)"
        placeholder="Buscar por nombre o código..."
        class="flex h-9 w-full max-w-xs rounded-sm border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />

      <button @click="inventarioStore.fetchAll()"
        class="inline-flex items-center gap-1.5 text-sm text-[var(--sapButton_TextColor)] hover:bg-[var(--sapButton_Hover_Background)] h-8 px-2 transition-colors rounded-sm">
        <span :class="['sap-icon--refresh w-4 h-4 flex items-center justify-center', inventarioStore.loading && 'animate-spin']" />
        Actualizar
      </button>
    </div>

    <!-- Tabla Compact -->
    <div class="rounded-md border border-border overflow-hidden">
      <div v-if="inventarioStore.loading" class="p-8 text-center text-muted-foreground">
        <span class="sap-icon--refresh w-6 h-6 flex items-center justify-center mx-auto mb-2 animate-spin" />Cargando...
      </div>
      <table v-else class="w-full caption-bottom text-sm">
        <thead class="border-b border-border">
          <tr>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Código</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Nombre</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Categoría</th>
            <th class="h-8 px-2 text-center font-medium text-muted-foreground text-xs">Disponible</th>
            <th class="h-8 px-2 text-center font-medium text-muted-foreground text-xs">En Uso</th>
            <th class="h-8 px-2 text-center font-medium text-muted-foreground text-xs">Malogradas</th>
            <th class="h-8 px-2 text-center font-medium text-muted-foreground text-xs">Perdidas</th>
            <th class="h-8 px-2 text-center font-medium text-muted-foreground text-xs">Total</th>
          </tr>
        </thead>
        <tbody class="[&_tr:last-child]:border-0">
          <tr v-for="item in inventarioStore.itemsFiltrados" :key="item.id"
            class="cursor-default border-b border-border hover:bg-muted/20 transition-colors">
            <td class="px-2 py-1.5">
              <router-link :to="`/app/herramienta/${item.id}`"
                class="text-[var(--sapLinkColor)] hover:underline font-medium text-xs">
                {{ item.codigo_interno }}
              </router-link>
            </td>
            <td class="px-2 py-1.5">
              <router-link :to="`/app/herramienta/${item.id}`"
                class="text-[var(--sapLinkColor)] hover:underline text-sm">
                {{ item.nombre }}
              </router-link>
            </td>
            <td class="px-2 py-1.5 text-muted-foreground text-xs">{{ item.categoria?.nombre || '—' }}</td>
            <td class="px-2 py-1.5 text-center">
              <span class="text-sm font-semibold" :style="{ color: item.cant_disponible > 0 ? 'var(--sapPositiveTextColor)' : 'var(--sapContent_LabelColor)' }">
                {{ item.cant_disponible ?? 0 }}
              </span>
            </td>
            <td class="px-2 py-1.5 text-center">
              <span class="text-sm font-semibold" :style="{ color: 'var(--sapInformationTextColor)' }">{{ item.cant_en_uso ?? 0 }}</span>
            </td>
            <td class="px-2 py-1.5 text-center">
              <span class="text-sm font-semibold" :style="{ color: item.cant_malograda > 0 ? 'var(--sapNegativeTextColor)' : 'var(--sapContent_LabelColor)' }">{{ item.cant_malograda ?? 0 }}</span>
            </td>
            <td class="px-2 py-1.5 text-center">
              <span class="text-sm font-semibold" :style="{ color: item.cant_perdida > 0 ? 'var(--sapNeutralTextColor)' : 'var(--sapContent_LabelColor)' }">{{ item.cant_perdida ?? 0 }}</span>
            </td>
            <td class="px-2 py-1.5 text-center font-mono text-sm">
              {{ (item.cant_disponible ?? 0) + (item.cant_en_uso ?? 0) + (item.cant_malograda ?? 0) + (item.cant_perdida ?? 0) }}
            </td>
          </tr>
          <tr v-if="inventarioStore.itemsFiltrados.length === 0">
            <td colspan="8" class="px-3 py-6 text-center text-muted-foreground">Sin materiales con esos filtros</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useInventarioStore } from '@/stores/inventario'

const inventarioStore = useInventarioStore()

const filtroTipo = ref('')
const soloConStock = ref(false)
const busquedaTexto = ref('')

onMounted(() => inventarioStore.fetchAll())
</script>
