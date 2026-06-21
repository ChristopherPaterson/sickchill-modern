<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'
import { useShowsStore } from '@/stores/shows'
import type { Episode, EpisodeStatus, Show } from '@/api/types'

const props = defineProps<{ id: string }>()
const store = useShowsStore()

const show = ref<Show | null>(null)
const episodes = ref<Episode[]>([])
const loading = ref(true)
const notice = ref<string | null>(null)

const STATUSES: EpisodeStatus[] = [
  'unaired', 'wanted', 'snatched', 'downloaded', 'archived', 'skipped', 'ignored', 'failed',
]

async function load() {
  const id = Number(props.id)
  show.value = await store.fetchShow(id)
  episodes.value = await store.fetchEpisodes(id)
  loading.value = false
}

onMounted(load)

async function setStatus(ep: Episode, status: EpisodeStatus) {
  const prev = ep.status
  ep.status = status
  try {
    await api.patch(`/episodes/${ep.id}/status`, { status })
  } catch {
    ep.status = prev
    notice.value = 'Failed to update status'
  }
}

async function searchEpisode(ep: Episode) {
  notice.value = `Searching ${seCode(ep)}…`
  const { data } = await api.post<{ message: string }>(`/episodes/${ep.id}/search`)
  notice.value = data.message
}

async function searchWanted() {
  notice.value = 'Searching wanted episodes…'
  const { data } = await api.post<{ message: string }>(`/shows/${props.id}/search-wanted`)
  notice.value = data.message
  episodes.value = await store.fetchEpisodes(Number(props.id))
}

function seCode(ep: Episode) {
  return `S${String(ep.season).padStart(2, '0')}E${String(ep.episode).padStart(2, '0')}`
}

function bySeason() {
  const map = new Map<number, Episode[]>()
  for (const ep of episodes.value) {
    if (!map.has(ep.season)) map.set(ep.season, [])
    map.get(ep.season)!.push(ep)
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0])
}
</script>

<template>
  <AppLayout :title="show?.name ?? 'Show'">
    <p v-if="loading">Loading…</p>
    <template v-else-if="show">
      <div class="head">
        <p class="overview muted">{{ show.overview ?? 'No overview.' }}</p>
        <button class="secondary" @click="searchWanted">Search wanted</button>
      </div>
      <p v-if="notice" class="notice">{{ notice }}</p>

      <section v-for="[season, eps] in bySeason()" :key="season" class="season">
        <h2>Season {{ season }}</h2>
        <ul class="ep-list">
          <li v-for="ep in eps" :key="ep.id" class="ep">
            <span class="ep-num">{{ ep.episode }}</span>
            <span class="ep-name">{{ ep.name ?? 'TBA' }}</span>
            <select class="status" :value="ep.status" @change="setStatus(ep, ($event.target as HTMLSelectElement).value as EpisodeStatus)">
              <option v-for="s in STATUSES" :key="s" :value="s">{{ s }}</option>
            </select>
            <button class="mini" @click="searchEpisode(ep)">Search</button>
          </li>
        </ul>
      </section>
    </template>
  </AppLayout>
</template>

<style scoped>
.head { display: flex; gap: 1rem; align-items: flex-start; }
.overview { margin-top: 0; flex: 1; }
.notice { font-size: 0.85rem; color: var(--accent); margin: 0.25rem 0 0.75rem; }
.season h2 { font-size: 1rem; margin: 1rem 0 0.5rem; }
.ep-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.ep {
  display: grid;
  grid-template-columns: 2rem 1fr auto auto;
  align-items: center;
  gap: 0.5rem;
  background: var(--surface);
  border-radius: var(--radius);
  padding: 0.5rem 0.75rem;
}
.ep-num { color: var(--muted); font-variant-numeric: tabular-nums; }
.ep-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.status { width: auto; padding: 0.25rem 0.4rem; font-size: 0.8rem; text-transform: capitalize; }
.mini { padding: 0.3rem 0.6rem; font-size: 0.75rem; }
.muted { color: var(--muted); }
</style>
