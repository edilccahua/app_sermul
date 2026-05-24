<template>
  <!-- Stack de toasts fijo en bottom-right -->
  <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-[360px] max-w-[calc(100vw-2rem)]">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="[
          'flex items-start gap-3 rounded-lg border px-4 py-3 shadow-lg backdrop-blur-sm',
          'transition-all duration-300',
          t.variant === 'success'
            ? 'bg-[var(--sapSuccessBackground)] border border-[var(--sapSuccessBorderColor)] text-[var(--sapPositiveTextColor)]'
            : toastVariant === 'error'
            ? 'bg-[var(--sapErrorBackground)] border border-[var(--sapErrorBorderColor)] text-[var(--sapNegativeTextColor)]'
            : 'bg-card border-border text-foreground',
        ]"
      >
        <!-- Icono según variante -->
        <span class="mt-0.5 flex-shrink-0 text-lg">
          <span v-if="t.variant === 'success'">✓</span>
          <span v-else-if="t.variant === 'error'">✕</span>
          <span v-else>ℹ</span>
        </span>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold">{{ t.title }}</p>
          <p v-if="t.description" class="text-xs opacity-80 mt-0.5">{{ t.description }}</p>
        </div>
        <button
          @click="dismiss(t.id)"
          class="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity text-sm ml-1"
          tabindex="-1"
        >✕</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToast } from './use-toast'
const { toasts, dismiss } = useToast()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
