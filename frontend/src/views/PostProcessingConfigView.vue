<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'

interface ProcessingStatus { configured: boolean; enabled: boolean; library_root: string | null; method: string }
const status = ref<ProcessingStatus | null>(null)
const form = reactive({ library_root: '', method: 'move', enabled: false })
const saving = ref(false)
const saved = ref(false)

async function load() {
  const { data } = await api.get<ProcessingStatus>('/config/processing')
  status.value = data
  form.library_root = data.library_root ?? ''
  form.method = data.method
  form.enabled = data.enabled
}

onMounted(load)

async function save() {
  saving.value = true
  saved.value = false
  await api.put('/config/processing', {
    library_root: form.library_root,
    method: form.method,
    enabled: form.enabled,
  })
  await load()
  saving.value = false
  saved.value = true
}
</script>

<template>
  <AppLayout title="Post Processing">
    <div class="card section">
      <h2>Library filing</h2>
      <p class="muted hint">
        When a download completes, the app renames and moves the file into your TV
        library. Auto-processing is <strong>off by default</strong>; enable it below
        once your library path is correct.
      </p>
      <p class="status">
        Status:
        <span v-if="status?.configured" class="ok">Library set ✓</span>
        <span v-else class="warn">No library root</span>
        ·
        <span :class="status?.enabled ? 'ok' : 'warn'">{{ status?.enabled ? 'Auto-processing ON' : 'Auto-processing off' }}</span>
      </p>

      <label>TV library root<input v-model="form.library_root" placeholder="/volume1/media/tv" /></label>
      <label>File method
        <select v-model="form.method">
          <option value="move">Move (default)</option>
          <option value="copy">Copy (keep original)</option>
          <option value="hardlink">Hardlink (best for seeding)</option>
        </select>
      </label>
      <label class="toggle"><input v-model="form.enabled" type="checkbox" /> Enable automatic post-processing</label>

      <p v-if="saved" class="ok">Saved.</p>
      <button :disabled="saving" @click="save">{{ saving ? 'Saving…' : 'Save' }}</button>
    </div>
  </AppLayout>
</template>

<style scoped>
.section h2 { margin: 0 0 0.35rem; font-size: 1.05rem; }
.hint { margin: 0 0 0.75rem; font-size: 0.85rem; }
.status { margin: 0 0 0.75rem; font-size: 0.9rem; }
label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8rem; color: var(--muted); margin-bottom: 0.6rem; }
label.toggle { flex-direction: row; align-items: center; gap: 0.5rem; }
label.toggle input { width: auto; }
.muted { color: var(--muted); }
.ok { color: var(--ok); }
.warn { color: #fbbf24; }
</style>
