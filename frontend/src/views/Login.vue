<template>
  <div class="min-h-screen flex items-center justify-center bg-background">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-1 text-center">
        <CardTitle class="text-2xl font-bold">SERMUL</CardTitle>
        <CardDescription>
          Sistema de Gestión de Herramientas para Paradas de Planta
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="space-y-2">
            <label class="text-sm font-medium">DNI</label>
            <Input
              v-model="dni"
              type="text"
              placeholder="Ingrese su DNI"
              :disabled="loading"
              autofocus
              @keyup.enter="handleLogin"
            />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">Contraseña</label>
            <Input
              v-model="password"
              type="password"
              placeholder="Ingrese su contraseña"
              :disabled="loading"
              @keyup.enter="handleLogin"
            />
          </div>
          <div v-if="error" class="text-sm text-destructive">
            {{ error }}
          </div>
          <Button type="submit" class="w-full" :disabled="loading || !dni || !password">
            <span v-if="loading">Ingresando...</span>
            <span v-else>Iniciar Sesión</span>
          </Button>
        </form>
      </CardContent>
      <CardFooter class="text-center text-sm text-muted-foreground">
        <p>Usuarios demo: 12345678/admin123 (Residente) | 11223344/almacen123 (Almacenero)</p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const router = useRouter()
const authStore = useAuthStore()

const dni = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  const success = await authStore.login(dni.value, password.value)
  loading.value = false
  if (success) {
    router.push('/app/dashboard')
  } else {
    error.value = authStore.error || 'DNI o contraseña incorrectos'
  }
}
</script>
