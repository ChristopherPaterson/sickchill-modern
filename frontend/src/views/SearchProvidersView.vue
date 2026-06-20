<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'

interface Provider {
  id: number
  name: string
  type: 'newznab' | 'torznab'
  url: string
  enabled: boolean
  priority: number
  min_seeders: number
}

const providers = ref<Provider[]>([])
const error = ref<string | null>(null)
const saving = ref(false)

const form = reactive({
  name: '',
  type: 'torznab' as 'newznab' | 'torznab',
  url: '',
  api_key: '',
  min_seeders: 0,
  priority: 0,
})

async function load() {
  const { data } = await api.get<Provider[]>('/providers')
  providers.value = data
}

onMounted(load)

async function add() {
  if (!form.name || !form.url) {
    error.value = 'Name and URL are required'
    return
  }
  saving.value = true
  error.value = null
  try {
    await api.post('/providers', { ...form })
    form.name = ''
    form.url = ''
    form.api_key = ''
    await load()
  } catch {
    error.value = 'Failed to add provider'
  } finally {
    saving.value = false
  }
}

async function toggle(p: Provider) {
  await api.patch(`/providers/${p.id}`, { ...p, enabled: !p.enabled })
  await load()
}

async function remove(p: Provider) {
  await api.delete(`/providers/${p.id}`)
  await load()
}
</script>

<template>
  <AppLayout title="Search Providers">
    <div class="card form">
      <h2>Add a provider</h2>
      <p class="muted hint">
        Point this at a Torznab feed (Prowlarr/Jackett) or a Newznab usenet
        indexer. The URL is the API base, e.g. http://prowlarr:9696/1/api
      </p>
      <div class="grid">
        <label>Name<input v-model="form.name" placeholder="My Prowlarr" /></label>
        <label>Type
          <select v-model="form.type">
            <option value="torznab">Torznab (torrent)</option>
            <option value="newznab">Newznab (usenet)</option>
          </select>
        </label>
        <label class="wide">URL<input v-model="form.url" placeholder="http://host:port/api" /></label>
        <label class="wide">API key<input v-model="form.api_key" placeholder="optional" /></label>
        <label>Min seeders<input v-model.number="form.min_seeders" type="number" min="0" /></label>
        <label>Priority<input v-model.number="form.priority" type="number" /></label>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button :disabled="saving" @click="add">{{ saving ? 'Saving…' : 'Add provider' }}</button>
    </div>

    <ul class="list">
      <li v-for="p in providers" :key="p.id" class="card row">
        <div class="info">
          <div class="name">{{ p.name }} <span class="tag">{{ p.type }}</span></div>
          <div class="url muted">{{ p.url }}</div>
        </div>
        <button class="secondary mini" @click="toggle(p)">{{ p.enabled ? 'Enabled' : 'Disabled' }}</button>
        <button class="secondary mini danger" @click="remove(p)">Delete</button>
      </li>
      <li v-if="providers.length === 0" class="muted empty">No providers configured yet.</li>
    </ul>
  </AppLayout>
</template>

<style scoped>
.form h2 { margin: 0 0 0.25rem; font-size: 1.05rem; }
.hint { margin: 0 0 0.75rem; font-size: 0.8rem; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; margin-bottom: 0.75rem; }
.grid label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8rem; color: var(--muted); }
.grid .wide { grid-column: 1 / -1; }
.list { list-style: none; margin: 1rem 0 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.row { display: flex; align-items: center; gap: 0.5rem; }
.info { flex: 1; min-width: 0; }
.name { font-weight: 600; }
.tag { font-size: 0.7rem; color: var(--accent); background: var(--surface-2); padding: 0.1rem 0.4rem; border-radius: 6px; }
.url { font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mini { padding: 0.35rem 0.6rem; font-size: 0.8rem; }
.danger { color: var(--danger); }
.muted { color: var(--muted); }
.error { color: var(--danger); }
.empty { padding: 0.5rem; }
</style>
