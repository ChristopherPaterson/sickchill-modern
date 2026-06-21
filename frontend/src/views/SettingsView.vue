<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

/* ---- TheTVDB ---- */
interface IndexerStatus { configured: boolean; has_pin: boolean; language: string }
const indexer = ref<IndexerStatus | null>(null)
const indexerForm = reactive({ api_key: '', pin: '', language: 'eng' })
const indexerSaving = ref(false)
const indexerSaved = ref(false)

async function loadIndexer() {
  const { data } = await api.get<IndexerStatus>('/config/indexer')
  indexer.value = data
  indexerForm.language = data.language
}

async function saveIndexer() {
  indexerSaving.value = true
  indexerSaved.value = false
  const payload: Record<string, string> = { language: indexerForm.language }
  if (indexerForm.api_key) payload.api_key = indexerForm.api_key
  if (indexerForm.pin) payload.pin = indexerForm.pin
  await api.put('/config/indexer', payload)
  indexerForm.api_key = ''
  indexerForm.pin = ''
  await loadIndexer()
  indexerSaving.value = false
  indexerSaved.value = true
}

/* ---- Download client (SABnzbd) ---- */
interface DownloadStatus { configured: boolean; enabled: boolean; url: string | null; category: string | null }
const download = ref<DownloadStatus | null>(null)
const dlForm = reactive({ url: '', api_key: '', category: '', enabled: false })
const dlSaving = ref(false)
const dlSaved = ref(false)
const testMsg = ref<string | null>(null)

async function loadDownload() {
  const { data } = await api.get<DownloadStatus>('/config/download')
  download.value = data
  dlForm.url = data.url ?? ''
  dlForm.category = data.category ?? ''
  dlForm.enabled = data.enabled
}

async function saveDownload() {
  dlSaving.value = true
  dlSaved.value = false
  const payload: Record<string, string | boolean> = {
    url: dlForm.url,
    category: dlForm.category,
    enabled: dlForm.enabled,
  }
  if (dlForm.api_key) payload.api_key = dlForm.api_key
  await api.put('/config/download', payload)
  dlForm.api_key = ''
  await loadDownload()
  dlSaving.value = false
  dlSaved.value = true
}

async function testDownload() {
  testMsg.value = 'Testing…'
  const { data } = await api.post<{ message: string }>('/config/download/test')
  testMsg.value = data.message
}

onMounted(() => {
  loadIndexer()
  loadDownload()
})
</script>

<template>
  <AppLayout title="General">
    <!-- TheTVDB -->
    <div class="card section">
      <h2>Metadata Indexer (TheTVDB)</h2>
      <p class="muted hint">
        Register a free key at
        <a href="https://thetvdb.com/dashboard/account/apikey" target="_blank" rel="noopener">thetvdb.com</a>.
        The free tier also needs a subscriber PIN; a licensed key does not.
      </p>
      <p class="status">
        Status:
        <span v-if="indexer?.configured" class="ok">Configured ✓</span>
        <span v-else class="warn">Not configured</span>
        <span v-if="indexer?.has_pin" class="muted"> · PIN set</span>
      </p>
      <label>API key
        <input v-model="indexerForm.api_key" type="password" autocomplete="off"
               :placeholder="indexer?.configured ? 'Leave blank to keep current key' : 'Paste your TVDB API key'" />
      </label>
      <label>Subscriber PIN (free tier only)
        <input v-model="indexerForm.pin" type="password" autocomplete="off"
               :placeholder="indexer?.has_pin ? 'Leave blank to keep current PIN' : 'optional'" />
      </label>
      <label>Language<input v-model="indexerForm.language" placeholder="eng" /></label>
      <p v-if="indexerSaved" class="ok">Saved.</p>
      <button :disabled="indexerSaving" @click="saveIndexer">{{ indexerSaving ? 'Saving…' : 'Save' }}</button>
    </div>

    <!-- Download client -->
    <div class="card section">
      <h2>Download Client (SABnzbd)</h2>
      <p class="muted hint">
        Where snatched NZBs are sent. Find the API key in SABnzbd under
        Config → General. Downloads are <strong>off by default</strong>: enable
        the toggle below only when you want it to start sending.
      </p>
      <p class="status">
        Status:
        <span v-if="download?.configured" class="ok">Configured ✓</span>
        <span v-else class="warn">Not configured</span>
        ·
        <span :class="download?.enabled ? 'ok' : 'warn'">{{ download?.enabled ? 'Downloads ENABLED' : 'Downloads disabled' }}</span>
      </p>
      <label>SABnzbd URL<input v-model="dlForm.url" placeholder="http://synology:8080" /></label>
      <label>API key
        <input v-model="dlForm.api_key" type="password" autocomplete="off"
               :placeholder="download?.configured ? 'Leave blank to keep current key' : 'SABnzbd API key'" />
      </label>
      <label>Category<input v-model="dlForm.category" placeholder="tv (optional)" /></label>
      <label class="toggle"><input v-model="dlForm.enabled" type="checkbox" /> Enable downloads (send snatches to SABnzbd)</label>
      <p v-if="testMsg" class="muted test">{{ testMsg }}</p>
      <p v-if="dlSaved" class="ok">Saved.</p>
      <div class="actions">
        <button :disabled="dlSaving" @click="saveDownload">{{ dlSaving ? 'Saving…' : 'Save' }}</button>
        <button class="secondary" @click="testDownload">Test connection</button>
      </div>
    </div>

    <div class="card section">
      <p class="muted">Signed in as <strong>{{ auth.username ?? 'admin' }}</strong></p>
    </div>
  </AppLayout>
</template>

<style scoped>
.section { margin-bottom: 1rem; }
.section h2 { margin: 0 0 0.35rem; font-size: 1.05rem; }
.hint { margin: 0 0 0.75rem; font-size: 0.85rem; }
.status { margin: 0 0 0.75rem; font-size: 0.9rem; }
label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8rem; color: var(--muted); margin-bottom: 0.6rem; }
label.toggle { flex-direction: row; align-items: center; gap: 0.5rem; }
label.toggle input { width: auto; }
.actions { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
.test { font-style: italic; }
.muted { color: var(--muted); }
.ok { color: var(--ok); }
.warn { color: #fbbf24; }
</style>
