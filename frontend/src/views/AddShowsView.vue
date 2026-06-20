<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'

interface SearchResult {
  tvdb_id: number
  name: string
  overview: string | null
  network: string | null
  poster_url: string | null
}

const router = useRouter()
const query = ref('')
const results = ref<SearchResult[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const addingId = ref<number | null>(null)

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  error.value = null
  results.value = []
  try {
    const { data } = await api.get<SearchResult[]>('/search/shows', { params: { q: query.value } })
    results.value = data
    if (data.length === 0) error.value = 'No matches found'
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status
    error.value = status === 503
      ? 'No metadata indexer configured. Set SCM_TVDB_API_KEY on the server.'
      : 'Search failed'
  } finally {
    loading.value = false
  }
}

async function add(result: SearchResult) {
  addingId.value = result.tvdb_id
  try {
    await api.post('/shows', { tvdb_id: result.tvdb_id, quality: 'HD' })
    router.push({ name: 'shows' })
  } catch {
    error.value = `Failed to add ${result.name}`
  } finally {
    addingId.value = null
  }
}
</script>

<template>
  <AppLayout title="Add Shows">
    <form class="search-bar" @submit.prevent="search">
      <input v-model="query" placeholder="Search for a TV show…" autofocus />
      <button :disabled="loading" type="submit">{{ loading ? 'Searching…' : 'Search' }}</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <ul class="results">
      <li v-for="r in results" :key="r.tvdb_id" class="card result">
        <div
          class="poster"
          :style="r.poster_url ? `background-image:url(${r.poster_url})` : ''"
        />
        <div class="info">
          <div class="name">{{ r.name }}</div>
          <div class="network muted">{{ r.network ?? '—' }}</div>
          <p class="overview muted">{{ r.overview ?? 'No overview.' }}</p>
        </div>
        <button class="add" :disabled="addingId === r.tvdb_id" @click="add(r)">
          {{ addingId === r.tvdb_id ? 'Adding…' : 'Add' }}
        </button>
      </li>
    </ul>
  </AppLayout>
</template>

<style scoped>
.search-bar { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
.search-bar input { flex: 1; }
.search-bar button { white-space: nowrap; }
.results { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.75rem; }
.result { display: grid; grid-template-columns: 60px 1fr auto; gap: 0.75rem; align-items: start; }
.poster { width: 60px; aspect-ratio: 2/3; background: var(--surface-2) center/cover no-repeat; border-radius: 8px; }
.info { min-width: 0; }
.name { font-weight: 600; }
.network { font-size: 0.8rem; }
.overview {
  font-size: 0.85rem;
  margin: 0.35rem 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.add { align-self: center; }
.muted { color: var(--muted); }
.error { color: var(--danger); }
</style>
