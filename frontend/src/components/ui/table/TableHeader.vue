<script setup>
defineProps({ class: String })
</script>
<template>
  <thead :class="['[&_tr]:border-b', $props.class]">
    <slot />
  </thead>
</template>
