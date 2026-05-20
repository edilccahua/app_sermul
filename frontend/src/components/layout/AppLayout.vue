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
      <nav class="flex-1 py-4">
        <button
          v-for="item in navItems"
          :key="item.label"
          @click="activeNav = item.label"
          :class="[
            'w-full flex items-center gap-3 px-4 py-2 text-sm transition-colors',
            activeNav === item.label
              ? 'bg-accent text-accent-foreground'
              : 'hover:bg-accent/50',
          ]"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span v-if="sidebarOpen">{{ item.label }}</span>
        </button>
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

        <!-- Short Code Input -->
        <div class="flex-1 max-w-md">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              ref="shortCodeInput"
              v-model="shortCode"
              placeholder="Short code (ej: HER-001) - Enter para buscar"
              class="pl-9"
              @keyup.enter="handleShortCodeSearch"
              @focus="shortCodeInput?.select()"
            />
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
    <CheckOutSheet v-model:open="checkOutOpen" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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
  CubeIcon,
  CalendarIcon,
  UsersIcon,
  ShoppingCartIcon,
} from '@heroicons/vue/24/outline'
import CheckOutSheet from '@/components/almacen/CheckOutSheet.vue'

const router = useRouter()
const authStore = useAuthStore()

const sidebarOpen = ref(true)
const activeNav = ref('Dashboard')
const shortCode = ref('')
const shortCodeInput = ref(null)
const checkOutOpen = ref(false)

const navItems = [
  { label: 'Dashboard', icon: HomeIcon },
  { label: 'Pañol', icon: ArchiveBoxIcon },
  { label: 'Inventario', icon: CubeIcon },
  { label: 'Paradas', icon: CalendarIcon },
  { label: 'Grupos', icon: UsersIcon },
  { label: 'Reservas', icon: ShoppingCartIcon },
]

const userInitials = computed(() => {
  if (!authStore.usuario) return '?'
  return `${authStore.usuario.nombre[0]}${authStore.usuario.apellido[0]}`
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function handleShortCodeSearch() {
  if (shortCode.value.trim()) {
    checkOutOpen.value = true
  }
}

onMounted(() => {
  authStore.initAuth()
  nextTick(() => {
    shortCodeInput.value?.$el?.focus()
  })
})
</script>
