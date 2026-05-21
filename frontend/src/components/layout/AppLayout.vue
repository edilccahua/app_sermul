<template>
  <div class="min-h-screen bg-background flex">
    <!-- Sidebar -->
    <aside
      :class="[
        'bg-card border-r border-border flex flex-col transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-16',
      ]"
    >
      <!-- Logo -->
      <div class="h-14 flex items-center px-4 border-b border-border">
        <span v-if="sidebarOpen" class="font-bold text-lg">SERMUL APP</span>
        <span v-else class="font-bold text-lg mx-auto">S</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-4 flex flex-col gap-1">
        <!-- Almacén Check-OUT: acción especial, abre sheet -->
        <button
          @click="checkOutOpen = true"
          :class="[
            'w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors rounded-md mx-1',
            'hover:bg-accent/50 text-muted-foreground hover:text-foreground',
          ]"
        >
          <ArchiveBoxIcon class="w-5 h-5 flex-shrink-0" />
          <span v-if="sidebarOpen">Almacén — Salida</span>
        </button>

        <!-- Almacén Check-IN: devoluciones -->
        <button
          @click="checkInOpen = true"
          :class="[
            'w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors rounded-md mx-1',
            'hover:bg-accent/50 text-muted-foreground hover:text-foreground',
          ]"
        >
          <ArrowLeftOnRectangleIcon class="w-5 h-5 flex-shrink-0" />
          <span v-if="sidebarOpen">Almacén — Entrada</span>
        </button>

        <!-- Rutas de navegación -->
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-4 py-2 text-sm transition-colors rounded-md mx-1',
            route.path.startsWith(item.path)
              ? 'bg-primary/10 text-primary font-medium'
              : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground',
          ]"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span v-if="sidebarOpen">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- User -->
      <div class="border-t border-border p-4">
        <DropdownMenu>
          <DropdownMenuTrigger class="w-full flex items-center gap-3">
            <Avatar class="w-8 h-8">
              <AvatarFallback>{{ userInitials }}</AvatarFallback>
            </Avatar>
            <div v-if="sidebarOpen" class="text-left flex-1 min-w-0">
              <p class="text-sm font-medium truncate">{{ authStore.nombreCompleto }}</p>
              <p class="text-xs text-muted-foreground truncate">{{ authStore.rolCodigo }}</p>
            </div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Mi cuenta</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem @click="handleLogout">
              Cerrar sesión
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Topbar -->
      <header class="h-14 bg-card border-b border-border flex items-center px-4 gap-4">
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="p-2 hover:bg-accent rounded-md"
        >
          <Bars3Icon class="w-5 h-5" />
        </button>

        <!-- Short Code Input + Autocomplete -->
        <div class="flex-1 max-w-md relative">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              ref="shortCodeInput"
              v-model="shortCode"
              placeholder="Buscar por código o nombre..."
              class="pl-9"
              @keyup.enter="handleShortCodeSearch"
              @keydown.arrow-down.prevent="sugerenciaIndex = Math.min(sugerenciaIndex + 1, sugerenciasTopbar.length - 1)"
              @keydown.arrow-up.prevent="sugerenciaIndex = Math.max(sugerenciaIndex - 1, 0)"
              @keydown.escape="sugerenciasTopbar = []"
              @focus="onTopbarFocus"
              @blur="onTopbarBlur"
            />
          </div>
          <!-- Dropdown de sugerencias -->
          <div
            v-if="sugerenciasTopbar.length > 0 && shortCode.length >= 2"
            class="absolute top-full left-0 right-0 mt-1 z-50 bg-card border border-border rounded-md shadow-xl overflow-hidden"
          >
            <button
              v-for="(s, idx) in sugerenciasTopbar"
              :key="s.id"
              @mousedown.prevent="seleccionarSugerencia(s)"
              :class="[
                'w-full flex items-center gap-3 px-3 py-2 text-left text-sm transition-colors',
                idx === sugerenciaIndex
                  ? 'bg-primary/10'
                  : 'hover:bg-muted/30',
                idx < sugerenciasTopbar.length - 1 ? 'border-b border-border/50' : '',
              ]"
            >
              <code class="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">{{ s.codigo_interno }}</code>
              <span class="truncate">{{ s.nombre }}</span>
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="flex items-center gap-2">
          <Badge variant="outline" class="text-xs">
            {{ authStore.rolCodigo }}
          </Badge>
        </div>
      </header>

      <!-- Content Area -->
      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>

    <!-- CheckOut Sheet -->
    <CheckOutSheet v-model:open="checkOutOpen" v-model:initial-code="initialCode" />
    <!-- CheckIn Sheet -->
    <CheckInSheet v-model:open="checkInOpen" />
    <!-- Toaster global -->
    <Toaster />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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
import {
  Bars3Icon,
  MagnifyingGlassIcon,
  HomeIcon,
  ArchiveBoxIcon,
  ArrowLeftOnRectangleIcon,
  CubeIcon,
  ClipboardDocumentListIcon,
  CalendarIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'
import CheckOutSheet from '@/components/almacen/CheckOutSheet.vue'
import CheckInSheet from '@/components/almacen/CheckInSheet.vue'
import { Toaster } from '@/components/ui/toast'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarOpen = ref(true)
const shortCode = ref('')
const initialCode = ref('')
const shortCodeInput = ref(null)
const checkOutOpen = ref(false)
const checkInOpen = ref(false)

const sugerenciasTopbar = ref([])
const sugerenciaIndex = ref(0)
let debounceTopbar = null

// Rutas de navegación con router-link (Almacén es acción especial, no ruta)
const navItems = [
  { label: 'Dashboard', name: 'Dashboard', path: '/app/dashboard', icon: HomeIcon },
  { label: 'Catálogo', name: 'Catalogo', path: '/app/catalogo', icon: CubeIcon },
  { label: 'Inventario', name: 'Inventario', path: '/app/inventario', icon: ClipboardDocumentListIcon },
  { label: 'Paradas', name: 'Paradas', path: '/app/paradas', icon: CalendarIcon },
  { label: 'Historial', name: 'Historial', path: '/app/historial', icon: ClockIcon },
]

const userInitials = computed(() => {
  if (!authStore.usuario) return '?'
  return `${authStore.usuario.nombre[0]}${authStore.usuario.apellido[0]}`
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// ── Topbar: autocomplete con catálogo ──
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

function seleccionarSugerencia(s) {
  shortCode.value = s.codigo_interno
  sugerenciasTopbar.value = []
  initialCode.value = s.codigo_interno
  checkOutOpen.value = true
  shortCode.value = ''
}

function onTopbarFocus() {
  shortCodeInput.value?.$el?.select()
}

function onTopbarBlur() {
  setTimeout(() => { sugerenciasTopbar.value = [] }, 150)
}

function handleShortCodeSearch() {
  const code = shortCode.value.trim()
  if (code) {
    initialCode.value = code
    shortCode.value = ''
    checkOutOpen.value = true
    sugerenciasTopbar.value = []
  }
}

onMounted(() => {
  authStore.initAuth()
  nextTick(() => {
    shortCodeInput.value?.$el?.focus()
  })
})
</script>
