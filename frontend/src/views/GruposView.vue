<template>
  <div
    class="p-6 space-y-4"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══ Dynamic Page Header — List Report ══════════════════════════════════ -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--group w-7 h-7 flex items-center justify-center text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Grupos de Trabajo
          </h1>
          <p
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Gestión de grupos, integrantes y asignaciones por parada
          </p>
        </div>
      </div>
      <!-- Acciones Globales -->
      <div class="flex gap-2">
        <router-link
          to="/app/grupos/importar"
          class="flex items-center gap-1.5 h-9 px-4 text-sm rounded-sm transition-colors"
          :style="{ background: 'transparent', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)', border: '1px solid var(--sapButton_BorderColor)' }"
        >
          <span class="sap-icon--excel-attachment text-sm" /> Importar Excel
        </router-link>
        <button
          class="flex items-center gap-1.5 h-9 px-4 text-sm font-semibold rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
          @click="abrirCrear"
        >
          <span class="sap-icon--add text-sm" /> Crear Grupo
        </button>
      </div>
    </div>

    <!-- ══ Filter Bar ══════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <label
          class="text-xs font-normal"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >Parada:</label>
        <select
          v-model="filtroParadaId"
          class="h-9 px-3 text-sm border rounded-sm outline-none"
          :style="{
            background: 'var(--sapField_Background)',
            color: 'var(--sapField_TextColor, var(--sapTextColor))',
            borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
          }"
        >
          <option :value="null">
            Todas las paradas
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

    <!-- ══ Table Toolbar ═══════════════════════════════════════════════════════ -->
    <div class="flex items-center justify-between">
      <span
        class="text-sm"
        :style="{ color: 'var(--sapContent_LabelColor)' }"
      >
        Grupos
        <span
          class="font-semibold"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          ({{ gruposStore.items.length }})
        </span>
      </span>
    </div>

    <!-- ══ Tabla (Compact Mode) ════════════════════════════════════════════════ -->
    <div
      class="border overflow-hidden rounded-sm"
      :style="{ borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow0)' }"
    >
      <div
        v-if="gruposStore.loading"
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
          Cargando grupos...
        </p>
      </div>
      <table
        v-else
        class="w-full caption-bottom text-sm"
      >
        <thead :style="{ background: 'var(--sapList_HeaderBackground)', borderBottom: '1px solid var(--sapList_BorderColor)' }">
          <tr>
            <th
              class="h-8 px-3 text-left font-semibold text-xs select-none"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Código
            </th>
            <th
              class="h-8 px-3 text-left font-semibold text-xs select-none"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Nombre
            </th>
            <th
              class="h-8 px-3 text-left font-semibold text-xs select-none"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Parada
            </th>
            <th
              class="h-8 px-3 text-left font-semibold text-xs select-none"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Circuito / Área
            </th>
            <th
              class="h-8 px-3 text-right font-semibold text-xs select-none"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >
              Acciones
            </th>
          </tr>
        </thead>
        <tbody :style="{ background: 'var(--sapGroup_ContentBackground)' }">
          <template
            v-for="grupo in gruposStore.items"
            :key="grupo.id"
          >
            <!-- Fila principal -->
            <tr
              class="cursor-pointer border-b transition-colors hover-sap-list"
              :style="{ borderColor: 'var(--sapList_BorderColor)' }"
              @click="toggleExpand(grupo.id)"
            >
              <td class="px-3 py-1.5 font-mono text-xs">
                <router-link
                  :to="`/app/grupos/${grupo.id}`"
                  class="hover:underline transition-colors"
                  :style="{ color: 'var(--sapLinkColor)' }"
                  @click.stop
                >
                  {{ grupo.codigo }}
                </router-link>
              </td>
              <td class="px-3 py-1.5 font-medium text-sm">
                <router-link
                  :to="`/app/grupos/${grupo.id}`"
                  class="hover:underline transition-colors"
                  :style="{ color: 'var(--sapLinkColor)' }"
                  @click.stop
                >
                  GRUPO {{ grupo.codigo }} — {{ grupo.nombre }}
                </router-link>
              </td>
              <td
                class="px-3 py-1.5 text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ grupo.parada?.nombre ?? '—' }}
              </td>
              <td
                class="px-3 py-1.5 text-xs"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ grupo.circuito_area || '—' }}
              </td>
              <td class="px-3 py-1.5 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    class="w-7 h-7 flex items-center justify-center rounded-sm transition-colors hover-sap-selection"
                    :style="{ color: 'var(--sapContent_IconColor)' }"
                    style="background:transparent"
                    title="Editar grupo"
                    @click.stop="abrirEditar(grupo)"
                  >
                    <span class="sap-icon--edit text-sm" />
                  </button>
                  <button
                    class="w-7 h-7 flex items-center justify-center rounded-sm transition-colors hover-sap-selection"
                    :style="{ color: 'var(--sapContent_IconColor)' }"
                    style="background:transparent"
                  >
                    <span
                      :class="expandido === grupo.id ? 'sap-icon--chevron-up' : 'sap-icon--chevron-down'"
                      class="text-sm"
                    />
                  </button>
                </div>
              </td>
            </tr>
            <!-- Fila expandida: integrantes -->
            <tr
              v-if="expandido === grupo.id"
              :key="'exp-' + grupo.id"
            >
              <td
                colspan="6"
                class="px-8 py-4 border-b"
                :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapList_BorderColor)' }"
              >
                <div
                  v-if="loadingIntegrantes"
                  class="text-xs flex items-center gap-2"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  <span class="sap-icon--refresh animate-spin" /> Cargando integrantes...
                </div>
                <div v-else>
                  <div class="flex items-center gap-2 mb-2">
                    <p
                      class="text-xs font-semibold"
                      :style="{ color: 'var(--sapTextColor)' }"
                    >
                      Integrantes ({{ grupoDetalle?.integrantes?.length ?? 0 }})
                    </p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-for="int in grupoDetalle?.integrantes ?? []"
                      :key="int.id"
                      class="inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-sm border"
                      :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                    >
                      <span class="sap-icon--employee text-xs" />
                      {{ int.usuario?.nombre }} {{ int.usuario?.apellido }}
                      <button
                        class="ml-1 hover:text-[var(--sapNegativeTextColor)] transition-colors"
                        :style="{ color: 'var(--sapContent_LabelColor)' }"
                        @click="solicitarQuitarIntegrante(grupo.id, int)"
                      >
                        <span class="sap-icon--decline text-xs" />
                      </button>
                    </span>
                    <p
                      v-if="!grupoDetalle?.integrantes?.length"
                      class="text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >
                      Sin integrantes aún.
                    </p>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          
          <tr v-if="!gruposStore.loading && !gruposStore.items.length">
            <td
              colspan="5"
              class="py-10 text-center"
            >
              <span
                class="sap-icon--group text-3xl block mb-2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              />
              <p
                class="text-sm"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                No hay grupos con los filtros seleccionados.
              </p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Dialog Crear/Editar -->
    <div
      v-if="dialogOpen"
      class="fixed inset-0 z-50 flex items-center justify-center"
      style="background: rgba(0,0,0,0.4)"
    >
      <div
        class="w-full max-w-lg rounded-sm border shadow-xl"
        :style="{ background: 'var(--sapDialog_Background)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow2)' }"
      >
        <!-- Dialog Header -->
        <div
          class="flex items-center gap-2 px-5 py-4 border-b"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <span
            class="sap-icon--group"
            :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
          />
          <h2
            class="text-base font-semibold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            {{ editando ? 'Editar Grupo' : 'Crear Grupo' }}
          </h2>
          <button
            class="ml-auto"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
            @click="dialogOpen = false"
          >
            <span class="sap-icon--decline" />
          </button>
        </div>
        <!-- Dialog Body -->
        <div class="p-5 grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Código *:</label>
            <div class="flex gap-1">
              <input
                v-model="form.codigo"
                class="h-9 flex-1 border px-3 text-sm rounded-sm"
                :style="inputStyle"
                placeholder="GRUPO 1"
              >
              <button
                type="button"
                class="h-9 px-2 text-xs border rounded-sm"
                :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
                title="Auto-numerar"
                @click="autoNumerarCodigo"
              >
                <span class="sap-icon--generate-shortcut" />
              </button>
            </div>
          </div>
          <div class="space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Nombre *:</label>
            <input
              v-model="form.nombre"
              class="h-9 w-full border px-3 text-sm rounded-sm"
              :style="inputStyle"
            >
          </div>
          <div class="col-span-2 space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Descripción de Labores:</label>
            <input
              v-model="form.descripcion"
              class="h-9 w-full border px-3 text-sm rounded-sm"
              :style="inputStyle"
              placeholder="ej. &quot;Mantenimiento de válvulas sector B&quot;"
            >
          </div>
          <div class="space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Parada:</label>
            <select
              v-model="form.parada_id"
              class="h-9 w-full border px-3 text-sm rounded-sm"
              :style="selectStyle"
            >
              <option value="">
                Sin parada
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
          <div class="space-y-1">
            <label
              class="text-xs font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Circuito / Área:</label>
            <input
              v-model="form.circuito_area"
              class="h-9 w-full border px-3 text-sm rounded-sm"
              :style="inputStyle"
              placeholder="ej. Molino 4 - Tintaya"
            >
          </div>
          <div class="col-span-2 flex justify-end mb-1">
            <button
              type="button"
              class="h-8 px-3 text-xs border rounded-sm flex items-center gap-1 transition-colors"
              :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
              @click="abrirNuevoPersonal"
            >
              <span class="sap-icon--add-contact" />
              + Nuevo Personal
            </button>
          </div>
          <div
            v-if="errorForm"
            class="col-span-2 flex items-center gap-2 p-3 rounded-sm border"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
          >
            <span
              class="sap-icon--message-error"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            />
            <p
              class="text-xs"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              {{ errorForm }}
            </p>
          </div>
        </div>
        <!-- Dialog Footer -->
        <div
          class="flex gap-3 px-5 py-4 border-t"
          :style="{ borderColor: 'var(--sapList_BorderColor)' }"
        >
          <button
            class="flex-1 h-9 text-sm border rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
            @click="dialogOpen = false"
          >
            Cancelar
          </button>
          <button
            :disabled="guardando"
            class="flex-1 h-9 text-sm font-medium rounded-sm transition-colors"
            :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
            @click="guardar"
          >
            <span
              v-if="guardando"
              class="sap-icon--refresh animate-spin mr-1"
            />
            {{ editando ? 'Guardar Cambios' : 'Crear Grupo' }}
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- AlertDialog: Confirmar quitar integrante -->
  <div
    v-if="alertDialogOpen"
    class="fixed inset-0 z-[60] flex items-center justify-center"
    style="background: rgba(0,0,0,0.5)"
  >
    <div
      class="w-full max-w-md rounded-sm border shadow-xl p-6 space-y-4"
      :style="{ background: 'var(--sapDialog_Background)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-start gap-3">
        <span
          class="sap-icon--message-warning text-2xl shrink-0"
          :style="{ color: 'var(--sapCriticalColor)' }"
        />
        <div>
          <h3
            class="text-base font-semibold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Quitar integrante
          </h3>
          <p
            class="text-sm mt-1"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            ¿Deseas quitar a
            <strong :style="{ color: 'var(--sapTextColor)' }">
              {{ integrantePendiente?.usuario?.nombre }} {{ integrantePendiente?.usuario?.apellido }}
            </strong>
            del grupo?
          </p>
          <!-- Verificando herramientas -->
          <div
            v-if="verificandoHerramientas"
            class="flex items-center gap-2 mt-2 text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            <span class="sap-icon--refresh animate-spin" /> Verificando herramientas en uso...
          </div>
          <!-- Advertencia: herramientas pendientes -->
          <div
            v-else-if="herramientasEnUso.length > 0"
            class="mt-2 p-3 rounded-sm border"
            :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
          >
            <p
              class="text-xs font-semibold mb-1"
              :style="{ color: 'var(--sapNegativeTextColor)' }"
            >
              ⚠ Este trabajador tiene {{ herramientasEnUso.length }} herramienta(s) sin devolver:
            </p>
            <ul class="text-xs space-y-0.5">
              <li
                v-for="h in herramientasEnUso"
                :key="h.id ?? h.codigo_interno"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
              >
                <code>{{ h.codigo_interno }}</code> — {{ h.nombre }} ({{ h.cantidad ?? 1 }} ud.)
              </li>
            </ul>
            <p
              class="text-xs mt-2"
              :style="{ color: 'var(--sapCriticalColor)' }"
            >
              Al confirmar, las herramientas se registrarán como pendientes de devolución.
            </p>
          </div>
          <!-- Sin herramientas -->
          <p
            v-else
            class="text-xs mt-1"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            No tiene herramientas en uso. Esta acción no se puede deshacer.
          </p>
        </div>
      </div>
      <div class="flex gap-3 pt-2">
        <button
          class="flex-1 h-9 text-sm border rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="alertDialogOpen = false"
        >
          Cancelar
        </button>
        <button
          :disabled="quitandoIntegrante || verificandoHerramientas"
          class="flex-1 h-9 text-sm font-medium rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Reject_Background, var(--sapNegativeTextColor))', color: 'var(--sapButton_Reject_TextColor)', border: 'none', opacity: (quitandoIntegrante || verificandoHerramientas) ? '0.6' : '1' }"
          @click="confirmarQuitarIntegrante"
        >
          {{ forzarPerdida ? 'Desactivar y Marcar Pérdida' : 'Desactivar Sin más' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Nuevo Personal Dialog -->
  <div
    v-if="dialogNuevoPersonalOpen"
    class="fixed inset-0 z-[60] flex items-center justify-center"
    style="background: rgba(0,0,0,0.5)"
  >
    <div
      class="w-full max-w-sm rounded-sm border shadow-xl"
      :style="{ background: 'var(--sapDialog_Background)', borderColor: 'var(--sapList_BorderColor)', boxShadow: 'var(--sapContent_Shadow2)' }"
    >
      <div
        class="flex items-center gap-2 px-5 py-4 border-b"
        :style="{ borderColor: 'var(--sapList_BorderColor)' }"
      >
        <span
          class="sap-icon--add-contact"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <h2
          class="text-base font-semibold"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          Nuevo Personal
        </h2>
        <button
          class="ml-auto"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
          @click="dialogNuevoPersonalOpen = false"
        >
          <span class="sap-icon--decline" />
        </button>
      </div>
      <div class="p-5 space-y-4">
        <div class="space-y-1">
          <label
            class="text-xs font-normal"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >DNI *:</label>
          <input
            v-model="formPersonal.dni"
            class="h-9 w-full border px-3 text-sm rounded-sm"
            :style="inputStyle"
          >
        </div>
        <div class="space-y-1">
          <label
            class="text-xs font-normal"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >Nombre *:</label>
          <input
            v-model="formPersonal.nombre"
            class="h-9 w-full border px-3 text-sm rounded-sm"
            :style="inputStyle"
          >
        </div>
        <div class="space-y-1">
          <label
            class="text-xs font-normal"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >Apellido *:</label>
          <input
            v-model="formPersonal.apellido"
            class="h-9 w-full border px-3 text-sm rounded-sm"
            :style="inputStyle"
          >
        </div>
        <div class="space-y-1">
          <label
            class="text-xs font-normal"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >Rol *:</label>
          <select
            v-model="formPersonal.rol_id"
            class="h-9 w-full border px-3 text-sm rounded-sm"
            :style="selectStyle"
          >
            <option :value="4">
              Supervisor Mecánico (SUP_MEC)
            </option>
            <option :value="5">
              Supervisor SSOMA (SUP_SSOMA)
            </option>
            <option :value="6">
              Líder Mecánico (LIDER_MEC)
            </option>
            <option :value="7">
              Trabajador (TRABAJADOR)
            </option>
          </select>
        </div>
        <div
          v-if="errorPersonal"
          class="flex items-center gap-2 p-3 rounded-sm border"
          :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
        >
          <span
            class="sap-icon--message-error"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          />
          <p
            class="text-xs"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          >
            {{ errorPersonal }}
          </p>
        </div>
      </div>
      <div
        class="flex gap-3 px-5 py-4 border-t"
        :style="{ borderColor: 'var(--sapList_BorderColor)' }"
      >
        <button
          class="flex-1 h-9 text-sm border rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="dialogNuevoPersonalOpen = false"
        >
          Cancelar
        </button>
        <button
          :disabled="guardandoPersonal"
          class="flex-1 h-9 text-sm font-medium rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }"
          @click="guardarNuevoPersonal"
        >
          Guardar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useGruposStore } from '@/stores/grupos'
import { useParadasStore } from '@/stores/paradas'
import { useToast } from '@/components/ui/toast'
import { usuariosAPI, gruposAPI } from '@/api'

const dialogNuevoPersonalOpen = ref(false)
const guardandoPersonal = ref(false)
const errorPersonal = ref(null)
const formPersonal = reactive({ dni: '', nombre: '', apellido: '', rol_id: 7 })

function abrirNuevoPersonal() {
  formPersonal.dni = ''
  formPersonal.nombre = ''
  formPersonal.apellido = ''
  formPersonal.rol_id = 7
  errorPersonal.value = null
  dialogNuevoPersonalOpen.value = true
}

async function guardarNuevoPersonal() {
  errorPersonal.value = null
  if (!formPersonal.dni || !formPersonal.nombre || !formPersonal.apellido || !formPersonal.rol_id) {
    errorPersonal.value = 'Complete todos los campos obligatorios.'
    return
  }
  guardandoPersonal.value = true
  try {
    const res = await usuariosAPI.create(formPersonal)
    toast({ title: 'Usuario creado', description: 'Personal agregado correctamente.', variant: 'success' })
    dialogNuevoPersonalOpen.value = false
  } catch (err) {
    errorPersonal.value = err.response?.data?.detail || 'Error al crear personal'
  } finally {
    guardandoPersonal.value = false
  }
}

const gruposStore = useGruposStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

// Filtros
const filtroParadaId = ref('')

async function aplicarFiltros() {
  const params = {}
  if (filtroParadaId.value) params.parada_id = filtroParadaId.value
  await gruposStore.fetchAll(params, true)
}

watch([filtroParadaId], () => {
  aplicarFiltros()
})

// Expandir integrantes
const expandido = ref(null)
const grupoDetalle = ref(null)
const loadingIntegrantes = ref(false)

async function toggleExpand(id) {
  if (expandido.value === id) {
    expandido.value = null
    return
  }
  expandido.value = id
  loadingIntegrantes.value = true
  try {
    grupoDetalle.value = await gruposStore.fetchById(id)
  } finally {
    loadingIntegrantes.value = false
  }
}

// AlertDialog para confirmar quitar integrante
const alertDialogOpen = ref(false)
const integrantePendiente = ref(null) // { grupoId, usuario: {id, nombre, apellido} }
const quitandoIntegrante = ref(false)
const herramientasEnUso = ref([]) // lista de herramientas que tiene el integrante
const verificandoHerramientas = ref(false)

async function solicitarQuitarIntegrante(grupoId, integrante) {
  integrantePendiente.value = { grupoId, ...integrante }
  herramientasEnUso.value = []
  verificandoHerramientas.value = true
  alertDialogOpen.value = true
  try {
    const { data } = await gruposAPI.herramientasEnUso(grupoId, integrante.usuario.id)
    // La API devuelve { herramientas: [...], total: N }
    herramientasEnUso.value = data?.herramientas ?? (Array.isArray(data) ? data : [])
  } catch {
    // Si falla la verificación, abre el dialog de todas formas
    herramientasEnUso.value = []
  } finally {
    verificandoHerramientas.value = false
  }
}

async function confirmarQuitarIntegrante() {
  if (!integrantePendiente.value) return
  quitandoIntegrante.value = true
  try {
    await gruposStore.removeIntegrante(
      integrantePendiente.value.grupoId,
      integrantePendiente.value.usuario.id
    )
    grupoDetalle.value = gruposStore.grupoActual
    toast({ title: 'Integrante removido', variant: 'success' })
    alertDialogOpen.value = false
  } catch (e) {
    toast({ title: 'Error', description: e.response?.data?.detail || 'No se pudo quitar al integrante.', variant: 'error' })
  } finally {
    quitandoIntegrante.value = false
    integrantePendiente.value = null
  }
}

// Dialog Crear/Editar
const dialogOpen = ref(false)
const editando = ref(null)
const guardando = ref(false)
const errorForm = ref(null)
const form = reactive({ codigo: '', nombre: '', descripcion: '', parada_id: '', estado: 'Activo', circuito_area: '' })

// Auto-numeración: GRUPO X - "descripción"
function autoNumerarCodigo() {
  const numeros = gruposStore.items
    .map((g) => {
      const match = g.nombre?.match(/^GRUPO\s+(\d+)/i) || g.codigo?.match(/^GRP-(\d+)/i) || g.codigo?.match(/^GRUPO\s+(\d+)/i)
      return match ? parseInt(match[1]) : 0
    })
    .filter(Boolean)
  const siguiente = numeros.length > 0 ? Math.max(...numeros) + 1 : 1
  const desc = form.descripcion?.trim()
  form.codigo = String(siguiente)
  form.nombre = desc || ''
}

function abrirCrear() {
  editando.value = null
  form.codigo = ''
  form.nombre = ''
  form.descripcion = ''
  form.parada_id = ''
  form.circuito_area = ''
  errorForm.value = null
  dialogOpen.value = true
}

function abrirEditar(grupo) {
  editando.value = grupo.id
  form.codigo = grupo.codigo
  form.nombre = grupo.nombre
  form.descripcion = grupo.descripcion ?? ''
  form.parada_id = grupo.parada_id ?? ''
  form.circuito_area = grupo.circuito_area ?? ''
  errorForm.value = null
  dialogOpen.value = true
}

async function guardar() {
  if (!form.codigo.trim() || !form.nombre.trim()) {
    errorForm.value = 'Código y Nombre son obligatorios.'
    return
  }
  if (!form.parada_id) {
    errorForm.value = 'Debe seleccionar una Parada.'
    return
  }
  guardando.value = true
  errorForm.value = null
  try {
    const payload = {
      codigo: form.codigo.trim(),
      nombre: form.nombre.trim(),
      descripcion: form.descripcion?.trim() || null,
      circuito_area: form.circuito_area?.trim() || null,
      parada_id: Number(form.parada_id),
    }
    if (editando.value) {
      await gruposStore.update(editando.value, payload)
      toast({ title: 'Grupo actualizado', variant: 'success' })
    } else {
      await gruposStore.create(payload)
      toast({ title: 'Grupo creado', variant: 'success' })
    }
    dialogOpen.value = false
  } catch (err) {
    errorForm.value = err.response?.data?.detail || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

const selectStyle = {
  background: 'var(--sapField_Background)',
  borderColor: 'var(--sapField_BorderColor)',
  color: 'var(--sapField_TextColor)',
}
const inputStyle = {
  background: 'var(--sapField_Background)',
  borderColor: 'var(--sapField_BorderColor)',
  color: 'var(--sapField_TextColor)',
}

onMounted(async () => {
  await paradasStore.fetchAll()
  if (paradasStore.items.length > 0) {
    const activa = paradasStore.items.find(p => p.estado === 'Activa')
    filtroParadaId.value = activa?.id ?? paradasStore.items[0].id
  }
})
</script>
