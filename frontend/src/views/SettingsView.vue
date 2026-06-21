<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

interface IndexerStatus {
  configured: boolean
  has_pin: boolean
  language: string
}

const status = ref<IndexerStatus | null>(null)
const saving = ref(false)
const saved = ref(false)
const error = ref<string | null>(null)

const form = reactive({ api_key: '', pin: '', language: 'eng' })

async function loadStatus() {
  const { data } = await api.get<IndexerStatus>('/config/indexer')
  status.value = data
  form.language = data.language
}

onMounted(loadStatus)

async function save() {
  saving.value = true
  saved.value = false
  error.value = null
  try {
    // Only send the key/pin if the user actually entered something, so a blank
    // field never wipes the stored secret.
    const payload: Record<string, string> = { language: form.language }
    if (form.api_key) payload.api_key = form.api_key
    if (form.pin) payload.pin = form.pin
    await api.put('/config/indexer', payload)
    form.api_key = ''
    form.pin = ''
    await loadStatus()
    saved.value = true
  } catch {
    error.value = 'Failed to save'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppLayout title="General">
    <div class="card section">
      <h2>Metadata Indexer (TheTVDB)</h2>
      <p class="muted hint">
        Register a free key at
        <a href="https://thetvdb.com/dashboard/account/apikey" target="_blank" rel="noopener">thetvdb.com</a>.
        The free tier also needs a subscriber PIN; a licensed key does not.
      </p>

      <p class="status">
        Status:
        <span v-if="status?.configured" class="ok">Configured ✓</span>
        <span v-else class="warn">Not configured</span>
        <span v-if="status?.has_pin" class="muted"> · PIN set</span>
      </p>

      <label>API key
        <input
          v-model="form.api_key"
          type="password"
          autocomplete="off"
          :placeholder="status?.configured ? 'Leave blank to keep current key' : 'Paste your TVDB API key'"
        />
      </label>
      <label>Subscriber PIN (free tier only)
        <input v-model="form.pin" type="password" autocomplete="off"
               :placeholder="status?.has_pin ? 'Leave blank to keep current PIN' : 'optional'" />
      </label>
      <label>Language
        <input v-model="form.language" placeholder="eng" />
      </label>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="saved" class="ok">Saved.</p>
      <button :disabled="saving" @click="save">{{ saving ? 'Saving…' : 'Save' }}</button>
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
button { margin-top: 0.5rem; }
.muted { color: var(--muted); }
.ok { color: var(--ok); }
.warn { color: #fbbf24; }
.error { color: var(--danger); }
</style>
