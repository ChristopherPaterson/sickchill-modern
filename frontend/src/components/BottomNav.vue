<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { MENU, MOBILE_PRIMARY } from '@/menu'

defineEmits<{ openMenu: [] }>()

// Primary destinations on the bottom bar; everything else lives in the drawer.
const primary = MOBILE_PRIMARY.map((key) => MENU.find((g) => g.key === key)!).filter(Boolean)
</script>

<template>
  <nav class="bottom-nav">
    <RouterLink
      v-for="group in primary"
      :key="group.key"
      :to="{ name: group.route ?? group.key }"
      class="nav-item"
      active-class="active"
    >
      <span class="icon">{{ group.icon }}</span>
      <span class="label">{{ group.label }}</span>
    </RouterLink>

    <button class="nav-item menu-btn" @click="$emit('openMenu')">
      <span class="icon">☰</span>
      <span class="label">Menu</span>
    </button>
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
  background: transparent;
  border-radius: 0;
}
.nav-item .icon { font-size: 1.25rem; }
.nav-item.active { color: var(--accent); }
.menu-btn { font-weight: 400; }
</style>
