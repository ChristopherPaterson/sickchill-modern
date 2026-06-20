<script setup lang="ts">
import BottomNav from './BottomNav.vue'

defineProps<{ title?: string }>()
</script>

<template>
  <div class="app-shell">
    <header v-if="title" class="app-header">{{ title }}</header>
    <main class="app-content">
      <slot />
    </main>
    <BottomNav />
  </div>
</template>
