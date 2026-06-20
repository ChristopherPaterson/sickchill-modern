import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { Episode, Show } from '@/api/types'

export const useShowsStore = defineStore('shows', () => {
  const shows = ref<Show[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchShows(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<Show[]>('/shows')
      shows.value = data
    } catch {
      error.value = 'Failed to load shows'
    } finally {
      loading.value = false
    }
  }

  async function fetchShow(id: number): Promise<Show> {
    const { data } = await api.get<Show>(`/shows/${id}`)
    return data
  }

  async function fetchEpisodes(id: number): Promise<Episode[]> {
    const { data } = await api.get<Episode[]>(`/shows/${id}/episodes`)
    return data
  }

  return { shows, loading, error, fetchShows, fetchShow, fetchEpisodes }
})
