<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'
import type { HistoryEntry } from '@/api/types'

const entries = ref<HistoryEntry[]>([])
const loading = ref(true)

onMounted(async () => {
  const { data } = await api.get<HistoryEntry[]>('/history')
  entries.value = data
  loading.value = false
})
</script>

<template>
  <AppLayout title="History">
    <p v-if="loading">Loading…</p>
    <p v-else-if="entries.length === 0" class="muted">No history yet.</p>
    <ul v-else class="list">
      <li v-for="e in entries" :key="e.id" class="card row">
        <span class="badge">{{ e.action }}</span>
        <span class="rel">{{ e.release_name ?? '—' }}</span>
        <span class="muted">{{ e.provider ?? '' }}</span>
      </li>
    </ul>
  </AppLayout>
</template>

<style scoped>
.list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.row { display: flex; align-items: center; gap: 0.5rem; }
.rel { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.badge { font-size: 0.7rem; padding: 0.15rem 0.4rem; border-radius: 6px; background: var(--surface-2); }
.muted { color: var(--muted); font-size: 0.8rem; }
</style>
