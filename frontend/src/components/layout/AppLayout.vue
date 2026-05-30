<template>
  <div
    class="h-screen flex overflow-hidden"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══════════════════════════════════════════════════════════════════════
         SIDEBAR — SAP Fiori Left Navigation
    ══════════════════════════════════════════════════════════════════════════ -->
    <aside
      :class="[
        'flex flex-col h-screen transition-all duration-300 border-r shrink-0',
        sidebarOpen ? 'w-64' : 'w-16',
      ]"
      :style="{
        background: 'var(--sapGroup_ContentBackground)',
        borderColor: 'var(--sapList_BorderColor)',
      }"
    >
      <!-- Logo / App Title -->
      <div
        class="h-16 flex items-center px-4 shrink-0 border-b"
        :style="{ borderColor: 'var(--sapList_BorderColor)' }"
      >
        <span
          v-if="sidebarOpen"
          class="font-bold text-lg tracking-widest flex items-baseline gap-1"
          style="color: var(--sapButton_Emphasized_Background); font-family: '72', sans-serif;"
        >
          LOGIST
          <span class="text-[10px] font-normal tracking-normal opacity-70" style="color: var(--sapContent_LabelColor);">v0.9 Beta</span>
        </span>
        <span
          v-else
          class="font-bold text-lg mx-auto"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        >S</span>
      </div>

      <!-- ── NAVEGACIÓN ─────────────────────────────────────────────────── -->
      <nav
        class="flex-1 py-2 flex flex-col overflow-y-auto"
        style="gap: 1px;"
      >
        <!-- ─ SECCIÓN: PRINCIPAL ─────────────────────────────────────────── -->
        <template v-if="puedeVerDashboard">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Principal
            </p>
          </div>
          <div
            v-else
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            to="/app/dashboard"
            icon="sap-icon--home"
            label="Dashboard"
            :active="route.path === '/app/dashboard'"
            :sidebar-open="sidebarOpen"
          />
        </template>

        <!-- ─ SECCIÓN: GRUPAL ────────────────────────────────────────────── -->
        <template v-if="puedeVerAlmacen">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Grupal
            </p>
          </div>
          <div
            v-else
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            to="/app/almacen/despacho-masivo"
            icon="sap-icon--shipping-status"
            label="Entregas"
            :active="route.path.startsWith('/app/almacen/despacho-masivo')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/almacen/devolucion-masiva"
            icon="sap-icon--response"
            label="Devoluciones"
            :active="route.path.startsWith('/app/almacen/devolucion-masiva')"
            :sidebar-open="sidebarOpen"
          />
        </template>

        <!-- ─ SECCIÓN: PLANIFICACIÓN ─────────────────────────────────────── -->
        <template v-if="puedeVerAlmacen">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Planificación
            </p>
          </div>
          <div
            v-else
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            to="/app/almacen/solicitudes"
            icon="sap-icon--list"
            label="Requerimientos"
            :active="route.path.startsWith('/app/almacen/solicitudes')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/almacen/solicitud-crear"
            icon="sap-icon--add-document"
            label="Nuevo Requerimiento"
            :active="route.path.startsWith('/app/almacen/solicitud-crear')"
            :sidebar-open="sidebarOpen"
          />
        </template>

        <!-- ─ SECCIÓN: INDIVIDUAL ────────────────────────────────────────── -->
        <template v-if="puedeVerAlmacen">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Individual
            </p>
          </div>
          <div
            v-else
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            to="/app/almacen/salida"
            icon="sap-icon--outbox"
            label="Préstamos"
            :active="route.path.startsWith('/app/almacen/salida')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/almacen/entrada"
            icon="sap-icon--inbox"
            label="Recepción"
            :active="route.path.startsWith('/app/almacen/entrada')"
            :sidebar-open="sidebarOpen"
          />
        </template>

        <!-- ─ SECCIÓN: INVENTARIO ────────────────────────────────────────── -->
        <template v-if="true">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Inventario
            </p>
          </div>
          <div
            v-if="!sidebarOpen"
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            v-if="puedeVerCatalogo"
            to="/app/catalogo"
            icon="sap-icon--inventory"
            label="Catálogo"
            :active="route.path.startsWith('/app/catalogo') || route.path.startsWith('/app/herramienta')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/stock"
            icon="sap-icon--product"
            label="Stock"
            :active="route.path.startsWith('/app/stock')"
            :sidebar-open="sidebarOpen"
          />
        </template>

        <!-- ─ SECCIÓN: GESTIÓN ───────────────────────────────────────────── -->
        <template v-if="puedeVerGestion">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Gestión
            </p>
          </div>
          <div
            v-else
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            to="/app/paradas"
            icon="sap-icon--factory"
            label="Paradas"
            :active="route.path.startsWith('/app/paradas')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/grupos"
            icon="sap-icon--group"
            label="Grupos"
            :active="route.path.startsWith('/app/grupos')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            v-if="puedeVerPersonal"
            to="/app/personal"
            icon="sap-icon--employee"
            label="Personal"
            :active="route.path.startsWith('/app/personal')"
            :sidebar-open="sidebarOpen"
          />
        </template>

        <!-- ─ SECCIÓN: AUDITORÍA ─────────────────────────────────────────── -->
        <template v-if="puedeVerHistorial">
          <div
            v-if="sidebarOpen"
            class="px-3 pt-3 pb-1"
          >
            <p
              class="text-[10px] font-semibold uppercase tracking-widest"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Auditoría
            </p>
          </div>
          <div
            v-else
            class="mx-3 my-2 border-t"
            :style="{ borderColor: 'var(--sapList_BorderColor)' }"
          />

          <NavLink
            to="/app/historial"
            icon="sap-icon--history"
            label="Historial"
            :active="route.path.startsWith('/app/historial')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/reportes"
            icon="sap-icon--bar-chart"
            label="Reportes"
            :active="route.path.startsWith('/app/reportes')"
            :sidebar-open="sidebarOpen"
          />
          <NavLink
            to="/app/about"
            icon="sap-icon--hint"
            label="Acerca de"
            :active="route.path.startsWith('/app/about')"
            :sidebar-open="sidebarOpen"
          />
        </template>
      </nav>
    </aside>

    <!-- ══════════════════════════════════════════════════════════════════════
         MAIN CONTENT AREA
    ══════════════════════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- ── TOPBAR — Fiori Shell Bar ──────────────────────────────────── -->
      <header
        class="h-16 flex items-center px-6 gap-3 shrink-0 border-b z-30"
        :style="{
          background: 'var(--sapShell_Background)',
          borderColor: 'var(--sapList_BorderColor)',
        }"
      >
        <!-- Hamburger -->
        <button
          class="w-10 h-10 flex items-center justify-center rounded-sm transition-colors hover-sap-shell"
          :style="{ color: 'var(--sapShell_TextColor)' }"
          style="background: transparent;"
          title="Menú lateral"
          @click="toggleSidebar"
        >
          <span class="sap-icon--menu2 text-lg" />
        </button>

        <!-- Búsqueda global -->
        <div class="flex-1 max-w-lg relative">
          <div class="relative">
            <span
              class="sap-icon--search absolute left-3 top-1/2 -translate-y-1/2 text-sm"
              :style="{ color: 'var(--sapShell_TextColor)', opacity: 0.6 }"
            />
            <input
              ref="shortCodeInput"
              v-model="shortCode"
              type="text"
              placeholder="Buscar herramienta por código o nombre..."
              class="w-full pl-9 pr-3 h-10 text-base rounded-sm border transition-colors focus:ring-1 focus:ring-[var(--sapButton_Emphasized_Background)] focus:ring-offset-0"
              :style="{
                background: 'var(--sapShell_SearchBackground)',
                borderColor: 'var(--sapShell_SearchBorderColor)',
                color: 'var(--sapShell_TextColor)',
              }"
              @keyup.enter="handleShortCodeSearch"
              @keydown.arrow-down.prevent="sugerenciaIndex = Math.min(sugerenciaIndex + 1, sugerenciasTopbar.length - 1)"
              @keydown.arrow-up.prevent="sugerenciaIndex = Math.max(sugerenciaIndex - 1, 0)"
              @keydown.escape="sugerenciasTopbar = []"
              @focus="onTopbarFocus"
              @blur="onTopbarBlur"
            >
          </div>
          <!-- Dropdown de sugerencias -->
          <div
            v-if="sugerenciasTopbar.length > 0 && shortCode.length >= 2"
            class="absolute top-full left-0 right-0 mt-1 z-50 border overflow-hidden"
            :style="{
              background: 'var(--sapGroup_ContentBackground)',
              borderColor: 'var(--sapList_BorderColor)',
              boxShadow: 'var(--sapContent_Shadow2)',
            }"
          >
            <button
              v-for="(s, idx) in sugerenciasTopbar"
              :key="s.id"
              :class="['w-full flex items-center gap-3 px-3 py-2 text-left text-sm transition-colors', idx < sugerenciasTopbar.length - 1 ? 'border-b' : '']"
              :style="{
                background: idx === sugerenciaIndex ? 'var(--sapList_SelectionBackgroundColor)' : 'transparent',
                color: 'var(--sapTextColor)',
                borderColor: 'var(--sapList_BorderColor)',
              }"
              @mouseenter="sugerenciaIndex = idx"
              @mouseleave="sugerenciaIndex = -1"
              @mousedown.prevent="seleccionarSugerencia(s)"
            >
              <code
                class="font-mono text-xs px-1.5 py-0.5 rounded-sm"
                :style="{ background: 'var(--sapNeutralBackground)', color: 'var(--sapNeutralTextColor)' }"
              >{{
                s.codigo_interno }}</code>
              <span class="truncate">{{ s.nombre }}</span>
              <span
                class="ml-auto text-xs shrink-0"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >Ver →</span>
            </button>
          </div>
        </div>

        <!-- ── Acciones derechas del Shell Bar ──────────────────────────── -->
        <div class="flex items-center gap-1 shrink-0 ml-auto">
          <!-- ─ Campana de notificaciones ─────────────────────────────── -->
          <div
            ref="campanaTrigger"
            class="relative"
          >
            <button
              class="relative w-10 h-10 flex items-center justify-center rounded-sm transition-colors hover-sap-shell"
              :style="{ background: 'transparent', color: 'var(--sapShell_TextColor)' }"
              title="Notificaciones"
              @click="toggleCampana"
            >
              <span class="sap-icon--bell text-lg" />
              <!-- Badge contador -->
              <span
                v-if="notif.tieneNoLeidas.value"
                class="absolute top-1 right-1 min-w-[16px] h-4 px-1 text-[10px] font-bold rounded-sm flex items-center justify-center leading-none"
                :style="{
                  background: 'var(--sapButton_Reject_Background)',
                  color: 'var(--sapButton_Reject_TextColor)',
                }"
              >{{ notif.cantidadNoLeidas.value > 9 ? '9+' : notif.cantidadNoLeidas.value }}</span>
            </button>

            <!-- Popover de notificaciones -->
            <Transition name="notif-popover">
              <div
                v-if="campanaAbierta"
                class="absolute right-0 top-full mt-2 w-80 border z-50 flex flex-col overflow-hidden"
                :style="{
                  background: 'var(--sapGroup_ContentBackground)',
                  borderColor: 'var(--sapList_BorderColor)',
                  boxShadow: 'var(--sapContent_Shadow2)',
                  maxHeight: '420px',
                }"
                @click.stop
              >
                <!-- Header del popover -->
                <div
                  class="flex items-center justify-between px-4 py-2.5 border-b shrink-0"
                  :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                >
                  <span
                    class="text-sm font-semibold"
                    :style="{ color: 'var(--sapTextColor)' }"
                  >
                    Notificaciones
                    <span
                      v-if="notif.tieneNoLeidas.value"
                      class="ml-1.5 text-xs font-normal"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >({{ notif.cantidadNoLeidas.value }} sin
                      leer)</span>
                  </span>
                  <button
                    v-if="notif.tieneNoLeidas.value"
                    class="text-xs transition-colors"
                    :style="{ color: 'var(--sapLinkColor)' }"
                    @click="notif.marcarTodasComoLeidas()"
                  >
                    Marcar todo leído
                  </button>
                </div>

                <!-- Lista de notificaciones -->
                <div class="overflow-y-auto flex-1">
                  <div
                    v-for="n in notif.notificaciones.value"
                    :key="n.id"
                    class="flex gap-3 px-4 py-3 border-b cursor-pointer transition-colors hover-sap-selection"
                    :style="{
                      background: n.leida ? 'transparent' : 'var(--sapInformationBackground)',
                      borderColor: 'var(--sapList_BorderColor)',
                    }"
                    @click="abrirNotificacion(n)"
                  >
                    <!-- Ícono de nivel -->
                    <span
                      :class="[notif.iconoPorNivel(n.nivel), 'text-base shrink-0 mt-0.5']"
                      :style="{ color: notif.estiloPorNivel(n.nivel).iconColor }"
                    />
                    <!-- Contenido -->
                    <div class="flex-1 min-w-0">
                      <p
                        class="text-sm font-semibold truncate"
                        :style="{ color: 'var(--sapTextColor)' }"
                      >
                        {{ n.titulo }}
                      </p>
                      <p
                        class="text-xs mt-0.5 leading-snug"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      >
                        {{ n.mensaje }}
                      </p>
                      <p
                        class="text-[10px] mt-1 font-mono"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                      >
                        {{ notif.tiempoRelativo(n.timestamp) }}
                      </p>
                    </div>
                    <!-- Punto no leída -->
                    <div
                      v-if="!n.leida"
                      class="w-2 h-2 rounded-full shrink-0 mt-1"
                      :style="{ background: 'var(--sapButton_Emphasized_Background)' }"
                    />
                  </div>
                  <!-- Estado vacío -->
                  <div
                    v-if="!notif.notificaciones.value.length"
                    class="py-8 text-center text-sm"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    <span class="sap-icon--message-information text-2xl block mb-2" />
                    Sin notificaciones
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- ─ Menú de usuario (DropdownMenu shadcn-vue) ──────────────── -->
          <DropdownMenu>
            <DropdownMenuTrigger
              class="flex items-center gap-2 px-2 py-1 rounded-sm transition-colors h-10 hover-sap-shell"
              :style="{ background: 'transparent', color: 'var(--sapShell_TextColor)' }"
            >
              <!-- Avatar -->
              <Avatar class="w-7 h-7 shrink-0 rounded-sm">
                <AvatarFallback
                  class="text-xs font-semibold rounded-sm"
                  :style="{
                    background: 'color-mix(in srgb, var(--sapShell_TextColor) 0%, transparent)',
                    color: 'var(--sapShell_TextColor)',
                  }"
                >
                  {{ userInitials }}
                </AvatarFallback>
              </Avatar>
              <!-- Nombre (solo en desktop) -->
              <span
                class="text-base font-medium hidden md:block max-w-[150px] truncate"
                :style="{ color: 'var(--sapShell_TextColor)' }"
              >{{ authStore.usuario?.nombre ?? 'Usuario' }}</span>
              <!-- Flecha -->
              <span
                class="sap-icon--slim-arrow-down text-sm"
                :style="{ color: 'var(--sapShell_TextColor)', opacity: 0.7 }"
              />
            </DropdownMenuTrigger>

            <DropdownMenuContent
              align="end"
              class="w-56"
            >
              <!-- Header con DNI y Rol -->
              <div
                class="px-3 py-2.5 border-b"
                :style="{ borderColor: 'var(--sapList_BorderColor)' }"
              >
                <p
                  class="text-sm font-semibold"
                  :style="{ color: 'var(--sapTextColor)' }"
                >
                  {{ authStore.nombreCompleto }}
                </p>
                <p
                  class="text-xs font-mono mt-0.5"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  DNI: {{ authStore.usuario?.dni ?? '—' }}
                </p>
                <span
                  class="inline-block text-[10px] font-semibold px-1.5 py-0.5 mt-1 rounded-sm"
                  :style="{
                    background: 'var(--sapInformationBackground)',
                    color: 'var(--sapInformationTextColor)',
                    border: '1px solid var(--sapInformationBorderColor)',
                  }"
                >{{ authStore.rolCodigo }}</span>
              </div>

              <!-- Mi Perfil -->
              <DropdownMenuItem
                class="gap-2 cursor-pointer"
                @click="router.push('/app/perfil')"
              >
                <span
                  class="sap-icon--employee text-sm"
                  :style="{ color: 'var(--sapContent_IconColor)' }"
                />
                Mi Perfil
              </DropdownMenuItem>

              <!-- Separador: Apariencia -->
              <DropdownMenuSeparator />
              <DropdownMenuLabel
                class="text-[10px] uppercase tracking-widest"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                Apariencia
              </DropdownMenuLabel>

              <!-- Radio group de tema -->
              <DropdownMenuRadioGroup
                :model-value="themeStore.mode"
                @update:model-value="themeStore.setMode($event)"
              >
                <DropdownMenuRadioItem
                  value="light"
                  class="gap-2 cursor-pointer"
                >
                  <span
                    class="sap-icon--light-mode text-sm"
                    :style="{ color: 'var(--sapContent_IconColor)' }"
                  />
                  Tema claro
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem
                  value="dark"
                  class="gap-2 cursor-pointer"
                >
                  <span
                    class="sap-icon--dark-mode text-sm"
                    :style="{ color: 'var(--sapContent_IconColor)' }"
                  />
                  Tema oscuro
                </DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>

              <!-- Separador: Cerrar sesión -->
              <DropdownMenuSeparator />
              <DropdownMenuItem
                class="gap-2 cursor-pointer"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
                @click="handleLogout"
              >
                <span
                  class="sap-icon--log text-sm"
                  :style="{ color: 'var(--sapNegativeColor)' }"
                />
                Cerrar Sesión
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <!-- ── CONTENT AREA ─────────────────────────────────────────────── -->
      <main
        class="flex-1 overflow-auto"
        :style="{ background: 'var(--sapBackgroundColor)' }"
      >
        <router-view />
      </main>
    </div>

    <!-- Toaster global (Toast de éxito/error) -->
    <Toaster />

    <!-- Overlay para cerrar campana al clickear fuera -->
    <div
      v-if="campanaAbierta"
      class="fixed inset-0 z-40"
      @click="campanaAbierta = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useNotificaciones } from '@/composables/useNotificaciones'
import { catalogoAPI } from '@/api'

// ── UI Components ────────────────────────────────────────────────────────────
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from '@/components/ui/dropdown-menu'
import { Toaster } from '@/components/ui/toast'

// ─────────────────────────────────────────────────────────────────────────────
// Subcomponente NavLink (definido inline para máxima cohesión del archivo)
// ─────────────────────────────────────────────────────────────────────────────
import { defineComponent, h, resolveComponent } from 'vue'

const NavLink = defineComponent({
  name: 'NavLink',
  props: {
    to: { type: String, required: true },
    icon: { type: String, required: true },
    label: { type: String, required: true },
    active: { type: Boolean, default: false },
    sidebarOpen: { type: Boolean, default: true },
    indent: { type: Boolean, default: false },
  },
  setup(props) {
    const RouterLink = resolveComponent('RouterLink')

    const activeStyle = {
      background: 'var(--sapList_SelectionBackgroundColor)',
      color: 'var(--sapButton_Emphasized_Background)',
    }
    const inactiveStyle = {
      background: 'transparent',
      color: 'var(--sapContent_LabelColor)',
    }

    return () =>
      h(
        RouterLink,
        {
          to: props.to,
          class: [
            'flex items-center gap-3 px-3 py-2 text-sm transition-colors mx-1 rounded-sm',
            props.indent ? 'pl-9' : '',
            props.active ? 'font-medium' : '',
          ],
          style: props.active ? activeStyle : inactiveStyle,
        },
        {
          default: () => [
            h('span', {
              class: [props.icon, 'w-5 h-5 flex items-center justify-center shrink-0', props.indent ? 'text-sm' : 'text-base'],
              style: { color: props.active ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_IconColor)' },
            }),
            props.sidebarOpen
              ? h('span', { class: 'truncate', style: { fontSize: props.indent ? '0.8125rem' : '0.875rem', fontFamily: '"72", sans-serif' } }, props.label)
              : null,
          ],
        }
      )
  },
})

// ─────────────────────────────────────────────────────────────────────────────
// Stores y composables
// ─────────────────────────────────────────────────────────────────────────────
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const notif = useNotificaciones()

// ─────────────────────────────────────────────────────────────────────────────
// Estado local
// ─────────────────────────────────────────────────────────────────────────────
const sidebarOpen = ref(true)
function toggleSidebar() { sidebarOpen.value = !sidebarOpen.value }
const shortCode = ref('')
const shortCodeInput = ref(null)
const sugerenciasTopbar = ref([])
const sugerenciaIndex = ref(0)
const campanaAbierta = ref(false)
let debounceTopbar = null

// ─────────────────────────────────────────────────────────────────────────────
// Computadas — Controles de Acceso por Rol (RBAC)
// ─────────────────────────────────────────────────────────────────────────────
const ROLES_GESTION = ['RESIDENTE', 'ADMIN', 'ALMACENERO']
const ROLES_DASHBOARD = ['RESIDENTE', 'ADMIN']

/** ALMACÉN: Salida, Entrada, Despacho Masivo, Devolución Masiva, Solicitudes */
const puedeVerAlmacen = computed(() =>
  ROLES_GESTION.includes(authStore.rolCodigo)
)

/** GESTIÓN: Personal, Grupos, Paradas */
const puedeVerGestion = computed(() =>
  ROLES_GESTION.includes(authStore.rolCodigo)
)

/** GENERAL: Dashboard ejecutivo */
const puedeVerDashboard = computed(() =>
  ROLES_DASHBOARD.includes(authStore.rolCodigo)
)

/** Catálogo: gestión de materiales */
const puedeVerCatalogo = computed(() =>
  ROLES_GESTION.includes(authStore.rolCodigo)
)

/** Historial y Reportes */
const puedeVerHistorial = computed(() =>
  ROLES_GESTION.includes(authStore.rolCodigo)
)

/** Personal: solo Residentes y Admin */
const PUEDEN_PERSONAL = ['RESIDENTE', 'ADMIN']
const puedeVerPersonal = computed(() =>
  PUEDEN_PERSONAL.includes(authStore.rolCodigo)
)

/** Iniciales para el Avatar */
const userInitials = computed(() => {
  if (!authStore.usuario) return '?'
  const n = authStore.usuario.nombre?.[0] ?? ''
  const a = authStore.usuario.apellido?.[0] ?? ''
  return `${n}${a}`.toUpperCase()
})

// ─────────────────────────────────────────────────────────────────────────────
// Campana de Notificaciones
// ─────────────────────────────────────────────────────────────────────────────
function toggleCampana() {
  campanaAbierta.value = !campanaAbierta.value
}

function abrirNotificacion(n) {
  notif.marcarComoLeida(n.id)
  campanaAbierta.value = false
  if (n.ruta) {
    router.push(n.ruta)
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Búsqueda global (topbar autocomplete)
// ─────────────────────────────────────────────────────────────────────────────
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
  shortCode.value = ''
  sugerenciasTopbar.value = []
  router.push({ name: 'HerramientaDetalle', params: { id: s.id } })
}

function handleShortCodeSearch() {
  const code = shortCode.value.trim()
  if (!code) return
  if (sugerenciasTopbar.value.length > 0) {
    seleccionarSugerencia(sugerenciasTopbar.value[sugerenciaIndex.value])
    return
  }
  catalogoAPI.search(code).then(({ data }) => {
    if (data.length > 0) seleccionarSugerencia(data[0])
  }).catch(() => { })
  shortCode.value = ''
}

function onTopbarFocus() {
  shortCodeInput.value?.select()
}

function onTopbarBlur() {
  setTimeout(() => { sugerenciasTopbar.value = [] }, 150)
}

// ─────────────────────────────────────────────────────────────────────────────
// Logout
// ─────────────────────────────────────────────────────────────────────────────
function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// ─────────────────────────────────────────────────────────────────────────────
// Lifecycle
// ─────────────────────────────────────────────────────────────────────────────
onMounted(() => {
  authStore.initAuth()
  themeStore.init()
  nextTick(() => {
    shortCodeInput.value?.focus()
  })
})
</script>

<style scoped>
/* ── Transición del popover de notificaciones ────────────────────────────── */
.notif-popover-enter-active,
.notif-popover-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.notif-popover-enter-from,
.notif-popover-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* ── Scroll personalizado (Fiori thin scrollbar) ─────────────────────────── */
nav::-webkit-scrollbar {
  width: 4px;
}

nav::-webkit-scrollbar-track {
  background: transparent;
}

nav::-webkit-scrollbar-thumb {
  background: var(--sapList_BorderColor);
  border-radius: 2px;
}
</style>
