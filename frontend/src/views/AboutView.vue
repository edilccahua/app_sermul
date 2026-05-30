<template>
  <div class="max-w-4xl mx-auto p-6 space-y-6 pb-20">
    <!-- Header Page -->
    <header class="mb-6">
      <h1 class="text-2xl font-bold font-['72'] tracking-tight" :style="{ color: 'var(--sapTextColor)' }">
        Acerca de LOGIST
      </h1>
      <p class="text-sm mt-1" :style="{ color: 'var(--sapContent_LabelColor)' }">
        Información del sistema y contacto del desarrollador.
      </p>
    </header>

    <!-- Project Info Card -->
    <div class="rounded-sm border overflow-hidden" :style="{
      background: 'var(--sapGroup_ContentBackground)',
      borderColor: 'var(--sapList_BorderColor)'
    }">
      <div class="px-5 py-4 border-b flex items-center gap-2"
        :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'transparent' }">
        <span class="sap-icon--sys-monitor text-lg" :style="{ color: 'var(--sapContent_IconColor)' }" />
        <h2 class="text-base font-semibold" :style="{ color: 'var(--sapTextColor)' }">
          El Proyecto
        </h2>
      </div>
      <div class="p-5 space-y-4 text-sm" :style="{ color: 'var(--sapTextColor)' }">
        <p>
          <strong>LOGIST v0.9 (Beta)</strong> es una plataforma integral diseñada específicamente para optimizar el control de
          activos, herramientas y equipos de protección personal (EPP) durante las <strong>Paradas de Planta</strong> en
          el sector minero.
        </p>
        <p>
          El sistema digitaliza el flujo completo de almacén, desde la planificación pre-parada hasta la liquidación
          final, asegurando trazabilidad absoluta de cada activo, reduciendo los tiempos de atención y
          rastreando las pérdidas económicas por extravíos no documentados.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div class="p-4 rounded-sm border"
            :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'var(--sapBackgroundColor)' }">
            <h3 class="font-bold mb-2">Características Principales</h3>
            <ul class="list-disc pl-5 space-y-1" :style="{ color: 'var(--sapContent_LabelColor)' }">
              <li>Gestión de Cuadrillas y Paradas</li>
              <li>Despacho ultrarrápido con Short Codes</li>
              <li>Reservas Pre-turno</li>
              <li>Historial Inmutable de Auditoría</li>
            </ul>
          </div>
          <div class="p-4 rounded-sm border"
            :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'var(--sapBackgroundColor)' }">
            <h3 class="font-bold mb-2">Tech Stack </h3>
            <ul class="list-disc pl-5 space-y-1" :style="{ color: 'var(--sapContent_LabelColor)' }">
              <li>Vue 3 + Tailwind CSS (SAP Fiori & 4/HANNA)</li>
              <li>FastAPI + Python 3.11</li>
              <li>PostgreSQL 15</li>
              <li>Docker & Docker Compose</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Developer Info Card -->
    <div class="rounded-sm border overflow-hidden" :style="{
      background: 'var(--sapGroup_ContentBackground)',
      borderColor: 'var(--sapList_BorderColor)'
    }">
      <div class="px-5 py-4 border-b flex items-center gap-2"
        :style="{ borderColor: 'var(--sapList_BorderColor)', background: 'transparent' }">
        <span class="sap-icon--employee text-lg" :style="{ color: 'var(--sapContent_IconColor)' }" />
        <h2 class="text-base font-semibold" :style="{ color: 'var(--sapTextColor)' }">
          Desarrollado Por
        </h2>
      </div>
      <div class="p-5 flex flex-col md:flex-row gap-6 items-start">
        <div class="w-24 h-24 rounded-sm flex items-center justify-center shrink-0 border" :style="{
          background: 'var(--sapInformationBackground)',
          borderColor: 'var(--sapInformationBorderColor)',
          color: 'var(--sapInformationTextColor)'
        }">
          <span class="text-3xl font-bold">EC</span>
        </div>

        <div class="flex-1 space-y-3">
          <div>
            <h3 class="text-xl font-bold font-['72']" :style="{ color: 'var(--sapTextColor)' }">Edilson Ccahua Ccahua
            </h3>
            <p class="text-sm font-medium" :style="{ color: 'var(--sapContent_LabelColor)' }">Ingeniero & Desarrollador
              de Software</p>
          </div>

          <div class="flex flex-col gap-2 pt-2 text-sm">
            <!-- WhatsApp -->
            <a href="https://wa.me/51940836175?text=Hola%20Edilson,%20te%20contacto%20por%20el%20sistema%20SERMUL."
              target="_blank" rel="noopener noreferrer"
              class="flex items-center gap-2 transition-colors hover:underline w-fit"
              :style="{ color: 'var(--sapLinkColor)' }">
              <span class="sap-icon--call text-base" />
              <span>+51 940836175</span>
            </a>

            <!-- Email -->
            <a href="mailto:edilccahua.151@gmail.com"
              class="flex items-center gap-2 transition-colors hover:underline w-fit"
              :style="{ color: 'var(--sapLinkColor)' }">
              <span class="sap-icon--email text-base" />
              <span>edilccahua.151@gmail.com</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Página estática de información del proyecto y contacto
</script>
