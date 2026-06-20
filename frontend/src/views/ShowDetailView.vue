<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { api } from '@/api/client'
import { useShowsStore } from '@/stores/shows'
import type { Episode, Show } from '@/api/types'

const props = defineProps<{ id: string }>()
const store = useShowsStore()

const show = ref<Show | null>(null)
const episodes = ref<Episode[]>([])
const loading = ref(true)

onMounted(async () => {
  const id = Number(props.id)
  show.value = await store.fetchShow(id)
  episodes.value = await store.fetchEpisodes(id)
  loading.value = false
})

async function searchEpisode(ep: Episode) {
  await api.post(`/episodes/${ep.id}/search`)
}

// Group episodes by season for display.
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
      <p class="overview muted">{{ show.overview ?? 'No overview.' }}</p>

      <section v-for="[season, eps] in bySeason()" :key="season" class="season">
        <h2>Season {{ season }}</h2>
        <ul class="ep-list">
          <li v-for="ep in eps" :key="ep.id" class="ep">
            <span class="ep-num">{{ ep.episode }}</span>
            <span class="ep-name">{{ ep.name ?? 'TBA' }}</span>
            <span class="badge" :data-status="ep.status">{{ ep.status }}</span>
            <button class="mini" @click="searchEpisode(ep)">Search</button>
          </li>
        </ul>
      </section>
    </template>
  </AppLayout>
</template>

<style scoped>
.overview { margin-top: 0; }
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
.badge {
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: 6px;
  background: var(--surface-2);
}
.badge[data-status='downloaded'] { background: #14532d; color: var(--ok); }
.badge[data-status='wanted'] { background: #422006; color: #fbbf24; }
.mini { padding: 0.3rem 0.6rem; font-size: 0.75rem; }
.muted { color: var(--muted); }
</style>
