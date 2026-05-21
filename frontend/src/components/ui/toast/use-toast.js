/**
 * Sistema de Toast — useToast composable
 * Gestiona una cola de notificaciones globales.
 * Se consume desde cualquier componente con:
 *   const { toast } = useToast()
 *   toast({ title: '¡Éxito!', description: '...', variant: 'success' })
 */
import { ref } from 'vue'

const toasts = ref([])
let idCounter = 0

export function useToast() {
  /**
   * @param {{ title: string, description?: string, variant?: 'default'|'success'|'error', duration?: number }} options
   */
  function toast({ title, description = '', variant = 'default', duration = 3500 }) {
    const id = ++idCounter
    toasts.value.push({ id, title, description, variant })
    setTimeout(() => dismiss(id), duration)
    return id
  }

  function dismiss(id) {
    const idx = toasts.value.findIndex((t) => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  return { toast, dismiss, toasts }
}
