<template>
  <Sheet :open="open" @update:open="$emit('update:open', $event)">
    <SheetContent side="right" class="w-[400px] sm:w-[540px]">
      <SheetHeader>
        <SheetTitle>Check-Out de Herramienta</SheetTitle>
        <SheetDescription>
          Entrega rápida de herramienta al grupo de trabajo
        </SheetDescription>
      </SheetHeader>

      <div class="py-6 space-y-4">
        <!-- Short Code -->
        <div class="space-y-2">
          <label class="text-sm font-medium">Short Code</label>
          <Input
            v-model="shortCode"
            placeholder="ej: HER-001"
            autofocus
            @keyup.enter="buscarHerramienta"
          />
        </div>

        <!-- Resultado de búsqueda -->
        <div v-if="buscando" class="text-sm text-muted-foreground">
          Buscando...
        </div>

        <div v-else-if="herramienta" class="space-y-3">
          <Card>
            <CardHeader>
              <CardTitle class="text-lg">{{ herramienta.nombre }}</CardTitle>
              <CardDescription>{{ herramienta.categoria }}</CardDescription>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <span class="text-muted-foreground">Disponibles:</span>
                <span class="font-medium">{{ herramienta.disponibles }}</span>
                <span class="text-muted-foreground">Ubicación:</span>
                <span class="font-medium">{{ herramienta.ubicacion }}</span>
              </div>
            </CardContent>
          </Card>

          <!-- Grupo de destino -->
          <div class="space-y-2">
            <label class="text-sm font-medium">Grupo de destino</label>
            <Input placeholder="Seleccionar grupo..." />
          </div>
        </div>

        <div v-else-if="shortCode && !buscando" class="text-sm text-destructive">
          Herramienta no encontrada
        </div>
      </div>

      <SheetFooter>
        <SheetClose as-child>
          <Button variant="outline">Cancelar</Button>
        </SheetClose>
        <Button :disabled="!herramienta">
          Confirmar Entrega
        </Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetClose,
} from '@/components/ui/sheet'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const props = defineProps({
  open: { type: Boolean, default: false },
})

defineEmits(['update:open'])

const shortCode = ref('')
const buscando = ref(false)
const herramienta = ref(null)

function buscarHerramienta() {
  if (!shortCode.value.trim()) return
  buscando.value = true
  // TODO: llamar API /api/inventario/buscar?codigo=...
  setTimeout(() => {
    buscando.value = false
    herramienta.value = {
      nombre: `Herramienta ${shortCode.value}`,
      categoria: 'Herramientas manuales',
      disponibles: 3,
      ubicacion: 'Mina',
    }
  }, 500)
}

watch(
  () => props.open,
  (val) => {
    if (val) {
      shortCode.value = ''
      herramienta.value = null
      buscando.value = false
    }
  }
)
</script>
