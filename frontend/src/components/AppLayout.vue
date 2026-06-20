<script setup lang="ts">
import { ref } from 'vue'
import BottomNav from './BottomNav.vue'
import MobileDrawer from './MobileDrawer.vue'
import TopNav from './TopNav.vue'
import { useIsDesktop } from '@/composables/useMediaQuery'

defineProps<{ title?: string }>()

// Width-based layout switch (no UA sniffing), reacts live to resize:
//  - desktop: SickChill-style top menu bar with dropdowns
//  - mobile: bottom bar for primary items + full-menu drawer
const isDesktop = useIsDesktop()
const drawerOpen = ref(false)
</script>

<template>
  <div class="app-shell" :class="{ 'is-desktop': isDesktop }">
    <TopNav v-if="isDesktop" />

    <div class="app-main">
      <header v-if="title" class="app-header">{{ title }}</header>
      <main class="app-content">
        <slot />
      </main>
    </div>

    <template v-if="!isDesktop">
      <BottomNav @open-menu="drawerOpen = true" />
      <MobileDrawer :open="drawerOpen" @close="drawerOpen = false" />
    </template>
  </div>
</template>
