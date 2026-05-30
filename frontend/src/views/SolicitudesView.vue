<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Dynamic Page Header + Filter Bar -->
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background, var(--sapGroup_ContentBackground))', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3 mb-4">
        <span
          class="sap-icon--list text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Listas de solicitudes de Reserva de herramientas
          </h1>
          <p
            class="text-s"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Gestión de solicitudes de herramientas por parada
          </p>
        </div>
      </div>

      <!-- Filter Bar (Sin Estado) -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-2">
          <label
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >Parada:</label>
          <select
            v-model="filtros.parada_id"
            class="h-8 px-2 text-xs border rounded-sm outline-none"
            :style="fieldStyle"
          >
            <option value="">
              Todas
            </option>
            <option
              v-for="p in paradasStore.items"
              :key="p.id"
              :value="p.id"
            >
              {{ p.codigo }} - {{ p.nombre }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Table Toolbar -->
    <div
      class="flex items-center gap-3 px-6 py-2 border-b shrink-0"
      :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <span
        class="text-sm font-medium"
        :style="{ color: 'var(--sapTextColor)' }"
      >
        Solicitudes ({{ reservasStore.items.length }})
      </span>
      <router-link
        to="/app/almacen/solicitud-crear"
        class="ml-auto flex items-center gap-1.5 h-8 px-3 text-xs font-semibold rounded-sm transition-colors"
        :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }"
      >
        <span class="sap-icon--add-product" /> Nueva Solicitud
      </router-link>
    </div>

    <!-- Tabla -->
    <div class="flex-1 overflow-auto p-4 md:p-6">
      <div
        class="border rounded-sm overflow-hidden"
        :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
      >
        <table class="w-full text-sm text-left">
          <thead
            class="text-xs uppercase border-b"
            :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <tr>
              <th class="px-4 py-3 font-semibold">
                Código
              </th>
              <th class="px-4 py-3 font-semibold">
                Grupo
              </th>
              <th class="px-4 py-3 font-semibold">
                Parada
              </th>
              <th class="px-4 py-3 font-semibold text-center">
                Fecha y Turno
              </th>
              <th class="px-4 py-3 font-semibold text-center">
                Estado
              </th>
              <th class="px-4 py-3 font-semibold text-center">
                Ítems
              </th>
              <th class="px-4 py-3 font-semibold text-center">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="reservasStore.loading">
              <td
                colspan="7"
                class="px-4 py-12 text-center"
              >
                <span
                  class="sap-icon--refresh animate-spin text-3xl"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
              </td>
            </tr>
            <tr
              v-for="r in reservasStore.items"
              v-else
              :key="r.id"
              class="border-b transition-colors hover:bg-muted/20 last:border-0"
              :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
            >
              <td
                class="px-4 py-3 font-mono font-medium"
                :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
              >
                {{ r.codigo_reserva }}
              </td>
              <td class="px-4 py-3">
                {{ r.grupo?.nombre ?? '—' }}
              </td>
              <td
                class="px-4 py-3 text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ r.parada?.nombre ?? '—' }}
              </td>
              <td class="px-4 py-3 text-center text-xs">
                <div>{{ r.fecha_programada ? new Date(r.fecha_programada).toLocaleDateString('es-PE') : '—' }}</div>
                <div :style="{ color: 'var(--sapContent_LabelColor)' }">
                  {{ r.turno }}
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span
                  class="px-2 py-0.5 rounded-sm border text-[10px] font-bold uppercase"
                  :style="estadoBadgeStyle(r.estado)"
                >
                  {{ r.estado }}
                </span>
              </td>
              <td class="px-4 py-3 text-center font-semibold">
                {{ r.detalles?.length ?? '0' }}
              </td>
              <td class="px-4 py-3 text-center">
                <!-- Botón único Revisar -->
                <router-link
                  v-if="r.estado !== 'Cancelada' && r.estado !== 'Despachada'"
                  :to="`/app/almacen/despacho-masivo?parada_id=${r.parada_id || r.parada?.id}&grupo_id=${r.grupo_id || r.grupo?.id}`"
                  class="inline-flex items-center justify-center h-7 px-3 text-xs font-semibold rounded-sm transition-colors border hover-sap-button"
                  :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
                >
                  <span class="sap-icon--inspect mr-1" /> Revisar
                </router-link>
                <span
                  v-else
                  class="text-xs italic"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  {{ r.estado === 'Despachada' ? 'Completado' : 'Cancelado' }}
                </span>
              </td>
            </tr>
            <tr v-if="!reservasStore.loading && reservasStore.items.length === 0">
              <td
                colspan="7"
                class="px-4 py-12 text-center text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                No hay solicitudes para la parada seleccionada.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, watch } from 'vue'
import { useReservasStore } from '@/stores/reservas'
import { useParadasStore } from '@/stores/paradas'

const reservasStore = useReservasStore()
const paradasStore = useParadasStore()

const filtros = reactive({ parada_id: '' })

const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

function estadoBadgeStyle(estado) {
  const map = {
    Pendiente: { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
    Aprobada: { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' },
    Rechazada: { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' },
    Despachada: { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' },
    Cancelada: { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' },
  }
  return map[estado] || map.Pendiente
}

async function aplicarFiltros() {
  const params = {}
  if (filtros.parada_id) params.parada_id = filtros.parada_id
  await reservasStore.fetchAll(params)
}

watch(filtros, () => {
  aplicarFiltros()
}, { deep: true })

onMounted(async () => {
  await paradasStore.fetchAll()
  if (paradasStore.paradaActiva) {
    filtros.parada_id = paradasStore.paradaActiva.id
  } else if (paradasStore.items.length > 0) {
    filtros.parada_id = paradasStore.items[paradasStore.items.length - 1].id
  } else {
    await reservasStore.fetchAll()
  }
})
</script>

<style scoped>
select:focus {
  outline: 2px solid var(--sapField_Hover_BorderColor, var(--sapButton_Emphasized_Background));
  outline-offset: -1px;
}
</style>
