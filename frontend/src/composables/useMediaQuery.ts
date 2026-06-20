import { onUnmounted, ref, type Ref } from 'vue'

/**
 * Reactive matchMedia. Returns a ref that tracks whether `query` matches the
 * current viewport, updating live on resize / orientation change.
 *
 * Initialised synchronously so the correct layout renders on first paint (no
 * mobile-to-desktop flash). Guarded for non-browser contexts.
 */
export function useMediaQuery(query: string): Ref<boolean> {
  const supported = typeof window !== 'undefined' && 'matchMedia' in window
  const mql = supported ? window.matchMedia(query) : null
  const matches = ref(mql ? mql.matches : false)

  if (mql) {
    const update = (e: MediaQueryListEvent) => (matches.value = e.matches)
    mql.addEventListener('change', update)
    onUnmounted(() => mql.removeEventListener('change', update))
  }

  return matches
}

/** True on tablet/desktop-width viewports. The single source of truth for the
 *  desktop-vs-mobile layout switch. */
export function useIsDesktop(): Ref<boolean> {
  return useMediaQuery('(min-width: 1024px)')
}
