<script setup>
defineProps({ class: String })
</script>
<template>
  <tr
    :class="[
      'border-b border-border transition-colors hover:bg-muted/30 data-[state=selected]:bg-muted',
      $props.class,
    ]"
  >
    <slot />
  </tr>
</template>
