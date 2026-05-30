<template>
  <div class="p-6 space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <span class="sap-icon--group w-7 h-7 flex items-center justify-center text-[var(--sapButton_Emphasized_Background)]" />
      <h1 class="text-xl font-bold">
        Mi Grupo de Trabajo
      </h1>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="p-12 text-center text-[var(--sapContent_LabelColor)]"
    >
      <span class="sap-icon--refresh w-8 h-8 flex items-center justify-center mx-auto mb-3 animate-spin" />
      Cargando información del grupo...
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!grupo"
      class="bg-[var(--sapNeutralBackground)] border border-[var(--sapNeutralBorderColor)] text-[var(--sapNeutralTextColor)] p-6 rounded-sm flex items-center gap-4"
    >
      <span class="sap-icon--message-information text-3xl shrink-0" />
      <div>
        <h3 class="font-bold text-lg mb-1">
          No asignado
        </h3>
        <p class="text-sm">
          Actualmente no te encuentras asignado a ningún grupo de trabajo activo. Comunícate con tu supervisor.
        </p>
      </div>
    </div>

    <!-- Grupo Asignado -->
    <div
      v-else
      class="space-y-6"
    >
      <!-- Info General -->
      <div class="bg-card border border-border rounded-sm shadow-[var(--sapContent_Shadow0)]">
        <div class="bg-[var(--sapObjectHeader_Background)] p-6 rounded-t-sm border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div class="space-y-1">
            <h2 class="text-2xl font-bold">
              GRUPO {{ grupo.codigo }} — {{ grupo.nombre }}
            </h2>
            <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-[var(--sapContent_LabelColor)]">
              <span class="flex items-center gap-1.5">
                <span class="sap-icon--tag" />
                <code class="font-mono bg-muted px-1.5 py-0.5 rounded">{{ grupo.codigo }}</code>
              </span>
              <span class="flex items-center gap-1.5">
                <span class="sap-icon--factory" />
                <span class="font-medium text-[var(--sapTextColor)]">{{ grupo.parada ? grupo.parada.codigo + ' - ' + grupo.parada.nombre : '—' }}</span>
              </span>
            </div>
          </div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-[var(--sapSuccessBackground)] text-[var(--sapPositiveTextColor)] border border-[var(--sapSuccessBorderColor)] self-start md:self-center shrink-0">
            En Curso
          </span>
        </div>
        
        <div class="p-6">
          <div class="mb-2 text-sm text-[var(--sapContent_LabelColor)] font-medium">
            Descripción de la Tarea
          </div>
          <p class="text-[var(--sapTextColor)] text-sm whitespace-pre-wrap">
            {{ grupo.descripcion }}
          </p>
        </div>
      </div>

      <!-- Supervisores y Líder desde integrantes -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="(sup, idx) in supervisores"
          :key="idx"
          class="bg-card border border-border rounded-sm p-6 shadow-[var(--sapContent_Shadow0)]"
        >
          <div class="flex items-center gap-2 mb-4">
            <span class="sap-icon--lead text-[var(--sapContent_IconColor)] text-lg" />
            <h3 class="font-bold text-base">
              {{ sup.usuario.rol?.codigo === 'SUP_MEC' ? 'Supervisor de Operaciones' : 'Supervisor SSOMA' }}
            </h3>
          </div>
          <div class="flex items-center gap-4">
            <Avatar class="w-12 h-12 border border-[var(--sapList_BorderColor)]">
              <AvatarFallback class="bg-muted text-[var(--sapContent_LabelColor)]">
                {{ sup.usuario.nombre[0] }}{{ sup.usuario.apellido[0] }}
              </AvatarFallback>
            </Avatar>
            <div class="text-sm">
              <div class="font-bold text-[var(--sapTextColor)]">
                {{ sup.usuario.nombre }} {{ sup.usuario.apellido }}
              </div>
              <div class="text-[var(--sapContent_LabelColor)] flex gap-3 mt-1">
                <span class="font-mono text-xs">{{ sup.usuario.dni }}</span>
                <span>{{ sup.usuario.especialidad?.nombre || sup.usuario.rol?.codigo }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Líder -->
      <div
        v-if="lider"
        class="bg-card border border-border rounded-sm p-6 shadow-[var(--sapContent_Shadow0)]"
        :style="{ background: 'var(--sapInformationBackground)' }"
      >
        <div class="flex items-center gap-2 mb-4">
          <span
            class="sap-icon--manager text-lg"
            :style="{ color: 'var(--sapInformationTextColor)' }"
          />
          <h3
            class="font-bold text-base"
            :style="{ color: 'var(--sapInformationTextColor)' }"
          >
            Líder de Frente
          </h3>
        </div>
        <div class="flex items-center gap-4">
          <Avatar
            class="w-12 h-12 border"
            :style="{ borderColor: 'var(--sapInformationBorderColor)' }"
          >
            <AvatarFallback :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)' }">
              {{ lider.usuario.nombre[0] }}{{ lider.usuario.apellido[0] }}
            </AvatarFallback>
          </Avatar>
          <div class="text-sm">
            <div
              class="font-bold"
              :style="{ color: 'var(--sapInformationTextColor)' }"
            >
              {{ lider.usuario.nombre }} {{ lider.usuario.apellido }}
            </div>
            <div
              class="flex gap-3 mt-1"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              <span class="font-mono text-xs">{{ lider.usuario.dni }}</span>
              <span>{{ lider.usuario.especialidad?.nombre || lider.usuario.rol?.codigo }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Integrantes -->
      <div class="bg-card border border-border rounded-sm shadow-[var(--sapContent_Shadow0)] overflow-hidden">
        <div class="bg-[var(--sapPageHeader_Background)] border-b border-border p-4 flex items-center justify-between">
          <h3 class="font-bold text-sm">
            Compañeros de Grupo ({{ grupo.integrantes?.length || 0 }})
          </h3>
        </div>
        <table class="w-full text-sm">
          <thead class="bg-muted/30 border-b border-border">
            <tr>
              <th class="h-8 px-4 text-left font-medium text-[var(--sapContent_LabelColor)] text-xs w-24">
                DNI
              </th>
              <th class="h-8 px-4 text-left font-medium text-[var(--sapContent_LabelColor)] text-xs">
                Nombre Completo
              </th>
              <th class="h-8 px-4 text-left font-medium text-[var(--sapContent_LabelColor)] text-xs">
                Rol
              </th>
              <th class="h-8 px-4 text-left font-medium text-[var(--sapContent_LabelColor)] text-xs">
                Especialidad
              </th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr
              v-for="int in tecnicos"
              :key="int.id"
              class="border-b border-border hover:bg-muted/10 transition-colors"
            >
              <td class="px-4 py-2 text-xs font-mono text-[var(--sapContent_LabelColor)]">
                {{ int.usuario.dni }}
              </td>
              <td class="px-4 py-2 font-medium">
                {{ int.usuario.nombre }} {{ int.usuario.apellido }}
              </td>
              <td class="px-4 py-2">
                <span class="text-xs bg-muted px-2 py-0.5 rounded-sm text-[var(--sapContent_LabelColor)]">{{ int.usuario.rol?.codigo }}</span>
              </td>
              <td class="px-4 py-2 text-xs text-[var(--sapContent_LabelColor)]">
                {{ int.usuario.especialidad?.nombre || '—' }}
              </td>
            </tr>
            <tr v-if="!grupo.integrantes || grupo.integrantes.length === 0">
              <td
                colspan="5"
                class="px-4 py-8 text-center text-[var(--sapContent_LabelColor)]"
              >
                No hay integrantes adicionales registrados.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { gruposAPI } from '@/api'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useToast } from '@/components/ui/toast'

const authStore = useAuthStore()
const { toast } = useToast()

const grupo = ref(null)
const loading = ref(true)

const supervisores = computed(() =>
  grupo.value?.integrantes?.filter(i => ['SUP_MEC', 'SUP_SSOMA'].includes(i.usuario.rol?.codigo)) || []
)

const lider = computed(() =>
  grupo.value?.integrantes?.find(i => i.es_lider_frente) || null
)

const tecnicos = computed(() =>
  grupo.value?.integrantes?.filter(i => !['SUP_MEC', 'SUP_SSOMA'].includes(i.usuario.rol?.codigo) && !i.es_lider_frente) || []
)

async function fetchMiGrupo() {
  loading.value = true
  try {
    const { data } = await gruposAPI.get({ usuario_id: authStore.usuario.id })
    // Tomamos el primer grupo devuelto (suele haber 1 activo por parada)
    if (data && data.length > 0) {
      grupo.value = data[0]
    } else {
      grupo.value = null
    }
  } catch (err) {
    toast({ title: 'Error', description: 'No se pudo cargar la información del grupo.', variant: 'error' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMiGrupo()
})
</script>
