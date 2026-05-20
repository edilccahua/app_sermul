<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Dashboard</h1>
    <p class="text-muted-foreground">Bienvenido, {{ authStore.nombreCompleto }} ({{ authStore.rolCodigo }})</p>
    <p class="text-sm text-muted-foreground mt-2">Sprint 0 - Módulo en construcción</p>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>
