<script setup>
defineProps({ class: String })
</script>
<template>
  <td
    :class="[
      'px-3 py-3 align-middle [&:has([role=checkbox])]:pr-0',
      $props.class,
    ]"
  >
    <slot />
  </td>
</template>
