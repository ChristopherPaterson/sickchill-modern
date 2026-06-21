<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useShowsStore } from '@/stores/shows'
import type { ShowListItem } from '@/api/types'

const store = useShowsStore()
const router = useRouter()

onMounted(() => store.fetchShows())

type SortKey = 'next_air_date' | 'name' | 'network' | 'status'
const sortKey = ref<SortKey>('name')
const sortAsc = ref(true)

// Filters
const search = ref('')
const statusFilter = ref<'all' | 'continuing' | 'ended'>('all')
const pausedOnly = ref(false)

function sortBy(key: SortKey) {
  if (sortKey.value === key) sortAsc.value = !sortAsc.value
  else {
    sortKey.value = key
    sortAsc.value = true
  }
}

function caret(key: SortKey) {
  if (sortKey.value !== key) return ''
  return sortAsc.value ? ' ▲' : ' ▼'
}

const rows = computed<ShowListItem[]>(() => {
  const q = search.value.trim().toLowerCase()
  const dir = sortAsc.value ? 1 : -1
  return store.shows
    .filter((s) => {
      if (statusFilter.value !== 'all' && s.status !== statusFilter.value) return false
      if (pausedOnly.value && !s.paused) return false
      if (q && !`${s.name} ${s.network ?? ''}`.toLowerCase().includes(q)) return false
      return true
    })
    .sort((a, b) => {
      const k = sortKey.value
      // Nulls (e.g. no next air date) always sort last.
      const av = a[k]
      const bv = b[k]
      if (av == null && bv == null) return 0
      if (av == null) return 1
      if (bv == null) return -1
      const as = av.toString().toLowerCase()
      const bs = bv.toString().toLowerCase()
      return as < bs ? -dir : as > bs ? dir : 0
    })
})

function open(id: number) {
  router.push({ name: 'show-detail', params: { id } })
}

function formatDate(d: string | null): string {
  if (!d) return '—'
  return new Date(d).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })
}

function pct(s: ShowListItem): number {
  return s.episode_count ? Math.round((s.downloaded_count / s.episode_count) * 100) : 0
}
</script>

<template>
  <AppLayout title="Shows">
    <p v-if="store.loading">Loading…</p>
    <p v-else-if="store.error" class="error">{{ store.error }}</p>
    <p v-else-if="store.shows.length === 0" class="muted">No shows yet. Add one to get started.</p>

    <template v-else>
      <div class="toolbar">
        <input v-model="search" class="search" placeholder="Search shows…" />
        <select v-model="statusFilter" class="filter">
          <option value="all">All statuses</option>
          <option value="continuing">Continuing</option>
          <option value="ended">Ended</option>
        </select>
        <label class="paused-toggle"><input v-model="pausedOnly" type="checkbox" /> Paused only</label>
      </div>
      <p class="count muted">{{ rows.length }} of {{ store.shows.length }} shows</p>

      <div class="table-wrap">
        <table class="shows">
          <thead>
            <tr>
              <th class="sortable" @click="sortBy('next_air_date')">Next Ep{{ caret('next_air_date') }}</th>
              <th class="sortable" @click="sortBy('name')">Show{{ caret('name') }}</th>
              <th class="sortable" @click="sortBy('network')">Network{{ caret('network') }}</th>
              <th>Quality</th>
              <th>Downloads</th>
              <th>Active</th>
              <th class="sortable" @click="sortBy('status')">Status{{ caret('status') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in rows" :key="s.id" @click="open(s.id)">
              <td class="muted nowrap">{{ formatDate(s.next_air_date) }}</td>
              <td class="name">{{ s.name }}</td>
              <td class="muted">{{ s.network ?? '—' }}</td>
              <td class="muted">{{ s.quality }}</td>
              <td class="downloads">
                <div class="bar"><div class="fill" :style="{ width: pct(s) + '%' }" /></div>
                <span class="frac">{{ s.downloaded_count }} / {{ s.episode_count }}</span>
              </td>
              <td><span class="badge" :class="s.paused ? 'no' : 'yes'">{{ s.paused ? 'No' : 'Yes' }}</span></td>
              <td><span class="badge" :data-status="s.status">{{ s.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </AppLayout>
</template>

<style scoped>
.toolbar { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; }
.toolbar .search { flex: 1; min-width: 180px; }
.toolbar .filter { width: auto; }
.paused-toggle { display: flex; align-items: center; gap: 0.35rem; font-size: 0.85rem; color: var(--muted); white-space: nowrap; }
.paused-toggle input { width: auto; }
.count { font-size: 0.8rem; margin: 0 0 0.75rem; }

.table-wrap { overflow-x: auto; }
.shows { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.shows th, .shows td { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--surface-2); }
.shows th {
  color: var(--muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em;
  position: sticky; top: 0; background: var(--bg); white-space: nowrap;
}
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--text); }
.shows tbody tr { cursor: pointer; }
.shows tbody tr:hover { background: var(--surface); }
.nowrap { white-space: nowrap; }
.name { font-weight: 600; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.muted { color: var(--muted); }

.downloads { min-width: 130px; }
.bar { height: 6px; border-radius: 3px; background: var(--surface-2); overflow: hidden; margin-bottom: 3px; }
.fill { height: 100%; background: var(--accent); }
.frac { font-size: 0.72rem; color: var(--muted); }

.badge { font-size: 0.72rem; padding: 0.15rem 0.45rem; border-radius: 6px; background: var(--surface-2); text-transform: capitalize; white-space: nowrap; }
.badge[data-status='continuing'] { background: #14361f; color: var(--ok); }
.badge[data-status='ended'] { background: #3a2330; color: #f0a0c0; }
.badge.yes { background: #14361f; color: var(--ok); }
.badge.no { background: #422006; color: #fbbf24; }
.error { color: var(--danger); }
</style>
