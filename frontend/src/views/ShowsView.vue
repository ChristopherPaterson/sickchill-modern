<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useShowsStore } from '@/stores/shows'

const store = useShowsStore()
const router = useRouter()

onMounted(() => store.fetchShows())

function open(id: number) {
  router.push({ name: 'show-detail', params: { id } })
}
</script>

<template>
  <AppLayout title="Shows">
    <p v-if="store.loading">Loading…</p>
    <p v-else-if="store.error" class="error">{{ store.error }}</p>
    <p v-else-if="store.shows.length === 0" class="muted">
      No shows yet. Add one to get started.
    </p>

    <div v-else class="show-grid">
      <button
        v-for="show in store.shows"
        :key="show.id"
        class="show-card secondary"
        @click="open(show.id)"
      >
        <div class="poster" :style="show.poster_url ? `background-image:url(${show.poster_url})` : ''" />
        <div class="meta">
          <div class="name">{{ show.name }}</div>
          <div class="sub muted">{{ show.network ?? '—' }} · {{ show.status }}</div>
        </div>
      </button>
    </div>
  </AppLayout>
</template>

<style scoped>
.show-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.75rem;
}
.show-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  text-align: left;
}
.poster {
  aspect-ratio: 2 / 3;
  background: var(--surface-2) center/cover no-repeat;
}
.meta { padding: 0.5rem 0.6rem; }
.name { font-weight: 600; font-size: 0.9rem; }
.sub { font-size: 0.75rem; }
.muted { color: var(--muted); }
.error { color: var(--danger); }
</style>
