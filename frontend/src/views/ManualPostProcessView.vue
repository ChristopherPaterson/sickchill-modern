<script setup lang="ts">
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'

interface ProcessResult { release: string; status: string; message: string; destination: string | null }

const results = ref<ProcessResult[]>([])
const running = ref(false)
const folder = ref('')

async function runCompleted() {
  running.value = true
  results.value = []
  try {
    const { data } = await api.post<ProcessResult[]>('/postprocess/run')
    results.value = data
  } finally {
    running.value = false
  }
}

async function runFolder() {
  if (!folder.value.trim()) return
  running.value = true
  results.value = []
  try {
    const { data } = await api.post<ProcessResult[]>('/postprocess/folder', { path: folder.value })
    results.value = data
  } finally {
    running.value = false
  }
}
</script>

<template>
  <AppLayout title="Manual Post-Processing">
    <div class="card section">
      <p class="muted hint">
        File completed downloads into your library now. Configure the library path
        under Config → Post Processing first.
      </p>
      <button :disabled="running" @click="runCompleted">
        {{ running ? 'Processing…' : 'Process completed downloads' }}
      </button>
    </div>

    <div class="card section">
      <h2>Process a specific folder</h2>
      <div class="row">
        <input v-model="folder" placeholder="/path/to/downloads" />
        <button class="secondary" :disabled="running" @click="runFolder">Process</button>
      </div>
    </div>

    <ul v-if="results.length" class="results">
      <li v-for="(r, i) in results" :key="i" class="card result">
        <span class="badge" :data-status="r.status">{{ r.status }}</span>
        <div class="info">
          <div class="rel">{{ r.release || '(item)' }}</div>
          <div class="msg muted">{{ r.message }}</div>
        </div>
      </li>
    </ul>
  </AppLayout>
</template>

<style scoped>
.section { margin-bottom: 1rem; }
.section h2 { margin: 0 0 0.5rem; font-size: 1rem; }
.hint { margin: 0 0 0.75rem; font-size: 0.85rem; }
.row { display: flex; gap: 0.5rem; }
.row input { flex: 1; }
.results { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.result { display: flex; gap: 0.6rem; align-items: flex-start; }
.info { min-width: 0; }
.rel { font-weight: 600; font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; }
.msg { font-size: 0.8rem; }
.badge { font-size: 0.7rem; padding: 0.15rem 0.45rem; border-radius: 6px; background: var(--surface-2); white-space: nowrap; }
.badge[data-status='filed'] { background: #14361f; color: var(--ok); }
.badge[data-status='skipped'] { background: #1e293b; color: var(--muted); }
.badge[data-status='no_match'], .badge[data-status='no_file'] { background: #422006; color: #fbbf24; }
.badge[data-status='error'] { background: #3a1d1d; color: var(--danger); }
.muted { color: var(--muted); }
</style>
