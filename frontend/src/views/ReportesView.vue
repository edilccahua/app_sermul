<template>
  <div class="h-full flex flex-col items-center justify-center p-12 text-center"
    :style="{ background: 'var(--sapBackgroundColor)' }">
    <span class="sap-icon--excel-attachment text-6xl mb-4" :style="{ color: 'var(--sapContent_LabelColor)' }" />
    <h2 class="text-xl font-bold mb-2" :style="{ color: 'var(--sapTextColor)' }">
      Reportes Exportables
    </h2>
    <p class="text-sm max-w-md" :style="{ color: 'var(--sapContent_LabelColor)' }">
      Esta sección estará disponible próximamente. Podrás descargar reportes en formato Excel con:
    </p>
    <ul class="text-sm mt-4 space-y-1 text-left" :style="{ color: 'var(--sapContent_LabelColor)' }">
      <li>• Inventario completo con valorización</li>
      <li>• Historial por rango de fechas y parada</li>
      <li>• Detalle de pérdidas con responsables</li>
      <li>• Herramientas asignadas por grupo</li>
    </ul>
  </div>
</template>

<script setup>
// Placeholder for future reporting implementation
</script>
