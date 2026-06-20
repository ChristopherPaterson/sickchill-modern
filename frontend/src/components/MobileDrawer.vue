<script setup lang="ts">
import { useRouter } from 'vue-router'
import { MENU, type MenuLink } from '@/menu'
import { useAuthStore } from '@/stores/auth'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const router = useRouter()
const auth = useAuthStore()

function onItem(item: MenuLink) {
  emit('close')
  if (item.action === 'logout') {
    auth.logout()
    router.push({ name: 'login' })
  } else if (item.route) {
    router.push({ name: item.route })
  }
}
</script>

<template>
  <Transition name="drawer">
    <div v-if="open" class="scrim" @click="emit('close')">
      <aside class="drawer" @click.stop>
        <div class="head">
          <span class="brand">SickChill <span>Modern</span></span>
          <button class="close secondary" @click="emit('close')">✕</button>
        </div>

        <div class="scroll">
          <section v-for="group in MENU" :key="group.key" class="group">
            <!-- Direct-link group -->
            <button
              v-if="group.route && !group.children"
              class="row head-row"
              @click="onItem({ label: group.label, icon: group.icon, route: group.route })"
            >
              <span class="icon">{{ group.icon }}</span>{{ group.label }}
            </button>

            <!-- Group with children -->
            <template v-else>
              <div class="group-label">{{ group.label }}</div>
              <button
                v-for="item in group.children"
                :key="item.label"
                class="row"
                @click="onItem(item)"
              >
                <span class="icon">{{ item.icon }}</span>{{ item.label }}
              </button>
            </template>
          </section>
        </div>

        <div class="foot">Signed in as {{ auth.username ?? 'admin' }}</div>
      </aside>
    </div>
  </Transition>
</template>

<style scoped>
.scrim {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  justify-content: flex-end;
}
.drawer {
  width: min(86vw, 360px);
  height: 100%;
  background: var(--bg);
  border-left: 1px solid var(--surface-2);
  display: flex;
  flex-direction: column;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid var(--surface-2);
}
.brand { font-weight: 700; }
.brand span { color: var(--accent); }
.close { padding: 0.4rem 0.7rem; }
.scroll { flex: 1; overflow-y: auto; padding: 0.5rem; }
.group { margin-bottom: 0.5rem; }
.group-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  padding: 0.6rem 0.75rem 0.25rem;
}
.row {
  width: 100%;
  text-align: left;
  background: transparent;
  color: var(--text);
  font-weight: 400;
  padding: 0.7rem 0.75rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.row:hover { background: var(--surface); }
.head-row { font-weight: 600; }
.foot { padding: 0.9rem 1rem; border-top: 1px solid var(--surface-2); color: var(--muted); font-size: 0.85rem; }

.drawer-enter-active, .drawer-leave-active { transition: opacity 0.18s ease; }
.drawer-enter-from, .drawer-leave-to { opacity: 0; }
</style>
