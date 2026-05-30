<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- Dynamic Page Header -->
    <div
      class="px-6 py-4 border-b shrink-0"
      :style="{ background: 'var(--sapPageHeader_Background)', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3">
        <router-link
          to="/app/grupos"
          class="h-8 w-8 flex items-center justify-center rounded-sm hover:bg-muted/30 transition-colors"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          <span class="sap-icon--nav-back" />
        </router-link>
        <span
          class="sap-icon--excel-attachment text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Importar Grupos desde Excel
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            Carga masiva de grupos e integrantes desde archivo .xlsx
          </p>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-6">
      <div class="max-w-2xl mx-auto space-y-4">
        <!-- Paso 1: Selección de parada -->
        <div
          class="p-6 rounded-sm border"
          :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
        >
          <h2
            class="text-base font-semibold mb-4"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Configuración
          </h2>
          <div class="space-y-1.5">
            <label
              class="text-sm font-normal"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            >Parada de destino *:</label>
            <select
              v-model="paradaId"
              class="h-10 w-full border px-3 text-sm rounded-sm"
              :style="selectStyle"
            >
              <option value="">
                Seleccionar parada...
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

        <!-- Instrucciones + plantilla -->
        <div
          class="p-4 rounded-sm border"
          :style="{ background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }"
        >
          <div class="flex items-start gap-2">
            <span
              class="sap-icon--message-information shrink-0 mt-0.5"
              :style="{ color: 'var(--sapInformationTextColor)' }"
            />
            <div class="flex-1">
              <p
                class="text-sm font-semibold mb-1"
                :style="{ color: 'var(--sapTextColor)' }"
              >
                Columnas esperadas en el Excel:
              </p>
              <div class="flex flex-wrap gap-1">
                <code
                  v-for="col in columnasEsperadas"
                  :key="col"
                  class="text-xs px-2 py-0.5 rounded-sm border font-mono"
                  :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                >{{ col }}</code>
              </div>
              <p
                class="text-xs mt-2"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                El sistema también intenta detectar bloques con el formato "GRUPO X —..." automáticamente.
              </p>
            </div>
          </div>
          <button
            class="mt-3 flex items-center gap-2 h-8 px-3 text-xs border rounded-sm transition-colors"
            :style="{ background: 'transparent', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
            @click="descargarPlantilla"
          >
            <span class="sap-icon--download" /> Descargar Plantilla CSV
          </button>
        </div>

        <!-- Zona Drag & Drop -->
        <div
          class="border-2 border-dashed rounded-sm p-10 text-center cursor-pointer transition-colors"
          :style="arrastrandoSobre
            ? { background: 'var(--sapInformationBackground)', borderColor: 'var(--sapButton_Emphasized_Background)' }
            : { background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)' }"
          @dragover.prevent="arrastrandoSobre = true"
          @dragleave="arrastrandoSobre = false"
          @drop.prevent="onDrop"
          @click="$refs.fileInput.click()"
        >
          <span
            class="sap-icon--excel-attachment text-5xl block mb-3"
            :style="{ color: arrastrandoSobre ? 'var(--sapButton_Emphasized_Background)' : 'var(--sapContent_LabelColor)' }"
          />
          <p
            class="text-sm font-medium mb-1"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            {{ archivoSeleccionado ? archivoSeleccionado.name : 'Arrastra y suelta tu archivo aquí' }}
          </p>
          <p
            class="text-xs"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            o haz clic para seleccionar · .xlsx, .xls
          </p>
          <input
            ref="fileInput"
            type="file"
            accept=".xlsx,.xls"
            class="hidden"
            @change="onFileChange"
          >
        </div>

        <!-- Error API -->
        <div
          v-if="errorApi"
          class="flex items-start gap-2 p-3 rounded-sm border"
          :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
        >
          <span
            class="sap-icon--message-error shrink-0"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          />
          <p
            class="text-sm"
            :style="{ color: 'var(--sapNegativeTextColor)' }"
          >
            {{ errorApi }}
          </p>
        </div>

        <!-- Botón procesar -->
        <button
          :disabled="!archivoSeleccionado || !paradaId || procesando"
          class="w-full h-12 text-sm font-medium rounded-sm transition-colors"
          :style="archivoSeleccionado && paradaId && !procesando
            ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)', border: 'none' }
            : { background: 'var(--sapNeutralBackground)', color: 'var(--sapContent_LabelColor)', border: '1px solid var(--sapList_BorderColor)' }"
          @click="procesarArchivo"
        >
          <span
            v-if="procesando"
            class="flex items-center justify-center gap-2"
          >
            <span class="sap-icon--refresh animate-spin" /> Procesando...
          </span>
          <span v-else>
            <span class="sap-icon--upload mr-2" /> Procesar Archivo
          </span>
        </button>

        <!-- Resultado de la importación -->
        <div
          v-if="resultado"
          class="space-y-4"
        >
          <!-- Cards de resumen -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div
              v-for="stat in resumenStats"
              :key="stat.label"
              class="p-3 rounded-sm border text-center"
              :style="{ background: stat.bg, borderColor: stat.border }"
            >
              <p
                class="text-2xl font-bold"
                :style="{ color: stat.color }"
              >
                {{ stat.value }}
              </p>
              <p
                class="text-xs mt-1"
                :style="{ color: 'var(--sapContent_LabelColor)' }"
              >
                {{ stat.label }}
              </p>
            </div>
          </div>

          <!-- Grupos creados -->
          <div
            v-if="resultado.grupos_creados?.length"
            class="p-4 rounded-sm border"
            :style="{ background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)' }"
          >
            <p
              class="text-sm font-semibold mb-2"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              Grupos creados:
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="g in resultado.grupos_creados"
                :key="g.codigo"
                class="text-xs px-2 py-1 rounded-sm border"
                :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapSuccessBorderColor)', color: 'var(--sapTextColor)' }"
              >
                GRUPO <code class="font-mono">{{ g.codigo }}</code> — {{ g.nombre }} ({{ g.integrantes_count }} integrantes)
              </span>
            </div>
          </div>

          <!-- Tabla de errores -->
          <div
            v-if="resultado.errores?.length"
            class="rounded-sm border overflow-hidden"
            :style="{ borderColor: 'var(--sapErrorBorderColor)' }"
          >
            <div
              class="px-4 py-2 border-b flex items-center gap-2"
              :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
            >
              <span
                class="sap-icon--message-error"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
              />
              <p
                class="text-xs font-semibold"
                :style="{ color: 'var(--sapNegativeTextColor)' }"
              >
                {{ resultado.errores.length }} error{{ resultado.errores.length > 1 ? 'es' : '' }}
              </p>
            </div>
            <div
              v-for="(err, i) in resultado.errores"
              :key="i"
              class="px-4 py-2 border-b last:border-0 text-xs"
              :style="{ background: 'var(--sapGroup_ContentBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapNegativeTextColor)' }"
            >
              Fila {{ err.fila }}: {{ err.mensaje }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGruposStore } from '@/stores/grupos'
import { useParadasStore } from '@/stores/paradas'
import { useToast } from '@/components/ui/toast'

const gruposStore = useGruposStore()
const paradasStore = useParadasStore()
const { toast } = useToast()

const paradaId = ref('')
const archivoSeleccionado = ref(null)
const arrastrandoSobre = ref(false)
const procesando = ref(false)
const resultado = ref(null)
const errorApi = ref(null)
const fileInput = ref(null)

const columnasEsperadas = ['DNI', 'NOMBRES Y APELLIDOS', 'CARGO', 'NOMBRE GRUPO', 'LIDER DNI', 'SUPERVISOR DNI']

function onDrop(e) {
  arrastrandoSobre.value = false
  const file = e.dataTransfer.files[0]
  if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
    archivoSeleccionado.value = file
  }
}

function onFileChange(e) {
  archivoSeleccionado.value = e.target.files[0] || null
}

function descargarPlantilla() {
  const csv = columnasEsperadas.join(',') + '\n'
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'plantilla_grupos.csv'
  a.click()
  URL.revokeObjectURL(url)
}

async function procesarArchivo() {
  if (!archivoSeleccionado.value || !paradaId.value || procesando.value) return
  procesando.value = true
  errorApi.value = null
  resultado.value = null
  try {
    const formData = new FormData()
    formData.append('file', archivoSeleccionado.value)
    formData.append('parada_id', paradaId.value)
    const { gruposAPI } = await import('@/api')
    const response = await gruposAPI.importExcel(formData)
    resultado.value = response.data
    toast({
      title: `✓ Importación completada`,
      description: `${resultado.value.grupos_creados?.length ?? 0} grupos creados`,
      variant: 'success',
    })
    // Refrescar lista de grupos
    await gruposStore.fetchAll({ parada_id: paradaId.value }, true)
  } catch (err) {
    errorApi.value = err.response?.data?.detail || 'Error al procesar el archivo'
  } finally {
    procesando.value = false
  }
}

const resumenStats = computed(() => {
  if (!resultado.value) return []
  return [
    {
      label: 'Filas procesadas',
      value: resultado.value.filas_procesadas ?? 0,
      color: 'var(--sapTextColor)',
      bg: 'var(--sapGroup_ContentBackground)',
      border: 'var(--sapList_BorderColor)',
    },
    {
      label: 'Grupos creados',
      value: resultado.value.grupos_creados?.length ?? 0,
      color: 'var(--sapPositiveTextColor)',
      bg: 'var(--sapSuccessBackground)',
      border: 'var(--sapSuccessBorderColor)',
    },
    {
      label: 'Usuarios creados',
      value: resultado.value.usuarios_creados ?? 0,
      color: 'var(--sapInformationTextColor)',
      bg: 'var(--sapInformationBackground)',
      border: 'var(--sapInformationBorderColor)',
    },
    {
      label: 'Errores',
      value: resultado.value.errores?.length ?? 0,
      color: resultado.value.errores?.length ? 'var(--sapNegativeTextColor)' : 'var(--sapPositiveTextColor)',
      bg: resultado.value.errores?.length ? 'var(--sapErrorBackground)' : 'var(--sapSuccessBackground)',
      border: resultado.value.errores?.length ? 'var(--sapErrorBorderColor)' : 'var(--sapSuccessBorderColor)',
    },
  ]
})

const selectStyle = {
  background: 'var(--sapField_Background)',
  borderColor: 'var(--sapField_BorderColor)',
  color: 'var(--sapField_TextColor)',
}

onMounted(() => paradasStore.fetchAll())
</script>
