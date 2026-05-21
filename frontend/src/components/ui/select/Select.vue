<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  class: String,
})
const emit = defineEmits(['update:modelValue'])

const value = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
</script>

<template>
  <select
    v-model="value"
    :class="[
      'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1',
      'text-sm shadow-sm transition-colors placeholder:text-muted-foreground',
      'focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
      $props.class,
    ]"
  >
    <slot />
  </select>
</template>
