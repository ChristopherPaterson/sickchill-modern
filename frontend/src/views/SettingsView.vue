<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <AppLayout title="Settings">
    <div class="card">
      <p class="muted">Signed in as <strong>{{ auth.username ?? 'admin' }}</strong></p>
    </div>
    <p class="muted note">
      Provider, indexer, quality and notification settings will live here, backed
      by the /settings API (key/value store) and the provider registry.
    </p>
    <button class="secondary" @click="logout">Sign out</button>
  </AppLayout>
</template>

<style scoped>
.muted { color: var(--muted); }
.note { font-size: 0.85rem; margin: 1rem 0; }
</style>
