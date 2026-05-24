<template>
  <div class="h-screen bg-background flex overflow-hidden">
    <!-- ═══════════════════════════ SIDEBAR ═══════════════════════════ -->
    <aside
      :class="[
        'bg-card border-r border-border flex flex-col h-screen transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-16',
      ]"
    >
      <!-- Logo -->
      <div class="h-14 flex items-center px-4 border-b border-border shrink-0">
        <span v-if="sidebarOpen" class="font-bold text-lg tracking-wide">SERMUL APP</span>
        <span v-else class="font-bold text-lg mx-auto">S</span>
      </div>

      <!-- Nav con secciones -->
      <nav class="flex-1 py-3 flex flex-col gap-0.5 overflow-y-auto">
        <!-- Dashboard -->
        <router-link to="/app/dashboard"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path === '/app/dashboard' ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path === '/app/dashboard' ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--home w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path === '/app/dashboard' ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Dashboard</span>
        </router-link>

        <!-- Materiales -->
        <p v-if="sidebarOpen" class="px-4 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-widest" :style="{ color: 'var(--sapContent_LabelColor)' }">Materiales</p>
        <div v-else class="mx-3 my-1 border-t border-border/60" />

        <router-link v-if="puedeEditarCatalogo" to="/app/catalogo"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path.startsWith('/app/catalogo') ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path.startsWith('/app/catalogo') ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--inventory w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path.startsWith('/app/catalogo') ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Catálogo</span>
        </router-link>

        <router-link to="/app/stock"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path.startsWith('/app/stock') ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path.startsWith('/app/stock') ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--product w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path.startsWith('/app/stock') ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Stock</span>
        </router-link>

        <!-- Almacén -->
        <p v-if="sidebarOpen" class="px-4 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-widest" :style="{ color: 'var(--sapContent_LabelColor)' }">Almacén</p>
        <div v-else class="mx-3 my-1 border-t border-border/60" />

        <router-link v-if="puedeVerAlmacen" to="/app/almacen/salida"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path.startsWith('/app/almacen/salida') ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path.startsWith('/app/almacen/salida') ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--outbox w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path.startsWith('/app/almacen/salida') ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Salida (Entrega)</span>
        </router-link>

        <router-link v-if="puedeVerAlmacen" to="/app/almacen/entrada"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path.startsWith('/app/almacen/entrada') ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path.startsWith('/app/almacen/entrada') ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--inbox w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path.startsWith('/app/almacen/entrada') ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Entrada (Devolución)</span>
        </router-link>

        <!-- Grupos -->
        <p v-if="sidebarOpen" class="px-4 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-widest" :style="{ color: 'var(--sapContent_LabelColor)' }">Grupos</p>
        <div v-else class="mx-3 my-1 border-t border-border/60" />

        <router-link v-if="puedeEditarCatalogo" to="/app/grupos"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path === '/app/grupos' ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path === '/app/grupos' ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--group w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path === '/app/grupos' ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Gestión</span>
        </router-link>

        <router-link v-if="puedeEditarCatalogo" to="/app/grupos/importar"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path === '/app/grupos/importar' ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path === '/app/grupos/importar' ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--excel-attachment w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path === '/app/grupos/importar' ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Importar Excel</span>
        </router-link>

        <!-- Reservas -->
        <p v-if="sidebarOpen" class="px-4 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-widest" :style="{ color: 'var(--sapContent_LabelColor)' }">Reservas</p>
        <div v-else class="mx-3 my-1 border-t border-border/60" />

        <router-link to="/app/reservas"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path === '/app/reservas' ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path === '/app/reservas' ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--list w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path === '/app/reservas' ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Lista</span>
        </router-link>

        <router-link to="/app/reservas/crear"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path === '/app/reservas/crear' ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path === '/app/reservas/crear' ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--add-product w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path === '/app/reservas/crear' ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Crear</span>
        </router-link>

        <router-link v-if="puedeAprobarReservas" to="/app/reservas/aprobar"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path === '/app/reservas/aprobar' ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path === '/app/reservas/aprobar' ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--approvals w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path === '/app/reservas/aprobar' ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Aprobar</span>
        </router-link>

        <!-- General -->
        <p v-if="sidebarOpen" class="px-4 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-widest" :style="{ color: 'var(--sapContent_LabelColor)' }">General</p>
        <div v-else class="mx-3 my-1 border-t border-border/60" />

        <router-link to="/app/paradas"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path.startsWith('/app/paradas') ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path.startsWith('/app/paradas') ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--pause w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path.startsWith('/app/paradas') ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Paradas</span>
        </router-link>

        <router-link to="/app/historial"
          class="flex items-center gap-3 px-4 py-2 text-sm transition-colors mx-1 rounded-sm"
          :class="route.path.startsWith('/app/historial') ? 'font-medium' : 'hover:bg-accent/50'"
          :style="route.path.startsWith('/app/historial') ? { background: 'var(--sapButton_Selected_Background, rgba(0,112,242,0.08))', color: 'var(--sapButton_Emphasized_Background)' } : { color: 'var(--sapContent_LabelColor)' }">
          <span class="sap-icon--history w-5 h-5 flex items-center justify-center shrink-0"
            :style="{ color: route.path.startsWith('/app/historial') ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' }" />
          <span v-if="sidebarOpen" class="truncate">Historial</span>
        </router-link>
      </nav>



      <!-- User -->
      <div class="border-t border-border p-4 shrink-0">
        <DropdownMenu>
          <DropdownMenuTrigger class="w-full flex items-center gap-3">
            <Avatar class="w-8 h-8 shrink-0">
              <AvatarFallback>{{ userInitials }}</AvatarFallback>
            </Avatar>
            <div v-if="sidebarOpen" class="text-left flex-1 min-w-0">
              <p class="text-sm font-medium truncate">{{ authStore.nombreCompleto }}</p>
              <p class="text-xs truncate" :style="{ color: 'var(--sapContent_LabelColor)' }">
                {{ authStore.rolCodigo }}
              </p>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Mi cuenta</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="handleLogout">Cerrar sesión</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>

    <!-- ═══════════════════════════ MAIN CONTENT ═══════════════════════════ -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Topbar -->
      <header class="h-14 bg-card border-b border-border flex items-center px-4 gap-4 shrink-0">
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="p-2 hover:bg-accent rounded-sm transition-colors"
        >
          <span
            class="sap-icon--menu2 w-5 h-5 flex items-center justify-center"
            :style="{ color: 'var(--sapContent_IconColor)' }"
          />
        </button>

        <!-- Búsqueda global → navega a HerramientaDetalle -->
        <div class="flex-1 max-w-md relative">
          <div class="relative">
            <span
              class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 flex items-center justify-center"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            />
            <Input
              ref="shortCodeInput"
              v-model="shortCode"
              placeholder="Buscar herramienta por código o nombre..."
              class="pl-9"
              @keyup.enter="handleShortCodeSearch"
              @keydown.arrow-down.prevent="sugerenciaIndex = Math.min(sugerenciaIndex + 1, sugerenciasTopbar.length - 1)"
              @keydown.arrow-up.prevent="sugerenciaIndex = Math.max(sugerenciaIndex - 1, 0)"
              @keydown.escape="sugerenciasTopbar = []"
              @focus="onTopbarFocus"
              @blur="onTopbarBlur"
            />
          </div>
          <!-- Dropdown de sugerencias — navega a HerramientaDetalle -->
          <div
            v-if="sugerenciasTopbar.length > 0 && shortCode.length >= 2"
            class="absolute top-full left-0 right-0 mt-1 z-50 bg-card border border-border overflow-hidden"
            :style="{ boxShadow: 'var(--sapContent_Shadow1)' }"
          >
            <button
              v-for="(s, idx) in sugerenciasTopbar"
              :key="s.id"
              @mousedown.prevent="seleccionarSugerencia(s)"
              :class="[
                'w-full flex items-center gap-3 px-3 py-2 text-left text-sm transition-colors',
                idx === sugerenciaIndex ? 'bg-primary/10' : 'hover:bg-muted/30',
                idx < sugerenciasTopbar.length - 1 ? 'border-b border-border/50' : '',
              ]"
            >
              <code
                class="font-mono text-xs px-1.5 py-0.5 rounded-sm bg-muted"
              >{{ s.codigo_interno }}</code>
              <span class="truncate">{{ s.nombre }}</span>
              <span
                class="ml-auto text-xs shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Ver detalle →</span>
            </button>
          </div>
        </div>

        <!-- Toggle de Tema y Rol badge -->
        <div class="flex items-center gap-2 shrink-0">
          <button
            @click="themeStore.toggle()"
            class="w-8 h-8 flex items-center justify-center rounded-sm hover:bg-accent/50 transition-colors"
            :title="themeStore.mode === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
          >
            <span
              :class="[
                themeStore.mode === 'dark' ? 'sap-icon--light-mode' : 'sap-icon--dark-mode',
                'w-4 h-4',
              ]"
              :style="{ color: 'var(--sapContent_IconColor)' }"
            />
          </button>
          <Badge variant="outline" class="text-xs">{{ authStore.rolCodigo }}</Badge>
        </div>
      </header>

      <!-- Content Area -->
      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>

    <!-- Toaster global -->
    <Toaster />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { catalogoAPI } from '@/api'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu'
import { Toaster } from '@/components/ui/toast'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const sidebarOpen = ref(true)
const shortCode = ref('')
const shortCodeInput = ref(null)

const puedeEditarCatalogo = computed(() =>
  ['RESIDENTE', 'ADMIN', 'ALMACENERO'].includes(authStore.rolCodigo)
)
const puedeAprobarReservas = computed(() =>
  ['RESIDENTE', 'ADMIN', 'ALMACENERO'].includes(authStore.rolCodigo)
)
const puedeVerAlmacen = computed(() =>
  ['RESIDENTE', 'ADMIN', 'ALMACENERO'].includes(authStore.rolCodigo)
)

const sugerenciasTopbar = ref([])
const sugerenciaIndex = ref(0)
let debounceTopbar = null

const userInitials = computed(() => {
  if (!authStore.usuario) return '?'
  return `${authStore.usuario.nombre[0]}${authStore.usuario.apellido[0]}`
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// ── Topbar: autocomplete → navega a HerramientaDetalle (FIX Sprint 2) ─────────
watch(shortCode, (val) => {
  clearTimeout(debounceTopbar)
  const q = val.trim()
  if (!q || q.length < 2) {
    sugerenciasTopbar.value = []
    sugerenciaIndex.value = 0
    return
  }
  debounceTopbar = setTimeout(async () => {
    try {
      const { data } = await catalogoAPI.search(q)
      sugerenciasTopbar.value = data.slice(0, 5)
      sugerenciaIndex.value = 0
    } catch {
      sugerenciasTopbar.value = []
    }
  }, 200)
})

// FIX: Ya no abre el Sheet — navega a la vista de detalle de la herramienta
function seleccionarSugerencia(s) {
  shortCode.value = ''
  sugerenciasTopbar.value = []
  router.push({ name: 'HerramientaDetalle', params: { id: s.id } })
}

function onTopbarFocus() {
  shortCodeInput.value?.$el?.select()
}

function onTopbarBlur() {
  setTimeout(() => { sugerenciasTopbar.value = [] }, 150)
}

function handleShortCodeSearch() {
  const code = shortCode.value.trim()
  if (!code) return
  // Si hay sugerencias y una está seleccionada → navegar a ella
  if (sugerenciasTopbar.value.length > 0) {
    seleccionarSugerencia(sugerenciasTopbar.value[sugerenciaIndex.value])
    return
  }
  // Si no, buscar en catálogo y navegar al primer resultado
  catalogoAPI.search(code).then(({ data }) => {
    if (data.length > 0) {
      seleccionarSugerencia(data[0])
    }
  }).catch(() => {})
  shortCode.value = ''
}

onMounted(() => {
  authStore.initAuth()
  nextTick(() => {
    shortCodeInput.value?.$el?.focus()
  })
})
</script>
