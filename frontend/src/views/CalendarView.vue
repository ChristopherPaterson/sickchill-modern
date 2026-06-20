<script setup lang="ts">
import AppLayout from '@/components/AppLayout.vue'
</script>

<template>
  <AppLayout title="Schedule">
    <p class="muted">
      Coming episodes will appear here. Wire this to a backend endpoint that
      returns upcoming/recently-aired episodes (see app/api/routes — add a
      /episodes/upcoming route backed by the show service).
    </p>
  </AppLayout>
</template>

<style scoped>
.muted { color: var(--muted); }
</style>
