<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { MENU, type MenuGroup, type MenuLink } from '@/menu'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const openKey = ref<string | null>(null)

function toggle(group: MenuGroup) {
  openKey.value = openKey.value === group.key ? null : group.key
}
function close() {
  openKey.value = null
}
function onItem(item: MenuLink) {
  close()
  if (item.action === 'logout') {
    auth.logout()
    router.push({ name: 'login' })
  } else if (item.route) {
    router.push({ name: item.route })
  }
}

// Close dropdowns on outside click / Escape.
function onDocClick(e: MouseEvent) {
  if (!(e.target as HTMLElement).closest('.top-nav')) close()
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}
onMounted(() => {
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onKey)
})
onUnmounted(() => {
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onKey)
})
</script>

<template>
  <header class="top-nav">
    <RouterLink :to="{ name: 'shows' }" class="brand" @click="close">
      SickChill <span>Modern</span>
    </RouterLink>

    <nav class="menu">
      <template v-for="group in MENU" :key="group.key">
        <!-- Direct link (no children) -->
        <RouterLink
          v-if="group.route && !group.children"
          :to="{ name: group.route }"
          class="top-item"
          active-class="active"
          @click="close"
        >
          {{ group.label }}
        </RouterLink>

        <!-- Dropdown group -->
        <div v-else class="group" :class="{ open: openKey === group.key }">
          <button class="top-item" @click.stop="toggle(group)">
            {{ group.label }}
            <span class="caret">▾</span>
          </button>
          <ul v-if="openKey === group.key" class="dropdown">
            <li v-for="item in group.children" :key="item.label">
              <button class="drop-item" @click="onItem(item)">
                <span class="icon">{{ item.icon }}</span>{{ item.label }}
              </button>
            </li>
          </ul>
        </div>
      </template>
    </nav>

    <div class="spacer" />
    <span class="user">{{ auth.username ?? 'admin' }}</span>
  </header>
</template>

<style scoped>
.top-nav {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0 1rem;
  height: 56px;
  background: var(--surface);
  border-bottom: 1px solid var(--surface-2);
}
.brand { font-weight: 700; font-size: 1.05rem; margin-right: 1rem; color: var(--text); }
.brand span { color: var(--accent); }
.menu { display: flex; align-items: center; gap: 0.1rem; }
.group { position: relative; }
.top-item {
  background: transparent;
  color: var(--muted);
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}
.top-item:hover { background: var(--surface-2); color: var(--text); }
.top-item.active { color: var(--accent); }
.group.open .top-item { background: var(--surface-2); color: var(--text); }
.caret { font-size: 0.7rem; opacity: 0.7; }
.dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 230px;
  list-style: none;
  margin: 0;
  padding: 0.35rem;
  background: var(--surface);
  border: 1px solid var(--surface-2);
  border-radius: var(--radius);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}
.drop-item {
  width: 100%;
  text-align: left;
  background: transparent;
  color: var(--text);
  font-weight: 400;
  padding: 0.55rem 0.6rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.drop-item:hover { background: var(--surface-2); }
.spacer { flex: 1; }
.user { color: var(--muted); font-size: 0.85rem; }
</style>
