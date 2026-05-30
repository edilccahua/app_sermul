<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Header Object Page -->
    <div
      class="px-6 py-4 shrink-0 border-b"
      :style="{ background: 'var(--sapObjectHeader_Background, var(--sapGroup_ContentBackground))', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-4 mb-2">
        <button
          v-if="route.params.id"
          class="w-8 h-8 flex items-center justify-center rounded-sm transition-colors mr-2 hover-sap-selection"
          :style="{ color: 'var(--sapContent_IconColor)' }"
          style="background:transparent"
          @click="router.back()"
        >
          <span class="sap-icon--nav-back text-lg" />
        </button>
        <Avatar
          class="w-14 h-14 shrink-0 border-2"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <AvatarFallback
            class="text-xl"
            :style="{ background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)' }"
          >
            {{ userInitials }}
          </AvatarFallback>
        </Avatar>
        <div class="flex-1 min-w-0">
          <h1
            class="text-2xl font-bold truncate"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            {{ usuarioInfo?.nombre }} {{ usuarioInfo?.apellido }}
          </h1>
          <div class="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-sm">
            <span
              class="flex items-center gap-1.5"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              <span class="sap-icon--employee" /> {{ usuarioInfo?.dni }}
            </span>
            <span
              class="flex items-center gap-1.5"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              <span class="sap-icon--role" /> {{ usuarioInfo?.rol?.nombre || authStore.rolCodigo }}
            </span>
            <span
              v-if="usuarioInfo?.activo !== undefined"
              class="flex items-center gap-1.5 font-medium px-2 py-0.5 rounded-sm border text-xs"
              :style="usuarioInfo.activo
                ? { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
                : { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
            >
              {{ usuarioInfo.activo ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
        </div>
        <!-- Solo botón cerrar sesión si es el propio perfil -->
        <button
          v-if="esPropioPerfil"
          class="inline-flex items-center gap-2 rounded-sm px-4 py-2 text-sm font-medium transition-colors shrink-0 border"
          :style="{ background: 'var(--sapButton_Reject_Background)', color: 'var(--sapButton_Reject_TextColor)', borderColor: 'var(--sapButton_Reject_BorderColor)' }"
          @click="handleLogout"
        >
          <span class="sap-icon--log w-4 h-4 flex items-center justify-center" />
          Cerrar Sesión
        </button>
      </div>
    </div>

    <!-- Body con Tabs -->
    <div class="flex-1 overflow-auto p-4 md:p-6">
      <div
        v-if="loading"
        class="py-10 text-center"
      >
        <span
          class="sap-icon--refresh animate-spin text-3xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
      </div>
      <div
        v-else-if="error"
        class="p-4 border rounded-sm"
        :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
      >
        <p :style="{ color: 'var(--sapNegativeTextColor)' }">
          {{ error }}
        </p>
      </div>
      <Tabs
        v-else
        default-value="info"
        class="w-full"
      >
        <TabsList
          class="mb-4 bg-transparent border-b rounded-none w-full justify-start h-auto p-0"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <TabsTrigger
            value="info"
            class="data-[state=active]:border-b-2 data-[state=active]:border-[var(--sapButton_Emphasized_Background)] rounded-none px-4 py-2 font-semibold text-sm transition-all"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Información
          </TabsTrigger>
          <TabsTrigger
            v-if="esPropioPerfil"
            value="seguridad"
            class="data-[state=active]:border-b-2 data-[state=active]:border-[var(--sapButton_Emphasized_Background)] rounded-none px-4 py-2 font-semibold text-sm transition-all"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Seguridad
          </TabsTrigger>
          <TabsTrigger
            value="grupos"
            class="data-[state=active]:border-b-2 data-[state=active]:border-[var(--sapButton_Emphasized_Background)] rounded-none px-4 py-2 font-semibold text-sm transition-all"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Historial de Grupos
          </TabsTrigger>
          <TabsTrigger
            value="paradas"
            class="data-[state=active]:border-b-2 data-[state=active]:border-[var(--sapButton_Emphasized_Background)] rounded-none px-4 py-2 font-semibold text-sm transition-all"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Participación en Paradas
          </TabsTrigger>
          <TabsTrigger
            value="herramientas"
            class="data-[state=active]:border-b-2 data-[state=active]:border-[var(--sapButton_Emphasized_Background)] rounded-none px-4 py-2 font-semibold text-sm transition-all"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            <span class="sap-icon--wrench mr-1" /> Herramientas Prestadas
          </TabsTrigger>
        </TabsList>

        <TabsContent
          value="info"
          class="mt-0 outline-none"
        >
          <div
            class="max-w-xl p-6 border rounded-sm shadow-[var(--sapContent_Shadow0)] space-y-4"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <div class="flex items-center gap-2 mb-4">
              <span
                class="sap-icon--hint text-lg"
                :style="{ color: 'var(--sapContent_IconColor)' }"
              />
              <h2
                class="text-base font-bold"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                Datos Personales
              </h2>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Nombres:</span>
              <span
                class="col-span-2 font-medium"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ usuarioInfo?.nombre }}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Apellidos:</span>
              <span
                class="col-span-2 font-medium"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ usuarioInfo?.apellido }}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Documento:</span>
              <span
                class="col-span-2 font-medium font-mono"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ usuarioInfo?.dni }}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Especialidad:</span>
              <span
                class="col-span-2 font-medium"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ usuarioInfo?.especialidad?.nombre || 'No asignada' }}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Teléfono:</span>
              <span
                class="col-span-2 font-medium"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ usuarioInfo?.telefono || '—' }}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm">
              <span :style="{ color: 'var(--sapContent_LabelColor)' }">Correo:</span>
              <span
                class="col-span-2 font-medium"
                :style="{ color: 'var(--sapTextColor)' }"
              >{{ usuarioInfo?.email || '—' }}</span>
            </div>
          </div>
        </TabsContent>

        <TabsContent
          v-if="esPropioPerfil"
          value="seguridad"
          class="mt-0 outline-none"
        >
          <div
            class="max-w-xl p-6 border rounded-sm shadow-[var(--sapContent_Shadow0)] space-y-4"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <div class="flex items-center gap-2 mb-4">
              <span
                class="sap-icon--shield text-lg"
                :style="{ color: 'var(--sapContent_IconColor)' }"
              />
              <h2
                class="text-base font-bold"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                Cambiar Contraseña
              </h2>
            </div>
            <form
              class="space-y-4"
              @submit.prevent="cambiarPassword"
            >
              <div
                v-if="errorPassword"
                class="p-3 border rounded-sm flex items-start gap-2 text-sm"
                :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)', color: 'var(--sapNegativeTextColor)' }"
              >
                <span class="sap-icon--message-error mt-0.5" />
                <span>{{ errorPassword }}</span>
              </div>
              <div>
                <label
                  class="text-sm block mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Nueva Contraseña</label>
                <input
                  v-model="form.new_password"
                  type="password"
                  required
                  minlength="6"
                  class="w-full h-10 px-3 text-sm border rounded-sm outline-none"
                  :style="fieldStyle"
                >
              </div>
              <div>
                <label
                  class="text-sm block mb-1"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >Confirmar Contraseña</label>
                <input
                  v-model="form.confirm_password"
                  type="password"
                  required
                  minlength="6"
                  class="w-full h-10 px-3 text-sm border rounded-sm outline-none"
                  :style="fieldStyle"
                >
              </div>
              <div class="pt-2 flex justify-end">
                <button
                  type="submit"
                  :disabled="guardando"
                  class="h-10 px-6 text-sm font-semibold rounded-sm transition-colors flex items-center gap-2"
                  :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
                >
                  <span
                    v-if="guardando"
                    class="sap-icon--refresh animate-spin"
                  />
                  Guardar Contraseña
                </button>
              </div>
            </form>
          </div>
        </TabsContent>

        <TabsContent
          value="grupos"
          class="mt-0 outline-none"
        >
          <div
            class="border rounded-sm overflow-hidden shadow-[var(--sapContent_Shadow0)]"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <table class="w-full text-sm text-left">
              <thead
                class="text-xs uppercase border-b"
                :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
              >
                <tr>
                  <th class="px-4 py-3 font-semibold">
                    Grupo
                  </th>
                  <th class="px-4 py-3 font-semibold">
                    Parada
                  </th>
                  <th class="px-4 py-3 font-semibold text-center">
                    Ingreso
                  </th>
                  <th class="px-4 py-3 font-semibold text-center">
                    Salida
                  </th>
                  <th class="px-4 py-3 font-semibold text-center">
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="g in usuarioInfo?.historial_grupos || []"
                  :key="g.grupo_id + g.fecha_ingreso"
                  class="border-b transition-colors hover:bg-muted/30 last:border-0"
                  :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                >
                  <td class="px-4 py-3">
                    <p class="font-semibold">
                      GRUPO {{ g.grupo_codigo }} — {{ g.grupo_nombre }}
                    </p>
                  </td>
                  <td class="px-4 py-3">
                    <p>{{ g.parada_nombre }}</p>
                    <code
                      class="text-[10px]"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >{{ g.parada_codigo }}</code>
                  </td>
                  <td class="px-4 py-3 text-center text-xs font-mono">
                    {{ formatDate(g.fecha_ingreso) }}
                  </td>
                  <td class="px-4 py-3 text-center text-xs font-mono">
                    {{ g.fecha_salida ? formatDate(g.fecha_salida) : '—' }}
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span
                      class="px-2 py-0.5 text-[10px] font-bold rounded-sm border"
                      :style="g.activo ? { background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' } : { background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)', borderColor: 'var(--sapNeutralBorderColor)' }"
                    >
                      {{ g.activo ? 'VIGENTE' : 'HISTÓRICO' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!usuarioInfo?.historial_grupos?.length">
                  <td
                    colspan="5"
                    class="px-4 py-8 text-center text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    No hay historial de grupos.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent
          value="paradas"
          class="mt-0 outline-none"
        >
          <div
            class="border rounded-sm overflow-hidden shadow-[var(--sapContent_Shadow0)]"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <table class="w-full text-sm text-left">
              <thead
                class="text-xs uppercase border-b"
                :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
              >
                <tr>
                  <th class="px-4 py-3 font-semibold">
                    Parada
                  </th>
                  <th class="px-4 py-3 font-semibold">
                    Grupo
                  </th>
                  <th class="px-4 py-3 font-semibold">
                    Líder
                  </th>
                  <th class="px-4 py-3 font-semibold text-center">
                    Fecha Ingreso
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in usuarioInfo?.historial_paradas || []"
                  :key="p.parada_id + p.fecha_ingreso"
                  class="border-b transition-colors hover:bg-muted/30 last:border-0"
                  :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                >
                  <td class="px-4 py-3">
                    <p class="font-semibold">
                      {{ p.parada_nombre }}
                    </p>
                    <code
                      class="text-[10px]"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >{{ p.parada_codigo }}</code>
                  </td>
                  <td class="px-4 py-3">
                    <p>GRUPO {{ p.grupo_codigo }} — {{ p.grupo_nombre }}</p>
                  </td>
                  <td class="px-4 py-3 text-xs">
                    {{ p.lider_nombre }}
                  </td>
                  <td class="px-4 py-3 text-center text-xs font-mono">
                    {{ formatDate(p.fecha_ingreso) }}
                  </td>
                </tr>
                <tr v-if="!usuarioInfo?.historial_paradas?.length">
                  <td
                    colspan="4"
                    class="px-4 py-8 text-center text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    No hay participación en paradas.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </TabsContent>
        <TabsContent
          value="herramientas"
          class="mt-0 outline-none"
        >
          <div
            class="border rounded-sm overflow-hidden shadow-[var(--sapContent_Shadow0)]"
            :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          >
            <table class="w-full text-sm text-left">
              <thead
                class="text-xs uppercase border-b"
                :style="{ background: 'var(--sapList_HeaderBackground)', color: 'var(--sapContent_LabelColor)', borderColor: 'var(--sapList_BorderColor)' }"
              >
                <tr>
                  <th class="px-4 py-3 font-semibold text-center">
                    Stock
                  </th>
                  <th class="px-4 py-3 font-semibold">
                    Código Interno
                  </th>
                  <th class="px-4 py-3 font-semibold">
                    Herramienta
                  </th>
                  <th class="px-4 py-3 font-semibold text-center">
                    Último Préstamo
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="h in herramientasPrestadas"
                  :key="h.catalogo_id"
                  class="border-b transition-colors hover:bg-muted/30 last:border-0"
                  :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                >
                  <td class="px-4 py-3 text-center">
                    <span
                      class="px-2 py-0.5 text-xs font-bold rounded-sm border"
                      :style="{ background: 'var(--sapInformationBackground)', color: 'var(--sapInformationTextColor)', borderColor: 'var(--sapInformationBorderColor)' }"
                    >
                      {{ h.cantidad_en_posesion }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <code
                      class="text-xs font-mono"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >{{ h.codigo_interno }}</code>
                  </td>
                  <td class="px-4 py-3">
                    <p class="font-semibold">
                      {{ h.nombre }}
                    </p>
                    <p
                      v-if="h.marca"
                      class="text-[10px]"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      {{ h.marca }}
                    </p>
                  </td>
                  <td class="px-4 py-3 text-center text-xs font-mono">
                    {{ formatDate(h.fecha_ultimo_prestamo) }}
                  </td>
                </tr>
                <tr v-if="!loadingHerramientas && herramientasPrestadas.length === 0">
                  <td
                    colspan="4"
                    class="py-16 text-center"
                  >
                    <div class="flex flex-col items-center justify-center">
                      <span
                        class="sap-icon--product text-4xl block mb-3"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      />
                      <p
                        class="text-sm"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      >
                        No tiene herramientas prestadas a título personal.
                      </p>
                    </div>
                  </td>
                </tr>
                <tr v-if="loadingHerramientas">
                  <td
                    colspan="4"
                    class="py-10 text-center"
                  >
                    <span
                      class="sap-icon--refresh animate-spin text-2xl"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usuariosAPI, prestamoPersonalAPI } from '@/api'
import { useToast } from '@/components/ui/toast'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { toast } = useToast()

const usuarioInfo = ref(null)
const loading = ref(true)
const error = ref(null)

const herramientasPrestadas = ref([])
const loadingHerramientas = ref(false)

const form = ref({ new_password: '', confirm_password: '' })
const guardando = ref(false)
const errorPassword = ref(null)

const esPropioPerfil = computed(() => {
  if (!route.params.id) return true
  return route.params.id === String(authStore.usuario?.id)
})

const userInitials = computed(() => {
  if (!usuarioInfo.value) return '?'
  return `${usuarioInfo.value.nombre?.[0] || ''}${usuarioInfo.value.apellido?.[0] || ''}`
})

const fieldStyle = {
  background: 'var(--sapField_Background)',
  color: 'var(--sapField_TextColor, var(--sapTextColor))',
  borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
}

function formatDate(isoStr) {
  if (!isoStr) return '—'
  return new Date(isoStr).toLocaleDateString('es-PE')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

async function cargarUsuario() {
  loading.value = true
  error.value = null
  try {
    const targetId = route.params.id || authStore.usuario?.id
    if (!targetId) throw new Error('ID de usuario no disponible')
    const { data } = await usuariosAPI.getById(targetId)
    usuarioInfo.value = data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error al cargar el perfil del usuario'
  } finally {
    loading.value = false
  }
}

async function cargarHerramientas(usuarioId) {
  loadingHerramientas.value = true
  try {
    const { data } = await prestamoPersonalAPI.herramientas(usuarioId)
    herramientasPrestadas.value = data || []
  } catch (err) {
    console.error("Error al cargar herramientas prestadas:", err)
  } finally {
    loadingHerramientas.value = false
  }
}

async function cambiarPassword() {
  errorPassword.value = null
  if (form.value.new_password !== form.value.confirm_password) {
    errorPassword.value = 'Las contraseñas no coinciden.'
    return
  }
  if (form.value.new_password.length < 6) {
    errorPassword.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }

  guardando.value = true
  try {
    await usuariosAPI.changePassword(authStore.usuario.id, form.value.new_password)
    toast({ title: 'Contraseña actualizada', description: 'Tu contraseña se ha cambiado correctamente.', variant: 'success' })
    form.value.new_password = ''
    form.value.confirm_password = ''
  } catch (err) {
    errorPassword.value = err.response?.data?.detail || 'Error al cambiar la contraseña. Intente nuevamente.'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await cargarUsuario()
  if (usuarioInfo.value) {
    await cargarHerramientas(usuarioInfo.value.id)
  }
})
</script>
