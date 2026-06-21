export type ShowStatus = 'continuing' | 'ended' | 'paused' | 'unknown'

export type EpisodeStatus =
  | 'unaired'
  | 'wanted'
  | 'snatched'
  | 'downloaded'
  | 'archived'
  | 'skipped'
  | 'ignored'
  | 'failed'

export interface Show {
  id: number
  tvdb_id: number | null
  tmdb_id: number | null
  imdb_id: string | null
  name: string
  overview: string | null
  network: string | null
  status: ShowStatus
  quality: string
  language: string
  paused: boolean
  location: string | null
  poster_url: string | null
}

export interface Episode {
  id: number
  show_id: number
  season: number
  episode: number
  name: string | null
  air_date: string | null
  status: EpisodeStatus
  quality: string | null
}

export interface ShowStats {
  total: number
  downloaded: number
  wanted: number
  snatched: number
}

/** Row in the show-list table (SickChill-style columns). */
export interface ShowListItem {
  id: number
  name: string
  network: string | null
  quality: string
  status: ShowStatus
  paused: boolean
  episode_count: number
  downloaded_count: number
  next_air_date: string | null
}

export interface HistoryEntry {
  id: number
  show_id: number | null
  action: string
  provider: string | null
  release_name: string | null
  season: number | null
  episode: number | null
}
