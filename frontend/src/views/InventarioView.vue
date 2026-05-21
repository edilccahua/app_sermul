<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center gap-3">
      <ClipboardDocumentListIcon class="w-7 h-7 text-primary" />
      <h1 class="text-2xl font-bold">Inventario Físico</h1>
      <span class="text-sm text-muted-foreground ml-auto">{{ inventarioStore.items.length }} unidades</span>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3 flex-wrap">
      <select v-model="filtroEstado" @change="inventarioStore.setFiltroEstado(filtroEstado)"
        class="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
        <option value="">Todos los estados</option>
        <option v-for="e in estados" :key="e" :value="e">{{ e.replace('_', ' ') }}</option>
      </select>
      <select v-model="filtroUbicacion" @change="inventarioStore.setFiltroUbicacion(filtroUbicacion)"
        class="h-9 rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
        <option value="">Todas las ubicaciones</option>
        <option value="Mina">Mina</option>
        <option value="Ciudad">Ciudad</option>
        <option value="Transito_Compra">Tránsito/Compra</option>
      </select>
      <button @click="inventarioStore.fetchAll()"
        class="inline-flex items-center gap-1.5 rounded-md border border-border px-3 h-9 text-sm hover:bg-muted transition-colors">
        <ArrowPathIcon :class="['w-4 h-4', inventarioStore.loading && 'animate-spin']" />
        Actualizar
      </button>
    </div>

    <!-- Tabla -->
    <div class="rounded-md border border-border overflow-hidden">
      <div v-if="inventarioStore.loading" class="p-8 text-center text-muted-foreground">
        <ArrowPathIcon class="w-6 h-6 mx-auto mb-2 animate-spin" />Cargando...
      </div>
      <table v-else class="w-full caption-bottom text-sm">
        <thead class="border-b border-border">
          <tr>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">ID</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Código / Nombre</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Estado</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Ubic. Física</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Macro</th>
            <th class="h-10 px-3 text-right font-medium text-muted-foreground">Costo</th>
            <th v-if="puedeEditar" class="h-10 px-3"></th>
          </tr>
        </thead>
        <tbody class="[&_tr:last-child]:border-0">
          <tr v-for="item in inventarioStore.itemsFiltrados" :key="item.id"
            class="border-b border-border hover:bg-muted/20 transition-colors">
            <td class="px-3 py-3 text-muted-foreground text-xs">#{{ item.id }}</td>
            <td class="px-3 py-3">
              <code class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{{ item.catalogo?.codigo_interno }}</code>
              <p class="text-sm font-medium mt-0.5">{{ item.catalogo?.nombre }}</p>
            </td>
            <td class="px-3 py-3">
              <span :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', badgeEstado(item.estado)]">
                {{ item.estado.replace('_', ' ') }}
              </span>
            </td>
            <td class="px-3 py-3 text-sm text-muted-foreground">{{ item.ubicacion_fisica || '—' }}</td>
            <td class="px-3 py-3">
              <span :class="['text-xs px-2 py-0.5 rounded-full', badgeUbicacion(item.ubicacion_macro)]">
                {{ item.ubicacion_macro }}
              </span>
            </td>
            <td class="px-3 py-3 text-right font-mono text-sm">
              {{ item.catalogo?.costo_reposicion ? `S/. ${item.catalogo.costo_reposicion.toFixed(2)}` : '—' }}
            </td>
            <td v-if="puedeEditar" class="px-3 py-3">
              <button @click="cambiarUbicacion(item)"
                class="text-xs text-muted-foreground hover:text-foreground underline">Ubicación</button>
            </td>
          </tr>
          <tr v-if="inventarioStore.itemsFiltrados.length === 0">
            <td colspan="7" class="px-3 py-8 text-center text-muted-foreground">Sin unidades con esos filtros</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal ubicación -->
    <div v-if="modalUbicacion" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="modalUbicacion = null" />
      <div class="relative z-10 bg-card border border-border rounded-xl shadow-2xl w-full max-w-sm mx-4 p-6">
        <h2 class="text-lg font-bold mb-4">Cambiar Ubicación Macro</h2>
        <p class="text-sm text-muted-foreground mb-3">{{ modalUbicacion.catalogo?.codigo_interno }} — {{ modalUbicacion.catalogo?.nombre }}</p>
        <select v-model="nuevaUbicacion"
          class="h-9 w-full rounded-md border border-input bg-background px-3 text-sm mb-4 focus:outline-none focus:ring-1 focus:ring-ring">
          <option value="Ciudad">Ciudad</option>
          <option value="Transito_Compra">Tránsito/Compra</option>
          <option value="Mina">Mina</option>
        </select>
        <div class="flex gap-3">
          <button @click="modalUbicacion = null"
            class="flex-1 rounded-md border border-border px-4 py-2 text-sm hover:bg-muted transition-colors min-h-[44px]">Cancelar</button>
          <button @click="confirmarUbicacion" :disabled="cambiando"
            class="flex-1 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 min-h-[44px]">
            {{ cambiando ? 'Guardando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useInventarioStore } from '@/stores/inventario'
import { useToast } from '@/components/ui/toast'
import { ClipboardDocumentListIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const inventarioStore = useInventarioStore()
const { toast } = useToast()

const filtroEstado = ref('')
const filtroUbicacion = ref('')
const modalUbicacion = ref(null)
const nuevaUbicacion = ref('Mina')
const cambiando = ref(false)

const estados = ['Disponible','En_Uso','Malograda','En_Mantenimiento','Perdida','Baja']
const puedeEditar = computed(() => ['RESIDENTE','ADMIN','ALMACENERO'].includes(authStore.rolCodigo))

function badgeEstado(estado) {
  const map = {
    Disponible: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
    En_Uso: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
    Malograda: 'bg-rose-500/15 text-rose-400 border border-rose-500/30',
    Perdida: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
    Baja: 'bg-slate-500/15 text-slate-400 border border-slate-500/30',
    En_Mantenimiento: 'bg-violet-500/15 text-violet-400 border border-violet-500/30',
  }
  return map[estado] || 'bg-muted text-muted-foreground'
}

function badgeUbicacion(ub) {
  return { Mina: 'bg-sky-500/15 text-sky-400', Ciudad: 'bg-slate-500/15 text-slate-400', Transito_Compra: 'bg-orange-500/15 text-orange-400' }[ub] || 'bg-muted text-muted-foreground'
}

function cambiarUbicacion(item) { modalUbicacion.value = item; nuevaUbicacion.value = item.ubicacion_macro }

async function confirmarUbicacion() {
  cambiando.value = true
  try {
    await inventarioStore.cambiarUbicacion(modalUbicacion.value.id, nuevaUbicacion.value)
    toast({ title: 'Ubicación actualizada', variant: 'success' })
    modalUbicacion.value = null
  } catch (err) {
    toast({ title: 'Error', description: err.response?.data?.detail, variant: 'error' })
  } finally { cambiando.value = false }
}

onMounted(() => inventarioStore.fetchAll())
</script>
