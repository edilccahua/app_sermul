<script setup>
defineProps({
  class: String,
})
</script>

<template>
  <div class="w-full overflow-auto" :class="$props.class">
    <table class="w-full caption-bottom text-sm">
      <slot />
    </table>
  </div>
</template>
