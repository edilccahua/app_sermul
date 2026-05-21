<script setup>
defineProps({ class: String })
</script>
<template>
  <th
    :class="[
      'h-10 px-3 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0',
      $props.class,
    ]"
  >
    <slot />
  </th>
</template>
