<template>
  <div
    class="p-6 space-y-4 h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══ Dynamic Page Header — List Report ══════════════════════════════════ -->
    <div class="flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--employee w-7 h-7 flex items-center justify-center text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Personal
          </h1>
          <p
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Gestión de trabajadores y roles
          </p>
        </div>
      </div>
      <!-- Global Actions -->
      <div class="flex gap-2">
        <button
          class="flex items-center gap-1.5 h-9 px-4 text-sm font-semibold rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
        >
          <span class="sap-icon--add text-sm" /> Registrar Trabajador
        </button>
      </div>
    </div>

    <!-- ══ Filter Bar ══════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-3 shrink-0">
      <div class="relative w-72">
        <span
          class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        />
        <input
          v-model="busqueda"
          placeholder="Buscar por DNI o nombre..."
          class="h-9 w-full pl-9 pr-3 text-sm border rounded-sm outline-none transition-colors"
          :style="{
            background: 'var(--sapField_Background)',
            color: 'var(--sapField_TextColor, var(--sapTextColor))',
            borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
          }"
        >
      </div>
    </div>

    <!-- ══ Table Toolbar ═══════════════════════════════════════════════════════ -->
    <div class="flex items-center justify-between shrink-0 mt-2">
      <span
        class="text-sm"
        :style="{ color: 'var(--sapContent_LabelColor)' }"
      >
        Trabajadores
        <span
          class="font-semibold"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          ({{ usuariosFiltrados.length }})
        </span>
      </span>
    </div>

    <!-- ══ Tabla (Compact Mode) ════════════════════════════════════════════════ -->
    <div
      class="border overflow-hidden rounded-sm flex-1 flex flex-col"
      :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
    >
      <div
        v-if="loading"
        class="py-12 text-center"
        :style="{ background: 'var(--sapGroup_ContentBackground)' }"
      >
        <span
          class="sap-icon--refresh animate-spin text-3xl block mb-3"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <p
          class="text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Cargando personal...
        </p>
      </div>
      
      <div v-else class="flex-1 overflow-auto">
        <table class="w-full text-sm">
          <thead class="sticky top-0 z-10">
            <tr
              :style="{
                background: 'var(--sapList_HeaderBackground)',
                borderBottom: '1px solid var(--sapList_BorderColor)',
              }"
            >
              <th
                class="h-8 px-3 text-left text-xs font-semibold"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                DNI
              </th>
              <th
                class="h-8 px-3 text-left text-xs font-semibold"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Nombre Completo
              </th>
              <th
                class="h-8 px-3 text-left text-xs font-semibold"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Rol
              </th>
              <th
                class="h-8 px-3 text-left text-xs font-semibold"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Especialidad
              </th>
              <th
                class="h-8 px-3 text-left text-xs font-semibold"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Teléfono
              </th>
            </tr>
          </thead>
          <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
            <tr
              v-for="u in usuariosFiltrados"
              :key="u.id"
              class="border-b transition-colors hover:bg-black/5"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
            >
              <td class="px-3 py-1.5 font-mono text-xs">
                <router-link
                  :to="`/app/personal/${u.id}`"
                  class="hover:underline transition-colors"
                  :style="{ color: 'var(--sapLinkColor)' }"
                >
                  {{ u.dni }}
                </router-link>
              </td>
              <td class="px-3 py-1.5 font-medium text-sm">
                <router-link
                  :to="`/app/personal/${u.id}`"
                  class="hover:underline transition-colors"
                  :style="{ color: 'var(--sapLinkColor)' }"
                >
                  {{ u.nombre }} {{ u.apellido }}
                </router-link>
              </td>
              <td
                class="px-3 py-1.5 text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ u.rol?.nombre || u.rol?.codigo }}
              </td>
              <td
                class="px-3 py-1.5 text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ u.especialidad?.nombre || '—' }}
              </td>
              <td
                class="px-3 py-1.5 text-xs font-mono"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ u.telefono || '—' }}
              </td>
            </tr>

            <tr v-if="!usuariosFiltrados.length">
              <td
                colspan="5"
                class="py-10 text-center"
              >
                <span
                  class="sap-icon--search text-3xl block mb-2"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                />
                <p
                  class="text-sm font-semibold"
                  :style="{ color: 'var(--sapTextColor)' }"
                >
                  Sin resultados
                </p>
                <p
                  class="text-xs"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  No se encontraron trabajadores con esa búsqueda.
                </p>
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
import { usuariosAPI } from '@/api'

const usuarios = ref([])
const busqueda = ref('')
const loading = ref(true)

const usuariosFiltrados = computed(() => {
  const q = busqueda.value.toUpperCase()
  if (!q) return usuarios.value
  return usuarios.value.filter(u =>
    u.dni.toUpperCase().includes(q) ||
    u.nombre.toUpperCase().includes(q) ||
    u.apellido.toUpperCase().includes(q)
  )
})

onMounted(async () => {
  try {
    const { data } = await usuariosAPI.get()
    usuarios.value = data
  } catch (e) {
    // error silencioso
  } finally {
    loading.value = false
  }
})
</script>
