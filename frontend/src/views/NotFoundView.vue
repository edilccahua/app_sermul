<template>
  <div class="h-full flex flex-col items-center justify-center p-6 text-center">
    <div class="max-w-md space-y-6">
      <div 
        class="w-24 h-24 mx-auto rounded-sm flex items-center justify-center border"
        :style="{ 
          background: 'var(--sapErrorBackground)',
          borderColor: 'var(--sapErrorBorderColor)',
          color: 'var(--sapNegativeTextColor)'
        }"
      >
        <span class="sap-icon--sys-cancel-2 text-4xl" />
      </div>
      
      <div class="space-y-2">
        <h1 
          class="text-2xl font-bold font-['72']"
          :style="{ color: 'var(--sapTextColor)' }"
        >
          Página no encontrada (404)
        </h1>
        <p 
          class="text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Lo sentimos, la página que buscas no existe, ha sido movida o no tienes permisos para acceder a ella.
        </p>
      </div>

      <button
        class="inline-flex items-center gap-2 px-6 py-2.5 rounded-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
        :style="{ 
          background: 'var(--sapButton_Emphasized_Background)',
          color: 'var(--sapButton_Emphasized_TextColor)',
          borderColor: 'var(--sapButton_Emphasized_BorderColor)'
        }"
        style="border-width: 1px;"
        @click="router.push('/app/dashboard')"
      >
        <span class="sap-icon--home" />
        Volver al Inicio
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
