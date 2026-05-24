<template>
  <div class="h-full flex flex-col" :style="{ background: 'var(--sapBackgroundColor)' }">

    <!-- Object Page Header -->
    <div class="px-6 py-4 border-b shrink-0" :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }">
      <div class="flex items-center gap-3 mb-2">
        <button @click="$router.push('/app/reservas')" class="h-8 w-8 flex items-center justify-center rounded-sm hover:bg-muted/30"
          :style="{ color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--nav-back" />
        </button>
        <span class="sap-icon--outbox text-2xl" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
        <div v-if="reserva">
          <h1 class="text-xl font-bold" :style="{ color: 'var(--sapTextColor)' }">
            Despachar Reserva
            <code class="font-mono text-base ml-2" :style="{ color: 'var(--sapButton_Emphasized_Background)' }">{{ reserva.codigo }}</code>
          </h1>
          <p class="text-sm" :style="{ color: 'var(--sapContent_LabelColor)' }">
            {{ reserva.grupo?.nombre }} · {{ reserva.parada?.nombre }} · Turno {{ reserva.turno }}
          </p>
        </div>
        <div v-if="reserva" class="ml-auto">
          <span class="text-xs px-2 py-0.5 rounded-sm border font-medium" :style="estadoBadgeStyle(reserva.estado)">
            {{ reserva.estado }}
          </span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <span class="sap-icon--refresh animate-spin text-3xl" :style="{ color: 'var(--sapButton_Emphasized_Background)' }" />
    </div>

    <!-- Error -->
    <div v-else-if="errorCarga" class="flex-1 flex items-center justify-center p-6">
      <div class="p-6 rounded-sm border text-center" :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }">
        <p class="text-sm" :style="{ color: 'var(--sapNegativeTextColor)' }">{{ errorCarga }}</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="reserva" class="flex-1 overflow-y-auto p-6">
      <div class="max-w-3xl mx-auto space-y-4">

        <!-- Checklist de ítems -->
        <div class="rounded-sm border overflow-hidden" :style="{ borderColor: 'var(--sapList_BorderColor)' }">
          <!-- Header con checkbox "todos" -->
          <div class="flex items-center gap-3 px-4 py-2 border-b"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }">
            <input type="checkbox" :checked="todosSeleccionados" @change="toggleTodos" class="rounded-sm" />
            <span class="flex-1 text-xs font-semibold uppercase tracking-wide">Herramienta</span>
            <span class="w-24 text-xs font-semibold uppercase tracking-wide text-center">Solicitado</span>
            <span class="w-24 text-xs font-semibold uppercase tracking-wide text-center">Disponible</span>
          </div>

          <!-- Filas de ítems -->
          <div v-for="item in reserva.detalles ?? []" :key="item.id"
            class="flex items-center gap-3 px-4 py-3 border-b last:border-0 transition-colors"
            :class="{ 'opacity-40': item.cantidad_disponible === 0 }"
            :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'var(--sapGroup_ContentBackground)' }">
            <input
              type="checkbox"
              v-model="itemsSeleccionados"
              :value="item.id"
              :disabled="item.cantidad_disponible === 0"
              class="rounded-sm"
            />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium" :style="{ color: 'var(--sapTextColor)' }">{{ item.catalogo?.nombre }}</p>
              <code class="text-xs font-mono" :style="{ color: 'var(--sapContent_LabelColor)' }">{{ item.catalogo?.codigo_interno }}</code>
            </div>
            <span class="w-24 text-sm text-center" :style="{ color: 'var(--sapTextColor)' }">{{ item.cantidad }}</span>
            <span class="w-24 text-center">
              <span class="text-xs px-2 py-0.5 rounded-sm border font-medium"
                :style="item.cantidad_disponible > 0
                  ? { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
                  : { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }">
                {{ item.cantidad_disponible > 0 ? item.cantidad_disponible : 'Agotado' }}
              </span>
            </span>
          </div>

          <p v-if="!reserva.detalles?.length" class="text-xs text-center py-4" :style="{ color: 'var(--sapContent_LabelColor)' }">
            Esta reserva no tiene ítems.
          </p>
        </div>

        <!-- Resumen selección -->
        <div class="flex items-center gap-2 text-xs" :style="{ color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--accept" :style="{ color: 'var(--sapPositiveTextColor)' }" />
          {{ itemsSeleccionados.length }} de {{ reserva.detalles?.length ?? 0 }} ítems seleccionados para despachar
        </div>

        <!-- Error API -->
        <div v-if="errorApi" class="flex items-start gap-2 p-3 rounded-sm border"
          :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }">
          <span class="sap-icon--message-error shrink-0" :style="{ color: 'var(--sapNegativeTextColor)' }" />
          <p class="text-sm" :style="{ color: 'var(--sapNegativeTextColor)' }">{{ errorApi }}</p>
        </div>

        <!-- Acciones -->
        <div class="flex gap-3">
          <button @click="$router.push('/app/reservas')" class="flex-1 h-12 text-sm border rounded-sm"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }">
            Cancelar
          </button>
          <button @click="despachar" :disabled="itemsSeleccionados.length === 0 || despachando"
            class="flex-2 h-12 px-8 text-sm font-medium rounded-sm transition-colors"
            :style="itemsSeleccionados.length > 0 && !despachando
              ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }
              : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }">
            <span v-if="despachando" class="flex items-center gap-2"><span class="sap-icon--refresh animate-spin" /> Despachando...</span>
            <span v-else>✓ Despachar ({{ itemsSeleccionados.length }}) Ítems</span>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReservasStore } from '@/stores/reservas'
import { useSound } from '@/composables/useSound'
import { useToast } from '@/components/ui/toast'

const route = useRoute()
const router = useRouter()
const reservasStore = useReservasStore()
const { playSuccess, playError } = useSound()
const { toast } = useToast()

const reserva = ref(null)
const loading = ref(false)
const errorCarga = ref(null)
const despachando = ref(false)
const errorApi = ref(null)
const itemsSeleccionados = ref([])

const todosSeleccionados = computed(() => {
  const disponibles = (reserva.value?.detalles ?? []).filter((i) => i.cantidad_disponible > 0)
  return disponibles.length > 0 && itemsSeleccionados.value.length === disponibles.length
})

function toggleTodos() {
  if (todosSeleccionados.value) {
    itemsSeleccionados.value = []
  } else {
    itemsSeleccionados.value = (reserva.value?.detalles ?? [])
      .filter((i) => i.cantidad_disponible > 0)
      .map((i) => i.id)
  }
}

function estadoBadgeStyle(estado) {
  return {
    Pendiente:  { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
    Aprobada:   { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
    Despachada: { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' },
  }[estado] ?? {}
}

async function despachar() {
  if (!itemsSeleccionados.value.length || despachando.value) return
  despachando.value = true
  errorApi.value = null
  try {
    await reservasStore.despachar(reserva.value.id, itemsSeleccionados.value)
    playSuccess()
    toast({
      title: '✓ Reserva despachada',
      description: `${itemsSeleccionados.value.length} ítems entregados`,
      variant: 'success',
    })
    router.push('/app/reservas')
  } catch (err) {
    playError()
    errorApi.value = err.response?.data?.detail || 'Error al despachar'
  } finally {
    despachando.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    reserva.value = await reservasStore.fetchById(route.params.id)
    // Pre-seleccionar todos los ítems disponibles
    itemsSeleccionados.value = (reserva.value?.detalles ?? [])
      .filter((i) => i.cantidad_disponible > 0)
      .map((i) => i.id)
  } catch {
    errorCarga.value = 'No se pudo cargar la reserva.'
  } finally {
    loading.value = false
  }
})
</script>
