<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'

interface BacklogItem {
  episode_id: number
  show_id: number
  show_name: string
  season: number
  episode: number
  name: string | null
  air_date: string | null
}

const items = ref<BacklogItem[]>([])
const loading = ref(true)
const running = ref(false)
const notice = ref<string | null>(null)
const router = useRouter()

async function load() {
  loading.value = true
  const { data } = await api.get<BacklogItem[]>('/search/backlog')
  items.value = data
  loading.value = false
}

onMounted(load)

async function searchAll() {
  running.value = true
  notice.value = 'Searching all wanted episodes…'
  try {
    const { data } = await api.post<{ message: string }>('/search/backlog')
    notice.value = data.message
    await load()
  } finally {
    running.value = false
  }
}

function seCode(i: BacklogItem) {
  return `S${String(i.season).padStart(2, '0')}E${String(i.episode).padStart(2, '0')}`
}
</script>

<template>
  <AppLayout title="Backlog Overview">
    <div class="bar">
      <p class="muted count">{{ items.length }} wanted episode(s)</p>
      <button :disabled="running || items.length === 0" @click="searchAll">
        {{ running ? 'Searching…' : 'Search all wanted' }}
      </button>
    </div>
    <p v-if="notice" class="notice">{{ notice }}</p>

    <p v-if="loading">Loading…</p>
    <p v-else-if="items.length === 0" class="muted">
      Nothing wanted. Mark episodes as "wanted" on a show to populate the backlog.
    </p>
    <ul v-else class="list">
      <li v-for="i in items" :key="i.episode_id" class="card row"
          @click="router.push({ name: 'show-detail', params: { id: i.show_id } })">
        <span class="se">{{ seCode(i) }}</span>
        <div class="info">
          <div class="show">{{ i.show_name }}</div>
          <div class="ep muted">{{ i.name ?? 'TBA' }}</div>
        </div>
        <span class="air muted">{{ i.air_date ?? '—' }}</span>
      </li>
    </ul>
  </AppLayout>
</template>

<style scoped>
.bar { display: flex; align-items: center; gap: 1rem; }
.count { flex: 1; margin: 0; font-size: 0.9rem; }
.notice { font-size: 0.85rem; color: var(--accent); margin: 0.5rem 0; }
.list { list-style: none; margin: 1rem 0 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.row { display: flex; align-items: center; gap: 0.75rem; cursor: pointer; }
.row:hover { background: var(--surface-2); }
.se { font-variant-numeric: tabular-nums; color: var(--accent); font-size: 0.85rem; white-space: nowrap; }
.info { flex: 1; min-width: 0; }
.show { font-weight: 600; }
.ep { font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.air { font-size: 0.8rem; white-space: nowrap; }
.muted { color: var(--muted); }
</style>
