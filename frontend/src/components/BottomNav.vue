<script setup lang="ts">
import { RouterLink } from 'vue-router'

const items = [
  { name: 'shows', label: 'Shows', icon: '📺' },
  { name: 'calendar', label: 'Calendar', icon: '🗓️' },
  { name: 'history', label: 'History', icon: '🕘' },
  { name: 'settings', label: 'Settings', icon: '⚙️' },
]
</script>

<template>
  <nav class="bottom-nav">
    <RouterLink
      v-for="item in items"
      :key="item.name"
      :to="{ name: item.name }"
      class="nav-item"
      active-class="active"
    >
      <span class="icon">{{ item.icon }}</span>
      <span class="label">{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: calc(var(--nav-h) + env(safe-area-inset-bottom));
  padding-bottom: env(safe-area-inset-bottom);
  display: flex;
  background: var(--surface);
  border-top: 1px solid var(--surface-2);
  z-index: 20;
}
.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--muted);
  font-size: 0.7rem;
}
.nav-item .icon { font-size: 1.25rem; }
.nav-item.active { color: var(--accent); }
</style>
