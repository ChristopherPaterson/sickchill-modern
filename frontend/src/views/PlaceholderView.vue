<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const title = (route.meta.title as string) ?? 'Page'
</script>

<template>
  <AppLayout :title="title">
    <div class="card placeholder">
      <h2>{{ title }}</h2>
      <p class="muted">
        This screen is scaffolded but not implemented yet. The navigation,
        routing and layout (desktop and mobile) are in place; the page content is
        the next build step.
      </p>
    </div>
  </AppLayout>
</template>

<style scoped>
.placeholder h2 { margin: 0 0 0.5rem; font-size: 1.1rem; }
.muted { color: var(--muted); margin: 0; }
</style>
