<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="sap-icon--calendar w-7 h-7 flex items-center justify-center text-[var(--sapButton_Emphasized_Background)]" />
        <h1 class="text-xl font-bold">Gestión de Paradas</h1>
      </div>
      <button v-if="puedeCrear" @click="abrirModal()"
        class="inline-flex items-center gap-2 rounded-sm border border-[var(--sapButton_BorderColor)] bg-[var(--sapButton_Background)] px-3 py-1.5 text-sm text-[var(--sapButton_TextColor)] hover:bg-[var(--sapButton_Hover_Background)] transition-colors">
        <span class="sap-icon--add w-4 h-4 flex items-center justify-center" />Nueva Parada
      </button>
    </div>

    <!-- Table Toolbar -->
    <div class="flex items-center justify-between text-sm text-[var(--sapContent_LabelColor)]">
      <span>Paradas ({{ paradasStore.items.length }})</span>
    </div>

    <div class="rounded-md border border-border overflow-hidden">
      <div v-if="paradasStore.loading" class="p-8 text-center text-muted-foreground">
        <span class="sap-icon--refresh w-6 h-6 flex items-center justify-center mx-auto mb-2 animate-spin" />Cargando paradas...
      </div>
      <table v-else class="w-full caption-bottom text-sm">
        <thead class="border-b border-border">
          <tr>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Código</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Nombre</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Inicio</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Fin</th>
            <th class="h-8 px-2 text-left font-medium text-muted-foreground text-xs">Estado</th>
            <th v-if="puedeCrear" class="h-8 px-2"></th>
          </tr>
        </thead>
        <tbody class="[&_tr:last-child]:border-0">
          <tr v-for="p in paradasStore.items" :key="p.id"
            class="border-b border-border hover:bg-muted/20 transition-colors">
            <td class="px-2 py-1.5">
              <code class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{{ p.codigo }}</code>
            </td>
            <td class="px-2 py-1.5 font-medium text-sm">{{ p.nombre }}</td>
            <td class="px-2 py-1.5 text-sm text-muted-foreground">{{ formatDate(p.fecha_inicio) }}</td>
            <td class="px-2 py-1.5 text-sm text-muted-foreground">{{ p.fecha_fin ? formatDate(p.fecha_fin) : '—' }}</td>
            <td class="px-2 py-1.5">
              <span :class="['inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', badgeEstado(p.estado)]">
                {{ p.estado }}
              </span>
            </td>
            <td v-if="puedeCrear" class="px-2 py-1.5">
              <button @click="abrirModal(p)"
                class="text-xs text-[var(--sapButton_TextColor)] hover:underline">Editar</button>
            </td>
          </tr>
          <tr v-if="paradasStore.items.length === 0">
            <td colspan="6" class="px-3 py-6 text-center text-muted-foreground">No hay paradas registradas</td>
          </tr>
        </tbody>
      </table>
    </div>


    <!-- Modal -->
    <div v-if="modalAbierto" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="cerrarModal" />
      <div class="relative z-10 bg-card border border-border shadow-[var(--sapContent_Shadow2)] w-full max-w-md mx-4 p-6">
        <h2 class="text-lg font-bold mb-4">{{ editando ? 'Editar Parada' : 'Nueva Parada' }}</h2>
        <form @submit.prevent="guardar" class="space-y-4">
          <div>
            <label class="text-sm font-medium block mb-1">Código *</label>
            <input v-model="form.codigo" required :disabled="!!editando"
              placeholder="ej: PAR-2026-002"
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring disabled:opacity-50" />
          </div>
          <div>
            <label class="text-sm font-medium block mb-1">Nombre *</label>
            <input v-model="form.nombre" required placeholder="ej: Mantenimiento Molino SAG"
              class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium block mb-1">Fecha Inicio *</label>
              <input v-model="form.fecha_inicio" type="date" required
                class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
            </div>
            <div>
              <label class="text-sm font-medium block mb-1">Fecha Fin</label>
              <input v-model="form.fecha_fin" type="date"
                class="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
            </div>
          </div>
          <div>
            <label class="text-sm font-medium block mb-1">Estado</label>
            <select v-model="form.estado"
              class="h-9 w-full rounded-md border border-input bg-background px-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring">
              <option value="Planificada">Planificada</option>
              <option value="Activa">Activa</option>
              <option value="Finalizada">Finalizada</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium block mb-1">Observaciones</label>
            <textarea v-model="form.observaciones" rows="2"
              class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring" />
          </div>
          <div class="flex gap-3 pt-2">
            <button type="button" @click="cerrarModal"
              class="flex-1 rounded-sm border border-[var(--sapButton_BorderColor)] bg-[var(--sapButton_Background)] px-4 py-2 text-sm text-[var(--sapButton_TextColor)] hover:bg-[var(--sapButton_Hover_Background)] transition-colors min-h-[44px]">Cancelar</button>
            <button type="submit" :disabled="guardando"
              class="flex-1 rounded-sm bg-[var(--sapButton_Emphasized_Background)] px-4 py-2 text-sm font-medium text-[var(--sapButton_Emphasized_TextColor)] hover:bg-[var(--sapButton_Emphasized_Hover_Background)] disabled:opacity-50 min-h-[44px]">
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
const form = ref({ codigo: '', nombre: '', fecha_inicio: '', fecha_fin: '', estado: 'Planificada', observaciones: '' })

const puedeCrear = computed(() => ['RESIDENTE', 'ADMIN'].includes(authStore.rolCodigo))

function badgeEstado(estado) {
  return {
    Planificada: 'bg-[var(--sapNeutralBackground)] text-[var(--sapNeutralTextColor)] border border-[var(--sapNeutralBorderColor)]',
    Activa: 'bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)] border border-[var(--sapSuccessBorderColor)]',
    Finalizada: 'bg-[var(--sapInformationBackground)] text-[var(--sapInformationTextColor)] border border-[var(--sapInformationBorderColor)]',
  }[estado] || 'bg-muted text-muted-foreground'
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' })
}

function abrirModal(p = null) {
  editando.value = p
  form.value = p
    ? { codigo: p.codigo, nombre: p.nombre, fecha_inicio: p.fecha_inicio?.split('T')[0] || '', fecha_fin: p.fecha_fin?.split('T')[0] || '', estado: p.estado, observaciones: p.observaciones || '' }
    : { codigo: '', nombre: '', fecha_inicio: '', fecha_fin: '', estado: 'Planificada', observaciones: '' }
  modalAbierto.value = true
}

function cerrarModal() { modalAbierto.value = false; editando.value = null }

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
