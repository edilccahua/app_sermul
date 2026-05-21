<template>
  <div class="p-6 space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <CubeIcon class="w-7 h-7 text-primary" />
        <h1 class="text-2xl font-bold">Catálogo de Materiales</h1>
      </div>
      <button
        v-if="puedeEditar"
        @click="abrirFormulario()"
        class="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors min-h-[44px]"
      >
        <PlusIcon class="w-4 h-4" />
        Nuevo Material
      </button>
    </div>

    <!-- Buscador -->
    <div class="relative max-w-sm">
      <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
      <input
        v-model="busqueda"
        placeholder="Buscar por nombre o código..."
        class="flex h-9 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
      />
    </div>

    <!-- Tabla -->
    <div class="rounded-md border border-border overflow-hidden">
      <div v-if="catalogoStore.loading" class="p-8 text-center text-muted-foreground">
        <ArrowPathIcon class="w-6 h-6 mx-auto mb-2 animate-spin" />
        Cargando catálogo...
      </div>

      <table v-else class="w-full caption-bottom text-sm">
        <thead class="border-b border-border">
          <tr>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Código</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Nombre</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Categoría</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Tipo</th>
            <th class="h-10 px-3 text-left font-medium text-muted-foreground">Devolutivo</th>
            <th class="h-10 px-3 text-right font-medium text-muted-foreground">Costo (S/.)</th>
            <th v-if="puedeEditar" class="h-10 px-3 text-left font-medium text-muted-foreground">Acciones</th>
          </tr>
        </thead>
        <tbody class="[&_tr:last-child]:border-0">
          <tr
            v-for="item in itemsFiltrados"
            :key="item.id"
            class="border-b border-border hover:bg-muted/20 transition-colors"
          >
            <td class="px-3 py-3">
              <code class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{{ item.codigo_interno }}</code>
            </td>
            <td class="px-3 py-3 font-medium">{{ item.nombre }}</td>
            <td class="px-3 py-3 text-muted-foreground text-xs">{{ item.categoria?.nombre || '—' }}</td>
            <td class="px-3 py-3">
              <span :class="['inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', badgeTipo(item.tipo_material)]">
                {{ item.tipo_material }}
              </span>
            </td>
            <td class="px-3 py-3">
              <span :class="item.es_devolutivo ? 'text-emerald-400' : 'text-muted-foreground'">
                {{ item.es_devolutivo ? '✓ Sí' : '— No' }}
              </span>
            </td>
            <td class="px-3 py-3 text-right font-mono text-sm">
              {{ item.costo_reposicion ? `S/. ${item.costo_reposicion.toFixed(2)}` : '—' }}
            </td>
            <td v-if="puedeEditar" class="px-3 py-3">
              <button
                @click="abrirFormulario(item)"
                class="text-xs text-muted-foreground hover:text-foreground underline transition-colors"
              >Editar</button>
            </td>
          </tr>
          <tr v-if="itemsFiltrados.length === 0">
            <td :colspan="puedeEditar ? 7 : 6" class="px-3 py-8 text-center text-muted-foreground">
              No se encontraron materiales
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Crear/Editar -->
    <div v-if="modalAbierto" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="cerrarModal" />
      <div class="relative z-10 bg-card border border-border rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
        <h2 class="text-lg font-bold mb-4">
          {{ materialEditando ? 'Editar Material' : 'Nuevo Material' }}
        </h2>
        <form @submit.prevent="guardarMaterial" class="space-y-4">
          <div>
            <label class="text-sm font-medium block mb-1">Código Interno *</label>
            <input v-model="form.codigo_interno" required :disabled="!!materialEditando"
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring disabled:opacity-50" />
          </div>
          <div>
            <label class="text-sm font-medium block mb-1">Nombre *</label>
            <input v-model="form.nombre" required
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div>
            <label class="text-sm font-medium block mb-1">Tipo de Material *</label>
            <select v-model="form.tipo_material" required
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
              <option value="">Seleccionar...</option>
              <option value="Herramienta">Herramienta Devolutiva</option>
              <option value="EPP_Devolutivo">EPP Devolutivo</option>
              <option value="EPP_Consumible">EPP Consumible</option>
              <option value="Suministro">Suministro</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium block mb-1">Costo Reposición (S/.)</label>
            <input v-model.number="form.costo_reposicion" type="number" min="0" step="0.01"
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div class="flex items-center gap-2">
            <input v-model="form.es_devolutivo" type="checkbox" id="devolutivo" class="w-4 h-4 accent-primary" />
            <label for="devolutivo" class="text-sm font-medium">Es devolutivo</label>
          </div>
          <div class="flex gap-3 pt-2">
            <button type="button" @click="cerrarModal"
              class="flex-1 rounded-md border border-border px-4 py-2 text-sm hover:bg-muted transition-colors min-h-[44px]">
              Cancelar
            </button>
            <button type="submit" :disabled="guardando"
              class="flex-1 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors min-h-[44px]">
              {{ guardando ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCatalogoStore } from '@/stores/catalogo'
import { useToast } from '@/components/ui/toast'
import {
  CubeIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowPathIcon,
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const catalogoStore = useCatalogoStore()
const { toast } = useToast()

const busqueda = ref('')
const modalAbierto = ref(false)
const materialEditando = ref(null)
const guardando = ref(false)

const form = ref({
  codigo_interno: '',
  nombre: '',
  tipo_material: '',
  costo_reposicion: null,
  es_devolutivo: true,
  categoria_id: 1,
})

// Solo RESIDENTE, ADMIN, ALMACENERO pueden crear/editar
const puedeEditar = computed(() => {
  const roles = ['RESIDENTE', 'ADMIN', 'ALMACENERO']
  return roles.includes(authStore.rolCodigo)
})

const itemsFiltrados = computed(() => {
  if (!busqueda.value) return catalogoStore.items
  const q = busqueda.value.toLowerCase()
  return catalogoStore.items.filter(
    (i) =>
      i.nombre.toLowerCase().includes(q) ||
      i.codigo_interno.toLowerCase().includes(q),
  )
})

// Badge de color por tipo_material
function badgeTipo(tipo) {
  const map = {
    Herramienta: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
    EPP_Devolutivo: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
    EPP_Consumible: 'bg-teal-500/15 text-teal-400 border border-teal-500/30',
    Suministro: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  }
  return map[tipo] || 'bg-muted text-muted-foreground'
}

function abrirFormulario(material = null) {
  materialEditando.value = material
  if (material) {
    form.value = {
      codigo_interno: material.codigo_interno,
      nombre: material.nombre,
      tipo_material: material.tipo_material,
      costo_reposicion: material.costo_reposicion,
      es_devolutivo: material.es_devolutivo,
      categoria_id: material.categoria_id,
    }
  } else {
    form.value = { codigo_interno: '', nombre: '', tipo_material: '', costo_reposicion: null, es_devolutivo: true, categoria_id: 1 }
  }
  modalAbierto.value = true
}

function cerrarModal() {
  modalAbierto.value = false
  materialEditando.value = null
}

async function guardarMaterial() {
  guardando.value = true
  try {
    if (materialEditando.value) {
      await catalogoStore.updateMaterial(materialEditando.value.id, form.value)
      toast({ title: 'Material actualizado', variant: 'success' })
    } else {
      await catalogoStore.createMaterial(form.value)
      toast({ title: 'Material creado exitosamente', variant: 'success' })
    }
    cerrarModal()
  } catch (err) {
    toast({
      title: 'Error al guardar',
      description: err.response?.data?.detail || 'Intenta nuevamente',
      variant: 'error',
    })
  } finally {
    guardando.value = false
  }
}

// Auto-sugerir código al escribir nombre (solo en creación)
watch(() => form.value.nombre, (nuevo) => {
  if (materialEditando.value || !nuevo || form.value.codigo_interno) return
  const partes = nuevo.trim().split(/\s+/)
  if (partes.length >= 1 && partes[0].length >= 3) {
    const prefix = partes[0].slice(0, 3).toUpperCase()
    const existentes = catalogoStore.items.filter((i) =>
      i.codigo_interno.startsWith(prefix),
    )
    const num = existentes.length + 1
    form.value.codigo_interno = `${prefix}-${String(num).padStart(3, '0')}`
  }
})

onMounted(() => catalogoStore.fetchAll())
</script>
