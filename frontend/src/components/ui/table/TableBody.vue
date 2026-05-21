<script setup>
defineProps({ class: String })
</script>
<template>
  <tbody :class="['[&_tr:last-child]:border-0', $props.class]">
    <slot />
  </tbody>
</template>
